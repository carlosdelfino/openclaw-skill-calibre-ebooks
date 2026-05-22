![visitors](https://visitor-badge.laobi.icu/badge?page_id=carlosdelfino.openclaw-skill-calibre-ebooks)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
![Language: English](https://img.shields.io/badge/Language-English-brightgreen.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Calibre](https://img.shields.io/badge/Calibre-Integration-orange)
![RAG](https://img.shields.io/badge/RAG-Semantic-green)
![Status](https://img.shields.io/badge/Status-Development-brightgreen)
![Repository Size](https://img.shields.io/github/repo-size/carlosdelfino/openclaw-skill-calibre-ebooks)
![Last Commit](https://img.shields.io/github/last-commit/carlosdelfino/openclaw-skill-calibre-ebooks)

<!-- Animated Header -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:1a56db,100:10b981&height=220&section=header&text=Calibre%20E-books&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=OpenClaw%20Skill%20for%20Local%20Calibre%20Library&descSize=18&descAlignY=55&descColor=94a3b8" width="100%" alt="Calibre E-books Header"/>
</p>

## Calibre E-books Skill

OpenClaw skill to query and operate the local Calibre library, with support for semantic search via RAG.

### Key Features

- **Metadata Query**: List, search, and view book information using `calibredb`
- **File Export**: Export books in different formats (PDF, EPUB, etc.)
- **Semantic Search**: Index and contextual search in documents using RAG
- **SQLite Fallback**: Direct read-only query on `metadata.db` when needed

### Configuration

- **Default Library**: `/mnt/Backup_2/Biblioteca`
- **Metadata Database**: `/mnt/Backup_2/Biblioteca/metadata.db`
- **Query Script**: `scripts/calibre_query.py`
- **RAG Script**: `scripts/document_semantic_rag.py`
- **RAG Base**: `/tmp/openclaw-calibre-rag/data`

### Prerequisites

- Calibre installed with `calibredb` available
- Python 3.8+ for query and RAG scripts
- RAG dependencies (optional): see `scripts/requirements-rag.txt`

### Basic Usage

#### List books

```bash
calibredb list --library-path "/mnt/Backup_2/Biblioteca" --fields id,title,authors,formats --limit 20
```

#### Search by term

```bash
calibredb search --library-path "/mnt/Backup_2/Biblioteca" "python"
```

#### View metadata

```bash
calibredb show_metadata --library-path "/mnt/Backup_2/Biblioteca" 123
```

#### Export book

```bash
mkdir -p /tmp/openclaw-calibre-export
calibredb export --library-path "/mnt/Backup_2/Biblioteca" --to-dir /tmp/openclaw-calibre-export 123
```

### RAG - Semantic Search

#### Check dependencies

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --check --json
```

#### Index book by Calibre ID

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --calibre-id 123 --format PDF --json
```

#### Search in RAG base

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --search "convolutional neural networks" --json
```

### Project Structure

```
calibre-ebooks/
├── .env                    # Environment configurations
├── .env.example            # Configuration example
├── README.md               # This file
├── SKILL.md                # Skill documentation for OpenClaw
└── scripts/
    ├── calibre_query.py           # Read-only query via SQLite
    ├── document_semantic_rag.py   # Conversion and RAG
    └── requirements-rag.txt       # RAG dependencies
```

### Important Notes

- Always pass the library directory to `calibredb`, not the `.db` file
- Use `scripts/calibre_query.py` as a fallback when `calibredb` fails
- Never use destructive commands without explicit user request
- For RAG, install dependencies via `pip install -r scripts/requirements-rag.txt`

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:10b981,50:1a56db,100:0f172a&height=120&section=footer" width="100%" alt="Footer"/>
</p>

---
**Summary:** OpenClaw skill for integration with local Calibre library, supporting metadata query, file export, and semantic search via RAG.
**Creation Date:** 2026-05-22
**Author:** Carlos Delfino
**Version:** 1.0
**Last Update:** 2026-05-22
**Updated by:** Carlos Delfino
**Change History:**
- 2026-05-22 - Created by Carlos Delfino - Version 1.0 - Adjustment to new documentation rules
