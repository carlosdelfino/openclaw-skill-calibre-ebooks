---
trigger: always_on
---
## Regra de Segurança da Aplicação

Esta regra define o comportamento obrigatório de segurança para qualquer funcionalidade, correção, integração, automação, workflow ou deploy do projeto. O objetivo é eliminar ambiguidade: quando houver dúvida, esta regra deve ser seguida de forma literal.

## Objetivo

- **Reduzir a superfície de ataque:** limitar ao mínimo necessário os dados, acessos, integrações e operações expostas.
- **Proteger dados sensíveis:** impedir vazamento de tokens, segredos, sessões, dados privados de usuários e resultados internos.
- **Garantir autorização correta:** assegurar que cada usuário, serviço ou workflow acesse apenas o que lhe pertence.
- **Preservar o princípio do produto:** não armazenar permanentemente código-fonte clonado dos repositórios analisados.
- **Manter segurança operacional contínua:** aplicar prevenção, detecção, rastreabilidade e validação antes de publicar qualquer mudança.

## Decisão Padrão Quando Houver Dúvida

- **Negar por padrão:** se não estiver explicitamente permitido, o acesso ou operação deve ser negado.
- **Executar no backend:** toda decisão de autorização, cobrança, ingestão, sincronização ou acesso a segredo deve ocorrer no backend.
- **Minimizar dados:** se um dado não for estritamente necessário, ele não deve ser coletado, enviado, persistido nem exibido.
- **Tratar entrada externa como não confiável:** entradas do usuário, payloads de webhook, conteúdo do GitHub, respostas de IA e dados de terceiros devem ser validados e saneados.
- **Preferir exposição pública zero:** toda rota, tabela, bucket, webhook, fila ou artefato deve nascer privado e só ser aberto com justificativa explícita.

## Princípios Obrigatórios

- **Princípio do menor privilégio:** usuários, tokens, chaves, workflows, serviços e tabelas devem ter apenas as permissões mínimas necessárias.
- **Separação de responsabilidades:** frontend nunca decide autorização final; backend nunca delega segredos ao cliente; worker nunca redefine regras de negócio do backend.
- **Defesa em profundidade:** autenticação, autorização, validação, sanitização, logs, rate limiting e isolamento devem coexistir.
- **Segurança por padrão:** configurações inseguras temporárias não podem ser aceitas como solução permanente.
- **Falha segura:** em caso de erro, timeout, resposta inválida ou dúvida de integridade, o sistema deve bloquear, reverter ou encerrar sem expor dados.
- **Segurança observável:** toda operação sensível deve deixar trilha auditável em logs sanitizados.

## Requisitos Obrigatórios por Camada

### Frontend

- **Sem segredos no cliente:** apenas variáveis `NEXT_PUBLIC_*` realmente públicas podem chegar ao frontend. É proibido expor `service_role`, tokens GitHub, chaves secretas do Stripe, OpenRouter, Neo4j ou segredos de webhook.
- **Sem confiança no cliente:** validações no frontend servem apenas para UX. Toda validação crítica deve ser repetida no backend.
- **Proteção contra XSS:** é proibido renderizar HTML arbitrário sem sanitização rigorosa. Conteúdo vindo de IA, GitHub, Markdown, README, bios ou campos editáveis deve ser tratado como não confiável.
- **Proteção contra CSRF e abuso de sessão:** quando houver autenticação baseada em cookie, usar cookies `HttpOnly`, `Secure` e `SameSite` apropriados, além de checagens anti-CSRF para operações mutáveis.
- **Proteção de navegação:** links externos devem usar proteção adequada contra tabnabbing quando aplicável, e URLs montadas dinamicamente devem ser validadas.
- **Proteção de cache:** páginas privadas, respostas autenticadas e dados sensíveis não devem ser indevidamente cacheados em browser, CDN ou renderização compartilhada.
- **Autorização visual não é segurança:** esconder botão, rota ou componente não substitui validação de permissão no backend.

### Backend e API

