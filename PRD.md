# 📋 OpsMesh — Product Requirements Document (PRD)

> **Documento de Requisitos de Produto**  
> **Versão:** 1.1.0  
> **Data:** 2026-09-09  
> **Autor:** Arquitetura de Produto & SRE / IA  
> **Idioma Padrão:** Português (PT-BR) | Suporte a EN e ES  
> **Classificação:** Open Source Enterprise / Engenharia de Alto Nível  

---

## 1. Sumário Executivo & Visão de Negócio

Em arquiteturas modernas de microsserviços distribuídos e nuvem híbrida, panes e incidentes críticos geram um custo de inatividade (*downtime*) que ultrapassa **$5.600 por minuto** (Gartner). Durante uma crise P0/P1 (queda de banco, estouro de conexões, falha de migração ou degradação em cascata), os engenheiros de plantão (*on-call*) sofrem com:

1. **Fadiga de Alertas & Fragmentação de Contexto:** Necessidade de consultar de 4 a 8 painéis distintos (Datadog, Grafana, CloudWatch, Sentry, Kibana, Kubernetes CLI, repositórios Git).
2. **Tempo Médio de Investigação Elevado (MTTD/MTTR):** Até 70% do tempo de um incidente é gasto na correlação de logs e identificação da causa raiz (*Root Cause Analysis - RCA*), e não na aplicação da correção.
3. **Risco Humano em Ações Sob Pressão:** Execução apressada de scripts manuais ou comandos destrutivos sem validação de impacto.

### 1.1 A Proposta do OpsMesh
O **OpsMesh** é uma plataforma multi-agente autônoma de **Resposta a Incidentes e SRE (Incident Commander)** desenvolvida com **LangGraph**, suporte duplo a ferramentas via **Model Context Protocol (MCP)** e **OpenAI Tools (DeepSeek, GPT, Llama)**, persistência em **PostgreSQL Serverless** e governança estrita com **Human-in-the-Loop (HITL)**.

O sistema recebe alertas de monitoramento, isola anomalias em segundos, consulta a base viva de runbooks da empresa, formula planos de remediação auditáveis com diff de código/configuração e aguarda a aprovação humana com um clique antes de executar mitigações seguras.

Por ser um projeto de **código aberto disponibilizado online na nuvem**, o OpsMesh implementa uma arquitetura de proteção financeira multi-camadas (FinOps Guardrails) para prevenir ataques de *Denial of Wallet (DoW)* e consumo desenfreado de tokens.

---

## 2. Personas do Sistema

| Persona | Papel Primário | Dor Principal | Benefício com OpsMesh |
| :--- | :--- | :--- | :--- |
| **SRE On-Call (Engenheiro de Plantão)** | Primeiro respondente em alertas P0/P1 | Acordado às 3h da manhã com contexto disperso e pressão por tempo | Recebe diagnóstico correlacionado em < 60s com sugestão exata de mitigação |
| **Incident Commander (Staff/Lead SRE)** | Condução da crise e orquestração de times | Dificuldade em manter alinhamento e documentar timeline do incidente | Painel em tempo real da investigação e geração automática do relatório Post-Mortem |
| **Engenheiro de Software / DevOps** | Criação de código e patches de infra | Necessidade de criar scripts manuais de rollback ou migração emergencial | Recebe diffs prontos e scripts idempotentes pré-validados pelos agentes |
| **Visitante / Avaliador Open Source** | Testa a plataforma online na demo pública | Quer testar cenários reais sem precisar configurar chaves ou infraestrutura | Testa cenários no Modo Replay com zero custo ou usa sua própria chave (BYOK) |
| **CTO / Mantenedor do Projeto** | Gestão de riscos, custos e conformidade | Risco de faturas gigantescas de API por bots ou curiosos na internet | Custo ocioso de $0/mês, teto diário intransponível de tokens e proteção anti-bot |

---

## 3. Casos de Uso Principais (Core Use Cases)

