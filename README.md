![visitors](https://visitor-badge.laobi.icu/badge?page_id=carlosdelfino.openclaw-skill-calibre-ebooks)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
![Language: Portuguese](https://img.shields.io/badge/Language-Portuguese-brightgreen.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Calibre](https://img.shields.io/badge/Calibre-Integration-orange)
![RAG](https://img.shields.io/badge/RAG-Semantic-green)
![Status](https://img.shields.io/badge/Status-Development-brightgreen)
![Repository Size](https://img.shields.io/github/repo-size/carlosdelfino/openclaw-skill-calibre-ebooks)
![Last Commit](https://img.shields.io/github/last-commit/carlosdelfino/openclaw-skill-calibre-ebooks)

<!-- Animated Header -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:1a56db,100:10b981&height=220&section=header&text=Calibre%20E-books&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=Skill%20OpenClaw%20para%20Biblioteca%20Calibre%20Local&descSize=18&descAlignY=55&descColor=94a3b8" width="100%" alt="Calibre E-books Header"/>
</p>

## Calibre E-books Skill

Skill OpenClaw para consultar e operar a biblioteca local do Calibre, com suporte a busca semântica via RAG.

### Funcionalidades Principais

- **Consulta de Metadados**: Listar, buscar e visualizar informações de livros usando `calibredb`
- **Exportação de Arquivos**: Exportar livros em diferentes formatos (PDF, EPUB, etc.)
- **Busca Semântica**: Indexação e busca contextual em documentos usando RAG
- **Fallback SQLite**: Consulta read-only direta no `metadata.db` quando necessário

### Configuração

- **Biblioteca Padrão**: `/mnt/Backup_2/Biblioteca`
- **Banco de Metadados**: `/mnt/Backup_2/Biblioteca/metadata.db`
- **Script de Consulta**: `scripts/calibre_query.py`
- **Script de RAG**: `scripts/document_semantic_rag.py`
- **Base RAG**: `/tmp/openclaw-calibre-rag/data`

### Pré-requisitos

- Calibre instalado com `calibredb` disponível
- Python 3.8+ para scripts de consulta e RAG
- Dependências RAG (opcional): ver `scripts/requirements-rag.txt`

### Uso Básico

#### Listar livros

```bash
calibredb list --library-path "/mnt/Backup_2/Biblioteca" --fields id,title,authors,formats --limit 20
```

#### Buscar por termo

```bash
calibredb search --library-path "/mnt/Backup_2/Biblioteca" "python"
```

#### Ver metadados

```bash
calibredb show_metadata --library-path "/mnt/Backup_2/Biblioteca" 123
```

#### Exportar livro

```bash
mkdir -p /tmp/openclaw-calibre-export
calibredb export --library-path "/mnt/Backup_2/Biblioteca" --to-dir /tmp/openclaw-calibre-export 123
```

### RAG - Busca Semântica

#### Checar dependências

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --check --json
```

#### Indexar livro pelo ID Calibre

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --calibre-id 123 --format PDF --json
```

#### Buscar na base RAG

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --search "redes neurais convolucionais" --json
```

### Estrutura do Projeto

```
calibre-ebooks/
├── .env                    # Configurações de ambiente
├── .env.example            # Exemplo de configurações
├── README.md               # Este arquivo
├── SKILL.md                # Documentação do skill para OpenClaw
└── scripts/
    ├── calibre_query.py           # Consulta read-only via SQLite
    ├── document_semantic_rag.py   # Conversão e RAG
    └── requirements-rag.txt       # Dependências RAG
```

### Notas Importantes

- Sempre passe o diretório da biblioteca para `calibredb`, não o arquivo `.db`
- Use `scripts/calibre_query.py` como fallback quando `calibredb` falhar
- Nunca use comandos destrutivos sem pedido explícito do usuário
- Para RAG, instale dependências via `pip install -r scripts/requirements-rag.txt`

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:10b981,50:1a56db,100:0f172a&height=120&section=footer" width="100%" alt="Footer"/>
</p>

---
**Resumo:** Skill OpenClaw para integração com biblioteca Calibre local, suportando consulta de metadados, exportação de arquivos e busca semântica via RAG.
**Data de Criação:** 2026-05-22
**Autor:** Carlos Delfino
**Versão:** 1.0
**Última Atualização:** 2026-05-22
**Atualizado por:** Carlos Delfino
**Histórico de Alterações:**
- 2026-05-22 - Criado por Carlos Delfino - Versão 1.0 - Ajuste às novas regras de documentação
