---
name: calibre-ebooks
description: Manage and query the local Calibre library through the Books API, using local Calibre/RAG helpers only when file resolution or semantic indexing is explicitly needed.
metadata: '{"openclaw":{"requires":{"bins":["python3"]}}}'
---
# Calibre E-books

Location: `/skills/calibre-ebooks/SKILL.md` from the OpenClaw workspace root.

Use this skill only to manage and query the local Calibre-backed Books API and,
when needed, prepare books that already exist in the local Calibre library for
semantic RAG.

## Primary Interface

Use the Books API first for local catalog discovery, metadata, formats, covers,
local file access, and library statistics.

- Base URL: `http://host.docker.internal:6180`
- Swagger UI: `http://host.docker.internal:6180/docs`
- ReDoc: `http://host.docker.internal:6180/redoc`
- OpenAPI JSON: `http://host.docker.internal:6180/openapi.json`
- Python API client: `scripts/books_api_client.py`

Do not assume endpoint names. Read `/openapi.json` through the Python API client,
then choose the path, method, query parameters, request body, and response schema
published by the running service.

## Directory Reference Map

Treat the skill directory as the sandbox for generated files `/workspace/tmp`. Keep temporary book files, covers, exported local files, and derived artifacts inside
`skills/calibre-ebooks/tmp/` unless a runtime explicitly provides a safer
attachment path.

External paths from the sandbox workspace and internal paths inside the sandbox:

- `skills/calibre-ebooks/` - skill root; contains this `SKILL.md`, helper
  scripts, server code, and temporary skill artifacts. Sandbox `/workspace/`
- `skills/calibre-ebooks/scripts/` - command-line clients and small automation
  helpers. Do not write exported files here. Sandbox `/workspace/scripts/`
- `skills/calibre-ebooks/tmp/downloads/` - temporary local book/file exports meant
  for attachment delivery when the user is authorized to access the local
  Calibre library. Delete files here after the runtime confirms the
  attachment was sent/read. Sandbox `/workspace/tmp/downloads/`.
- `skills/calibre-ebooks/tmp/calibre-covers/` - temporary cover images meant for
  `MEDIA:` attachment delivery. Delete files here after successful delivery. Sandbox `/workspace/tmp/calibre-covers/`
- `skills/calibre-ebooks/tmp/` - general scratch area for this skill. It is safe
  to create subdirectories here for short-lived generated artifacts. Sandbox `/workspace/tmp`
- `agents/rapport-bibliotecario/memory/calibre-import-queue/` - manual import
  queue for received book attachments. This is inside the OpenClaw workspace but
  outside this skill directory; use it only for queued inbound attachments.
- `memory/calibre-missing-books.md` - append-only missing-book log when this
  skill runs in an agent workspace that provides a `memory/` directory.

External or mapped paths and services:

- `BOOKS_API_URL` - optional API base URL override for `books_api_client.py`.
  If unset, the client uses `http://host.docker.internal:6180`.
- `http://host.docker.internal:6180` - Books API as seen from containerized
  runtimes. It is an internal service address, not a user-facing link.
- `LOG_DIR` - external server log directory when configured by the server. Do
  not expose it in normal user-facing replies.
- `/workspace/tmp/...` - operating-system temporary space. Use only for ephemeral local
  experiments. Prefer `skills/calibre-ebooks/tmp/...` for files that may need to
  be attached, inspected, or cleaned by the skill.


## Python API Client

Run commands from the OpenClaw workspace root:

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py --help
```

Or run from inside the skill directory:

```bash
cd skills/calibre-ebooks
python3 scripts/books_api_client.py --help
```

Configuration precedence:

1. `--base URL` command-line option.
2. `BOOKS_API_URL` environment variable loaded from the shell or `.env`.
3. Default `http://host.docker.internal:6180`.

The client reads `.env` files from these locations, in order, without
overwriting variables already set in the environment:

- `skills/calibre-ebooks/scripts/.env`
- `skills/calibre-ebooks/.env`
- current working directory `.env`

