---
name: calibre-openclaw-server
description: Run and maintain the Calibre OpenClaw Books API server with citeable RAG search over local Calibre books.
metadata: '{"openclaw":{"requires":{"bins":["python3"]}}}'
---
# Calibre OpenClaw Server

This directory contains the FastAPI server used by the `calibre-ebooks` skill.
The server manages books already present in the configured local Calibre
library and provides metadata, file access, covers, statistics, embeddings, and
semantic RAG search.

## Citeable RAG

Semantic search must return enough location metadata for reader-facing answers:

- `page_start` and `page_end` when the indexed source is a PDF;
- `section_title` when a chapter or section heading can be detected;
- `citation` as a ready-to-use human-readable citation string;
- `similarity` and the matched `content` excerpt.

Agents should use these fields to enrich answers with book excerpts and cite the
page, plus chapter/section when available. Do not invent page numbers, chapters,
sections, excerpts, or availability.

## Synchronization

Keep this server directory synchronized between:

- `skills/calibre-ebooks/calibre-openclaw-server`
- `/mnt/Backup_2/Biblioteca/calibre-openclaw-server`

Do not synchronize local runtime artifacts such as `.env`, `.git`, `.venv`,
`logs`, or `__pycache__`.
