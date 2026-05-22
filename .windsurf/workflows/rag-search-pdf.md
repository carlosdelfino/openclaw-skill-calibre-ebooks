![visitors](https://visitor-badge.laobi.icu/badge?page_id=carlosdelfino.openclaw-skill-calibre-ebooks)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
![Language: Portuguese](https://img.shields.io/badge/Language-Portuguese-brightgreen.svg)
![Workflow](https://img.shields.io/badge/Workflow-RAG-blue)
![RAG](https://img.shields.io/badge/RAG-Semantic-green)
![Status](https://img.shields.io/badge/Status-Development-brightgreen)

<!-- Animated Header -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:1a56db,100:10b981&height=220&section=header&text=RAG%20Search%20PDF&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=Busca%20Contextual%20com%20Links%20PDF&descSize=18&descAlignY=55&descColor=94a3b8" width="100%" alt="RAG Search PDF Header"/>
</p>

---
description: Busca contextual na base de documentos com links clicáveis para PDFs
---

# Workflow de Busca Contextual RAG com PDF Links

Este workflow permite realizar buscas inteligentes na sua base de documentos e abrir os PDFs diretamente na página encontrada.

## Uso

Digite `/rag-search-pdf` seguido do termo que deseja pesquisar.

## Exemplos

- `/rag-search-pdf redes neurais convolucionais`
- `/rag-search-pdf machine learning algorithms`
- `/rag-search-pdf python programming`
- `/rag-search-pdf data science`

## O que acontece

1. **Busca Semântica**: Encontra documentos relevantes usando embeddings
2. **Links Clicáveis**: Gera links diretos para os PDFs na página específica
3. **Abertura Automática**: Oferece opção para abrir o PDF no visualizador padrão
4. **Contexto Rico**: Mostra trechos relevantes com alta similaridade

## Resultados

Cada resultado inclui:
- 📄 Nome do documento
- 📖 Página específica com link clicável
- 🎯 Trecho relevante
- 📊 Pontuação de similaridade
- 🔗 Link direto: `file://[caminho]#page=[numero]`
- 🚀 Botão para abrir PDF automaticamente

## Funcionalidades Especiais

### Links Clicáveis
- Clique nos links `file://` para abrir o PDF diretamente na página
- Funciona com a maioria dos visualizadores de PDF
- Links são absolutos e funcionam em qualquer sistema

### Abertura Automática
- Use a ferramenta `rag_open_pdf` para abrir automaticamente
- Suporta Windows, macOS e Linux
- Abre no visualizador padrão do sistema

### Exemplo de Uso Avançado

```
Busque por "transformer architecture" e me mostre os 3 melhores resultados com links para PDF
```

## Dicas

- **Termos Específicos**: Use linguagem técnica para melhores resultados
- **Combinar Conceitos**: `deep learning convolutional networks`
- **Navegação Rápida**: Clique nos links para ir direto ao conteúdo
- **Visualização**: Os PDFs abrem na página exata do conteúdo encontrado

## Comandos Relacionados

- `/rag-search-pdf` - Busca com links para PDFs
- `rag_open_pdf` - Abre PDF automaticamente
- `rag_list_books` - Lista todos os livros disponíveis

## Configuração

Este workflow usa o MCP server `rag-local` com suporte aprimorado para PDFs. Certifique-se de que os PDFs originais estejam acessíveis nos caminhos registrados no banco de dados.

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:10b981,50:1a56db,100:0f172a&height=120&section=footer" width="100%" alt="Footer"/>
</p>

---
**Resumo:** Workflow para busca contextual em base de documentos com links clicáveis para PDFs, permitindo abertura direta na página encontrada via MCP server rag-local.
**Data de Criação:** 2026-05-08
**Autor:** Carlos Delfino
**Versão:** 1.0
**Última Atualização:** 2026-05-22
**Atualizado por:** Carlos Delfino
**Histórico de Alterações:**
- 2026-05-22 - Atualizado por Carlos Delfino - Adição de badges, header e footer animados seguindo novas regras de documentação - Versão 1.1
- 2026-05-08 - Criado por Carlos Delfino - Versão 1.0