Command syntax:

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py [--base URL] COMMAND [ARGS...]
```

Global option:

- `--base URL` - override `BOOKS_API_URL` and the default Books API URL for this
  invocation.

Commands:

- `docs` - print Swagger UI, ReDoc, and OpenAPI JSON URLs for the selected API
  base.
- `openapi` - fetch and print the current OpenAPI JSON document.
- `paths` - summarize available API paths with methods, operation IDs, path
  parameters, and query parameters.
- `search QUERY [--limit N]` - search books using the best matching GET endpoint
  discovered from OpenAPI.
- `book BOOK_ID` - fetch book details by ID using the best matching detail
  endpoint discovered from OpenAPI.
- `request METHOD PATH [--query KEY=VALUE ...] [--body JSON] [--output PATH]
  [--output-dir DIR]` - call a specific endpoint after inspecting OpenAPI.

`request` parameters:

- `METHOD` - one of `GET`, `POST`, `PUT`, `PATCH`, or `DELETE`.
- `PATH` - API path such as `/api/books`, or a full `http(s)` URL.
- `--query KEY=VALUE` - add one query-string pair. Repeat it for multiple
  parameters, for example `--query q=python --query limit=10`.
- `--body JSON` - send a raw JSON request body. The client sets
  `Content-Type: application/json`.
- `--output PATH` - save the response to a file or directory. If `PATH` ends
  with `/` or is an existing directory, the API filename or a safe fallback name
  is used.
- `--output-dir DIR` - create/use `DIR` and save the response there with the
  API filename or a safe fallback name. Prefer this for temporary local file
  exports and covers.

Show documentation URLs:

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py docs
```

Fetch the current OpenAPI specification:

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py openapi
```

List available API paths with methods and parameters:

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py paths
```

Search using endpoint discovery from OpenAPI:

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py search "termo ou titulo" --limit 10
```

Get book details by ID using endpoint discovery from OpenAPI:

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py book 123
```

Save a book cover image when the API exposes the cover endpoint:

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py request GET /api/books/123/cover --output-dir /workspace/tmp/calibre-covers
```
external folder: `skills/calibre-ebooks/tmp/calibre-covers`

Get library and RAG summary statistics:

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py request GET /api/stats/library
```

Select a random book from the API catalog when the OpenAPI spec exposes a
pagination/list endpoint:

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py request GET /api/books --query limit=1000
```

Call an explicit endpoint after inspecting OpenAPI:

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py request GET /books --query q=python --query limit=10
python3 skills/calibre-ebooks/scripts/books_api_client.py request GET /books/123
python3 skills/calibre-ebooks/scripts/books_api_client.py request POST /search --body '{"query":"python","limit":10}'
```

Save a file response when the API exposes a local file-access endpoint:

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py request GET /api/books/123/file --output-dir skills/calibre-ebooks/tmp/downloads
python3 skills/calibre-ebooks/scripts/books_api_client.py request GET /books/123/download --query format=EPUB --output-dir /workspace/tmp/downloads
```

external folder `skills/calibre-ebooks/tmp/downloads`

When the running API exposes `/api/books/{id}/file`, prefer it for local access:
the server returns the selected available Calibre format with the `X-Book-Format`
header. Use `/api/books/{id}/pdf` only when the user explicitly needs PDF or the
OpenAPI metadata confirms that PDF is available.

For local file exports meant to be sent as attachments to an authorized user,
save them in `/workspace/tmp/downloads`; externally this maps to
`skills/calibre-ebooks/tmp/downloads/`. Use `--output-dir` so the API-provided
complete filename is preserved. After the attachment is sent and the runtime has
confirmed the upload/read, delete the temporary copy to avoid accumulating book
files in the workspace. Never delete files from the Calibre library itself.

If `BOOKS_API_URL` is set, the client uses it instead of
`http://host.docker.internal:6180`. You can also pass `--base URL`.

## Recommended Workflow

1. Understand whether the user wants discovery, metadata, file access,
   or semantic analysis.
2. Run `books_api_client.py paths` or `openapi` before making specific API
   calls unless the exact endpoint has already been confirmed in this session.
3. Search and fetch details through the Books API. Confirm title, authors,
   formats, selected file format, and local access before promising
   delivery or analysis.
4. If the API exposes local file-access endpoints, use `books_api_client.py request` with the exact method and path from OpenAPI.
5. Never use destructive Calibre operations without explicit user request.
6. Do not search for, recommend, facilitate, or describe unauthorized sources
   for books. This skill is for the user's existing Calibre library only.