### UC-01: Triagem e Diagnóstico Autônomo de Incidente
* **Ator:** Webhook de Alerta (Datadog, Prometheus, Grafana, PagerDuty).
* **Fluxo:**
  1. O alerta é recebido no endpoint `POST /api/v1/incidents/webhook`.
  2. O PII Sanitizer mascara identificadores sensíveis (CPFs, cartões, credenciais, IPs públicos), preservando IPs de redes privadas RFC 1918 para diagnóstico de pods.
  3. O Agente Supervisor avalia a severidade e orquestra a investigação concorrente entre Agentes de Logs e Infraestrutura.
  4. O Agente de Runbooks faz busca híbrida (vetorial + esparsa) para encontrar o procedimento operacional padrão aplicável.
  5. Uma síntese executiva de causa raiz é montada em menos de 60 segundos com consumo estrito de até 12.000 tokens.

### UC-02: Human-in-the-Loop (HITL) para Remediação Crítica
* **Ator:** SRE On-Call via Slack / Webhook / Painel Web.
* **Fluxo:**
  1. O Agente de Remediação gera um plano tipado (`RemediationPlan`).
  2. O LangGraph dispara `interrupt_before=["execute_remediation"]` e salva o checkpoint no PostgreSQL Serverless.
  3. Notificação é enviada ao engenheiro com a explicação da causa raiz, o diff da mudança e botões de `Aprovar` ou `Rejeitar`.
  4. Somente após a assinatura do engenheiro, o endpoint `POST /api/v1/incidents/{incident_id}/resume` é acionado para execução.

### UC-03: Demonstração Pública Segura (Modo Sandbox / BYOK)
* **Ator:** Visitante anônimo ou avaliador na web.
* **Fluxo:**
  1. O visitante acessa a interface web e escolhe um dos 4 cenários de crise do Chaos Studio.
  2. Se a cota pública diária estiver ativa, o sistema pode rodar via **Modo Replay Zero-Token** (usando traces gravados do LogHub, sem chamadas externas pagas).
  3. Se o visitante desejar executar prompts vivos e personalizados, ele pode fornecer sua própria chave via header `X-OpenAI-API-Key` ou `X-DeepSeek-API-Key` (**BYOK**), com custo zero para os mantenedores.

---

## 4. Requisitos Funcionais (FR)

* **FR-01 (Ingestão de Alertas Padronizada):** Endpoint REST `POST /api/v1/incidents/webhook` compatível com payloads JSON de Datadog, Prometheus Alertmanager, Grafana e PagerDuty.
* **FR-02 (Anonimização Mandatória de PII & Preservação de VPC):**
  * Mascaramento determinístico de CPFs, CNPJs, cartões de crédito (Luhn), chaves de API, senhas e endereços IPv4/IPv6 públicos.
  * **Exceção de Infraestrutura:** Preservação estrita de faixas de IP privadas RFC 1918 (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) e hostnames de cluster Kubernetes para viabilizar o diagnóstico de pods.
* **FR-03 (Orquestração Hierárquica LangGraph):** Supervisor tipado com `SupervisorDecision`, com teto máximo de 4 iterações (`max_iterations = 4`) para evitar loops infinitos.
* **FR-04 (Universal Tool Gateway):** Interoperabilidade nativa entre ferramentas no formato **Anthropic MCP** (stdio/SSE) e **OpenAI Tools Function Calling** (compatível com DeepSeek V3/R1, GPT-4o, Groq e Llama).
* **FR-05 (RAG Híbrido sobre Runbooks):** Indexação e busca híbrida de SOPs em Markdown (Dense Qdrant + Sparse BM25 + Reciprocal Rank Fusion + Re-ranking).
* **FR-06 (Portão Transacional HITL):** Interrupção formal (`interrupt_before`) antes de qualquer mutação de infraestrutura, com retomada via `POST /api/v1/incidents/{incident_id}/resume`.
* **FR-07 (Persistência em PostgreSQL Serverless):** Checkpoints gerenciados por `AsyncPostgresSaver` em PostgreSQL Serverless (Neon/Supabase) com auto-pause.
* **FR-08 (Documentação Viva de API com Scalar):** Referência interativa e moderna da API em `/docs` ou `/scalar`.
* **FR-09 (Simulador Chaos Studio com Matriz Técnica):** Suite de 4 cenários baseados em dados reais do LogHub com alertas, logs, causa raiz e remediação pré-definidos.
* **FR-10 (Suporte Multilíngue):** Toda documentação viva, prompts e relatórios estruturados com suporte a Português (padrão), Inglês e Espanhol.
* **FR-11 (Bring Your Own Key - BYOK):** Suporte à injeção de chaves de API do usuário final através dos headers `X-OpenAI-API-Key` e `X-DeepSeek-API-Key`, permitindo execuções sem consumo da cota do servidor.
* **FR-12 (Sandbox Replay Zero-Token):** Capacidade de executar os 4 cenários da demo pública a partir de execuções pré-gravadas em cache, garantindo zero chamadas a APIs pagas para visitantes comuns.
* **FR-13 (Observabilidade de LLMs com LangSmith & Langfuse):** Tracing ponta a ponta dos grafos LangGraph, detalhando latência nó a nó, contagem de tokens de entrada/saída e cálculo de custo financeiro acumulado por incidente com suporte a exportação para LangSmith ou Langfuse.
* **FR-14 (Avaliação Contínua de Assertividade com Ragas):** Pipeline automatizado de testes de regressão no CI/CD com LLM-as-a-Judge medindo *Faithfulness* ($\ge 0.85$), *Answer Relevancy* ($\ge 0.80$) e *Context Precision* dos planos gerados pelos agentes contra o gabarito dos 4 cenários canônicos.