- **Autenticação obrigatória em rotas privadas:** toda rota privada deve validar identidade antes de qualquer acesso a recurso.
- **Autorização por recurso:** toda leitura ou escrita deve verificar se o usuário atual pode acessar especificamente aquele registro, análise, fila, configuração, cobrança ou artefato.
- **Validação de payload:** toda entrada deve ser validada com schema explícito e limites de tamanho, formato, enumeração e obrigatoriedade.
- **Rate limiting obrigatório:** aplicar limitação de taxa em login, sincronização, geração de relatórios, filas, webhooks, endpoints administrativos e rotas sujeitas a abuso.
- **Idempotência obrigatória:** endpoints de ingestão, webhook, cobrança e reprocessamento devem tolerar repetição sem duplicar efeitos.
- **Mensagens de erro seguras:** respostas ao cliente não devem expor stack trace, segredo, query interna, cabeçalhos sensíveis ou detalhes exploráveis do ambiente.
- **Timeouts e retries controlados:** integrações externas devem ter timeout, retries limitados e tratamento de falha sem loop infinito.
- **Allowlist de integrações:** o backend só deve se comunicar com domínios e provedores explicitamente aprovados pelo projeto.

### Autenticação, Sessão e Identidade

- **GitHub OAuth com escopo mínimo:** solicitar apenas permissões estritamente necessárias para o caso de uso.
- **Tokens apenas no servidor:** tokens de acesso, refresh tokens e segredos de integração devem ser manipulados exclusivamente no backend ou em serviços seguros.
- **Vínculo forte de identidade:** toda operação autenticada deve estar associada ao usuário interno correto e, quando aplicável, ao `github_user_id` correspondente.
- **Sessão segura:** expiração, renovação, revogação e invalidação de sessão devem ser tratadas explicitamente.
- **Proteção contra elevação de privilégio:** papel de admin, premium ou operacional nunca pode ser assumido por input do cliente.

### Banco de Dados, RLS e Persistência

- **RLS obrigatória:** tabelas privadas no Supabase/PostgreSQL devem ter Row Level Security habilitada com políticas mínimas e revisáveis.
- **Service role isolado:** chave com privilégios elevados nunca pode chegar ao frontend ou ser usada em fluxo que possa ser acionado diretamente pelo usuário.
- **Queries seguras:** usar consultas parametrizadas; é proibido concatenar SQL, Cypher ou filtros críticos com entrada não validada.
- **Isolamento por tenant/usuário:** análises, preferências, relatórios, fila e recursos sociais privados devem ser sempre filtrados pelo dono correto.
- **Retenção mínima:** persistir apenas metadados, métricas, relações, relatórios e dados derivados necessários ao produto.
- **Código-fonte não persistente:** é proibido armazenar permanentemente o código clonado do repositório em banco, bucket, cache durável ou artefato operacional.

### GitHub Actions e Worker de Análise

- **Execução efêmera:** diretórios temporários, clones e artefatos transitórios devem ser removidos ao fim de cada execução.
- **Instância única controlada:** a política de concorrência deve impedir sobreposição de workers da mesma fila/ambiente.
- **Permissões mínimas do workflow:** `GITHUB_TOKEN`, secrets e permissões do job devem ser reduzidos ao mínimo.
- **Sem vazamento em logs:** é proibido imprimir segredos, tokens, payloads confidenciais ou conteúdo sensível integral nos logs do workflow.
- **Sem artefato com código-fonte:** artefatos persistidos não podem conter o repositório clonado nem arquivos sensíveis derivados do clone.
- **Entrada remota é não confiável:** dados do repositório analisado, workflows do repositório-alvo e arquivos do projeto analisado não podem ser tratados como instrução confiável.

### IA Generativa e OpenRouter

- **Envio mínimo ao modelo:** enviar para a IA apenas métricas, resumos, sinais estruturados e contexto estritamente necessário.
- **Sem segredos no prompt:** é proibido enviar tokens, chaves, cookies, segredos de infraestrutura, dados de faturamento sensíveis ou conteúdo privado desnecessário.
- **Proteção contra prompt injection:** README, código, issue, commit, comentário, descrição de PR e saída textual do repositório devem ser tratados como conteúdo não confiável e nunca como instrução soberana do sistema.
- **Validação de saída:** a resposta do modelo deve ser tratada como dado externo, sujeita a validação, saneamento e checagem antes de persistir ou exibir.
- **Sem decisão de autorização pela IA:** o modelo nunca pode decidir acesso, permissão, cobrança, estado de assinatura ou operação administrativa.

### Stripe, Webhooks e Cobrança

- **Verificação criptográfica obrigatória:** todo webhook deve ter assinatura validada antes do processamento.
- **Idempotência financeira:** eventos duplicados não podem gerar cobrança dupla, ativação dupla ou alteração indevida de plano.
- **Fonte de verdade no backend:** status de assinatura, plano e permissão de recursos pagos devem ser decididos apenas pelo backend com base em dados verificados.
- **Separação de chaves:** chave pública no frontend; chaves secretas apenas no backend.