## Conversational Book Replies

Every book question should help the group conversation continue. Treat local
availability as one part of the answer, not as the whole answer. Prefer a
fluid paragraph or two over checklist-style replies.

When a user asks about a book, author, genre, topic, edition, or reading path:

1. Answer in a welcoming, intelligent tone that makes the reader feel invited
   into the library conversation.
2. If the book is confirmed in the local Calibre library, mention the confirmed
   title, author, id, and formats naturally in the prose, then add a
   reader-facing note about what the book is about, why it matters, who may
   enjoy it, or which question it helps answer.
3. If the book is not confirmed locally, do not answer like an inventory
   failure. Say naturally that the library does not have it yet, then continue
   by presenting the book or topic using verified public knowledge when
   available. Do not make the absence sound like a closed door.
4. Do not invent metadata. If external facts are not verified, phrase the reply
   as context, theme, or likely reading direction rather than as confirmed
   bibliographic detail.
5. End with one natural invitation to continue, such as asking whether the
   reader wants similar books in the local library, a reading order, a summary
   of the theme, or alternatives by the same subject. The invitation should feel
   conversational, not like a form.

For a missing book, the visible reply should usually flow like this:

1. "The book you mentioned is interesting..." or, when appropriate, a direct
   neutral variation such as "This book opens an interesting conversation
   about..."
2. "It is not in the local library yet..."
3. A short, useful presentation of the book, subject, author, or field.
4. Lawful places to look when verified or generally appropriate: Amazon, Google
   Books, the publisher, and the official site for the book when such a
   site is verified. If there is no verified official site, do not mention one.
5. "I have informed Carlos Delfino about the absence; he will try to find it."
6. One invitation to continue: similar books in the local library, related
   authors, reading order, or a short explanation of the topic.

Do not tell the group that the item was written to memory,
`calibre-missing-books.md`, logs, queues, or any other internal file. The public
wording is only that Carlos Delfino was informed about the absence.

Example missing-book voice:

`The book you mentioned is interesting because it enters a discussion about
memory, identity, and how personal experience shapes our choices. It is not
in the local library yet, but you can usually find it through lawful channels
such as Amazon, Google Books, or the publisher. I have informed Carlos Delfino
about the absence; he will try to find it. If you want, I can search the local
collection for something in the same line while you wait.`

Avoid dead-end replies such as only saying that the title is missing, only
listing IDs, mentioning internal memory/logging, or ending with a bare
operational status.

## References When Requested

If the user asks for references, sources, links, or where the cited information
came from, add a final `References` section to the visible reply.

In that section:

- Name each consulted source, such as Google Books, Amazon, the publisher, the
  official book site, a public library catalog, Wikipedia/Wikidata, or another
  verifiable catalog.
- Include a link only when the exact page was confirmed. Do not invent URLs,
  ASINs, ISBNs, publisher pages, or official sites.
- State which details came from each source: title, author, publisher, year,
  synopsis, subject, edition, ISBN, official page, or public availability.
- If the information came from the local library, cite it as `local Calibre
  library` and expose only user-safe details such as title, author, id, and
  formats.
- Do not cite internal commands, API endpoints, local filesystem paths, raw JSON,
  logs, OpenAPI schemas, or runtime diagnostics as references.
- For WhatsApp/Discord-style channels, use simple bullets instead of Markdown
  tables.

Recommended shape:

`References`

`- Google Books: volume page consulted for title, author, publisher, and
synopsis. <confirmed link>`

`- Publisher: official page consulted for description and edition data.
<confirmed link>`

## User-Facing Privacy

Treat API URLs, server addresses, ports, OpenAPI paths, schema names, command
lines, exit codes, filesystem paths, environment variables, timeout/connection
errors, service-credit errors, and dependency diagnostics as internal
instrumentation. Do not include those details in a user-facing reply unless the
user explicitly asks for a technical/debug answer.

When a catalog/API/local lookup fails, do not list the failed services,
commands, ports, URLs, paths, or raw errors. Reply in library language:

- "This title is not in the local library yet, but it connects with..."
- "I could not confirm this book in the collection right now; even so, its theme
  touches on..."
- "I have informed Carlos Delfino about the absence; he will try to find it. I can
  look for something close in the collection in the meantime."

