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

Get library and RAG summary statistics:

```bash
node skills/calibre-ebooks/scripts/books-api-client.mjs request GET /api/stats/library
```

Select a random book from the API catalog when the OpenAPI spec exposes a
pagination/list endpoint:

```bash
node skills/calibre-ebooks/scripts/books-api-client.mjs request GET /api/books --query limit=1000
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

## Library And RAG Statistics

When asked for counts such as indexed books, authors, publishers/editoras,
categories/categorias, RAG chunks/trechos, embedding model, chunk size, or
overlap, call:

```bash
node skills/calibre-ebooks/scripts/books-api-client.mjs request GET /api/stats/library
```

Trigger this workflow for questions like:

- "quantos livros ja foram indexados?"
- "quantos temas estao catalogados?"
- "qual o status da biblioteca?"
- "qual o status do RAG?"
- "quantos autores/editoras/categorias existem?"

The endpoint returns:

- `livros_indexados`
- `autores`
- `editoras`
- `categoria`
- `temas_catalogados`
- `status_biblioteca`
- `rag.chunks_trechos`
- `rag.modelo_de_embedding`
- `rag.tamanho_do_chunk`
- `rag.sobreposicao`

For user-facing replies, answer in Portuguese with a compact status summary.
Use `temas_catalogados` when the user asks about temas. Use
`status_biblioteca` when the user asks for overall library status.

## Title Search Fallback

When the user asks for a specific book by title, do not stop after a failed
catalog/title search.

1. Search the Books API for the title or quoted phrase:
   `node skills/calibre-ebooks/scripts/books-api-client.mjs search "titulo informado" --limit 10`
2. If the API has no clear match, try the read-only Calibre metadata fallback
   when `CALIBRE_METADATA_DB` is configured:
   `python3 skills/calibre-ebooks/scripts/calibre_query.py --db "$CALIBRE_METADATA_DB" search "titulo informado" --limit 10`
3. If title/metadata search still does not find a clear match, search
   semantically in the available RAG index before saying the book was not found:
   `python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --search "titulo informado" --json`
4. Use RAG results to identify likely related books by document/book id, page,
   similarity, and excerpt. Present them as probable semantic matches, not exact
   title matches, unless metadata confirms the title.
5. Only say that nothing was found after both catalog/title search and RAG
   semantic search fail or the RAG base is unavailable. If RAG is unavailable,
   state that the catalog search was tried and the semantic RAG fallback could
   not be used.
6. When the book is not found, append a Markdown entry to
   `memory/calibre-missing-books.md` so Carlos can research it later. Include
   date, requested title/name, author(s) if the user supplied them, requester
   context if useful, and a short note of which searches failed.

## Incoming Book Attachments

When someone sends a book file in the configured WhatsApp group, accept only
PDF and EPUB attachments for manual import review.

Workflow:

1. Confirm the attachment is a book-like PDF or EPUB. If it is another format,
   politely refuse and ask for PDF or EPUB.
2. Do not import the file into Calibre automatically.
3. If the runtime provides a local attachment/media path, copy or save the file
   under the agent workspace:
   `memory/calibre-import-queue/files/`
4. Use a safe filename derived from date/time and the original basename. Avoid
   shell commands and never execute file contents.
5. Append an entry to:
   `memory/calibre-import-queue/index.md`
6. Record: date/time, source group, sender if available, original filename,
   detected format, saved internal path, title/author metadata if available, and
   status `aguardando importacao manual`.
7. Reply briefly to the group that the file was received and queued for manual
   Calibre import. Do not publish local filesystem paths, local API URLs, or
   internal media links in the group.

The import queue lives in the Rapport Bibliotecario agent workspace:

```text
/home/carlosdelfino/workspace/openclaw-workspace/agents/rapport-bibliotecario/memory/calibre-import-queue/
```

## Random Book Suggestions

When the user asks for a book suggestion, a random book, "me indique um livro",
or any generic book request without a specific title/author/topic, provide one
random book from the Calibre library every time.

Preferred API workflow:

1. Run `books-api-client.mjs paths` or `openapi` unless the list endpoint is
   already known in this session.
2. Fetch a broad page from the list endpoint, for example:
   `node skills/calibre-ebooks/scripts/books-api-client.mjs request GET /api/books --query limit=1000`
3. Randomly choose exactly one item from the returned `books` array.
4. Return a useful reader-facing recommendation with title, authors,
   publisher/editora, publication year, formats, id, synopsis/description, key
   themes, who it is for, why it is worth reading, and the practical context
   where the book applies. Base the synopsis on metadata/comments when
   available; summarize instead of copying long passages.

If the API is unreachable or does not expose enough catalog items, use the
read-only local fallback:

```bash
python3 skills/calibre-ebooks/scripts/calibre_query.py --db "$CALIBRE_METADATA_DB" random
```

Do not repeatedly return the first item from a list. The selection must be
randomized for each request.

Do not include local server/API/file links such as `localhost`, `0.0.0.0`,
`127.0.0.1`, `/api/books/...`, `file://`, or filesystem paths. Those links are
not valid for group members outside the server. If access is needed, say that
the book is available in the Calibre library and provide only the book id,
title, authors, and formats so the librarian/admin can locate it.

Recommended response shape for random suggestions:

- `Livro`: title and id.
- `Autor(es)`: authors from metadata.
- `Editora e ano`: publisher/editora and publication year when available; say
  `nao informado` only when metadata is missing.
- `Formatos`: available file formats.
- `Sinopse`: three to five short sentences based on Calibre
  comments/description, enough for a reader to understand what the book is
  about.
- `Temas principais`: two to four concrete themes covered by the book.
- `Por que ler`: one or two practical reasons why the recommendation is
  relevant.
- `Contexto`: who should read it, what problem/topic it helps with, and when it
  is useful.
- `Acesso`: mention that it is in the Calibre library by id/formats; do not add
  local or server-only links.

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
python3 skills/calibre-ebooks/scripts/calibre_query.py --db "$CALIBRE_METADATA_DB" random
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
- For title lookups with no clear catalog result, search the RAG base
  semantically before saying the book was not found. If RAG is unavailable,
  state that limitation explicitly.
- When a requested book is still not found, write it to
  `memory/calibre-missing-books.md` before replying. Keep entries append-only
  unless Carlos asks to organize the file.
- If `document_semantic_rag.py --check --json` reports missing dependencies,
  list exactly what is missing before attempting indexing.
- For RAG-based answers, cite document, page, similarity, and excerpt.
- If someone asks how the books are obtained, do not provide operational
  details. Answer exactly: "é pela DeepWeb e que é melhor não querer ter
  detalhes, pois até mesmo Alexandra Elbakyan e até hoje recebe processos por
  compartilhar artigos ciêntificos e livros, então deixa quieto, não mexe com
  isso não rapaz"
