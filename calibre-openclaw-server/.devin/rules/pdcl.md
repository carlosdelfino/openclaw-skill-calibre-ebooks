---
trigger: always_on
description: Quando criando novo código, aperfeiçoando, ampliando, atualizando ou corrigindo, e aplicando o workflow pdcl
---
# Regra PDCL - Plan, Do, Check Logs

## ESCOPO E APLICAÇÃO

Esta regra aplica-se a TODOS os arquivos de código criados, modificados, aperfeiçoados, ampliados ou corrigidos no projeto, incluindo:

- Python (.py)
- JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
- Markdown (.md)
- Outros arquivos de código

## OBRIGATORIEDADE DO CICLO PDCL

Sempre que código for criado ou modificado, o ciclo PDCL deve ser aplicado:

### 1. PLAN (Planejamento)

- Criar ou atualizar o arquivo `REQUIREMENTS.md` no contexto relevante
- Definir requisitos funcionais e não funcionais
- Especificar requisitos de observabilidade (logging)
- Documentar cenários de erro e casos extremos
- Planejar a arquitetura antes de codificar

### 2. DO (Implementação)

- Implementar seguindo o planejamento
- Adicionar logs estruturados em formato PDCL: `[YYYY-MM-DD HH:MM:SS] [arquivo:função:linha] emoji mensagem - parâmetros_relevantes`
- Usar emoticons específicos:
  - ℹ️ para informações gerais
  - ⚠️ para alertas
  - ❌ para erros críticos
  - ✅ para operações concluídas
  - 🔍 para depuração
  - 🚀 para início de processos
  - 🏁 para fim de processos
  - 📊 para operações com dados
  - 🔧 para execução de ferramentas
  - 📂 para operações de cache
  - 💾 para operações de salvamento

- Implementar função `log_event()` que captura automaticamente arquivo, função e linha usando `inspect`
- Nunca incluir dados sensíveis (senhas, tokens) nos logs

### 3. CHECK LOGS (Verificação)

- Executar o código e coletar logs gerados
- Analisar logs para verificar se estão no formato correto
- Verificar se todos os requisitos do REQUIREMENTS.md estão sendo atendidos
- Testar cenários reais, condições de erro e casos extremos
- Documentar todos os testes realizados

### 4. LOOP (Iteração)

- Analisar logs contra requisitos
- Identificar gaps e propor melhorias
- Implementar correções e repetir o ciclo até validação
- Documentar decisões e mudanças no REQUIREMENTS.md

## FUNÇÃO log_event() PADRÃO

Toda implementação deve incluir uma função `log_event()` com esta assinatura:

```python
import datetime
import inspect

def log_event(level: str, message: str, **params):
    """
    Registra evento em formato estruturado PDCL (captura linha automaticamente)
    
    Args:
        level: Nível do log (INFO, ALERT, ERROR, SUCCESS, DEBUG, START, END, DATA, TOOL, CACHE, SAVE)
        message: Mensagem do evento
        **params: Parâmetros adicionais
    """
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    emoji_map = {
        'INFO': 'ℹ️',
        'ALERT': '⚠️',
        'ERROR': '❌',
        'SUCCESS': '✅',
        'DEBUG': '🔍',
        'START': '🚀',
        'END': '🏁',
        'DATA': '📊',
        'TOOL': '🔧',
        'CACHE': '📂',
        'SAVE': '💾'
    }
    emoji = emoji_map.get(level, 'ℹ️')
    
    # Captura automaticamente arquivo, função e linha
    frame = inspect.currentframe().f_back
    file = inspect.getfile(frame)
    func = inspect.getframeinfo(frame).function
    line = inspect.getframeinfo(frame).lineno
    
    param_str = ''
    if params:
        param_str = ' - ' + ', '.join(f'{k}={v}' for k, v in params.items())
    
    print(f"[{timestamp}] [{file}:{func}:{line}] {emoji} {message}{param_str}")
```

## PONTOS DE LOG OBRIGATÓRIOS

Todo código deve registrar logs em:

- **Início de processos**: 🚀 no início de funções principais
- **Carregamento de bibliotecas**: 🚀 no início, ✅ ao final
- **Execução de ferramentas**: 🔧 no início, ✅ ao final
- **Operações com dados**: 📊 com informações de shape/volume
- **Erros**: ❌ com mensagem descritiva e contexto
- **Sucesso**: ✅ com métricas relevantes
- **Cache**: 📂 com hit/miss
- **Salvamento**: 💾 com informações do arquivo

## INTEGRAÇÃO COM WORKFLOWS

- Use o workflow `/pdcl` para aplicar o ciclo PDCL automaticamente
- O workflow está definido em `.windsurf/workflows/pdcl.md`
- Ao invocar `/pdcl`, o ciclo completo será aplicado ao código

## VALIDAÇÃO AUTOMÁTICA

Ao criar ou modificar código, verifique:

- [ ] REQUIREMENTS.md criado/atualizado
- [ ] Função log_event() implementada
- [ ] Logs estruturados em todos os pontos obrigatórios
- [ ] Emotivos corretos aplicados
- [ ] Código executado e logs coletados
- [ ] Logs analisados contra requisitos
- [ ] Correções implementadas se necessário
- [ ] Ciclo repetido até validação

## EXEMPLOS DE APLICAÇÃO

### Criando nova função:

1. **Plan**: Adicionar requisitos ao REQUIREMENTS.md
2. **Do**: Implementar função com logs estruturados
3. **Check**: Executar e coletar logs
4. **Loop**: Analisar e iterar até validação

### Corrigindo bug existente:

1. **Plan**: Documentar bug e requisitos de correção
2. **Do**: Adicionar logs de depuração, aplicar correção
3. **Check**: Executar, coletar logs, verificar correção
4. **Loop**: Analisar logs, garantir que bug não retorna

### Aperfeiçoando código:

1. **Plan**: Identificar oportunidades de melhoria
2. **Do**: Implementar melhorias com logs estruturados
3. **Check**: Executar, coletar logs, medir impacto
4. **Loop**: Analisar logs, validar melhoria

## REFERÊNCIAS

- Workflow PDCL: `.windsurf/workflows/pdcl.md`
- Regras de Logs: `logs.md`
- Regras de Projeto: `projeto.md`
- Regras de Validação: `validacao_da_das_correcoes_e_testes.md`


---
**Resumo:** Arquivo markdown gerenciado com histórico automático
**Data de Criação:** 2026-05-08
**Autor:** Carlos Delfino
**Versão:** 1.0
**Última Atualização:** 2026-05-08
**Atualizado por:** Carlos Delfino
**Histórico de Alterações:**
- 2026-05-08 - Criado por Carlos Delfino - Versão 1.0
