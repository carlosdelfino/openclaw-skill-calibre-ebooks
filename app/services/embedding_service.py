import httpx
from typing import List, Optional
from pathlib import Path

from app.config import settings
from app.database.postgres_db import postgres_db
from app.services.conversion_service import conversion_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Setting keys used to track which embedding configuration produced the data.
SIGNATURE_KEY = "embedding_signature"
MODEL_KEY = "embedding_model"
DIMENSION_KEY = "embedding_dimension"


class EmptyDocumentError(Exception):
    """Raised when a document yields no usable text to embed."""


class ContextLengthExceededError(Exception):
    """Raised when a chunk is too long for the embedding model's context window.

    Token-dense text (e.g. dense math notation) can produce far more tokens than
    its character count suggests, overflowing the model's context length even
    when CHUNK_SIZE looks safe. Callers can catch this and split the text.
    """


class EmbeddingService:
    """Service for generating and managing embeddings using Ollama."""
    
    def __init__(self):
        self.client = httpx.Client(timeout=300.0)  # 5 minute timeout for large documents
        self._dimension: Optional[int] = None
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text using Ollama."""
        try:
            response = self.client.post(
                f"{settings.OLLAMA_HOST}/api/embeddings",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": text
                }
            )
            response.raise_for_status()
            data = response.json()
            embedding = data.get("embedding", [])
            if not embedding:
                raise ValueError(
                    f"Ollama returned an empty embedding for model "
                    f"'{settings.OLLAMA_MODEL}' (is the model pulled and running?)"
                )
            logger.info(f"Generated embedding for text ({len(text)} chars) -> vector size: {len(embedding)}")
            return embedding
        except httpx.HTTPStatusError as e:
            # Surface the real Ollama error body, which raise_for_status hides.
            body = ""
            try:
                body = e.response.text
            except Exception:
                pass
            if "context length" in body.lower() or "exceeds" in body.lower():
                raise ContextLengthExceededError(
                    f"Chunk of {len(text)} chars exceeds the model context window: {body}"
                ) from e
            logger.error(f"Error generating embedding: {e} - response body: {body}")
            raise
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def get_model_dimension(self) -> int:
        """Probe the active Ollama model to discover its embedding dimension."""
        if self._dimension is None:
            probe = self.generate_embedding("dimension probe")
            self._dimension = len(probe)
            logger.info(
                f"Embedding model '{settings.OLLAMA_MODEL}' produces "
                f"{self._dimension}-dimensional vectors"
            )
        return self._dimension
    
    def _build_signature(self, dimension: int) -> str:
        """Build a signature describing the current embedding configuration.

        Any change to this signature (model, vector dimension, chunk settings or
        the manual EMBEDDING_VERSION) means stored embeddings are stale and must
        be regenerated.
        """
        return (
            f"model={settings.OLLAMA_MODEL}"
            f"|dim={dimension}"
            f"|chunk={settings.CHUNK_SIZE}"
            f"|overlap={settings.CHUNK_OVERLAP}"
            f"|v={settings.EMBEDDING_VERSION}"
        )
    
    def get_version_info(self) -> dict:
        """Return the current and stored embedding configuration signatures."""
        stored_sig = postgres_db.get_setting(SIGNATURE_KEY)
        info = {
            "model": settings.OLLAMA_MODEL,
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
            "embedding_version": settings.EMBEDDING_VERSION,
            "stored_signature": stored_sig,
            "stored_model": postgres_db.get_setting(MODEL_KEY),
            "stored_dimension": postgres_db.get_setting(DIMENSION_KEY),
        }
        try:
            dimension = self.get_model_dimension()
            info["dimension"] = dimension
            info["current_signature"] = self._build_signature(dimension)
            info["up_to_date"] = stored_sig == info["current_signature"]
        except Exception as e:
            info["dimension"] = None
            info["current_signature"] = None
            info["up_to_date"] = None
            info["error"] = str(e)
        return info
    
    def _store_signature(self, dimension: int, signature: str):
        postgres_db.set_setting(SIGNATURE_KEY, signature)
        postgres_db.set_setting(MODEL_KEY, settings.OLLAMA_MODEL)
        postgres_db.set_setting(DIMENSION_KEY, str(dimension))
    
    def reconcile_embedding_version(self) -> dict:
        """Ensure stored embeddings match the active embedding configuration.

        If the configuration signature changed (e.g. a new embedding LLM), every
        stored embedding is invalidated and reset so the worker regenerates it
        with the new model. On first run the current signature is recorded as a
        baseline without touching existing data.
        """
        try:
            dimension = self.get_model_dimension()
        except Exception as e:
            logger.error(
                "Could not probe embedding model; skipping version reconciliation: %s",
                e,
            )
            return {"changed": False, "error": str(e)}

        current_sig = self._build_signature(dimension)
        stored_sig = postgres_db.get_setting(SIGNATURE_KEY)

        if stored_sig is None:
            self._store_signature(dimension, current_sig)
            logger.info("Embedding signature baseline recorded: %s", current_sig)
            return {"changed": False, "baseline": True, "signature": current_sig}

        if stored_sig == current_sig:
            logger.info("Embedding signature unchanged: %s", current_sig)
            return {"changed": False, "signature": current_sig}

        logger.warning(
            "Embedding configuration changed; invalidating all embeddings.\n"
            "  old: %s\n  new: %s",
            stored_sig,
            current_sig,
        )
        invalidated = postgres_db.invalidate_all_embeddings(dimension)
        self._store_signature(dimension, current_sig)
        logger.warning(
            "Invalidated %s embedding(s); they will be regenerated by the worker.",
            invalidated,
        )
        return {
            "changed": True,
            "invalidated": invalidated,
            "old_signature": stored_sig,
            "new_signature": current_sig,
        }
    
    def generate_embeddings_for_book(self, book_id: int, pdf_path: Path) -> int:
        """Generate and store embeddings for all chunks of a book."""
        try:
            # Convert PDF to text
            text = conversion_service.pdf_to_text(pdf_path)
            
            # Split into chunks (empty/whitespace-only chunks are dropped)
            chunks = conversion_service.chunk_text(text)
            if not chunks:
                raise EmptyDocumentError(
                    f"Book {book_id} produced no usable text (scanned PDF needing OCR?)"
                )
            
            expected_dim = self.get_model_dimension()
            
            # Generate embeddings for each chunk, validating dimensions.
            # Token-dense chunks (e.g. dense math) may overflow the model's
            # context window even when their character count is within
            # CHUNK_SIZE; those are split and retried instead of failing the
            # whole book.
            stored = 0
            for chunk in chunks:
                stored += self._embed_and_store_chunk(
                    book_id, stored, chunk, expected_dim
                )
            
            logger.info(f"Generated {stored} embeddings for book {book_id}")
            return stored
        except Exception as e:
            logger.error(f"Error generating embeddings for book {book_id}: {e}")
            raise

    def _embed_and_store_chunk(
        self,
        book_id: int,
        next_index: int,
        chunk: str,
        expected_dim: int,
        min_chars: int = 80,
        depth: int = 0,
    ) -> int:
        """Embed and store a single chunk, splitting it on context overflow.

        Returns the number of embeddings stored (>1 when the chunk had to be
        split). When a fragment is still too dense to embed even at the minimum
        size, it is skipped (logged) rather than aborting the whole book.
        """
        try:
            embedding = self.generate_embedding(chunk)
        except ContextLengthExceededError:
            if len(chunk) <= min_chars or depth >= 12:
                logger.warning(
                    "Skipping un-embeddable fragment for book %s "
                    "(%s chars still exceeds context window after splitting)",
                    book_id,
                    len(chunk),
                )
                return 0
            left, right = self._split_text(chunk)
            logger.info(
                "Chunk for book %s exceeded context window; splitting "
                "%s chars -> %s + %s chars (depth=%s)",
                book_id,
                len(chunk),
                len(left),
                len(right),
                depth + 1,
            )
            stored = self._embed_and_store_chunk(
                book_id, next_index, left, expected_dim, min_chars, depth + 1
            )
            stored += self._embed_and_store_chunk(
                book_id, next_index + stored, right, expected_dim, min_chars, depth + 1
            )
            return stored

        if len(embedding) != expected_dim:
            raise ValueError(
                f"Embedding dimension mismatch for book {book_id} "
                f"(got {len(embedding)}, expected {expected_dim}). "
                f"Model '{settings.OLLAMA_MODEL}' may have changed."
            )
        postgres_db.insert_chunk(
            book_id, next_index, chunk, embedding, settings.OLLAMA_MODEL
        )
        return 1

    @staticmethod
    def _split_text(text: str) -> tuple[str, str]:
        """Split text near the middle, preferring a whitespace boundary."""
        mid = len(text) // 2
        boundary = text.rfind(" ", 0, mid)
        if boundary <= 0:
            boundary = text.find(" ", mid)
        if boundary <= 0:
            boundary = mid
        return text[:boundary].strip(), text[boundary:].strip()
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for a search query."""
        return self.generate_embedding(query)
    
    def search_similar_content(self, query: str, limit: int = 10, 
                               threshold: float = None) -> List[dict]:
        """Search for similar content using semantic search."""
        threshold = threshold or settings.SIMILARITY_THRESHOLD
        
        try:
            # Generate embedding for query
            query_embedding = self.generate_query_embedding(query)
            
            # Perform semantic search in PostgreSQL
            results = postgres_db.semantic_search(query_embedding, limit, threshold)
            
            logger.info(
                "Semantic search returned %s results",
                len(results),
                extra={"operation": "semantic_search", "query_length": len(query or "")},
            )
            return results
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            raise
    
    def check_embeddings_status(self, book_id: int) -> dict:
        """Check if embeddings are ready for a book."""
        try:
            has_embeddings = postgres_db.has_embeddings(book_id)
            chunk_count = postgres_db.get_chunk_count(book_id)
            
            return {
                "book_id": book_id,
                "has_embeddings": has_embeddings,
                "chunk_count": chunk_count,
                "ready": has_embeddings and chunk_count > 0
            }
        except Exception as e:
            logger.error(f"Error checking embeddings status for book {book_id}: {e}")
            return {
                "book_id": book_id,
                "has_embeddings": False,
                "chunk_count": 0,
                "ready": False,
                "error": str(e)
            }
    
    def queue_embedding_generation(self, book_id: int, pdf_path: Path) -> dict:
        """Queue a book for embedding generation."""
        try:
            # Check if already queued
            existing = postgres_db.get_queue_status(book_id)
            if existing and existing['status'] in ['pending', 'processing']:
                return {
                    "book_id": book_id,
                    "status": "already_queued",
                    "queue_id": existing['id'],
                    "queue_status": existing['status']
                }
            
            # Add to queue
            queue_id = postgres_db.add_to_queue(book_id)
            
            logger.info(f"Book {book_id} queued for embedding generation (queue_id: {queue_id})")
            return {
                "book_id": book_id,
                "status": "queued",
                "queue_id": queue_id
            }
        except Exception as e:
            logger.error(f"Error queuing embedding generation for book {book_id}: {e}")
            raise
    
    def process_queue_item(self, queue_id: int, book_id: int, pdf_path: Path) -> int:
        """Process a single queue item (background task)."""
        try:
            # Update status to processing
            postgres_db.update_queue_status(queue_id, 'processing')
            
            # Generate embeddings
            chunk_count = self.generate_embeddings_for_book(book_id, pdf_path)
            
            # Update status to completed
            postgres_db.update_queue_status(queue_id, 'completed')
            
            logger.info(f"Successfully processed queue item {queue_id} for book {book_id} ({chunk_count} chunks)")
            return chunk_count
        except Exception as e:
            # Update status to failed
            postgres_db.update_queue_status(queue_id, 'failed', str(e))
            logger.error(f"Failed to process queue item {queue_id} for book {book_id}: {e}")
            raise
    
    def get_queue_status(self, book_id: int) -> Optional[dict]:
        """Get the current queue status for a book."""
        return postgres_db.get_queue_status(book_id)
    
    def get_all_queue_items(self, limit: int = 20) -> List[dict]:
        """Get all queue items."""
        return postgres_db.get_pending_queue_items(limit)


embedding_service = EmbeddingService()
