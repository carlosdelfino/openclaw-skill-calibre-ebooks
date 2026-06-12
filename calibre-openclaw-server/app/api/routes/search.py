from fastapi import APIRouter, HTTPException, Query

from app.models import SearchRequest, ContentSearchRequest, SearchResult, BookResponse, SemanticSearchResponse
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
    include_totals: bool = Query(
        default=False,
        description="Include total chunks and pages counts in semantic search results.",
    ),
    chunks_before: int = Query(default=0, ge=0, le=10, description="Number of chunks before each result to include"),
    chunks_after: int = Query(default=0, ge=0, le=10, description="Number of chunks after each result to include"),
    pages_before: int = Query(default=0, ge=0, le=10, description="Number of pages before each result to include"),
    pages_after: int = Query(default=0, ge=0, le=10, description="Number of pages after each result to include"),
):
    """Search catalog first, then embedded content when the catalog has no hit.
    
    When include_totals=True and semantic search is used, returns metadata with total chunks and pages above threshold.
    Context expansion parameters (chunks_before/after, pages_before/after) add surrounding context to each result.
    """
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

        semantic_response = embedding_service.search_similar_content(
            query=query,
            limit=min(limit, 50),
            threshold=semantic_threshold,
            include_totals=include_totals,
            chunks_before=chunks_before,
            chunks_after=chunks_after,
            pages_before=pages_before,
            pages_after=pages_after,
        )
        
        # Handle backward compatible return (list when include_totals=False, dict when True)
        if include_totals:
            semantic_results = semantic_response.get('results', [])
            return {
                "results": [
                    {
                        "result_type": "semantic",
                        **SearchResult(**result).model_dump(mode="json"),
                    }
                    for result in semantic_results
                ],
                "total_chunks": semantic_response.get('total_chunks'),
                "total_pages": semantic_response.get('total_pages'),
            }
        
        # Backward compatible: semantic_response is a list when include_totals=False
        return [
            {
                "result_type": "semantic",
                **SearchResult(**result).model_dump(mode="json"),
            }
            for result in semantic_response
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching books with query '{query}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/content")
async def search_content(request: ContentSearchRequest):
    """Search for similar content using semantic search (requires embeddings).
    
    When include_totals=True, returns metadata with total chunks and pages above threshold.
    """
    try:
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        response = embedding_service.search_similar_content(
            query=request.query,
            limit=request.limit,
            threshold=request.threshold,
            include_totals=request.include_totals,
            chunks_before=request.chunks_before,
            chunks_after=request.chunks_after,
            pages_before=request.pages_before,
            pages_after=request.pages_after,
        )
        
        # Handle backward compatible return (list when include_totals=False, dict when True)
        if request.include_totals:
            results = response.get('results', [])
            return SemanticSearchResponse(
                results=[SearchResult(**result) for result in results],
                total_chunks=response.get('total_chunks'),
                total_pages=response.get('total_pages')
            )
        
        # Backward compatible: response is a list when include_totals=False
        return [SearchResult(**result) for result in response]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in content search with query '{request.query}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
