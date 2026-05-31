![visitors](https://visitor-badge.laobi.icu/badge?page_id=carlosdelfino.openclaw-skill-calibre-ebooks)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
![Language: Portuguese](https://img.shields.io/badge/Language-Portuguese-brightgreen.svg)
![Workflow](https://img.shields.io/badge/Workflow-PDCL-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Status](https://img.shields.io/badge/Status-Development-brightgreen)

<!-- Animated Header -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:1a56db,100:10b981&height=220&section=header&text=PDCL&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=Plan%2C%20Do%2C%20Check%20Logs&descSize=18&descAlignY=55&descColor=94a3b8" width="100%" alt="PDCL Header"/>
</p>

---
description: Aplica metodologia PDCL (Plan, Do, Check Logs) com GenAI para desenvolvimento iterativo
---

# Workflow PDCL - Plan, Do, Check Logs

Este workflow implementa a metodologia PDCL (Plan, Do, Check Logs) com GenAI para desenvolvimento de software iterativo, baseada no artigo publicado em [mcu.tec.br](https://mcu.tec.br/metodologia/pdcl-plan-do-check-logs-com-genai-a-nova-metodologia-de-engenharia-de-software-orientada-por-logs-e-inteligencia-artificial-generativa/)

## Visão Geral

PDCL é uma evolução do PDCA tradicional, adaptada para trabalhar com Inteligência Artificial Generativa. O ciclo contínuo usa logs estruturados como elemento central de validação e comunicação entre o sistema e a IA.

## Uso

Digite `/pdcl` seguido da tarefa ou funcionalidade que deseja desenvolver.

## Exemplos

- `/pdcl criar sistema de monitoramento de temperatura`

- `/pdcl implementar API REST para usuários`

- `/pdcl adicionar autenticação JWT`

- `/pdcl otimizar performance de queries`

## O Ciclo PDCL

### 1. Plan (Planejamento)

- Criar ou atualizar o arquivo `REQUIREMENTS.md` com requisitos funcionais e não funcionais

- Definir comportamento esperado de forma clara, testável e interpretável por IA

- Interagir com a IA para refinar, organizar e complementar os requisitos

- Documentar restrições, limites e cenários de erro

### 2. Do (Implementação)

- Produzir código com base nos requisitos definidos

- Instrumentar o código com logs estruturados desde o início

- Seguir padrão de log: `[YYYY-MM-DD HH:MM:SS] [arquivo:função:linha] emoji mensagem - parâmetros_relevantes`

- Usar emoticons específicos: ℹ️ (info), ⚠️ (alerta), ❌ (erro), ✅ (concluído), 🔍 (debug), 🚀 (início), 🏁 (fim)

### 3. Check Logs (Verificação)

- Executar a aplicação de forma automatizada

- Coletar os logs gerados durante a execução

- Analisar logs com IA para comparar comportamento observado vs requisitos

- Identificar divergências, inconsistências ou falhas

- Verificar cobertura de cenários e tratamento de erros

### 4. Loop Iterativo

- Com base na análise de logs, a IA propõe correções no código

- Ajustar requisitos se necessário

- Melhorar instrumentação de logs

- Reexecutar e repetir o ciclo até validação completa

## Estrutura de Logs

Formato obrigatório para todos os logs:

```text
[YYYY-MM-DD HH:MM:SS] [arquivo:função:linha] emoji mensagem - parâmetros_relevantes
```

Emoticons padrão:

- ℹ️ Informações gerais

- ⚠️ Alertas e avisos

- ❌ Erros críticos

- ✅ Operações concluídas

- 🔍 Depuração

- 🚀 Início de processos

- 🏁 Fim de processos

## Arquivo REQUIREMENTS.md

Estrutura recomendada:

```markdown
# Nome do Sistema/Feature

## Requisitos Funcionais
- O sistema deve [ação específica]
- O sistema deve [condição] quando [evento]

## Requisitos Não Funcionais
- Tempo de resposta deve ser inferior a X
- Log deve conter timestamp, função e descrição clara
- Tratamento de erro deve ser implementado para [cenários]

## Cenários de Erro
- Quando [condição], sistema deve [comportamento]
- Em caso de falha em [componente], sistema deve [ação]
```

## O que acontece durante o workflow

1. **Análise de Requisitos**: A IA analisa a tarefa solicitada e propõe estrutura de requisitos

2. **Criação/Atualização de REQUIREMENTS.md**: Documento de requisitos é criado ou refinado

3. **Geração de Código**: Código é produzido com instrumentação de logs integrada

4. **Execução e Coleta de Logs**: Aplicação é executada e logs são capturados

5. **Análise Comparativa**: IA compara logs com requisitos e identifica gaps

6. **Iteração**: Correções são aplicadas e ciclo se repete até validação

## Dicas

- Nunca produza código sem instrumentação de logs

- Logs devem ser descritivos e conter contexto suficiente para análise

- REQUIREMENTS.md é um documento vivo, refine continuamente

- A qualidade dos logs determina a qualidade do ciclo PDCL

- Teste cenários reais, condições de erro e casos extremos

- Documente todas as decisões e alterações

## Princípios

- **Observabilidade**: Todo comportamento deve ser observável através de logs

- **Iteração Contínua**: O ciclo se repete até validação completa

- **Coautoria Humano-IA**: Requisitos são refinados em conjunto

- **Validação Semântica**: IA verifica comportamento, não apenas sintaxe

- **Controle em Malha Fechada**: Sistema auto-corrige baseado em feedback

## Integração com Memórias do Projeto

Este workflow integra-se automaticamente com as memórias do projeto:

 

- `projeto.md`: Metodologia PDCL já está documentada

 

- `logs.md`: Sistema de logging estruturado já está definido
- `validacao_da_das_correcoes_e_testes.md`: Testes sistemáticos após modificações

## Exemplo Completo

```text
/pdcl criar sistema de autenticação

1. Plan:
   REQUIREMENTS.md criado com:
   - Requisitos funcionais (login, logout, registro)
   - Requisitos não funcionais (tempo de resposta < 200ms)
   - Cenários de erro (senha incorreta, usuário não existe)

2. Do:
   Código gerado com logs:
   [2026-04-24 23:30:15] [auth.py:login:45] 🚀 Início do processo de login - usuario=john@example.com
   [2026-04-24 23:30:15] [auth.py:login:52] ℹ️ Validando credenciais
   [2026-04-24 23:30:15] [auth.py:login:58] ✅ Login realizado com sucesso - usuario=john@example.com

3. Check Logs:
   IA analisa logs vs requisitos
   Identifica: tempo de resposta medido, logs estruturados corretamente

4. Loop:
   IA sugere: adicionar medição de tempo entre validação e resposta
   Código atualizado
   Ciclo se repite
```

## Referências

- Artigo completo: [mcu.tec.br](https://mcu.tec.br/metodologia/pdcl-plan-do-check-logs-com-genai-a-nova-metodologia-de-engenharia-de-software-orientada-por-logs-e-inteligencia-artificial-generativa/)

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:10b981,50:1a56db,100:0f172a&height=120&section=footer" width="100%" alt="Footer"/>
</p>

---
**Resumo:** Workflow PDCL (Plan, Do, Check Logs) com GenAI para desenvolvimento iterativo de software usando logs estruturados como elemento central de validação.
**Data de Criação:** 2026-05-08
**Autor:** Carlos Delfino
**Versão:** 1.0
**Última Atualização:** 2026-05-22
**Atualizado por:** Carlos Delfino
**Histórico de Alterações:**
- 2026-05-22 - Atualizado por Carlos Delfino - Adição de badges, header e footer animados seguindo novas regras de documentação - Versão 1.1
- 2026-05-08 - Criado por Carlos Delfino - Versão 1.0
