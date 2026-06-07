import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

FORMAT_PRIORITY = ["PDF", "EPUB", "AZW3", "MOBI", "DJVU", "FB2", "TXT", "RTF", "DOCX", "HTMLZ"]


@contextmanager
def get_calibre_db():
    """Context manager for readonly Calibre database connection without file locking."""
    db_path = Path(settings.CALIBRE_DB_PATH)
    if not db_path.exists():
        raise FileNotFoundError(f"Calibre database not found at {db_path}")
    
    # Use read-only mode with no locking to allow external modifications
    # mode=ro: read-only
    # nolock=1: disable file locking (SQLite-specific)
    # immutable=1: treat database as read-only (optimization)
    conn = sqlite3.connect(
        f"file:{db_path}?mode=ro&nolock=1&immutable=1",
        uri=True,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class CalibreDB:
    """Interface for readonly access to Calibre metadata.db."""
    
    @staticmethod
    def get_all_books() -> List[Dict[str, Any]]:
        """Get all books from Calibre database."""
        query = """
        SELECT 
            b.id as calibre_id,
            b.title,
            b.path,
            b.uuid,
            GROUP_CONCAT(a.name, ', ') as authors,
            b.pubdate,
            b.series_index,
            b.last_modified
        FROM books b
        LEFT JOIN books_authors_link bal ON b.id = bal.book
        LEFT JOIN authors a ON bal.author = a.id
        GROUP BY b.id
        ORDER BY b.title
        """
        
        try:
            with get_calibre_db() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                books = [dict(row) for row in cursor.fetchall()]
                logger.info(f"Retrieved {len(books)} books from Calibre DB")
                return books
        except Exception as e:
            logger.error(f"Error retrieving books from Calibre DB: {e}")
            raise
    
    @staticmethod
    def get_book_by_id(calibre_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific book by Calibre ID."""
        query = """
        SELECT 
            b.id as calibre_id,
            b.title,
            b.path,
            b.uuid,
            GROUP_CONCAT(a.name, ', ') as authors,
            b.pubdate,
            b.series_index,
            b.last_modified
        FROM books b
        LEFT JOIN books_authors_link bal ON b.id = bal.book
        LEFT JOIN authors a ON bal.author = a.id
        WHERE b.id = ?
        GROUP BY b.id
        """
        
        try:
            with get_calibre_db() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (calibre_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            logger.error(f"Error retrieving book {calibre_id} from Calibre DB: {e}")
            raise
    
    @staticmethod
    def get_book_tags(calibre_id: int) -> List[str]:
        """Get tags for a specific book."""
        query = """
        SELECT t.name
        FROM tags t
        JOIN books_tags_link btl ON t.id = btl.tag
        WHERE btl.book = ?
        """
        
        try:
            with get_calibre_db() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (calibre_id,))
                tags = [row['name'] for row in cursor.fetchall()]
                return tags
        except Exception as e:
            logger.error(f"Error retrieving tags for book {calibre_id}: {e}")
            return []
    
    @staticmethod
    def get_book_publishers(calibre_id: int) -> List[str]:
        """Get publishers for a specific book."""
        query = """
        SELECT p.name
        FROM publishers p
        JOIN books_publishers_link bpl ON p.id = bpl.publisher
        WHERE bpl.book = ?
        """
        
        try:
            with get_calibre_db() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (calibre_id,))
                publishers = [row['name'] for row in cursor.fetchall()]
                return publishers
        except Exception as e:
            logger.error(f"Error retrieving publishers for book {calibre_id}: {e}")
            return []
    
    @staticmethod
    def get_book_file_info(calibre_id: int, preferred_format: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the path and format for the best available book file."""
        query = """
        SELECT b.path, d.name, d.format
        FROM data d
        JOIN books b ON d.book = b.id
        WHERE b.id = ?
        ORDER BY d.format
        """
        
        try:
            with get_calibre_db() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (calibre_id,))
                rows = [dict(row) for row in cursor.fetchall()]
                if rows:
                    available_formats = [row["format"].upper() for row in rows]
                    selected = None
                    if preferred_format:
                        selected = next(
                            (row for row in rows if row["format"].upper() == preferred_format.upper()),
                            None,
                        )
                    if selected is None:
                        selected = min(
                            rows,
                            key=lambda row: (
                                FORMAT_PRIORITY.index(row["format"].upper())
                                if row["format"].upper() in FORMAT_PRIORITY
                                else len(FORMAT_PRIORITY),
                                row["format"].upper(),
                            ),
                        )

                    file_format = selected["format"].lower()
                    file_path = f"{selected['path']}/{selected['name']}.{file_format}"
                    return {
                        "path": file_path,
                        "format": selected["format"].upper(),
                        "available_formats": available_formats,
                    }
                return None
        except Exception as e:
            logger.error(f"Error retrieving file path for book {calibre_id}: {e}")
            return None

    @staticmethod
    def get_book_file_path(calibre_id: int) -> Optional[str]:
        """Get the file path for the best available book format."""
        info = CalibreDB.get_book_file_info(calibre_id)
        return info["path"] if info else None
    
    @staticmethod
    def search_books(query: str) -> List[Dict[str, Any]]:
        """Search books by title, author, or tags."""
        search_query = """
        SELECT 
            b.id as calibre_id,
            b.title,
            b.path,
            GROUP_CONCAT(a.name, ', ') as authors
        FROM books b
        LEFT JOIN books_authors_link bal ON b.id = bal.book
        LEFT JOIN authors a ON bal.author = a.id
        WHERE b.title LIKE ? OR a.name LIKE ?
        GROUP BY b.id
        ORDER BY b.title
        """
        
        search_pattern = f"%{query}%"
        
        try:
            with get_calibre_db() as conn:
                cursor = conn.cursor()
                cursor.execute(search_query, (search_pattern, search_pattern))
                books = [dict(row) for row in cursor.fetchall()]
                logger.info(f"Search for '{query}' returned {len(books)} results")
                return books
        except Exception as e:
            logger.error(f"Error searching books in Calibre DB: {e}")
            raise