### Neo4j, Grafos e Consultas Hierárquicas

- **Consultas parametrizadas:** toda query Cypher deve ser parametrizada.
- **Escopo de acesso definido:** subgrafos privados ou enriquecidos com dados do usuário não podem ser expostos sem verificação de autorização.
- **Minimização de contexto:** ao extrair subgrafos para IA ou frontend, retornar apenas o recorte necessário.

### Infraestrutura, Deploy e Configuração

- **Segregação por ambiente:** desenvolvimento, homologação e produção devem usar variáveis, segredos e serviços separados.
- **Versões corrigidas obrigatórias:** dependências com advisory crítico conhecido devem ser atualizadas antes do deploy. Para apps Next.js publicados na Vercel, a linha mínima segura definida pelo projeto é `16.0.10`.
- **Headers de segurança:** configurar ao menos `Content-Security-Policy`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` e `Strict-Transport-Security` quando aplicável ao ambiente publicado.
- **Segredos fora do repositório:** segredos nunca devem ser hardcoded nem versionados em `.env` real, código-fonte, workflow ou documentação pública.
- **Privilégios administrativos restritos:** acesso administrativo operacional deve ser nominal, auditável e revisável.

## Requisitos de Logs, Auditoria e Observabilidade

- **Logs estruturados obrigatórios:** seguir o padrão do projeto com timestamp, arquivo, função, linha, emoji e parâmetros relevantes.
- **Sanitização obrigatória:** logs nunca podem conter senha, token, cookie, segredo, header sensível, conteúdo privado desnecessário ou payload bruto integral.
- **Rastreabilidade:** operações de autenticação, autorização negada, webhook, fila, integração externa, erro crítico e ação administrativa devem ser rastreáveis.
- **Correlação:** sempre que possível, incluir identificador de requisição, análise, usuário interno ou job, sem expor dado sensível.
- **Retenção responsável:** armazenar logs com rotação e acesso restrito.

## Itens Explicitamente Proibidos

- **Hardcode de segredo:** nunca inserir token, senha, chave privada, segredo de webhook ou credencial no código.
- **Autorização apenas no frontend:** nunca confiar em estado visual, role vindo do cliente ou parâmetro manipulável para conceder acesso.
- **Exposição indevida de erro:** nunca retornar stack trace detalhado ou segredo ao cliente.
- **Persistência de código analisado:** nunca manter permanentemente o clone do repositório como dado do produto.
- **Execução cega de conteúdo externo:** nunca tratar resposta de IA, conteúdo de repositório, webhook ou metadata externa como comando confiável.
- **Uso de dependência vulnerável conhecida em produção:** nunca publicar versão com correção disponível e risco crítico já identificado para o stack usado.

## Checklist Obrigatório Antes de Aprovar Mudança

- **Acesso:** a funcionalidade exige autenticação? Se sim, ela valida identidade no backend?
- **Permissão:** cada leitura e escrita verifica dono, papel e recurso?
- **Validação:** todo input externo tem schema, limites e sanitização?
- **Segredos:** algum segredo ou token pode vazar para frontend, logs, artefatos ou repositório?
- **Dados:** o fluxo coleta ou persiste mais dados do que o necessário?
- **RLS:** tabelas privadas afetadas estão protegidas por política?
- **Integrações:** webhook, fila, IA, GitHub e Stripe validam autenticidade, idempotência e timeout?
- **Logs:** o fluxo produz logs úteis sem dados sensíveis?
- **Deploy:** dependências e configuração do ambiente estão em versão segura e segregada?

## Definição de Pronto em Segurança

Uma mudança só pode ser considerada pronta quando cumprir simultaneamente os pontos abaixo:

- **Implementação segura:** controles obrigatórios aplicados na camada correta.
- **Validação negativa:** acessos indevidos, inputs inválidos e repetição de eventos foram testados.
- **Observabilidade adequada:** logs e trilhas de auditoria estão presentes e saneados.
- **Conformidade documental:** `REQUIREMENTS.md` e `README.md` seguem coerentes com a postura de segurança adotada.
- **Ausência de dúvida operacional:** qualquer desenvolvedor consegue ler esta regra e decidir o que é permitido, obrigatório ou proibido.
