from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from typing import Optional

from app.models import BookResponse, BookListResponse, SyncResponse
from app.services.book_service import book_service
from app.utils.logger import get_logger
from app.config import settings

logger = get_logger(__name__)
router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("", response_model=BookListResponse)
async def list_books(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    auto_sync: bool = Query(default=False, description="Auto-sync from Calibre if PostgreSQL is empty")
):
    """List all books with pagination."""
    try:
        logger.info(f"Listing books with limit={limit}, offset={offset}, auto_sync={auto_sync}")
        books = book_service.get_all_books(limit, offset)
        total = len(books)
        
        # Auto-sync if PostgreSQL is empty and auto_sync is enabled
        if total == 0 and auto_sync:
            logger.info("PostgreSQL is empty, auto-syncing from Calibre...")
            synced_count = book_service.sync_books_from_calibre()
            logger.info(f"Auto-synced {synced_count} books from Calibre")
            books = book_service.get_all_books(limit, offset)
            total = len(books)
        
        logger.info(f"Retrieved {total} books from PostgreSQL")
        if total == 0:
            logger.warning("No books found in PostgreSQL. Call /api/books/sync to sync from Calibre, or use ?auto_sync=true")
        return BookListResponse(
            books=books,
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Error listing books: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync", response_model=SyncResponse)
async def sync_books():
    """Synchronize books from Calibre to PostgreSQL."""
    try:
        synced_count = book_service.sync_books_from_calibre()
        return SyncResponse(
            synced_count=synced_count,
            message=f"Successfully synchronized {synced_count} books"
        )
    except Exception as e:
        logger.error(f"Error syncing books: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync/status")
async def sync_status():
    """Check synchronization status between Calibre and PostgreSQL."""
    try:
        from app.database.calibre_db import CalibreDB
        from app.database.postgres_db import postgres_db
        
        # Get counts from both databases
        calibre_db = CalibreDB()
        calibre_books = calibre_db.get_all_books()
        calibre_count = len(calibre_books)
        
        postgres_books = postgres_db.get_all_books(limit=1000000, offset=0)
        postgres_count = len(postgres_books)
        
        # Get last sync info (from most recent book update in PostgreSQL)
        with postgres_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(updated_at) FROM books")
            result = cursor.fetchone()
            last_sync = result[0] if result and result[0] else None
        
        is_synced = calibre_count == postgres_count
        
        return {
            "calibre_count": calibre_count,
            "postgres_count": postgres_count,
            "is_synced": is_synced,
            "last_sync": last_sync,
            "needs_sync": not is_synced,
            "message": f"Calibre: {calibre_count} books, PostgreSQL: {postgres_count} books"
        }
    except Exception as e:
        logger.error(f"Error checking sync status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/problems")
async def list_problem_books():
    """List books with problems (missing files, etc.)."""
    try:
        from app.database.calibre_db import CalibreDB
        from app.database.postgres_db import postgres_db
        from pathlib import Path
        
        calibre_db = CalibreDB()
        postgres_books = postgres_db.get_all_books(limit=1000000, offset=0)
        
        problem_books = []
        
        for book in postgres_books:
            problems = []
            
            # Check if file exists
            if book.get('file_path'):
                full_path = Path(settings.CALIBRE_LIBRARY_PATH) / book['file_path']
                if not full_path.exists():
                    problems.append("File not found")
            else:
                problems.append("No file path")
            
            # Check if has no embeddings
            book_id = book.get('id')
            if book_id and not postgres_db.has_embeddings(book_id):
                problems.append("No embeddings")
            
            if problems:
                problem_books.append({
                    "id": book.get('id'),
                    "calibre_id": book.get('calibre_id'),
                    "title": book.get('title'),
                    "author": book.get('author'),
                    "file_path": book.get('file_path'),
                    "problems": problems
                })
        
        return {
            "total": len(problem_books),
            "books": problem_books
        }
    except Exception as e:
        logger.error(f"Error listing problem books: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: int):
    """Get a specific book by ID."""
    try:
        book = book_service.get_book(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return BookResponse(**book)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting book {book_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{book_id}/cover")
async def get_book_cover(book_id: int):
    """Get the cover image for a book (JPG format)."""
    try:
        cover_data = book_service.get_book_cover(book_id)
        if not cover_data:
            raise HTTPException(status_code=404, detail="Cover not found")
        
        return Response(
            content=cover_data,
            media_type="image/jpeg",
            headers={"Content-Disposition": f"inline; filename=book_{book_id}_cover.jpg"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cover for book {book_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{book_id}/pdf")
async def get_book_pdf(book_id: int):
    """Get the complete PDF file for a book."""
    try:
        pdf_data = book_service.get_book_pdf(book_id)
        if not pdf_data:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=book_{book_id}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting PDF for book {book_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{book_id}/page/{page_num}/pdf")
async def get_book_page_pdf(book_id: int, page_num: int):
    """Get a specific page as PDF."""
    try:
        if page_num < 1:
            raise HTTPException(status_code=400, detail="Page number must be >= 1")
        
        pdf_data = book_service.get_book_page_pdf(book_id, page_num)
        if not pdf_data:
            raise HTTPException(status_code=404, detail="Page not found")
        
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=book_{book_id}_page_{page_num}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting page {page_num} for book {book_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{book_id}/markdown")
async def get_book_markdown(book_id: int):
    """Get the complete book content as Markdown."""
    try:
        markdown = book_service.get_book_markdown(book_id)
        if not markdown:
            raise HTTPException(status_code=404, detail="Book not found or conversion failed")
        
        return Response(
            content=markdown,
            media_type="text/markdown",
            headers={"Content-Disposition": f"inline; filename=book_{book_id}.md"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting markdown for book {book_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{book_id}/page/{page_num}/markdown")
async def get_book_page_markdown(book_id: int, page_num: int):
    """Get a specific page as Markdown."""
    try:
        if page_num < 1:
            raise HTTPException(status_code=400, detail="Page number must be >= 1")
        
        markdown = book_service.get_book_page_markdown(book_id, page_num)
        if not markdown:
            raise HTTPException(status_code=404, detail="Page not found or conversion failed")
        
        return Response(
            content=markdown,
            media_type="text/markdown",
            headers={"Content-Disposition": f"inline; filename=book_{book_id}_page_{page_num}.md"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting markdown for page {page_num} of book {book_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