---

## 5. Requisitos Não Funcionais (NFR)

* **NFR-01 (FinOps & Custo Ocioso $0/mês):** Conteinerização stateless no Google Cloud Run e Azure Container Apps com `min_instances = 0` (Scale-to-Zero). Em repouso, custo de computação rigorosamente zero.
* **NFR-02 (Latência & TTFT):** Time-to-First-Token (TTFT) inferior a 800ms em streaming SSE. Diagnóstico preliminar em até 60 segundos.
* **NFR-03 (Resiliência & Cascata de Modelos):** Fallback automático entre provedores de inferência (DeepSeek primário -> OpenAI/Groq secundário) em caso de timeout de 10s ou rate-limit (HTTP 429).
* **NFR-04 (Qualidade de Código & CI):** Hooks de pré-commit (`ruff`, `mypy`, `gitleaks`) e 100% dos testes unitários verdes antes de qualquer merge de PR.
* **NFR-05 (Segurança & RBAC):** Autenticação de webhooks via HMAC SHA-256 e links de aprovação HITL com expiração de 15 minutos.
* **NFR-06 (Auditabilidade & Não-Repúdio):** Cada incidente gera um `PostMortemReport` auditável com hash SHA-256 da timeline e da aprovação humana.
* **NFR-07 (Proteção Anti-Abuso & Disjuntor Diário de Gastos - Daily Circuit Breaker):**
  * **Rate Limiting por IP:** Máximo de 5 requisições por minuto e 2 incidentes completos por dia por IP na cota pública.
  * **Daily Cost Circuit Breaker:** Limite diário rígido configurável (ex.: $1.00/dia ou 150.000 tokens/dia). Ao atingir o teto, o sistema responde automaticamente com `HTTP 429 Too Many Requests`, convidando o usuário a utilizar BYOK ou executar via Docker local.
  * **Agent Token Budget:** Limite estrito de 12.000 tokens por incidente e truncamento de logs a 2.000 caracteres por chamada de ferramenta.

---

## 6. Métricas de Sucesso e KPIs de Negócio

| Métrica | Linha de Base (Operação Manual) | Meta com OpsMesh |
| :--- | :--- | :--- |
| **MTTD (Mean Time to Detect Root Cause)** | 25 a 45 minutos | **< 2 minutos** |
| **MTTR (Mean Time to Resolution)** | 45 a 120 minutos | **< 10 minutos** |
| **Custo de Infraestrutura Ociosa** | $150 - $400 / mês (VMs ligadas) | **$0.00 / mês (Scale-to-Zero)** |
| **Gasto Máximo com Tokens na Demo Pública** | Sem teto (Risco de faturas de milhares de dólares) | **Teto Rígido ($15 a $30/mês ou $0 via Replay)** |
| **Taxa de Precisão no Diagnóstico (Grounding)** | Sujeita a viés humano | **> 92%** de correlação correta |
