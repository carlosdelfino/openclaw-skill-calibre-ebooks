import httpx
from typing import List, Optional
from pathlib import Path

from app.config import settings
from app.database.postgres_db import postgres_db
from app.services.conversion_service import conversion_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating and managing embeddings using Ollama."""
    
    def __init__(self):
        self.client = httpx.Client(timeout=300.0)  # 5 minute timeout for large documents
    
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
            logger.info(f"Generated embedding for text ({len(text)} chars) -> vector size: {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings_for_book(self, book_id: int, pdf_path: Path) -> int:
        """Generate and store embeddings for all chunks of a book."""
        try:
            # Convert PDF to text
            text = conversion_service.pdf_to_text(pdf_path)
            
            # Split into chunks
            chunks = conversion_service.chunk_text(text)
            
            # Generate embeddings for each chunk
            for idx, chunk in enumerate(chunks):
                embedding = self.generate_embedding(chunk)
                postgres_db.insert_chunk(book_id, idx, chunk, embedding)
            
            logger.info(f"Generated {len(chunks)} embeddings for book {book_id}")
            return len(chunks)
        except Exception as e:
            logger.error(f"Error generating embeddings for book {book_id}: {e}")
            raise
    
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
            
            logger.info(f"Semantic search for '{query}' returned {len(results)} results")
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
    
    def process_queue_item(self, queue_id: int, book_id: int, pdf_path: Path):
        """Process a single queue item (background task)."""
        try:
            # Update status to processing
            postgres_db.update_queue_status(queue_id, 'processing')
            
            # Generate embeddings
            chunk_count = self.generate_embeddings_for_book(book_id, pdf_path)
            
            # Update status to completed
            postgres_db.update_queue_status(queue_id, 'completed')
            
            logger.info(f"Successfully processed queue item {queue_id} for book {book_id} ({chunk_count} chunks)")
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
