# calibre-openclaw-server

Servidor FastAPI para consultar uma biblioteca Calibre local e oferecer busca
semântica RAG com citações por página.

O servidor usa:

- Calibre `metadata.db` como catálogo de livros.
- PostgreSQL com `pgvector` para embeddings.
- Ollama para gerar embeddings.
- Systemd para manter a API ativa e rodar o RAG em janela agendada.

## Requisitos

- Python 3.10+
- PostgreSQL com extensão `vector`
- Ollama em execução
- Modelo de embedding configurado em `OLLAMA_MODEL`
- Biblioteca Calibre local com `metadata.db`

## Configuração

Crie um `.env` neste diretório ou no diretório pai `skills/calibre-ebooks/`.
Use `.env.example` como base.

Variáveis essenciais:

```env
CALIBRE_DB_PATH=/caminho/para/Biblioteca/metadata.db
CALIBRE_LIBRARY_PATH=/caminho/para/Biblioteca

API_KEY=token-seguro
ALLOW_UNAUTHENTICATED=false

POSTGRESQL_DB_USER=calibre_openclaw
POSTGRESQL_DB_PASSWD=senha-segura
POSTGRESQL_DB_DATABASE=calibre_openclaw
POSTGRESQL_DB_HOST=localhost
POSTGRESQL_DB_PORT=5432

OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=nomic-embed-text-v2-moe:latest
ALLOW_REMOTE_OLLAMA=false
```

Opções sensíveis, desabilitadas por padrão no código:

```env
ALLOW_BOOK_CONTENT_DOWNLOADS=false
ENABLE_NETWORK_BINDINGS_ENDPOINT=false
ENABLE_NETWORK_BINDINGS_MONITOR=false
ALLOW_GET_AUTO_SYNC=false
```

## Executar a API

```bash
cd skills/calibre-ebooks/calibre-openclaw-server
./run.sh
```

URLs principais:

- API: `http://127.0.0.1:6180`
- Swagger: `http://127.0.0.1:6180/docs`
- ReDoc: `http://127.0.0.1:6180/redoc`
- Health: `http://127.0.0.1:6180/health`

## Cliente Local

```bash
node scripts/books-api-client.mjs docs
node scripts/books-api-client.mjs paths
node scripts/books-api-client.mjs search "termo" --limit 10
node scripts/books-api-client.mjs book 123
node scripts/books-api-client.mjs request GET /books --query q=python
```

## RAG Manual

Para processar embeddings continuamente fora da janela noturna:

```bash
cd skills/calibre-ebooks
./calibre-openclaw-server/run-rag.sh
```

Por padrão o `run-rag.sh` roda até `Ctrl+C`. Para impor horário de parada em
execução manual:

```env
RAG_RUN_STOP_AT_LOCAL=18:00
```

Também é possível passar o limite diretamente:

```bash
./calibre-openclaw-server/run-rag.sh --stop-at-local 18:00
```

## RAG Agendado

O serviço noturno é gerado por `install_service.sh` e lê o agendamento do
`.env`. Não há horário fixo no código.

```env
RAG_STOP_AT_LOCAL=06:00
RAG_TIMER_ON_CALENDAR=*-*-* 01:00:00
RAG_RUNTIME_MAX_SEC=5h
RAG_SERVICE_CONTINUOUS=false
RAG_IDLE_SLEEP_SECONDS=60
RAG_PREFETCH_RANDOM_BOOKS=false
RAG_RECONCILE_ON_START=false
RAG_ALLOW_MODEL_PULL=false
INSTALL_NIGHTLY_EMBEDDINGS=false
```

Significado:

- `RAG_TIMER_ON_CALENDAR`: quando o timer systemd inicia o worker.
- `RAG_STOP_AT_LOCAL`: horário local em que o worker para de iniciar novos livros.
- `RAG_RUNTIME_MAX_SEC`: limite máximo imposto pelo systemd.
- `RAG_SERVICE_CONTINUOUS`: mantém o worker buscando novos livros enquanto houver janela. Deixe `false` salvo quando não precisar desse comportamento persistente.
- `RAG_IDLE_SLEEP_SECONDS`: pausa entre verificações quando não há fila.
- `RAG_PREFETCH_RANDOM_BOOKS`: permite enfileirar livros automaticamente quando a fila está vazia.
- `RAG_RECONCILE_ON_START`: permite invalidar embeddings antigos quando a assinatura muda.
- `RAG_ALLOW_MODEL_PULL`: permite que o script auxiliar rode `ollama pull` se o modelo faltar.
- `INSTALL_NIGHTLY_EMBEDDINGS`: permite instalar e habilitar o timer noturno.

Para desativar o limite interno de horário do worker, deixe
`RAG_STOP_AT_LOCAL` vazio. Nesse caso, use `RAG_RUNTIME_MAX_SEC` ou controle o
tempo pelo próprio systemd.

## Instalar Serviços

```bash
cd skills/calibre-ebooks/calibre-openclaw-server
./install_service.sh install
```

Serviços criados:

- `calibre-openclaw-server.service`
- `calibre-openclaw-server-nightly-embeddings.service`
- `calibre-openclaw-server-nightly-embeddings.timer`

Comandos úteis:

```bash
sudo systemctl status calibre-openclaw-server.service
sudo systemctl restart calibre-openclaw-server.service
sudo systemctl status calibre-openclaw-server-nightly-embeddings.timer
sudo systemctl start calibre-openclaw-server-nightly-embeddings.service
```

## Banco de Dados

O servidor usa sempre o banco definido em `POSTGRESQL_DB_DATABASE`.
Na inicialização, ele cria as tabelas necessárias se não existirem.

Tabelas principais:

- `books`
- `book_chunks`
- `processing_queue`
- `settings`

## Sincronização

Quando esta pasta for usada em mais de um local, mantenha sincronizadas as
cópias de código e preserve arquivos locais como `.env`, `.venv` e `logs/`.

Exemplo:

```bash
rsync -avc \
  --exclude '.env' \
  --exclude '.venv/' \
  --exclude 'logs/' \
  --exclude '__pycache__/' \
  skills/calibre-ebooks/calibre-openclaw-server/ \
  /mnt/Backup_2/Biblioteca/calibre-openclaw-server/
```
