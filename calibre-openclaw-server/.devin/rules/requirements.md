---
trigger: always_on
---

![visitors](https://visitor-badge.laobi.icu/badge?page_id=RapportTecnologia.GitAnalytics)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
![Language: Portuguese](https://img.shields.io/badge/Language-Portuguese-brightgreen.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Prática-green)
![Status](https://img.shields.io/badge/Status-Educa%C3%A7%C3%A3o-brightgreen)
![Repository Size](https://img.shields.io/github/repo-size/RapportTecnologia/GitAnalytics)
![Last Commit](https://img.shields.io/github/last-commit/RapportTecnologia/GitAnalytics)

<!-- Animated Header -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:1a56db,100:10b981&height=220&section=header&text=GitAnalytics&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=Pol%C3%ADtica%20de%20Engenharia%20de%20Requisitos&descSize=18&descAlignY=55&descColor=94a3b8" width="100%" alt="GitAnalytics Header"/>
</p>

## Regra de Requirements da Aplicação

Esta regra define como o projeto deve tratar requisitos funcionais, não funcionais, arquiteturais, operacionais e de análise. O objetivo é impedir requisitos vagos, contraditórios, não testáveis ou desconectados da arquitetura real do sistema.

## Objetivo

- **Manter uma fonte de verdade única:** `REQUIREMENTS.md` deve refletir o estado real e desejado do produto.
- **Garantir clareza de implementação:** cada funcionalidade relevante deve ter escopo, restrições, critérios de aceite e impactos arquiteturais explícitos.
- **Apoiar decisões de engenharia:** requisitos devem orientar frontend, backend, worker, banco, segurança, integrações, observabilidade e deploy.
- **Reduzir retrabalho e ambiguidade:** toda mudança relevante precisa deixar claro o que mudou, por que mudou e como será validado.
- **Preservar coerência documental:** `README.md`, rules e demais documentos operacionais devem permanecer alinhados com os requisitos vigentes.

## Decisão Padrão Quando Houver Dúvida

- **Documentar antes de escalar complexidade:** se a mudança altera escopo, arquitetura, fluxo, segurança, integração ou operação, ela deve aparecer em `REQUIREMENTS.md`.
- **Preferir requisitos verificáveis:** requisitos devem ser redigidos de forma mensurável, observável e testável.
- **Preferir arquitetura explícita:** quando uma decisão afeta responsabilidades entre camadas, a divisão deve ser registrada.
- **Evitar conhecimento implícito:** nada crítico deve depender apenas de memória, conversa ou convenção oral.
- **Sincronizar resumo executivo:** se o entendimento do produto mudou, `README.md` deve ser atualizado para refletir a visão atual.

## Princípios Obrigatórios de Engenharia de Requisitos

- **Clareza:** cada requisito deve ser compreensível sem interpretação livre excessiva.
- **Consistência:** requisitos não podem contradizer regras existentes, arquitetura definida ou restrições de segurança.
- **Rastreabilidade:** requisito deve se conectar a fluxo, componente, critério de sucesso, teste, log ou regra operacional.
- **Atomicidade:** requisitos amplos devem ser quebrados em itens menores quando possível.
- **Testabilidade:** todo requisito relevante deve permitir validação objetiva.
- **Viabilidade técnica:** requisitos devem considerar limites de stack, custo, segurança, latência, dados e operação.
- **Evolução controlada:** mudanças incrementais devem atualizar a documentação sem apagar o racional já consolidado.

## Quando Atualizar o `REQUIREMENTS.md`

Atualize obrigatoriamente o arquivo quando houver qualquer uma das situações abaixo:

- **Nova funcionalidade:** criação de fluxo, tela, rota, integração, automação, worker ou capacidade de análise.
- **Mudança de escopo:** algo entra ou sai do MVP, muda de prioridade ou passa a ter novo comportamento.
- **Mudança arquitetural:** alteração de responsabilidades entre frontend, backend, Actions, banco, cache, filas ou integrações.
- **Mudança operacional:** alteração em deploy, observabilidade, segurança, versionamento mínimo, ambiente ou política de execução.
- **Mudança de dados:** inclusão, remoção ou alteração de entidades, relações, retenção, RLS ou estratégia de persistência.
- **Mudança de integração:** novos provedores, novos webhooks, novos contratos de API ou mudança relevante em autenticação externa.
- **Mudança de critérios de aceite:** quando a forma de validar entrega muda de maneira relevante.

## Estrutura Obrigatória do `REQUIREMENTS.md`

O documento deve permanecer organizado como especificação viva do produto. Sempre que aplicável, manter ou atualizar explicitamente as seguintes áreas:

- **Visão geral do projeto:** problema, público, objetivo do MVP e proposta de valor.
- **Stack tecnológica definida:** tecnologias aprovadas, limites de versão e dependências críticas.
- **Arquitetura do projeto:** responsabilidades por camada, fluxos entre serviços, invariantes e princípios estruturais.
- **Escopo do produto:** funcionalidades principais e itens fora do escopo.
- **Fluxos do usuário:** entradas, passos principais, saídas e resultados esperados.
- **Autenticação e permissões:** papéis, acesso por recurso, backend obrigatório e regras de segurança aplicáveis.
- **Banco de dados e modelagem:** entidades, relações, retenção, sincronização e regras de integridade.
- **Integrações externas:** provedores, contratos, limites operacionais e responsabilidades.
- **Requisitos não funcionais:** performance, observabilidade, privacidade, idempotência, concorrência, disponibilidade e resiliência.
- **Ambiente e deploy:** ambientes, política de publicação, variáveis por camada e restrições operacionais.
- **Critérios de sucesso e aceite:** indicadores de valor e validações objetivas para entrega.
- **Estado atual e dúvidas em aberto:** situação presente do MVP e pendências conhecidas.

## Requisitos Obrigatórios por Perspectiva

### Produto e Negócio

- **Problema claramente definido:** o documento deve explicar qual dor real está sendo resolvida.
- **Público-alvo explícito:** deixar claro para quem cada fluxo existe.
- **Escopo do MVP delimitado:** o que entra e o que não entra deve estar visível.
- **Valor por funcionalidade:** toda funcionalidade importante deve justificar sua existência.

### Engenharia e Arquitetura

- **Responsabilidades por camada:** frontend, backend, workers e bancos devem ter limites claros.
- **Fonte de verdade por domínio:** definir onde cada dado e decisão de negócio são authoritative.
- **Invariantes operacionais:** registrar regras que não podem ser violadas, como processamento sequencial, persistência mínima e idempotência.
- **Impacto de mudança:** quando um requisito central mudar, os consumidores afetados devem ser considerados na documentação.

### Dados e Análise

- **Modelagem suficiente:** descrever entidades principais, relações e regras de retenção.
- **Dados derivados versus dados fonte:** distinguir o que pode ser persistido do que deve ser efêmero.
- **Critérios para análise e IA:** definir quais dados podem ser enviados, com quais limites e com qual objetivo.
- **Métricas e sinais esperados:** sempre que possível, explicitar quais saídas analíticas o sistema deve produzir.

### Segurança e Operação

- **Compatibilidade com rules de segurança:** requisitos não podem contrariar `.windsurf/rules/segurança.md`.
- **Observabilidade obrigatória:** requisitos críticos devem mencionar logs, rastreabilidade e tratamento de falhas quando aplicável.
- **Restrições operacionais explícitas:** deploy, ambientes, fila, concorrência, segredos e versionamento devem ser documentados.
- **Validação de risco:** integrações, automações e mudanças de arquitetura devem considerar risco operacional e superfície de ataque.

## Regras de Redação de Requisitos

- **Usar linguagem precisa:** evitar termos vagos como “rápido”, “seguro”, “inteligente” ou “simples” sem critério complementar.
- **Declarar intenção e restrição:** não descrever apenas a solução; registrar também o limite, a motivação e o comportamento esperado.
- **Evitar duplicação conflituosa:** a mesma decisão não deve aparecer com versões diferentes em seções diferentes.
- **Preferir listas objetivas:** requisitos devem ser fáceis de revisar e comparar.
- **Explicitar exceções:** se algo foge ao padrão, isso deve ser documentado.

## Sincronização Obrigatória com `README.md`

Sempre que `REQUIREMENTS.md` for alterado de forma relevante, `README.md` deve ser revisado para garantir alinhamento em pelo menos estes pontos:

- **Resumo do produto:** proposta de valor atual.
- **Stack principal:** tecnologias centrais realmente adotadas.
- **Arquitetura resumida:** visão de alto nível coerente com os requisitos.
- **Princípios do projeto:** decisões estruturais e operacionais centrais.
- **Postura de segurança:** resumo executivo compatível com a política operacional vigente.
- **Estado atual:** retrato fiel do momento do projeto.

## Anti-padrões Explicitamente Proibidos

- **Implementar sem atualizar requisitos:** quando a mudança altera comportamento relevante do sistema.
- **Requisito genérico demais:** itens que não permitem saber quando estão corretos ou concluídos.
- **Requisito contraditório:** documentos divergentes entre `REQUIREMENTS.md`, `README.md`, rules ou arquitetura real.
- **Arquitetura implícita:** deixar decisões críticas apenas no código sem documentação mínima.
- **Misturar desejo com estado atual:** confundir roadmap, MVP entregue e hipótese futura sem marcar a diferença.
- **Omitir restrições importantes:** especialmente em segurança, dados, observabilidade, custo, concorrência e deploy.

## Checklist Obrigatório Antes de Considerar os Requirements Atualizados

- **Escopo:** a mudança de produto está refletida?
- **Arquitetura:** responsabilidades e impactos entre camadas estão claros?
- **Dados:** entidades, retenção e integrações afetadas foram consideradas?
- **Segurança:** a mudança continua compatível com a regra de segurança?
- **Operação:** ambientes, deploy, fila, concorrência, logs e versionamento foram avaliados?
- **Aceite:** existe forma objetiva de validar o requisito?
- **README:** o resumo executivo também foi sincronizado quando necessário?
- **Consistência:** o documento permanece sem contradições internas?

## Definição de Pronto para Requisitos

Um requisito ou atualização documental só pode ser considerado pronto quando cumprir simultaneamente:

- **Clareza suficiente para implementação:** o time consegue construir sem depender de adivinhação.
- **Clareza suficiente para revisão:** o time consegue validar se a solução atende ao objetivo.
- **Coerência arquitetural:** a decisão respeita a divisão de responsabilidades do sistema.
- **Compatibilidade com segurança e operação:** não há conflito com políticas obrigatórias do projeto.
- **Sincronização documental:** `REQUIREMENTS.md` e `README.md` refletem a mesma realidade em níveis diferentes de detalhe.

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:10b981,50:1a56db,100:0f172a&height=120&section=footer" width="100%" alt="Footer"/>
</p>

---
**Resumo:** Política de engenharia de requisitos do GitAnalytics com regras claras para documentação, arquitetura, análise, rastreabilidade e sincronização entre REQUIREMENTS e README.
**Data de Criação:** 2026-05-19
**Autor:** Rapport GenerAtiva
**Versão:** 1.0
**Última Atualização:** 2026-05-19
**Atualizado por:** Carlos Delfino
**Histórico de Alterações:**

- 2026-05-08 - Atualizado por Carlos Delfino - Removendo arquivos do Agentic....
- 2026-05-19 - Criado por Rapport GenerAtiva - Versão 1.0
- 2026-05-19 - Atualizado por Rapport GenerAtiva - Expansão da regra de requirements com foco em engenharia de software, arquitetura, análise e coerência documental - Versão 1.0