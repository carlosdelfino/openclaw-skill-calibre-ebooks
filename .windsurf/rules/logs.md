---
trigger: always_on
---
Implemente sistema de logging estruturado em todo código produzido. Use emoticons específicos para cada tipo: ℹ️ para informações gerais, ⚠️ para alertas, ❌ para erros críticos, ✅ para operações concluídas, 🔍 para depuração, 🚀 para início de processos e 🏁 para fim. Cada linha deve seguir formato padrão: [YYYY-MM-DD HH:MM:SS] [arquivo:função:linha] emoji mensagem - parâmetros_relevantes. Nunca inclua dados sensíveis como senhas ou tokens. Para desktop, adicione flag --logs para controle de exibição. Para firmware, use porta serial em modo debug com script Python para captura e armazenamento. Armazene todos os logs na pasta logs/ com rotação automática diária ou ao atingir 10MB. Configure níveis de log através de variáveis de ambiente ou arquivo config.json.


---
**Resumo:** Arquivo markdown gerenciado com histórico automático
**Data de Criação:** 2026-05-08
**Autor:** Carlos Delfino
**Versão:** 1.0
**Última Atualização:** 2026-05-08
**Atualizado por:** Carlos Delfino
**Histórico de Alterações:**
- 2026-05-08 - Criado por Carlos Delfino - Versão 1.0
