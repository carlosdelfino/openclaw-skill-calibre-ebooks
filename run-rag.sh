#!/bin/bash

# Calibre OpenClaw Server - RAG Embedding Worker
# Run the embedding prefetch worker from the command line without systemd.

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

echo "=========================================="
echo "Calibre OpenClaw RAG - Startup Check"
echo "=========================================="
echo ""

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv "$VENV_DIR"
    "$VENV_PYTHON" -m pip install --upgrade pip --no-cache-dir
    echo -e "${GREEN}✓ Virtual environment created at $VENV_DIR${NC}"
else
    echo -e "${GREEN}✓ Virtual environment found at $VENV_DIR${NC}"
fi

ENV_FILE=""
CALL_DIR="$(pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

for dir in "$SCRIPT_DIR" "$CALL_DIR" "$PARENT_DIR"; do
    if [ -f "$dir/.env" ]; then
        ENV_FILE="$dir/.env"
        echo -e "${GREEN}✓ .env file found at $ENV_FILE${NC}"
        break
    fi
done

if [ -z "$ENV_FILE" ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo "Searched in:"
    echo "  - $SCRIPT_DIR/.env"
    echo "  - $CALL_DIR/.env"
    echo "  - $PARENT_DIR/.env"
    exit 1
fi

export ENV_DIR="$(dirname "$ENV_FILE")"
set -a
source "$ENV_FILE"
set +a

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}ERROR: requirements.txt not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ requirements.txt found${NC}"

if [ ! -f "$VENV_PYTHON" ]; then
    echo -e "${RED}ERROR: Virtual environment Python not found at $VENV_PYTHON${NC}"
    exit 1
fi

missing_packages=0
for package in fastapi uvicorn pydantic psycopg2 fitz httpx; do
    if "$VENV_PYTHON" -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✓ $package is installed${NC}"
    else
        echo -e "${YELLOW}✗ $package is NOT installed${NC}"
        missing_packages=$((missing_packages + 1))
    fi
done

if [ "$missing_packages" -gt 0 ]; then
    echo "Installing missing dependencies from requirements.txt..."
    "$VENV_PIP" install -r requirements.txt
fi

OLLAMA_URL="${OLLAMA_HOST:-http://localhost:11434}"
OLLAMA_MODEL_NAME="${OLLAMA_MODEL:-nomic-embed-text-v2-moe:latest}"

if curl -s "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama is running at $OLLAMA_URL${NC}"
    if curl -s "$OLLAMA_URL/api/tags" | grep -q "${OLLAMA_MODEL_NAME%%:*}"; then
        echo -e "${GREEN}✓ $OLLAMA_MODEL_NAME model is available${NC}"
    else
        echo -e "${YELLOW}⚠ $OLLAMA_MODEL_NAME model may not be downloaded${NC}"
        echo "  You can download it with: ollama pull $OLLAMA_MODEL_NAME"
    fi
else
    echo -e "${YELLOW}⚠ Ollama is not reachable at $OLLAMA_URL${NC}"
    echo "  Start it before running embeddings."
fi

PGUSER="${POSTGRESQL_DB_USER:-generativa}"
PGPASSWORD="${POSTGRESQL_DB_PASSWD:-}"
PGDATABASE="${POSTGRESQL_DB_DATABASE:-rapport_biblioteca}"
PGHOST="${POSTGRESQL_DB_HOST:-localhost}"
PGPORT="${POSTGRESQL_DB_PORT:-5432}"

if PGPASSWORD="$PGPASSWORD" psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is accessible${NC}"
else
    echo -e "${RED}ERROR: PostgreSQL is not accessible${NC}"
    echo "Check PostgreSQL and credentials in $ENV_FILE"
    exit 1
fi

CALIBRE_DB="${CALIBRE_DB_PATH:-/mnt/Backup_2/Biblioteca/metadata.db}"
if [ -f "$CALIBRE_DB" ]; then
    echo -e "${GREEN}✓ Calibre metadata.db found at $CALIBRE_DB${NC}"
else
    echo -e "${RED}ERROR: Calibre metadata.db not found at $CALIBRE_DB${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Checks passed. Running RAG embedding worker..."
echo "==========================================${NC}"
echo ""

"$VENV_PYTHON" -m app.nightly_embeddings --continuous "$@"