Do not end a normal book request by asking the user to restart services, run
commands, wait for ports, or retry the API. Offer a useful next step instead:
alternatives already confirmed in the local catalog, or a note that the item was
registered for later review.

## Long-running Operations And Progress Updates

Some Calibre and RAG operations can take several minutes, especially indexing,
semantic search over a large collection, attachment processing, and metadata
enrichment.

When an operation may take longer than 2 minutes:

1. Send an initial visible message saying what will be processed and which step
   is starting.
2. Prefer queue/background/status workflows over a single blocking command. Use
   API status endpoints or lightweight status commands when available.
3. While the operation is active, send a short status update every 120 seconds
   through the available chat/message tool.
4. Include the current step, elapsed time, completed/total count when known, and
   the next expected step.
5. If progress numbers are not available, still send a concise heartbeat such as
   "I am still processing; current step: generating embeddings; elapsed time:
   4 min."
6. Do not expose local filesystem paths, localhost URLs, internal API URLs, or
   server-only links in progress messages.
7. On completion, send one final summary with the result, relevant counts, and
   any failed or skipped items. On error or timeout, report the last completed
   step and the safest next action.

If the only available implementation is a single long blocking command, do not
claim that live progress messages are possible from the agent while that command
is running. Use a queued/background mode or a command that writes/checkpoints
status so the agent can poll and update the group every 120 seconds.

## Library And RAG Statistics

