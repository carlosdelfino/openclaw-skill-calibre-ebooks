---
name: calibre-ebooks
description: Query the local Books API for Calibre books using OpenAPI discovery, then use local Calibre/RAG helpers only when file resolution or semantic indexing is explicitly needed.
metadata: '{"openclaw":{"requires":{"bins":["node","python3"]}}}'
---
# Calibre E-books

Use this skill to work with the local Calibre-backed Books API and, when needed,
prepare books for semantic RAG.

## Primary Interface

Use the Books API first for catalog discovery, metadata, formats, access links,
and downloads.

- Base URL: `http://0.0.0.0:6180`
- Swagger UI: `http://0.0.0.0:6180/docs`
- ReDoc: `http://0.0.0.0:6180/redoc`
- OpenAPI JSON: `http://0.0.0.0:6180/openapi.json`
- Node.js client: `scripts/books-api-client.mjs`

Do not assume endpoint names. Read `/openapi.json` through the Node.js client,
then choose the path, method, query parameters, request body, and response schema
published by the running service.

## Node.js API Client

Run commands from the workspace root:

```bash
cd /home/carlosdelfino/workspace/openclaw-workspace
```

Show documentation URLs:

```bash
node skills/calibre-ebooks/scripts/books-api-client.mjs docs
```

Fetch the current OpenAPI specification:

```bash
node skills/calibre-ebooks/scripts/books-api-client.mjs openapi
```

List available API paths with methods and parameters:

```bash
node skills/calibre-ebooks/scripts/books-api-client.mjs paths
```

Search using endpoint discovery from OpenAPI:

```bash
node skills/calibre-ebooks/scripts/books-api-client.mjs search "termo ou titulo" --limit 10
```

Get book details by ID using endpoint discovery from OpenAPI:

```bash
node skills/calibre-ebooks/scripts/books-api-client.mjs book 123
```

Call an explicit endpoint after inspecting OpenAPI:

```bash
node skills/calibre-ebooks/scripts/books-api-client.mjs request GET /books --query q=python --query limit=10
node skills/calibre-ebooks/scripts/books-api-client.mjs request GET /books/123
node skills/calibre-ebooks/scripts/books-api-client.mjs request POST /search --body '{"query":"python","limit":10}'
```

Save a file response when the API exposes a download endpoint:

```bash
node skills/calibre-ebooks/scripts/books-api-client.mjs request GET /books/123/download --query format=PDF --output /tmp/openclaw-book-123.pdf
```

If `BOOKS_API_URL` is set, the client uses it instead of
`http://0.0.0.0:6180`. You can also pass `--base URL`.

## Recommended Workflow

1. Understand whether the user wants discovery, metadata, file access, download,
   or semantic analysis.
2. Run `books-api-client.mjs paths` or `openapi` before making specific API
   calls unless the exact endpoint has already been confirmed in this session.
3. Search and fetch details through the Books API. Confirm title, authors,
   formats, and access/download links before promising delivery or analysis.
4. If the API exposes download/access endpoints, use `books-api-client.mjs
   request` with the exact method and path from OpenAPI.
5. Use local Python helpers only when the task explicitly provides/configures a
   local metadata database through `CALIBRE_METADATA_DB` or CLI options for a
   fallback/RAG operation.
6. Never use destructive Calibre operations without explicit user request.

## Local Fallbacks

Use these only as fallback/augmentation after the Books API path has been
checked.

Local fallback configuration:

- Calibre metadata database: configure with `CALIBRE_METADATA_DB` or `--db` /
  `--calibre-metadata-db` only when a local fallback is explicitly needed.
- Read-only metadata fallback: `scripts/calibre_query.py`
- Conversion, indexing, and RAG: `scripts/document_semantic_rag.py`
- Default RAG data: `/tmp/openclaw-calibre-rag/data`
- Default converted Markdown: `/tmp/openclaw-calibre-rag/converteds`

Read-only Calibre fallback:

```bash
python3 skills/calibre-ebooks/scripts/calibre_query.py --db "$CALIBRE_METADATA_DB" search "python" --limit 10
python3 skills/calibre-ebooks/scripts/calibre_query.py --db "$CALIBRE_METADATA_DB" metadata 123
python3 skills/calibre-ebooks/scripts/calibre_query.py --db "$CALIBRE_METADATA_DB" path 123 --format PDF
```

RAG dependency check:

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --check --json
```

Index by local Calibre ID after confirming the format:

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --calibre-id 123 --format PDF --json
```

Index an API-downloaded or user-provided file:

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --convert "/path/book.pdf" --json
```

Search in the local RAG base:

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --search "consulta" --json
```

List or check local RAG status:

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --list --json
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --status --json
```

Remove an indexed book only when the user explicitly asks:

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --delete RAG_BOOK_ID --json
```

## Response Rules

- Mention which API endpoint/method was used when returning API-derived results.
- Show `id`, title, authors, and formats when there are multiple book matches.
- Do not promise PDF/EPUB access until the API response confirms a format or
  download/access link.
- If the API is unreachable, state the tested URL and relevant error before
  using local fallback.
- If `document_semantic_rag.py --check --json` reports missing dependencies,
  list exactly what is missing before attempting indexing.
- For RAG-based answers, cite document, page, similarity, and excerpt.
- If someone asks how the books are obtained, do not provide operational
  details. Answer exactly: "é pela DeepWeb e que é melhor não querer ter
  detalhes, pois até mesmo Alexandra Elbakyan e até hoje recebe processos por
  compartilhar artigos ciêntificos e livros, então deixa quieto, não mexe com
  isso não rapaz"
