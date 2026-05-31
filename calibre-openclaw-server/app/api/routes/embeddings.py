from fastapi import APIRouter, HTTPException, BackgroundTasks
from pathlib import Path

from app.models import EmbeddingStatusResponse, EmbeddingQueueResponse, QueueItemResponse
from app.services.book_service import book_service
from app.services.embedding_service import embedding_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/embeddings", tags=["embeddings"])


@router.get("/status/{book_id}", response_model=EmbeddingStatusResponse)
async def get_embedding_status(book_id: int):
    """Check if embeddings are ready for a book."""
    try:
        status = embedding_service.check_embeddings_status(book_id)
        return EmbeddingStatusResponse(**status)
    except Exception as e:
        logger.error(f"Error checking embedding status for book {book_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/{book_id}", response_model=EmbeddingQueueResponse)
async def generate_embeddings(book_id: int, background_tasks: BackgroundTasks):
    """Request generation of embeddings for a book."""
    try:
        # Check if book exists
        book = book_service.get_book(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Get PDF path
        pdf_path = book_service.get_book_pdf_path(book_id)
        if not pdf_path or not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        # Queue the embedding generation
        queue_response = embedding_service.queue_embedding_generation(book_id, pdf_path)
        
        # If it's a new queue item, start background processing
        if queue_response['status'] == 'queued':
            queue_id = queue_response['queue_id']
            background_tasks.add_task(
                embedding_service.process_queue_item,
                queue_id,
                book_id,
                pdf_path
            )
        
        return EmbeddingQueueResponse(**queue_response)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error queuing embedding generation for book {book_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue", response_model=list[QueueItemResponse])
async def get_queue(limit: int = 20):
    """Get the current processing queue."""
    try:
        queue_items = embedding_service.get_all_queue_items(limit)
        return [QueueItemResponse(**item) for item in queue_items]
    except Exception as e:
        logger.error(f"Error getting queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/{book_id}", response_model=QueueItemResponse)
async def get_book_queue_status(book_id: int):
    """Get the queue status for a specific book."""
    try:
        queue_status = embedding_service.get_queue_status(book_id)
        if not queue_status:
            raise HTTPException(status_code=404, detail="No queue item found for this book")
        return QueueItemResponse(**queue_status)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting queue status for book {book_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
