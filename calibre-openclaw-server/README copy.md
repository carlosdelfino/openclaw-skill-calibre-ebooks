# Calibre OpenClaw Server

REST API server for managing a local Calibre library with semantic search
capabilities using embeddings. It works only with books already present in the
configured Calibre library and does not provide unauthorized book sources. For
titles that are not in the local library, consult public catalog/store pages
such as Google Books or Amazon Books for metadata, editions, publisher
information, and lawful availability.

## Features

- **Book Management**: List, search, and retrieve books from Calibre library
- **Multiple Formats**: Export books as PDF or Markdown (full book or specific pages)
- **Cover Images**: Extract and serve book covers as JPG
- **Semantic Search**: Content-based search using vector embeddings
- **Citeable RAG Results**: Semantic hits include page, optional chapter/section,
  citation text, similarity, and excerpt for richer reader-facing answers
- **On-Demand Embeddings**: Generate embeddings only when requested
- **Queue System**: Background processing for embedding generation
- **Structured Logging**: JSON logs with daily rotation and compression
- **OpenAPI 3.0**: Auto-generated API documentation

## Architecture

- **Calibre DB**: Read-only access to `metadata.db` (SQLite)
- **PostgreSQL**: Stores book metadata, embeddings (with pgvector), and processing queue
- **Ollama**: Local embedding generation (nomic-embed-text-v2-moe:latest)
- **FastAPI**: REST API framework with automatic OpenAPI documentation

## Prerequisites

- Python 3.9+
- PostgreSQL with pgvector extension
- Ollama running locally with nomic-embed-text-v2-moe:latest model
- Calibre library with metadata.db

## Installation

1. Clone or navigate to the project directory:
```bash
cd /mnt/Backup_2/Biblioteca/calibre-openclaw-server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (copy `.env.example` to `.env` and adjust):
```bash
cp .env.example .env
```

4. Ensure Ollama is running:
```bash
ollama serve
```

5. Pull the embedding model:
```bash
ollama pull nomic-embed-text-v2-moe:latest
```

## Configuration

Edit `.env` file with your settings:

```env
# Calibre OpenClaw Server
CALIBRE_DB_PATH=/path/to/metadata.db
CALIBRE_LIBRARY_PATH=/path/to/calibre/library
SERVER_PORT=6180
SERVER_HOST=0.0.0.0

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=nomic-embed-text-v2-moe:latest

# Embeddings
CHUNK_SIZE=500
CHUNK_OVERLAP=50
SIMILARITY_THRESHOLD=0.3

# PostgreSQL
POSTGRESQL_DB_USER=generativa
POSTGRESQL_DB_PASSWD=your_password
POSTGRESQL_DB_DATABASE=rapport_biblioteca
POSTGRESQL_DB_HOST=localhost
POSTGRESQL_DB_PORT=5432

# Logs
LOG_DIR=/path/to/logs
LOG_RETENTION_DAYS=30
LOG_COMPRESS=true
```

## Database Setup

The PostgreSQL database should have the following tables (already created):

- `books`: Book metadata from Calibre
- `book_chunks`: Text chunks with embeddings, page/section citation metadata
  and vector column
- `processing_queue`: Queue for embedding generation tasks

## Running the Server

### Development Mode
```bash
python -m app.main
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 6180 --workers 4
```

## API Endpoints

### Books
- `GET /api/books` - List all books (paginated)
- `GET /api/books/sync` - Synchronize books from Calibre to PostgreSQL
- `GET /api/books/{book_id}` - Get book details
- `GET /api/books/{book_id}/cover` - Get book cover (JPG)
- `GET /api/books/{book_id}/pdf` - Get complete PDF
- `GET /api/books/{book_id}/page/{page_num}/pdf` - Get specific page as PDF
- `GET /api/books/{book_id}/markdown` - Get book as Markdown
- `GET /api/books/{book_id}/page/{page_num}/markdown` - Get page as Markdown

### Search
- `GET /api/search?query={text}` - Search by title, author, metadata
- `POST /api/search/content` - Semantic content search (requires embeddings)

### Embeddings
- `GET /api/embeddings/status/{book_id}` - Check embedding status
- `POST /api/embeddings/generate/{book_id}` - Request embedding generation
- `GET /api/embeddings/queue` - Get processing queue
- `GET /api/embeddings/queue/{book_id}` - Get queue status for specific book

### Documentation
- `GET /docs` - Swagger UI documentation
- `GET /openapi.json` - OpenAPI 3.0 specification
- `GET /health` - Health check endpoint

## Usage Examples

### Sync Books from Calibre
```bash
curl http://localhost:6180/api/books/sync
```

### List Books
```bash
curl http://localhost:6180/api/books?limit=10&offset=0
```

### Get Book Cover
```bash
curl http://localhost:6180/api/books/1/cover --output cover.jpg
```

### Search Books
```bash
curl "http://localhost:6180/api/search?query=python&limit=5"
```

### Check Embedding Status
```bash
curl http://localhost:6180/api/embeddings/status/1
```

### Generate Embeddings
```bash
curl -X POST http://localhost:6180/api/embeddings/generate/1
```

### Semantic Search
```bash
curl -X POST http://localhost:6180/api/search/content \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning algorithms", "limit": 10}'
```

## Workflow for Semantic Search

1. **Sync books**: Call `/api/books/sync` to import books from Calibre
2. **Check status**: Call `/api/embeddings/status/{book_id}` to check if embeddings exist
3. **Generate embeddings**: If not ready, call `/api/embeddings/generate/{book_id}`
4. **Monitor queue**: Call `/api/embeddings/queue/{book_id}` to check progress
5. **Search**: Once ready, use `/api/search/content` for semantic search

## Logging

Logs are stored in JSON format with daily rotation:
- Location: `{LOG_DIR}/YYYY-MM-DD.log`
- Old logs (>30 days) are compressed to `.log.gz`
- Logs include: timestamp, level, endpoint, method, params, IP, duration, status

## Development

### Project Structure
```
calibre-openclaw-server/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── models.py            # Pydantic models
│   ├── database/
│   │   ├── calibre_db.py     # Calibre SQLite access
│   │   └── postgres_db.py    # PostgreSQL access
│   ├── services/
│   │   ├── book_service.py   # Book business logic
│   │   ├── embedding_service.py  # Embedding generation
│   │   └── conversion_service.py # PDF conversion
│   ├── api/
│   │   └── routes/
│   │       ├── books.py      # Book endpoints
│   │       ├── search.py     # Search endpoints
│   │       └── embeddings.py # Embedding endpoints
│   └── utils/
│       └── logger.py         # Logging configuration
├── logs/                     # Log directory
├── requirements.txt
├── README.md
└── .env.example
```

## License

This project is part of the OpenClaw ecosystem.
