from pathlib import Path
from typing import List, Dict, Any, Optional

from app.config import settings
from app.database.calibre_db import CalibreDB
from app.database.postgres_db import postgres_db
from app.services.conversion_service import conversion_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BookService:
    """Service for managing book operations and synchronization."""
    
    def __init__(self):
        self.calibre_db = CalibreDB()
        self.library_path = Path(settings.CALIBRE_LIBRARY_PATH)
    
    def sync_books_from_calibre(self) -> int:
        """Synchronize books from Calibre to PostgreSQL, including removal of deleted books."""
        try:
            # Get all books from Calibre
            calibre_books = self.calibre_db.get_all_books()
            calibre_ids = {book['calibre_id'] for book in calibre_books}
            
            synced_count = 0
            removed_count = 0
            
            for book in calibre_books:
                calibre_id = book['calibre_id']
                
                # Get file path from Calibre
                file_path = self.calibre_db.get_book_file_path(calibre_id)
                if not file_path:
                    logger.warning(f"No file path found for book {calibre_id} - Title: {book['title']}")
                    continue
                
                # Build full path
                full_path = self.library_path / file_path
                
                # Check if file exists
                if not full_path.exists():
                    logger.warning(f"File not found for book {calibre_id} - Title: {book['title']}")
                    continue
                
                # Get additional metadata
                tags = self.calibre_db.get_book_tags(calibre_id)
                publishers = self.calibre_db.get_book_publishers(calibre_id)
                
                # Build metadata dict
                metadata = {
                    'uuid': book.get('uuid'),
                    'pubdate': book.get('pubdate'),
                    'series_index': book.get('series_index'),
                    'tags': tags,
                    'publishers': publishers,
                    'last_modified': book.get('last_modified')
                }
                
                # Insert or update in PostgreSQL
                postgres_db.insert_book(
                    calibre_id=calibre_id,
                    title=book['title'],
                    file_path=str(full_path),
                    author=book.get('authors'),
                    metadata=metadata
                )
                synced_count += 1
            
            # Remove books that are no longer in Calibre
            postgres_books = postgres_db.get_all_books(limit=1000000, offset=0)
            for postgres_book in postgres_books:
                postgres_calibre_id = postgres_book.get('calibre_id')
                if postgres_calibre_id not in calibre_ids:
                    # Book was removed from Calibre, remove from PostgreSQL
                    book_id = postgres_book.get('id')
                    logger.info(f"Removing book {book_id} (Calibre ID: {postgres_calibre_id}) - {postgres_book.get('title')}")
                    self._remove_book_from_postgres(book_id)
                    removed_count += 1
            
            logger.info(f"Synchronized {synced_count} books from Calibre to PostgreSQL")
            logger.info(f"Removed {removed_count} books that were deleted from Calibre")
            
            # Update the mtime after successful sync
            from pathlib import Path
            calibre_db_path = Path(settings.CALIBRE_DB_PATH)
            if calibre_db_path.exists():
                postgres_db.set_calibre_db_mtime(calibre_db_path.stat().st_mtime)
            
            return synced_count
        except Exception as e:
            logger.error(f"Error syncing books from Calibre: {e}")
            raise
    
    def _remove_book_from_postgres(self, book_id: int):
        """Remove a book and its embeddings from PostgreSQL."""
        try:
            # Delete book chunks (including embeddings)
            with postgres_db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM book_chunks WHERE book_id = %s", (book_id,))
                chunks_deleted = cursor.rowcount
                logger.info(f"Deleted {chunks_deleted} chunks for book {book_id}")
            
            # Delete book
            with postgres_db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
                logger.info(f"Deleted book {book_id} from PostgreSQL")
        except Exception as e:
            logger.error(f"Error removing book {book_id} from PostgreSQL: {e}")
            raise
    
    def get_book(self, book_id: int) -> Optional[Dict[str, Any]]:
        """Get a book by internal PostgreSQL ID."""
        return postgres_db.get_book_by_id(book_id)
    
    def get_book_by_calibre_id(self, calibre_id: int) -> Optional[Dict[str, Any]]:
        """Get a book by Calibre ID."""
        return postgres_db.get_book_by_calibre_id(calibre_id)
    
    def get_all_books(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all books with pagination."""
        logger.info(f"BookService.get_all_books called with limit={limit}, offset={offset}")
        books = postgres_db.get_all_books(limit, offset)
        logger.info(f"BookService.get_all_books returned {len(books)} books")
        return books
    
    def search_books(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search books by title, author, or metadata."""
        return postgres_db.search_books(query, limit)
    
    def get_book_pdf_path(self, book_id: int) -> Optional[Path]:
        """Get the PDF file path for a book."""
        book = postgres_db.get_book_by_id(book_id)
        if book:
            return Path(book['file_path'])
        return None
    
    def get_book_cover(self, book_id: int) -> Optional[bytes]:
        """Get the cover image for a book."""
        pdf_path = self.get_book_pdf_path(book_id)
        if pdf_path and pdf_path.exists():
            return conversion_service.extract_cover_image(pdf_path)
        return None
    
    def get_book_pdf(self, book_id: int) -> Optional[bytes]:
        """Get the PDF file for a book."""
        pdf_path = self.get_book_pdf_path(book_id)
        if pdf_path and pdf_path.exists():
            return conversion_service.get_pdf_bytes(pdf_path)
        return None
    
    def get_book_page_pdf(self, book_id: int, page_num: int) -> Optional[bytes]:
        """Get a specific page as PDF."""
        pdf_path = self.get_book_pdf_path(book_id)
        if pdf_path and pdf_path.exists():
            # For now, return the full PDF
            # TODO: Implement single page extraction
            return conversion_service.get_pdf_bytes(pdf_path)
        return None
    
    def get_book_markdown(self, book_id: int) -> Optional[str]:
        """Get the book content as Markdown."""
        pdf_path = self.get_book_pdf_path(book_id)
        if pdf_path and pdf_path.exists():
            return conversion_service.pdf_to_markdown(pdf_path)
        return None
    
    def get_book_page_markdown(self, book_id: int, page_num: int) -> Optional[str]:
        """Get a specific page as Markdown."""
        pdf_path = self.get_book_pdf_path(book_id)
        if pdf_path and pdf_path.exists():
            return conversion_service.pdf_page_to_markdown(pdf_path, page_num)
        return None
    
    def get_book_page_count(self, book_id: int) -> int:
        """Get the number of pages in a book."""
        pdf_path = self.get_book_pdf_path(book_id)
        if pdf_path and pdf_path.exists():
            return conversion_service.get_pdf_page_count(pdf_path)
        return 0


book_service = BookService()
