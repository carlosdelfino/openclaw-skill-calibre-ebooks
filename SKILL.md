---
name: calibre-ebooks
description: Query and operate the local Calibre library using calibredb and metadata.db. Use when the user asks to list, search, locate, summarize metadata, find available formats, export, or prepare books/e-books/PDFs/EPUBs from the Calibre library for reading, analysis, or RAG.
---

# Calibre E-books

Use this skill to work with the local Calibre library and a semantic RAG base derived from the books.

## Configuration

- Default Calibre library: `/mnt/Backup_2/Biblioteca`
- Metadata database: `/mnt/Backup_2/Biblioteca/metadata.db`
- Official command: `calibredb`
- Read-only metadata script: `scripts/calibre_query.py`
- Conversion, indexing, and RAG script: `scripts/document_semantic_rag.py`
- Default RAG base: `/tmp/openclaw-calibre-rag/data`
- Default converted Markdown: `/tmp/openclaw-calibre-rag/converteds`
- Always pass the library directory to `calibredb`, not the `.db` file:

```bash
calibredb list --library-path "/mnt/Backup_2/Biblioteca"
```

If `calibredb` fails due to sandbox, mutex, or Calibre configuration, request elevated permission to repeat the query. For read-only queries, use `scripts/calibre_query.py` as a SQLite fallback.

## Recommended workflow

1. Understand if the user wants discovery, metadata, exported file, or analysis/RAG.
2. Start with read-only operations: `list`, `search`, `show_metadata`, or `scripts/calibre_query.py`.
3. Confirm the correct `id` before exporting, changing metadata, adding, or removing anything.
4. Prefer exporting to `/tmp/openclaw-calibre-export` when the user requests file access.
5. For RAG, index the file or Calibre `id` with `document_semantic_rag.py`, then search with `--search`.
6. Never use destructive commands (`remove`, `remove_format`, `set_metadata`, `set_custom`, `restore_database`) without explicit request.

## Useful calibredb commands

List books:

```bash
calibredb list --library-path "/mnt/Backup_2/Biblioteca" --fields id,title,authors,formats --limit 20
```

Search by term:

```bash
calibredb search --library-path "/mnt/Backup_2/Biblioteca" "python"
```

View complete metadata of a book:

```bash
calibredb show_metadata --library-path "/mnt/Backup_2/Biblioteca" 123
```

Export a book to a temporary directory:

```bash
mkdir -p /tmp/openclaw-calibre-export
calibredb export --library-path "/mnt/Backup_2/Biblioteca" --to-dir /tmp/openclaw-calibre-export 123
```

Use full-text search if the index exists:

```bash
calibredb fts_search --library-path "/mnt/Backup_2/Biblioteca" "searched term"
```

## SQLite read-only fallback

Use the script when you only need to query `metadata.db` without depending on the Calibre process:

```bash
python3 skills/calibre-ebooks/scripts/calibre_query.py list --limit 20
python3 skills/calibre-ebooks/scripts/calibre_query.py search "python" --limit 10
python3 skills/calibre-ebooks/scripts/calibre_query.py metadata 123
python3 skills/calibre-ebooks/scripts/calibre_query.py path 123 --format PDF
```

The script returns JSON by default and does not write to the library.

## Conversion and RAG services

Before converting or searching semantically, check dependencies:

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --check --json
```

If Python dependencies are missing, install the RAG set:

```bash
pip install -r skills/calibre-ebooks/scripts/requirements-rag.txt
```

Index a book directly by Calibre ID:

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --calibre-id 123 --format PDF --json
```

Index an exported or resolved file:

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --convert "/path/book.pdf" --json
```

Index all supported documents in a folder:

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --convert-all "/path/folder"
```

Search in the RAG base:

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --search "convolutional neural networks" --json
```

List or check base status:

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --list --json
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --status --json
```

Removing a book from the RAG base requires the internal ID returned during indexing/listing, not the Calibre ID:

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --delete RAG_BOOK_ID --json
```

### RAG strategy

- Convert PDF to Markdown with PyMuPDF.
- Convert EPUB to Markdown with ebooklib, BeautifulSoup, and markdownify.
- Convert DjVu via OCR when external dependencies are available.
- Split text into chunks with configurable overlap.
- Generate embeddings via Ollama (`OLLAMA_MODEL`, skill default: `nomic-embed-text-v2-moe`).
- Store metadata and chunks in SQLite.
- Store embeddings in ChromaDB.
- Hybrid search: exact/partial text in SQLite first, semantic search in ChromaDB after.

### RAG configuration

The script reads `skills/calibre-ebooks/.env` and accepts CLI override:

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --status --data-dir /tmp/my-base --converted-dir /tmp/my-markdowns
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --search "term" --embedding-model nomic-embed-text-v2-moe
```

If a base was already created with another embedding model, use the same previous model. Only use `--allow-model-mismatch` when accepting potentially incorrect results.

## User responses

- Show `id`, title, authors, and formats when there are multiple results.
- Inform when a book lacks PDF/EPUB before promising analysis or delivery.
- When preparing RAG, first locate the book via `calibre_query.py`, confirm available format, then use `document_semantic_rag.py --calibre-id`.
- For RAG-based responses, cite document, page, similarity, and relevant excerpt.
- If the library is inaccessible, cite the tested path and relevant error.
- If `--check` points to missing dependencies, inform exactly which ones are missing before attempting to index.
