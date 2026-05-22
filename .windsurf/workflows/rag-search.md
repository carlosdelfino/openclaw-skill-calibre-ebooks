![visitors](https://visitor-badge.laobi.icu/badge?page_id=carlosdelfino.openclaw-skill-calibre-ebooks)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
![Language: Portuguese](https://img.shields.io/badge/Language-Portuguese-brightgreen.svg)
![Workflow](https://img.shields.io/badge/Workflow-RAG-blue)
![RAG](https://img.shields.io/badge/RAG-Semantic-green)
![Status](https://img.shields.io/badge/Status-Development-brightgreen)

<!-- Animated Header -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:1a56db,100:10b981&height=220&section=header&text=RAG%20Search&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=Busca%20Contextual%20em%20Documentos&descSize=18&descAlignY=55&descColor=94a3b8" width="100%" alt="RAG Search Header"/>
</p>

---
description: Busca contextual na base de documentos usando embeddings
---

# Workflow de Busca Contextual RAG

Este workflow permite realizar buscas inteligentes na sua base de documentos indexados usando embeddings e busca semântica.

## Uso

Digite `/rag-search` seguido do termo que deseja pesquisar.

## Exemplos

- `/rag-search redes neurais convolucionais`
- `/rag-search machine learning algorithms`
- `/rag-search python programming`
- `/rag-search data science`

## O que acontece

1. **Geração de Embedding**: O termo de busca é convertido em um vetor numérico usando Ollama
2. **Busca Semântica**: O sistema encontra documentos com significados similares
3. **Ranking**: Resultados são ordenados por relevância (similaridade)
4. **Apresentação**: Top 5 resultados são exibidos com contexto

## Resultados

Cada resultado inclui:
- 📄 Nome do documento
- 📖 Página específica
- 🎯 Trecho relevante
- 📊 Pontuação de similaridade
- 🔧 Opções para explorar mais

## Dicas

- Use termos específicos e técnicos para melhores resultados
- Combine conceitos: `transformer attention mechanism`
- Varie os termos se não encontrar resultados
- A similaridade varia de 0.0 a 1.0 (maior = mais relevante)

## Configuração

Este workflow usa o MCP server `rag-local` que deve estar configurado no Windsurf.

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:10b981,50:1a56db,100:0f172a&height=120&section=footer" width="100%" alt="Footer"/>
</p>

---
**Resumo:** Workflow para busca contextual em base de documentos usando embeddings e busca semântica via MCP server rag-local.
**Data de Criação:** 2026-05-08
**Autor:** Carlos Delfino
**Versão:** 1.0
**Última Atualização:** 2026-05-22
**Atualizado por:** Carlos Delfino
**Histórico de Alterações:**
- 2026-05-22 - Atualizado por Carlos Delfino - Adição de badges, header e footer animados seguindo novas regras de documentação - Versão 1.1
- 2026-05-08 - Criado por Carlos Delfino - Versão 1.0