When asked for counts such as indexed books, authors, publishers,
categories, RAG chunks/excerpts, embedding model, chunk size, or
overlap, call:

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py request GET /api/stats/library
```

Trigger this workflow for questions like:

- "how many books have already been indexed?"
- "how many topics are cataloged?"
- "what is the library status?"
- "how is the library doing?"
- "what is the library state?"
- "what condition is the library in?"
- "give me information about the library"
- "what is the RAG status?"
- "how many authors/publishers/categories are there?"

The endpoint returns:

- `indexed_books`
- `authors`
- `publishers`
- `categories`
- `cataloged_topics`
- `library_status`
- `rag.chunks_excerpts`
- `rag.embedding_model`
- `rag.chunk_size`
- `rag.overlap`
- `usage.total_registered_requests`
- `usage.most_requested_books`
- `usage.latest_requested_book`

For user-facing replies, answer in English with a compact status summary.
Use `cataloged_topics` when the user asks about topics. Use
`library_status` when the user asks for overall library status. For broad
questions about the library situation, state, condition, or general information,
treat them as library status requests and include catalog/RAG statistics plus
usage statistics when available: top 5 requested books and latest requested
book. Do not expose raw JSON, OpenAPI paths, local URLs, endpoint names, command
exit codes, or server parameters unless the user explicitly asks for technical
details.

## Book Covers

When the user asks for a book cover, or when a recommendation would benefit
from the cover, use the Books API cover endpoint after identifying the book id.

Workflow:

1. Find or confirm the book id through the Books API.
2. Save the cover image inside this skill's temporary workspace:
   `/workspace/tmp/calibre-covers/`; externally this maps to
   `skills/calibre-ebooks/tmp/calibre-covers/`
3. Use `--output-dir` so the API filename is used, or a deterministic filename
   such as `book-123-cover.jpg` when an explicit path is required.
4. Send the image as an attachment using a `MEDIA:` directive on its own line:
   `MEDIA:skills/calibre-ebooks/tmp/calibre-covers/book-123-cover.jpg`
5. In the visible text, mention the title and author briefly. Do not print local
   filesystem paths, local API URLs, or server-only links.
6. If the cover endpoint returns 404 or no image is available, say that the
   cover is not available for that book and continue with metadata if useful.
7. After the image attachment is sent and confirmed by the runtime, delete the
   temporary cover file from `/workspace/tmp/calibre-covers/`.

## Title Search Fallback

When the user asks for a specific book by title, do not stop after a failed
catalog/title search.

1. Search the Books API for the title or quoted phrase:
   `python3 skills/calibre-ebooks/scripts/books_api_client.py search "provided title" --limit 10`
2. If title/metadata search still does not find a clear match, search
   semantically in the available RAG index before saying the book was not found:
   `python3 skills/calibre-ebooks/calibre-openclaw-server/scripts/document_semantic_rag.py --search "provided title" --json`
3. Use RAG results to identify likely related books by document/book id, page,
   similarity, and excerpt. Present them as probable semantic matches, not exact
   title matches, unless metadata confirms the title.
4. Only say that nothing was found after both catalog/title search and RAG
   semantic search fail or the RAG base is unavailable. If RAG is unavailable,
   state that the catalog search was tried and the semantic RAG fallback could
   not be used.
5. When the book is not found, append a Markdown entry to
   `memory/calibre-missing-books.md` so Carlos can research it later. Include
   date, requested title/name, author(s) if the user supplied them, requester
   context if useful, and a short note of which searches failed.
6. After recording the missing book, suggest up to three alternatives from the
   existing library when possible. Infer category, style, genre, author,
   subject, and theme from the request and from any RAG snippets returned. Search
   the catalog/RAG again with those terms, then recommend books that are close in
   category, style, or theme. Clearly label them as alternatives, not as the
   requested book.
7. If the user wants to research the missing title outside the local library,
   suggest consulting Google Books or Amazon Books as public catalog/store pages
   for metadata, editions, publisher information, and lawful availability. Do
   not provide or imply unauthorized download sources.
8. Keep the visible reply open-ended and inviting: briefly introduce what the
   requested book or subject is about when you can verify it, connect it to a
   useful theme, then invite the reader to ask for similar books, context,
   author background, or a reading route.
9. In the visible reply, do not mention that the missing book was registered in
   memory or any internal file. Say only that Carlos Delfino was informed about
   the absence and will try to find it.

Alternative suggestions should include:

- title and id;
- authors;
- matching reason, e.g. same theme, similar genre, related subject, comparable
  style, or useful substitute;
- available formats;
- no local/server-only links.

## Incoming Book Attachments

When someone sends a book file in the configured WhatsApp group, accept only
book-like attachments in formats supported by the Calibre workflow, preferably
PDF, EPUB, AZW3, MOBI, DjVu, TXT, RTF, or DOCX, for manual import review.

Workflow:

1. Confirm the attachment is a book-like supported ebook/document format. If it
   is another format, politely refuse and ask for a common ebook format such as
   PDF or EPUB.
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
   status `waiting for manual import`.
7. Reply briefly to the group that the file was received and queued for manual
   Calibre import. Do not publish local filesystem paths, local API URLs, or
   internal media links in the group.

The import queue lives in the Rapport Bibliotecario agent workspace:

```text
/home/carlosdelfino/workspace/openclaw-workspace/agents/rapport-bibliotecario/memory/calibre-import-queue/
```

## Random Book Suggestions

When the user asks for a book suggestion, a random book, "recommend me a book",
or any generic book request without a specific title/author/topic, first try to
provide one book from the Calibre library. For topic-based recommendations such
as "recommend me a book about Python and digital twins", search the local library
first with the topic terms and reasonable variants. If no local result is
confirmed, say that the local library does not currently have a clear match and,
when possible, suggest nearby alternatives already present in Calibre. You may
also suggest consulting Google Books or Amazon Books for public catalog/store
information about titles that are not in the local library.

## Good Night Reading Suggestions

When the user says "good night", "good night everyone", "I am going to sleep", "see you
tomorrow", or another night-time farewell, treat it as a light recommendation
opportunity, not as a normal generic random-book request.

Response goals:

1. Reply warmly and briefly.
2. Suggest one light, restful book for bedtime reading: chronicles, poetry,
   short stories, contemplative literature, gentle essays, calm spirituality, or
   quiet classics. Avoid heavy, technical, violent, polemical, or dense books.
3. Search the local Calibre library first when available. If a suitable local
   book is confirmed, mention title, author, id, and formats naturally.
4. If the selected bedtime book is not confirmed in the local library, append an
   internal missing-book entry to `memory/calibre-missing-books.md` so it can be
   obtained later. Do not tell the group about memory, files, queues, logs, or
   internal registration.
5. Public wording for missing bedtime suggestions should be:
   "This one is not in the local library yet, but I have informed Carlos Delfino
   so he can try to find it."
6. Even when the book is missing locally, present it gently: why it fits bedtime,
   what mood it brings, and why it can help the reader slow down.
7. Keep the reply conversational, ideally one short paragraph. Close with a
   calm good-night sentence.

Example:

`Good night. To close the day lightly, I would suggest The Little Prince, by
Antoine de Saint-Exupery: it is a brief, luminous read, good for remembering
friendship, care, and simplicity before sleeping. This one is not in the local
library yet, but I have informed Carlos Delfino so he can try to find it. May
the reading be short and sleep come gently.`

Preferred API workflow:

1. Run `books_api_client.py paths` or `openapi` unless the list endpoint is
   already known in this session.
2. Fetch a broad page from the list endpoint, for example:
   `python3 skills/calibre-ebooks/scripts/books_api_client.py request GET /api/books --query limit=1000`
3. Randomly choose exactly one item from the returned `books` array.
4. Return a useful reader-facing recommendation with title, authors,
   publisher, publication year, formats, id, synopsis/description, key
   themes, who it is for, why it is worth reading, and the practical context
   where the book applies. Base the synopsis on metadata/comments when
   available; summarize instead of copying long passages.

If the API is unreachable or does not expose enough catalog items, use the
read-only local fallback:

```bash
python3 skills/calibre-ebooks/calibre-openclaw-server/scripts/calibre_query.py --db "$CALIBRE_METADATA_DB" random
```

Do not repeatedly return the first item from a list. The selection must be
randomized for each request.

Do not include local server/API/file links such as `localhost`, `0.0.0.0`,
`127.0.0.1`, `host.docker.internal`, `/api/books/...`, `file://`, or filesystem paths. Those links are
not valid for group members outside the server. If access is needed, say that
the book is available in the Calibre library and provide only the book id,
title, authors, and formats so the librarian/admin can locate it.

