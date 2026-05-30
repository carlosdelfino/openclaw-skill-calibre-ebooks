# calibre-ebooks

OpenClaw skill for using the local Calibre-backed Books API.

Primary API documentation:

- Swagger UI: `http://0.0.0.0:6180/docs`
- ReDoc: `http://0.0.0.0:6180/redoc`
- OpenAPI JSON: `http://0.0.0.0:6180/openapi.json`

Use the bundled Node.js client:

```bash
node skills/calibre-ebooks/scripts/books-api-client.mjs docs
node skills/calibre-ebooks/scripts/books-api-client.mjs paths
node skills/calibre-ebooks/scripts/books-api-client.mjs search "termo" --limit 10
node skills/calibre-ebooks/scripts/books-api-client.mjs book 123
node skills/calibre-ebooks/scripts/books-api-client.mjs request GET /books --query q=python
```

See `SKILL.md` for the full workflow. Local Python scripts are fallback helpers
for direct Calibre metadata queries and RAG indexing when the API is unavailable
or does not cover the requested operation.
