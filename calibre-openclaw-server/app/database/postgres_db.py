import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import json

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PostgreSQLDB:
    """Interface for PostgreSQL database operations."""
    
    def __init__(self):
        self._pool = None
    
    def initialize_pool(self):
        """Initialize connection pool."""
        if self._pool is None:
            self._pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=settings.postgres_dsn
            )
            logger.info("PostgreSQL connection pool initialized")
            # Ensure settings table exists
            self._ensure_settings_table()
            # Ensure embedding bookkeeping columns exist
            self._ensure_embeddings_schema()
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool."""
        if self._pool is None:
            self.initialize_pool()
        
        conn = self._pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            self._pool.putconn(conn)
    
    def close_pool(self):
        """Close all connections in the pool."""
        if self._pool:
            self._pool.closeall()
            self._pool = None
            logger.info("PostgreSQL connection pool closed")
    
    def _ensure_settings_table(self):
        """Ensure the settings table exists."""
        query = """
        CREATE TABLE IF NOT EXISTS settings (
            key VARCHAR(255) PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            logger.info("Settings table ensured")
    
    def _ensure_embeddings_schema(self):
        """Ensure embedding bookkeeping columns exist (idempotent migration)."""
        query = """
        ALTER TABLE book_chunks
            ADD COLUMN IF NOT EXISTS embedding_model TEXT
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                logger.info("book_chunks.embedding_model column ensured")
        except Exception as e:
            # book_chunks may not exist yet on a fresh database; log and continue.
            logger.warning(f"Could not ensure embeddings schema (will retry later): {e}")
    
    # Generic settings helpers
    def get_setting(self, key: str) -> Optional[str]:
        """Get a raw setting value by key."""
        query = "SELECT value FROM settings WHERE key = %s"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (key,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def set_setting(self, key: str, value: str):
        """Insert or update a setting value by key."""
        query = """
        INSERT INTO settings (key, value)
        VALUES (%s, %s)
        ON CONFLICT (key)
        DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (key, str(value)))
            logger.info(f"Setting '{key}' updated")
    
    def get_embedding_column_dimension(self) -> Optional[int]:
        """Return the declared dimension of book_chunks.embedding (pgvector typmod)."""
        query = """
        SELECT a.atttypmod
        FROM pg_attribute a
        JOIN pg_class c ON a.attrelid = c.oid
        WHERE c.relname = 'book_chunks' AND a.attname = 'embedding'
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            if result and result[0] and result[0] > 0:
                # For pgvector, atttypmod stores the dimension directly.
                return int(result[0])
            return None
    
    def invalidate_all_embeddings(self, new_dimension: Optional[int] = None) -> int:
        """Clear all stored embeddings so they can be regenerated.

        If ``new_dimension`` differs from the current column dimension, the
        embedding column type is altered to the new dimension. Completed/failed
        queue items are reset to pending so the worker reprocesses every book.
        Returns the number of chunks that had their embedding cleared.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE book_chunks SET embedding = NULL, embedding_model = NULL "
                "WHERE embedding IS NOT NULL"
            )
            cleared = cursor.rowcount

            current_dim = self.get_embedding_column_dimension()
            if new_dimension and current_dim and new_dimension != current_dim:
                logger.warning(
                    "Altering book_chunks.embedding dimension from %s to %s",
                    current_dim,
                    new_dimension,
                )
                cursor.execute(
                    f"ALTER TABLE book_chunks "
                    f"ALTER COLUMN embedding TYPE vector({int(new_dimension)})"
                )

            cursor.execute(
                "UPDATE processing_queue SET status = 'pending', "
                "completed_at = NULL, error_message = NULL "
                "WHERE status IN ('completed', 'failed')"
            )
            requeued = cursor.rowcount

            logger.warning(
                "Invalidated %s embedding(s) and reset %s queue item(s) to pending",
                cleared,
                requeued,
            )
            return cleared
    
    def get_calibre_db_mtime(self) -> Optional[float]:
        """Get the last modification time of Calibre metadata.db stored in PostgreSQL."""
        query = "SELECT value FROM settings WHERE key = 'calibre_db_mtime'"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                return float(result[0])
            return None
    
    def set_calibre_db_mtime(self, mtime: float):
        """Store the last modification time of Calibre metadata.db."""
        query = """
        INSERT INTO settings (key, value) 
        VALUES ('calibre_db_mtime', %s)
        ON CONFLICT (key) 
        DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (str(mtime),))
            logger.info(f"Calibre DB mtime updated to {mtime}")
    
    def get_last_storage_calc_time(self) -> Optional[float]:
        """Get the last storage calculation timestamp."""
        query = "SELECT value FROM settings WHERE key = 'last_storage_calc'"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                return float(result[0])
            return None
    
    def set_last_storage_calc_time(self, timestamp: float):
        """Store the last storage calculation timestamp."""
        query = """
        INSERT INTO settings (key, value) 
        VALUES ('last_storage_calc', %s)
        ON CONFLICT (key) 
        DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (str(timestamp),))
            logger.info(f"Last storage calc time updated to {timestamp}")
    
    # Books operations
    def insert_book(self, calibre_id: int, title: str, file_path: str, 
                    author: Optional[str] = None, metadata: Optional[Dict] = None) -> int:
        """Insert a new book into the database."""
        query = """
        INSERT INTO books (calibre_id, title, file_path, author, metadata)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (calibre_id) 
        DO UPDATE SET 
            title = EXCLUDED.title,
            file_path = EXCLUDED.file_path,
            author = EXCLUDED.author,
            metadata = EXCLUDED.metadata,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        # Convert metadata dict to JSON for PostgreSQL
        metadata_json = json.dumps(metadata) if metadata else None
        
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (calibre_id, title, file_path, author, metadata_json))
            result = cursor.fetchone()
            logger.info(f"Book '{title}' inserted/updated with ID {result['id']}")
            return result['id']
    
    def get_book_by_id(self, book_id: int) -> Optional[Dict[str, Any]]:
        """Get a book by internal ID."""
        query = "SELECT * FROM books WHERE id = %s"
        
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (book_id,))
            return cursor.fetchone()
    
    def get_book_by_calibre_id(self, calibre_id: int) -> Optional[Dict[str, Any]]:
        """Get a book by Calibre ID."""
        query = "SELECT * FROM books WHERE calibre_id = %s"
        
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (calibre_id,))
            return cursor.fetchone()
    
    def get_all_books(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all books with pagination."""
        query = "SELECT * FROM books ORDER BY title LIMIT %s OFFSET %s"
        
        logger.info(f"PostgreSQLDB.get_all_books: executing query with limit={limit}, offset={offset}")
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (limit, offset))
            books = cursor.fetchall()
            logger.info(f"PostgreSQLDB.get_all_books: retrieved {len(books)} books")
            return books
    
    def search_books(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search books by title, author, or metadata."""
        search_query = """
        SELECT * FROM books 
        WHERE title ILIKE %s 
           OR author ILIKE %s 
           OR metadata::text ILIKE %s
        ORDER BY title
        LIMIT %s
        """
        
        pattern = f"%{query}%"
        
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(search_query, (pattern, pattern, pattern, limit))
            return cursor.fetchall()
    
    # Book chunks operations
    def insert_chunk(self, book_id: int, chunk_index: int, content: str, 
                     embedding: Optional[List[float]] = None,
                     embedding_model: Optional[str] = None) -> int:
        """Insert a book chunk with optional embedding and the model used."""
        query = """
        INSERT INTO book_chunks (book_id, chunk_index, content, embedding, embedding_model)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (book_id, chunk_index)
        DO UPDATE SET 
            content = EXCLUDED.content,
            embedding = EXCLUDED.embedding,
            embedding_model = EXCLUDED.embedding_model
        RETURNING id
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (book_id, chunk_index, content, embedding, embedding_model))
            result = cursor.fetchone()
            return result['id']
    
    def get_chunks_by_book_id(self, book_id: int) -> List[Dict[str, Any]]:
        """Get all chunks for a book."""
        query = """
        SELECT * FROM book_chunks 
        WHERE book_id = %s 
        ORDER BY chunk_index
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (book_id,))
            return cursor.fetchall()
    
    def get_chunk_count(self, book_id: int) -> int:
        """Get the number of chunks for a book."""
        query = "SELECT COUNT(*) as count FROM book_chunks WHERE book_id = %s"
        
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (book_id,))
            result = cursor.fetchone()
            return result['count']

    def delete_chunks_for_book(self, book_id: int) -> int:
        """Delete all chunks and embeddings for a book."""
        query = "DELETE FROM book_chunks WHERE book_id = %s"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (book_id,))
            deleted = cursor.rowcount
            logger.info(f"Deleted {deleted} chunk(s) for book {book_id}")
            return deleted
    
    def has_embeddings(self, book_id: int) -> bool:
        """Check if a book has embeddings generated."""
        query = """
        SELECT COUNT(*) as count 
        FROM book_chunks 
        WHERE book_id = %s AND embedding IS NOT NULL
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (book_id,))
            result = cursor.fetchone()
            return result['count'] > 0
    
    # Semantic search
    def semantic_search(self, query_embedding: List[float], limit: int = 10, 
                        threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Search for similar content using vector similarity."""
        query = """
        SELECT 
            bc.id,
            bc.book_id,
            bc.chunk_index,
            bc.content,
            b.title,
            b.author,
            1 - (bc.embedding <=> %s) as similarity
        FROM book_chunks bc
        JOIN books b ON bc.book_id = b.id
        WHERE bc.embedding IS NOT NULL
        ORDER BY bc.embedding <=> %s
        LIMIT %s
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (query_embedding, query_embedding, limit))
            results = cursor.fetchall()
            
            # Filter by threshold
            filtered = [r for r in results if r['similarity'] >= threshold]
            logger.info(f"Semantic search returned {len(filtered)} results above threshold {threshold}")
            return filtered
    
    # Processing queue operations
    def add_to_queue(self, book_id: int, priority: int = 0) -> int:
        """Add a book to the processing queue."""
        query = """
        INSERT INTO processing_queue (book_id, status, priority)
        VALUES (%s, 'pending', %s)
        RETURNING id
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (book_id, priority))
            result = cursor.fetchone()
            logger.info(f"Book {book_id} added to processing queue with ID {result['id']}")
            return result['id']
    
    def get_queue_status(self, book_id: int) -> Optional[Dict[str, Any]]:
        """Get the processing status for a book."""
        query = """
        SELECT * FROM processing_queue 
        WHERE book_id = %s 
        ORDER BY created_at DESC 
        LIMIT 1
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (book_id,))
            return cursor.fetchone()
    
    def update_queue_status(self, queue_id: int, status: str, 
                           error_message: Optional[str] = None):
        """Update the status of a queue item."""
        query = """
        UPDATE processing_queue 
        SET status = %s, 
            error_message = %s,
            completed_at = CASE WHEN %s IN ('completed', 'failed') THEN CURRENT_TIMESTAMP ELSE NULL END
        WHERE id = %s
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (status, error_message, status, queue_id))
            logger.info(f"Queue item {queue_id} updated to status: {status}")
    
    def get_pending_queue_items(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get pending items from the processing queue."""
        query = """
        SELECT pq.*, b.title 
        FROM processing_queue pq
        JOIN books b ON pq.book_id = b.id
        WHERE pq.status = 'pending'
        ORDER BY pq.priority DESC, pq.created_at ASC
        LIMIT %s
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (limit,))
            return cursor.fetchall()

    def get_random_book_without_embeddings(self) -> Optional[Dict[str, Any]]:
        """Get one random book that has not been embedded yet."""
        query = """
        SELECT b.*
        FROM books b
        WHERE NOT EXISTS (
            SELECT 1
            FROM book_chunks bc
            WHERE bc.book_id = b.id
              AND bc.embedding IS NOT NULL
        )
        AND NOT EXISTS (
            SELECT 1
            FROM processing_queue pq
            WHERE pq.book_id = b.id
              AND pq.status = 'failed'
        )
        ORDER BY RANDOM()
        LIMIT 1
        """

        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query)
            return cursor.fetchone()


# Global instance
postgres_db = PostgreSQLDB()
