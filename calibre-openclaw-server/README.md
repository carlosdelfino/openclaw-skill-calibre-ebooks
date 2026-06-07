![visitors](https://visitor-badge.laobi.icu/badge?page_id=carlosdelfino.openclaw-skill-calibre-ebooks)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
![Language: English](https://img.shields.io/badge/Language-English-brightgreen.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Node.js](https://img.shields.io/badge/Node.js-20%2B-green)
![Status](https://img.shields.io/badge/Status-Development-brightgreen)
![Repository Size](https://img.shields.io/github/repo-size/carlosdelfino/openclaw-skill-calibre-ebooks)
![Last Commit](https://img.shields.io/github/last-commit/carlosdelfino/openclaw-skill-calibre-ebooks)

<!-- Animated Header -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:1a56db,100:10b981&height=220&section=header&text=Calibre%20Ebooks&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=OpenClaw%20Skill%20for%20Calibre%20Books%20API&descSize=18&descAlignY=55&descColor=94a3b8" width="100%" alt="Calibre Ebooks Header"/>
</p>

# calibre-ebooks

OpenClaw skill for managing and querying the local Calibre-backed Books API.
This server works with books already present in the configured Calibre library;
it does not provide unauthorized book sources. For titles that are not in the
local library, consult public catalog/store pages such as Google Books or Amazon
Books for metadata, editions, publisher information, and lawful availability.

Semantic RAG search returns citeable results. Indexed PDF chunks preserve the
page number and, when detectable, the chapter or section heading. The content
search response includes `page_start`, `page_end`, `section_title`, `citation`,
`similarity`, and the matched excerpt so agents can enrich answers with precise
book locations instead of uncited summaries.

Primary API documentation:

- Swagger UI: `http://0.0.0.0:6180/docs`
- ReDoc: `http://0.0.0.0:6180/redoc`
- OpenAPI JSON: `http://0.0.0.0:6180/openapi.json`

Use the bundled Node.js client:

```bash
node skills/calibre-ebooks/calibre-openclaw-server/scripts/books-api-client.mjs docs
node skills/calibre-ebooks/calibre-openclaw-server/scripts/books-api-client.mjs paths
node skills/calibre-ebooks/calibre-openclaw-server/scripts/books-api-client.mjs search "term" --limit 10
node skills/calibre-ebooks/calibre-openclaw-server/scripts/books-api-client.mjs book 123
node skills/calibre-ebooks/calibre-openclaw-server/scripts/books-api-client.mjs request GET /books --query q=python
```

See `SKILL.md` for the full workflow. Local Python scripts are fallback helpers
for direct Calibre metadata queries and RAG indexing when the API is unavailable
or does not cover the requested local-library operation.

## Cloning the Project

To clone this repository, run:

```bash
git clone git@github.com:carlosdelfino/openclaw-skill-calibre-ebooks.git
cd openclaw-skill-calibre-ebooks
```

## How to Contribute

Contributions are welcome! To help improve this project:

1. **Fork** the repository on GitHub

2. **Create a branch** for your feature or fix:

   ```bash
   git checkout -b feature/new-feature
   ```

3. **Make your changes** and commit with clear messages

4. **Push to your branch**:

   ```bash
   git push origin feature/new-feature
   ```

5. **Open a Pull Request** on GitHub describing your changes

### Contribution Guidelines

- Keep the code clean and well documented
- Follow the existing code standards
- Test your changes before submitting
- Add documentation for new features
- Respect the project formatting style

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:10b981,50:1a56db,100:0f172a&height=120&section=footer" width="100%" alt="Footer"/>
</p>

---
**Summary:** OpenClaw skill for managing a local Calibre library, including a Node.js client and auxiliary Python scripts.
**Creation Date:** 2025-05-30
**Author:** Rapport GenerAtiva
**Version:** 0.0.10
**Last Update:** 2025-05-31
**Updated by:** Carlos Delfino
**Changelog:**
- 2025-05-31 - Created by Rapport GenerAtiva - Version 0.0.10
- 2025-05-30 - Updated by Carlos Delfino - Applied documentation rules - Version 0.0.6
- 2025-05-30 - Created by Rapport GenerAtiva - Version 0.0.6
