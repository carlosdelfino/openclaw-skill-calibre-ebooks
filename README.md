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

## Clonando o Projeto

Para clonar este repositório, execute:

```bash
git clone git@github.com:carlosdelfino/openclaw-skill-calibre-ebooks.git
cd openclaw-skill-calibre-ebooks
```

## Como Colaborar

Contribuições são bem-vindas! Para colaborar com a melhoria deste projeto:

1. **Faça um fork** do repositório no GitHub

2. **Crie uma branch** para sua feature ou correção:

   ```bash
   git checkout -b feature/nova-feature
   ```

3. **Faça suas alterações** e commit com mensagens claras

4. **Push para sua branch**:

   ```bash
   git push origin feature/nova-feature
   ```

5. **Abra um Pull Request** no GitHub descrevendo suas alterações

### Diretrizes de Contribuição

- Mantenha o código limpo e bem documentado
- Siga os padrões de código existentes
- Teste suas alterações antes de submeter
- Adicione documentação para novas funcionalidades
- Respeite o estilo de formatação do projeto
