![visitors](https://visitor-badge.laobi.icu/badge?page_id=carlosdelfino.openclaw-skill-calibre-ebooks)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
![Language: Portuguese](https://img.shields.io/badge/Language-Portuguese-brightgreen.svg)
![Workflow](https://img.shields.io/badge/Workflow-Preparo-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Status](https://img.shields.io/badge/Status-Development-brightgreen)

<!-- Animated Header -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:1a56db,100:10b981&height=220&section=header&text=Preparo%20do%20Projeto&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=Workflow%20para%20Estrutura%20Inicial&descSize=18&descAlignY=55&descColor=94a3b8" width="100%" alt="Preparo do Projeto Header"/>
</p>

---
description: Prepara a estrutura inicial do projeto criando pastas essenciais e documentação
---

# Workflow de Preparo do Projeto

Este workflow configura a estrutura inicial do projeto, criando as pastas essenciais e a documentação necessária para organização e desenvolvimento.

## Visão Geral

O workflow de preparo estabelece a base do projeto criando:
- Pasta `scripts/` para armazenar todos os scripts Python
- Pasta `biblioteca/` para documentos e livros de referência
- Pasta `venv/` para ambiente virtual Python
- Atualização do `README.md` principal com informações do projeto
- Documentação dos arquivos na biblioteca (se existirem)
- Resumos em markdown para cada PDF (se existirem)

## Uso

Digite `/preparo-projeto` para executar o workflow de preparo.

## O Workflow

### 1. Criação de Pastas Essenciais

**Criar pasta `scripts/`**
- Esta pasta conterá todos os scripts Python do projeto
- Scripts de processamento de dados, análise, visualização, etc.

**Criar pasta `biblioteca/` (se não existir)**
- Esta pasta conterá documentos técnicos, livros e materiais de referência
- PDFs, artigos, documentação oficial, etc.

**Criar pasta `venv/`**
- Esta pasta conterá o ambiente virtual Python
- Bibliotecas e dependências do projeto isoladas

### 2. Atualização do README.md Principal

**Criar ou atualizar `README.md` na raiz do projeto**
- Seguir as regras de documentação definidas em `documentacao.md`
- Incluir badges obrigatórios no topo
- Incluir header animado
- Descrever o objetivo do projeto
- Listar a estrutura de pastas
- Incluir footer animado
- Adicionar resumo final e histórico

### 3. Documentação da Biblioteca (se houver arquivos)

**Criar `biblioteca/README.md`**
- Listar todos os documentos presentes na pasta biblioteca
- Descrição breve de cada documento
- Propósito e relevância para o projeto
- Data de adição ao projeto

### 4. Resumos de PDFs (se houver)

**Criar arquivo `.md` para cada PDF na biblioteca**
- Nome do arquivo: `[nome-do-pdf].md`
- Destacar pontos chave do documento
- Principais conceitos abordados
- Relevância para o projeto
- Seções importantes
- Referências cruzadas com outros documentos

## Estrutura Esperada Após Execução

```
projeto/
├── .windsurf/
│   └── workflows/
│       └── preparo-projeto.md
├── scripts/              (criado)
│   └── (scripts Python)
├── biblioteca/           (criado ou existente)
│   ├── README.md         (criado se houver documentos)
│   ├── documento1.pdf
│   ├── documento1.md     (criado para cada PDF)
│   ├── documento2.pdf
│   └── documento2.md
├── venv/                 (criado)
│   └── (ambiente virtual)
├── README.md             (criado ou atualizado)
└── (outros arquivos)
```

## Exemplo de Conteúdo

### README.md Principal

Deve seguir o padrão definido em `documentacao.md`:

```markdown
![visitors](https://visitor-badge.laobi.icu/badge?page_id=<org>.<repository>)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
![Language: Portuguese](https://img.shields.io/badge/Language-Portuguese-brightgreen.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Prática-green)
![Status](https://img.shields.io/badge/Status-Educa%C3%A7%C3%A3o-brightgreen)
![Repository Size](https://img.shields.io/github/repo-size/<org>/<repository>)
![Last Commit](https://img.shields.io/github/last-commit/<org>/<repository>)

<!-- Animated Header -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:1a56db,100:10b981&height=220&section=header&text=Nome%20do%20Projeto&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=Descrição%20do%20Projeto&descSize=18&descAlignY=55&descColor=94a3b8" width="100%" alt="Project Header"/>
</p>

## Descrição do Projeto

Conteúdo do projeto...

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:10b981,50:1a56db,100:0f172a&height=120&section=footer" width="100%" alt="Footer"/>
</p>

---
**Resumo:** [Descrição concisa]
**Data de Criação:** [AAAA-MM-DD]
**Autor:** [Nome]
**Versão:** [Versão]
**Última Atualização:** [AAAA-MM-DD]
**Atualizado por:** Carlos Delfino
**Histórico de Alterações:**
- 2026-05-08 - Atualizado por Carlos Delfino - Removendo arquivos do Agentic....
- [AAAA-MM-DD] - Criado por [Autor] - Versão [Versão]
```

### biblioteca/README.md

```markdown
# Biblioteca do Projeto

## Documentos Disponíveis

### 1. Desafio-Final-IA-Aplicada-a-Problemas-Reais.pdf
- **Descrição:** Documento principal do desafio de IA aplicada
- **Propósito:** Define os requisitos e objetivos do projeto
- **Data de Adição:** [AAAA-MM-DD]

### 2. Como-Estruturar-e-Avaliar-sua-Solucao-de-IA.pdf
- **Descrição:** Guia para estruturação e avaliação de soluções de IA
- **Propósito:** Fornece diretrizes para desenvolvimento e validação
- **Data de Adição:** [AAAA-MM-DD]

### 3. Desafio-1-Inferencia-de-Fluxos-Origem-Destino-com-IA.pdf
- **Descrição:** Especificações do desafio de inferência de fluxos
- **Propósito:** Detalha o problema de origem-destino a ser resolvido
- **Data de Adição:** [AAAA-MM-DD]
```

### biblioteca/[nome-do-pdf].md

```markdown
# [Nome do PDF]

## Resumo

Breve descrição do documento.

## Pontos Chave

- **Ponto 1:** Descrição do ponto chave
- **Ponto 2:** Descrição do ponto chave
- **Ponto 3:** Descrição do ponto chave

## Conceitos Principais

- Conceito 1
- Conceito 2
- Conceito 3

## Relevância para o Projeto

Explicação de como este documento contribui para o projeto.

## Seções Importantes

- Seção X: Descrição
- Seção Y: Descrição

## Referências Cruzadas

- Relacionado com: [outro documento]
- Complementa: [outro documento]
```

## Notas Importantes

- A pasta `venv/` deve ser criada mas não ativada automaticamente
- A ativação do ambiente virtual deve ser feita manualmente pelo usuário
- Os resumos de PDFs devem ser criados apenas se o PDF existir
- Se a biblioteca estiver vazia, o README.md da biblioteca pode ser omitido
- Todos os arquivos markdown devem seguir as regras de `documentacao.md`

## Integração com Memórias do Projeto

Este workflow integra-se com:
- `documentacao.md`: Regras de formatação para arquivos markdown
- `python.md`: Configuração de ambiente virtual Python
- `projeto.md`: Metodologia PDCL para desenvolvimento

## Próximos Passos

Após executar este workflow:
1. Ativar o ambiente virtual: `source venv/bin/activate` (Linux/Mac) ou `venv\Scripts\activate` (Windows)
2. Instalar dependências necessárias
3. Começar o desenvolvimento seguindo a metodologia PDCL

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:10b981,50:1a56db,100:0f172a&height=120&section=footer" width="100%" alt="Footer"/>
</p>

---
**Resumo:** Workflow para configuração inicial de projeto criando pastas essenciais (scripts, biblioteca, venv) e documentação seguindo padrões definidos.
**Data de Criação:** 2026-05-08
**Autor:** Carlos Delfino
**Versão:** 1.0
**Última Atualização:** 2026-05-22
**Atualizado por:** Carlos Delfino
**Histórico de Alterações:**
- 2026-05-22 - Atualizado por Carlos Delfino - Adição de badges, header e footer animados seguindo novas regras de documentação - Versão 1.1
- 2026-05-08 - Criado por Carlos Delfino - Versão 1.0
