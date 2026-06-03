import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Optional
import io

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ConversionService:
    """Service for converting PDF files to Markdown and extracting content."""
    
    @staticmethod
    def pdf_to_text(pdf_path: Path) -> str:
        """Convert entire PDF to text."""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            logger.info(f"Converted PDF {pdf_path} to text ({len(text)} characters)")
            return text
        except Exception as e:
            logger.error(f"Error converting PDF {pdf_path} to text: {e}")
            raise
    
    @staticmethod
    def pdf_to_markdown(pdf_path: Path) -> str:
        """Convert PDF to Markdown format."""
        try:
            doc = fitz.open(pdf_path)
            markdown = ""
            
            for page_num, page in enumerate(doc, start=1):
                # Get text with layout preservation
                text = page.get_text("markdown")
                markdown += f"\n\n--- Page {page_num} ---\n\n{text}"
            
            doc.close()
            logger.info(f"Converted PDF {pdf_path} to Markdown ({len(markdown)} characters)")
            return markdown
        except Exception as e:
            logger.error(f"Error converting PDF {pdf_path} to Markdown: {e}")
            raise
    
    @staticmethod
    def pdf_page_to_text(pdf_path: Path, page_num: int) -> str:
        """Extract text from a specific page (1-indexed)."""
        try:
            doc = fitz.open(pdf_path)
            if page_num < 1 or page_num > len(doc):
                doc.close()
                raise ValueError(f"Page {page_num} out of range (PDF has {len(doc)} pages)")
            
            page = doc[page_num - 1]
            text = page.get_text()
            doc.close()
            logger.info(f"Extracted text from page {page_num} of {pdf_path}")
            return text
        except Exception as e:
            logger.error(f"Error extracting page {page_num} from {pdf_path}: {e}")
            raise
    
    @staticmethod
    def pdf_page_to_markdown(pdf_path: Path, page_num: int) -> str:
        """Convert a specific page to Markdown (1-indexed)."""
        try:
            doc = fitz.open(pdf_path)
            if page_num < 1 or page_num > len(doc):
                doc.close()
                raise ValueError(f"Page {page_num} out of range (PDF has {len(doc)} pages)")
            
            page = doc[page_num - 1]
            markdown = page.get_text("markdown")
            doc.close()
            logger.info(f"Converted page {page_num} of {pdf_path} to Markdown")
            return markdown
        except Exception as e:
            logger.error(f"Error converting page {page_num} of {pdf_path} to Markdown: {e}")
            raise
    
    @staticmethod
    def extract_cover_image(pdf_path: Path) -> Optional[bytes]:
        """Extract the first page as a cover image (JPG)."""
        try:
            doc = fitz.open(pdf_path)
            if len(doc) == 0:
                doc.close()
                return None
            
            # Render first page as image
            page = doc[0]
            mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to JPG bytes
            img_data = pix.tobytes("jpeg")
            doc.close()
            
            logger.info(f"Extracted cover image from {pdf_path} ({len(img_data)} bytes)")
            return img_data
        except Exception as e:
            logger.error(f"Error extracting cover from {pdf_path}: {e}")
            return None
    
    @staticmethod
    def get_pdf_page_count(pdf_path: Path) -> int:
        """Get the number of pages in a PDF."""
        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()
            return page_count
        except Exception as e:
            logger.error(f"Error getting page count for {pdf_path}: {e}")
            return 0
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Split text into overlapping chunks.

        Chunks are snapped to whitespace boundaries so words are not cut in the
        middle, and empty/whitespace-only chunks are discarded. This produces
        cleaner inputs for the embedding model.
        """
        chunk_size = chunk_size or settings.CHUNK_SIZE
        overlap = overlap or settings.CHUNK_OVERLAP

        # Guard against pathological configuration that would loop forever.
        if overlap >= chunk_size:
            overlap = max(0, chunk_size // 5)

        text = (text or "").strip()
        if not text:
            logger.info("chunk_text received empty text; returning no chunks")
            return []

        chunks: List[str] = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + chunk_size, text_length)

            # Snap the end to the previous whitespace to avoid splitting a word,
            # unless that would make the chunk too small.
            if end < text_length:
                boundary = text.rfind(" ", start, end)
                if boundary > start + (chunk_size // 2):
                    end = boundary

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            # Advance, keeping the requested overlap, always moving forward.
            start = max(end - overlap, start + 1)

        logger.info(
            f"Split text into {len(chunks)} chunks (size={chunk_size}, overlap={overlap})"
        )
        return chunks
    
    @staticmethod
    def get_pdf_bytes(pdf_path: Path) -> bytes:
        """Get PDF file as bytes."""
        try:
            with open(pdf_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading PDF file {pdf_path}: {e}")
            raise


conversion_service = ConversionService()
