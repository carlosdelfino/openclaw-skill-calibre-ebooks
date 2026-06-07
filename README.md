![visitors](https://visitor-badge.laobi.icu/badge?page_id=carlosdelfino.openclaw-skill-calibre-ebooks)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
![Language: Portuguese](https://img.shields.io/badge/Language-Portuguese-brightgreen.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Status](https://img.shields.io/badge/Status-Desenvolvimento-brightgreen)
![Repository Size](https://img.shields.io/github/repo-size/carlosdelfino/openclaw-skill-calibre-ebooks)
![Last Commit](https://img.shields.io/github/last-commit/carlosdelfino/openclaw-skill-calibre-ebooks)

<!-- Animated Header -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:1a56db,100:10b981&height=220&section=header&text=Calibre%20Ebooks&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=OpenClaw%20Skill%20for%20Calibre%20Books%20API&descSize=18&descAlignY=55&descColor=94a3b8" width="100%" alt="Calibre Ebooks Header"/>
</p>

# calibre-ebooks

OpenClaw skill for managing and querying a local Calibre-backed Books API.
This skill only works with books already present in the user's Calibre library;
it does not find, source, or add books from outside the local library. For
titles that are not in the local library, consult public catalog/store pages
such as Google Books or Amazon Books for metadata, editions, publisher
information, and lawful availability.

Primary API documentation:

- Swagger UI: `http://0.0.0.0:6180/docs` (`http://host.docker.internal:6180/`)
- ReDoc: `http://0.0.0.0:6180/redoc` (`http://host.docker.internal:6180/`)
- OpenAPI JSON: `http://0.0.0.0:6180/openapi.json` (`http://host.docker.internal:6180/`)

Use the bundled Python API client:

```bash
python3 skills/calibre-ebooks/scripts/books_api_client.py docs
python3 skills/calibre-ebooks/scripts/books_api_client.py paths
python3 skills/calibre-ebooks/scripts/books_api_client.py search "termo" --limit 10
python3 skills/calibre-ebooks/scripts/books_api_client.py book 123
python3 skills/calibre-ebooks/scripts/books_api_client.py request GET /books --query q=python
```

See `SKILL.md` for the full workflow. Local Python scripts are helpers for
direct Calibre metadata queries and RAG indexing when the API is unavailable or
does not cover the requested local-library operation.

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

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:10b981,50:1a56db,100:0f172a&height=120&section=footer" width="100%" alt="Footer"/>
</p>

---
**Resumo:** OpenClaw skill para gerenciamento de biblioteca Calibre local, usando API local e scripts Python.
**Data de Criação:** 2025-05-30
**Autor:** Rapport GenerAtiva
**Versão:** 0.0.6
**Última Atualização:** 2025-05-30
**Atualizado por:** Carlos Delfino
**Histórico de Alterações:**
- 2025-05-30 - Atualizado por Carlos Delfino - Aplicação das regras de documentação - Versão 0.0.6
- 2025-05-30 - Criado por Rapport GenerAtiva - Versão 0.0.6
