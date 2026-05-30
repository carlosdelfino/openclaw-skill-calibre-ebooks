from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class BookResponse(BaseModel):
    """Response model for book data."""
    id: int
    calibre_id: Optional[int] = None
    title: str
    author: Optional[str] = None
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    indexed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    """Response model for book list."""
    books: List[BookResponse]
    total: int
    limit: int
    offset: int


class SearchRequest(BaseModel):
    """Request model for search."""
    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum results")


class ContentSearchRequest(BaseModel):
    """Request model for content search."""
    query: str = Field(..., min_length=1, description="Search query for content")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum results")
    threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="Similarity threshold")


class SearchResult(BaseModel):
    """Response model for search result."""
    id: int
    chunk_id: int
    book_id: int
    chunk_index: int
    content: str
    title: str
    author: Optional[str] = None
    similarity: float
    
    class Config:
        from_attributes = True


class EmbeddingStatusResponse(BaseModel):
    """Response model for embedding status."""
    book_id: int
    has_embeddings: bool
    chunk_count: int
    ready: bool
    error: Optional[str] = None


class EmbeddingQueueResponse(BaseModel):
    """Response model for embedding queue."""
    book_id: int
    status: str
    queue_id: Optional[int] = None
    queue_status: Optional[str] = None


class QueueItemResponse(BaseModel):
    """Response model for queue item."""
    id: int
    book_id: int
    title: str
    status: str
    priority: int
    estimated_seconds: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SyncResponse(BaseModel):
    """Response model for sync operation."""
    synced_count: int
    message: str


class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str
    detail: Optional[str] = None
