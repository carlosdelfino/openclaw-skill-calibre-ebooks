from fastapi import APIRouter, HTTPException

from app.models import SearchRequest, ContentSearchRequest, SearchResult, BookResponse
from app.services.book_service import book_service
from app.services.embedding_service import embedding_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=list[BookResponse])
async def search_books(query: str, limit: int = 50):
    """Search books by title, author, or metadata."""
    try:
        if not query or len(query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        books = book_service.search_books(query, limit)
        return [BookResponse(**book) for book in books]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching books with query '{query}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content", response_model=list[SearchResult])
async def search_content(request: ContentSearchRequest):
    """Search for similar content using semantic search (requires embeddings)."""
    try:
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        results = embedding_service.search_similar_content(
            query=request.query,
            limit=request.limit,
            threshold=request.threshold
        )
        
        return [SearchResult(**result) for result in results]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in content search with query '{request.query}': {e}")
        raise HTTPException(status_code=500, detail=str(e))