Recommended response shape for random suggestions:

- `Book`: title and id.
- `Author(s)`: authors from metadata.
- `Publisher and year`: publisher and publication year when available; say
  `not provided` only when metadata is missing.
- `Formats`: available file formats.
- `Synopsis`: three to five short sentences based on Calibre
  comments/description, enough for a reader to understand what the book is
  about.
- `Main themes`: two to four concrete themes covered by the book.
- `Why read it`: one or two practical reasons why the recommendation is
  relevant.
- `Context`: who should read it, what problem/topic it helps with, and when it
  is useful.
- `Access`: mention that it is in the Calibre library by id/formats; do not add
  local or server-only links.

## Response Rules

- Do not mention which API endpoint/method was used when returning API-derived
  results unless the user explicitly asked for technical details.
- Show `id`, title, authors, and formats when there are multiple book matches.
- Do not promise a specific format until the API response confirms that format
  or local file access.
- If the API is unreachable, keep the URL, port, path, timeout, connection
  error, and command output internal. Use local fallback when available, then
  answer in user-facing language without exposing operational details.
- For title lookups with no clear catalog result, search the RAG base
  semantically before saying the book was not found. If RAG is unavailable,
  do not expose dependency, path, or service details; just say the local
  catalog did not confirm a match.
- When a requested book is still not found, write it to
  `memory/calibre-missing-books.md` before replying. Keep entries append-only
  unless Carlos asks to organize the file.
- If a requested book is missing, try alternatives from the same category,
  style, or theme before ending the reply. Make clear that suggestions come from
  the current local library. If useful, suggest consulting Google Books or
  Amazon Books for public catalog/store information about the missing title.
- Missing locally does not mean the conversation ends. Give the reader useful
  context about the book or subject when verified, then leave one warm opening
  for the next interaction.
- If `document_semantic_rag.py --check --json` reports missing dependencies,
  keep exact dependency diagnostics internal unless the user asked for technical
  debugging. For normal users, say only that semantic analysis is unavailable
  right now and continue with local catalog options.
- For RAG-based answers, enrich the visible reply with the returned excerpt and
  cite document/book, page, chapter/section when available, similarity, and the
  relevant excerpt. If the API/script returns a `citation` field, use it as the
  citation base. Do not answer from memory when a RAG excerpt is available for
  the same claim.
- If someone asks where the books come from, explain only that this skill does
  not add or source books. It manages and queries books that are already present
  in the user's local Calibre library. For books outside the library, suggest
  lawful public catalog/store references such as Google Books or Amazon Books.
