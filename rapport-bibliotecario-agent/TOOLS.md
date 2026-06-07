# TOOLS.md - Rapport Bibliotecario

Este arquivo concentra ferramentas e comandos. Regras de comportamento ficam em
`AGENTS.md`; persona e limites ficam em `IDENTITY.md`.

## Fonte Principal

Use o skill `calibre-ebooks` para catalogo, metadados, formatos, capas,
download/acesso, status da biblioteca e fluxos Calibre:

`/skills/calibre-ebooks/SKILL.md` a partir da raiz do workspace OpenClaw.

Nao chame host, porta, endpoint, OpenAPI ou URL interna diretamente a partir
deste agente. Essas configuracoes pertencem ao skill.

Workflow:

1. Classificar o pedido: busca, metadados, capa, arquivo, status, RAG ou
   processamento.
2. Ler `skills/calibre-ebooks/SKILL.md` quando o runtime ainda nao trouxe o
   skill.
3. Usar o cliente e fluxos documentados pelo skill.
4. Confirmar `id`, titulo, autor e formato/acesso antes de apresentar,
   entregar, recomendar como local ou indexar.
5. Usar fallback local/legado somente quando o skill orientar ou nao cobrir a
   operacao.

## Higiene Visivel

Comandos, JSON, OpenAPI, endpoints, paths, parametros, codigos de saida, URLs
internas e diagnosticos sao insumos internos. Em canal publico, responda apenas
com o resultado util. Se heartbeat ou consulta falhar, registre detalhes apenas
em memoria local para recuperacao posterior; nao publique status de falha.

## Cliente do Skill

Executar a partir da raiz do workspace.

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py paths
python3 skills/calibre-ebooks/scripts/books_api_client.py search "termo" --limit 10
python3 skills/calibre-ebooks/scripts/books_api_client.py semantic "consulta" --limit 10 --threshold 0.3
python3 skills/calibre-ebooks/scripts/books_api_client.py book 123
python3 skills/calibre-ebooks/scripts/books_api_client.py request ...
```

Uso:

- `paths`: descoberta interna das operacoes publicadas pelo cliente.
- `search`: busca flexivel principal. O servidor procura primeiro no catalogo
  e, se nao houver resultado, cai para RAG/semantica quando disponivel.
- `semantic`: busca semantica/RAG pura no conteudo ja indexado pelo servidor;
  usar quando o pedido for explicitamente sobre trechos/conteudo/RAG.
- `book`: confirma metadados e formatos de um ID real.
- `request`: somente quando o `SKILL.md` orientar ou a operacao tiver sido
  descoberta pelo proprio cliente.

Nunca tratar resultado sem `id` real como livro confirmado da biblioteca.

## Status da Biblioteca e RAG

Para pedidos de status, contagem, temas, autores, editoras, uso ou RAG, use o
fluxo de status documentado no skill `calibre-ebooks`.

Campos uteis quando retornados:

- `livros_indexados`
- `temas_catalogados`
- `autores`
- `editoras`
- `rag.chunks_trechos`
- `rag.modelo_de_embedding`
- `rag.tamanho_do_chunk`
- `rag.sobreposicao`
- `status_biblioteca`
- `uso.livros_mais_pedidos`
- `uso.ultimo_livro_solicitado`

Transforme dados estruturados em portugues legivel. Nao estime colecao por IDs.

## Fallback Local Calibre

Use apenas quando `calibre-ebooks` orientar, quando o fluxo principal estiver
indisponivel ou quando a tarefa exigir arquivo local/RAG.

```bash
python3 skills/calibre-ebooks/scripts/calibre_query.py list --limit 20
python3 skills/calibre-ebooks/scripts/calibre_query.py search "termo" --limit 10
python3 skills/calibre-ebooks/scripts/calibre_query.py metadata 123
python3 skills/calibre-ebooks/scripts/calibre_query.py path 123
```

Uso:

- `list`: amostra read-only quando `CALIBRE_METADATA_DB` estiver configurado.
- `search`: localizar candidatos.
- `metadata`: confirmar titulo, autores, tags, formatos e observacoes.
- `path`: resolver arquivos reais para analise ou entrega.

## RAG Local do `calibre-ebooks`

Para pedidos comuns de descoberta de livros, use primeiro `search`; ele ja faz
catalogo e fallback semantico no servidor. Use a busca semantica pura do Books
API quando o objetivo for procurar conteudo ja indexado:

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py semantic "consulta" --limit 10 --threshold 0.3
```

Use o script local abaixo para manutencao/indexacao local, diagnostico de RAG ou
quando o endpoint semantico da API estiver indisponivel.

```bash
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --check --json
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --status --json
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --list --json
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --calibre-id 123 --json
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --convert "/path/livro.pdf" --json
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --search "consulta" --json
python3 skills/calibre-ebooks/scripts/document_semantic_rag.py --delete RAG_BOOK_ID --json
```

Uso:

- `--check`: dependencias, binarios e acesso local.
- `--status`: base, modelo, livros indexados e chunks.
- `--list`: itens indexados.
- `--calibre-id`: indexa livro confirmado por ID do Calibre.
- `--convert`: indexa arquivo confirmado.
- `--search`: busca hibrida texto + embeddings.
- `--delete`: remove item RAG somente com pedido explicito do usuario.

Defaults do RAG local:

- SQLite/chunks: `/tmp/openclaw-calibre-rag/data/documents.db`
- ChromaDB: `/tmp/openclaw-calibre-rag/data/chroma_db`
- Markdown convertido: `/tmp/openclaw-calibre-rag/converteds`
- Modelo padrao: `nomic-embed-text-v2-moe:latest` via Ollama, salvo ajuste do
  skill.

## Fluxo RAG Recomendado

1. Buscar candidato no catalogo.
2. Confirmar detalhe e formato.
3. Checar base RAG.
4. Indexar por ID ou arquivo confirmado quando necessario.
5. Para pedido comum, use `books_api_client.py search`; para pergunta
   explicitamente semantica/conteudo, use `books_api_client.py semantic`.
6. Responder com trecho, livro/documento, pagina quando disponivel e limite da
   evidencia.

## Livros Ausentes

Depois de busca local sem confirmacao:

- Registrar em `memory/calibre-missing-books.md`.
- Consultar Google Books preferencialmente.
- Usar Amazon Books somente com link real verificado.
- Nao inventar ASIN, ISBN, edicao, URL ou metadados.

Modelo interno de registro:

```text
YYYY-MM-DD - Pedido: "..."
Variacoes buscadas: ...
Resultado local: nao encontrado
Link externo confirmado: ...
```
