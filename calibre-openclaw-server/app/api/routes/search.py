from fastapi import APIRouter, HTTPException, Query

from app.models import SearchRequest, ContentSearchRequest, SearchResult, BookResponse
from app.services.book_service import book_service
from app.services.embedding_service import embedding_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("")
async def search_books(
    query: str,
    limit: int = Query(default=50, ge=1, le=100),
    semantic_fallback: bool = Query(
        default=True,
        description="When catalog search returns no results, search embedded content.",
    ),
    semantic_threshold: float = Query(default=0.3, ge=0.0, le=1.0),
):
    """Search catalog first, then embedded content when the catalog has no hit."""
    try:
        if not query or len(query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        books = book_service.search_books(query, limit)
        if books:
            return [
                {
                    "result_type": "catalog",
                    **BookResponse(**book).model_dump(mode="json"),
                }
                for book in books
            ]

        if not semantic_fallback:
            return []

        semantic_results = embedding_service.search_similar_content(
            query=query,
            limit=min(limit, 50),
            threshold=semantic_threshold,
        )
        return [
            {
                "result_type": "semantic",
                **SearchResult(**result).model_dump(mode="json"),
            }
            for result in semantic_results
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching books with query '{query}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


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
        raise HTTPException(status_code=500, detail="Internal server error")
