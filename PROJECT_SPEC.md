# 🚨 OpsMesh — Autonomous Incident Commander Multi-Agent (LangGraph + MCP/OpenAI + HITL)

> **Status:** Arquitetura e Especificação Técnica Consolidada (v1.1.0)  
> **Nível de Posicionamento:** Senior / Lead AI Agent Engineer  
> **Target:** Startups Globais de IA, Scale-ups de Produto, Times de SRE & Plataforma  
> **Licença:** Código Aberto (Open Source) com Proteção FinOps Anti-Abuso  
> **Idiomas:** Português (Padrão), Inglês e Espanhol  

---

## 📌 1. Visão Geral e Problema de Negócio

Quando um sistema corporativo de missão crítica sofre uma pane (quedas de microsserviços, estouro de conexões de banco de dados, falhas de migração ou degradação severa de latência), o tempo médio de resolução (MTTR) custa milhares de dólares por minuto. Engenheiros perdem tempo precioso navegando manualmente entre múltiplos painéis isolados.

O **OpsMesh** é um **Sistema Multi-Agente Autônomo de Investigação e Mitigação de Incidentes**. Utilizando uma topologia hierárquica no **LangGraph**, suporte universal a ferramentas via **Model Context Protocol (MCP)** e **OpenAI Tools (compatível com DeepSeek, GPT e Llama)**, persistência em **PostgreSQL Serverless** e **Human-in-the-Loop (HITL)** obrigatório, ele diagnostica a causa raiz, correlaciona logs e propõe ações de remediação seguras sem nunca executar alterações críticas sem autorização humana expressa.

Por ser um projeto open source destinado a implantação pública (Google Cloud Run / Azure Container Apps), o OpsMesh inclui uma arquitetura robusta de **proteção contra Denial of Wallet (DoW)**, garantindo que o custo de computação em repouso seja **$0/mês** e que o consumo de tokens de API possua um teto diário intransponível.

---

## 🏛️ 2. Arquitetura Multi-Agente e Fluxo Operacional

```mermaid
graph TD
    Alert[Webhook: POST /api/v1/incidents/webhook] --> PII[PII Sanitizer Middleware\nMascara PII Pública, Preserva RFC 1918]
    PII --> GuardrailCheck{Token Budget & Circuit Breaker?}
    
    GuardrailCheck -->|Cota Excedida| 429[HTTP 429: Cota Diária Atingida\nConvite para BYOK ou Docker Local]
    GuardrailCheck -->|Autorizado / BYOK| Supervisor[Supervisor: Incident Commander\nLangGraph with_structured_output]
    
    subgraph ToolGateway [Universal Tool Gateway: MCP + OpenAI Tools]
        Adapter[Protocol Adapter & Dispatcher]
        MCP_Server[Servidores MCP: Anthropic stdio/SSE]
        OpenAI_Tools[OpenAI Function Calling: DeepSeek / GPT]
        Adapter <--> MCP_Server
        Adapter <--> OpenAI_Tools
    end
    
    subgraph AgentMesh [Equipe de Agentes Especialistas - LangGraph]
        Supervisor -->|Delegar Diagnóstico de Logs| LogAgent[Log & Trace Analyst Agent]
        Supervisor -->|Delegar Análise de Infra| InfraAgent[Database & Infra Agent]
        Supervisor -->|Consultar Manuais de Crise| RAGAgent[Runbook Knowledge Agent\nRAG Híbrido: Qdrant + BM25]
        
        LogAgent <--> ToolGateway
        InfraAgent <--> ToolGateway
        
        LogAgent --> Synthesis[Nó de Síntese de Evidências]
        InfraAgent --> Synthesis
        RAGAgent --> Synthesis
    end
    
    Synthesis --> RemediationPlan[Agente de Remediação:\nGeração do Plano de Mitigação & Diff]
    
    RemediationPlan --> HITL_Gate{HITL Gate: Ação Crítica?}
    HITL_Gate -->|interrupt_before| PausedState[(LangGraph Checkpointer:\nPostgreSQL Serverless)]
    
    PausedState --> SRE_Notification([Engenheiro Humano de Plantão\nNotificação com Diff e Ações])
    
    SRE_Notification -->|Aprovar Rollback / Patch| ResumeEndpoint[POST /api/v1/incidents/{incident_id}/resume]
    ResumeEndpoint --> Execution[Execução Segura da Ação Remediadora]
    Execution --> PostMortem[AuditPostMortemAgent: Relatório Estruturado & PDF]
```

---

## ⚡ 3. Pilares Técnicos e Diferenciais de Engenharia

### 3.1 Universal Tool Gateway (MCP + OpenAI Tools)
* **Interoperabilidade Total:** Suporta ferramentas conectadas tanto via protocolo **Anthropic MCP** (stdio/SSE) quanto pelo padrão **OpenAI Function Calling** (`tools: [...]`).
* **Agnóstico de Provedor:** Permite alternar dinamicamente entre **DeepSeek** (`deepseek-chat`, `deepseek-reasoner` / R1), **OpenAI** (`gpt-4o-mini`, `gpt-4o`), **Groq** e **Llama 3 local via Ollama/vLLM** sem alterar uma única linha de código das ferramentas.

### 3.2 FinOps & Blindagem Anti-Estouro de Tokens (Anti-DoW)
Para viabilizar a hospedagem pública open source sem riscos financeiros:

1. **Computação Serverless (Scale-to-Zero):** Executado no **Google Cloud Run** e **Azure Container Apps** com `min_instances = 0`. Sem incidentes, zero custo de CPU/RAM ($0/mês).
2. **Daily Cost Circuit Breaker (Disjuntor Diário de Gastos):**
   * Contabilização agregada diária em tabela no PostgreSQL Serverless (`daily_token_usage`).
   * Teto diário rígido configurável (ex.: **$1.00/dia** ou **150.000 tokens/dia**).
   * Se o limite for atingido, a API pública bloqueia novas chamadas externas de LLM retornando `HTTP 429`.
3. **Padrão "Bring Your Own Key" (BYOK):**
   * Visitantes podem injetar sua própria chave via headers HTTP (`X-OpenAI-API-Key` ou `X-DeepSeek-API-Key`).
   * As requisições BYOK não consomem a cota do mantenedor e não ficam armazenadas em disco (stateless).
4. **Modo Sandbox "Replay Zero-Token" (Demo 100% Grátis):**
   * A demo online oferece um modo de replay com simulação dos 4 cenários canônicos usando rastros pré-gravados em cache do LogHub.
   * O visitante experimenta toda a interface e o grafo LangGraph com **zero chamadas a APIs pagas**.
5. **Rate Limiting por IP (Sliding Window):**
   * Máximo de 5 requisições por minuto e 2 incidentes completos por dia por IP na cota pública gratuita.
6. **Agent Token Budget & Turn Cap:**
   * Teto de **12.000 tokens** por incidente no grafo.
   * Limite de **4 iterações** do Supervisor (`max_iterations = 4`).
   * Truncamento de saídas de ferramentas a no máximo 2.000 caracteres por chamada.

### 3.3 Privacidade Cirúrgica (LGPD / GDPR) e Auditoria (EU AI Act)
* **Regra de IPs Públicos vs Privados:**
  * **IPs Públicos / WAN (Clientes):** Mascarados deterministicamente (`[REDACTED_PUBLIC_IP]`).
  * **IPs Privados RFC 1918 (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) e DNS de Pods K8s:** Estritamente preservados para que os agentes de infraestrutura possam diagnosticar a topologia interna de microsserviços.
* **Dados Pessoais & Credenciais:** Mascaramento de CPFs, CNPJs, cartões (Luhn), chaves de API, JWTs e senhas.
* **Audit Trail Não-Repudiável:** Cada incidente gera um `PostMortemReport` gravado no PostgreSQL Serverless contendo a timeline completa, assinaturas humanas e hash SHA-256 da decisão.

### 3.4 Documentação Viva em Dois Níveis
1. **Scalar API Reference (`/docs` ou `/scalar`):** Interface interativa moderna para explorar e testar a API REST com cliente HTTP embutido e gerador de snippets em tempo real.
2. **MkDocs Material com i18n:** Portal de documentação arquitetural, guias de deploy e runbooks operacionais em Português (padrão), Inglês e Espanhol.

### 3.5 Observabilidade de LLMs & Tracing de Custos (LangSmith & Langfuse)
* **Tracing de Nós LangGraph:** Cada nó do grafo (Supervisor, LogAgent, InfraAgent, RAGAgent, RemediationAgent) emite telemetria de latência, tokens consumidos e custos financeiros.
* **LangSmith (Nativo):** Ativado via `LANGSMITH_TRACING=true` para visualização da árvore de execução, inspeção do estado antes e depois de cada nó e captura do feedback humano no portão HITL.
* **Langfuse (Alternativa Open Source):** Suporte nativo a exportação via LiteLLM e OpenTelemetry para ambientes on-premise ou self-hosted.

### 3.6 Avaliação Contínua de Assertividade (Ragas no CI/CD)
* **Quality Gate de RAG e Remediação:** Avaliação quantitativa com LLM-as-a-Judge contra o gabarito dos 4 cenários canônicos:
  * **Faithfulness ($\ge 0.85$):** Garante que as causas raízes e os planos de mitigação propostos decorrem estritamente dos logs recuperados e dos runbooks, sem alucinações.
  * **Answer Relevancy ($\ge 0.80$):** Valida se o plano de remediação atende com precisão cirúrgica ao alerta emitido.
  * **Context Precision & Recall:** Avalia se o RAG de runbooks recuperou o SOP operacional correto para o incidente em curso.

---

## 🧪 4. Chaos Studio: Matriz Técnica dos 4 Cenários de Crise

| Cenário | Alerta & Payload de Entrada | Amostra de Logs (LogHub) | Causa Raiz Diagnosticada | Ação de Remediação & Diff |
| :--- | :--- | :--- | :--- | :--- |
| **1. Falha de Migração no Checkout** | Webhook Datadog: `HTTP 500 Spike > 15%` em `/api/v1/checkout` | OpenStack/Linux sample: `KeyError: 'billing_address_v2'` | Migração de banco incompleta; coluna ausente na tabela `orders`. | **SCHEMA_HOTFIX:** `ALTER TABLE orders ADD COLUMN IF NOT EXISTS billing_address_v2 JSONB;` ou rollback da versão. |
| **2. Esgotamento do Pool de Conexões** | Webhook Prometheus: `pg_connections_used > 98%` e CPU > 95% | Hadoop/HDFS sample com conexões travadas: `FATAL: remaining connection slots reserved` | Vazamento de conexões na aplicação (queries `idle in transaction` > 180s). | **DATABASE_TERMINATE_BACKENDS:** `SELECT pg_terminate_backend(pid) WHERE state = 'idle in transaction' > 120s;` seguido de rollout restart. |
| **3. Latência Anômala em Pagamentos** | Webhook Grafana: Latência p99 > 15.000ms no serviço `payment-gw` | Spark sample: `ReadTimeoutError: HTTPSConnectionPool(gateway.wire.com): Request timed out` | Provedor de pagamentos externo degradado provocando travamento em cascata. | **CIRCUIT_BREAKER_ACTIVATE:** Ativação de fallback assíncrono e chaveamento para adquirente secundária via config patch. |
| **4. Model Drift Crítico** | Alerta Customizado: Taxa de conversão do modelo de recomendação caiu 52% em 1h | Access logs com discrepância de pontuação e fallback para itens aleatórios | Quebra de contrato de features no pipeline de features online (*data drift*). | **CONFIG_ROLLBACK:** Rollback do deployment de inferência para a versão anterior estável (`v2.4.1 -> v2.4.0`). |

---

## 📁 5. Estrutura Canônica do Repositório

```
OpsMesh/
├── .github/workflows/          # CI/CD: Pre-commit, testes e deploy Cloud Run
├── .pre-commit-config.yaml     # Hooks: Ruff, Mypy, Gitleaks, validações
├── mkdocs.yml                  # Configuração MkDocs Material + i18n (PT-BR, EN, ES)
├── PRD.md                      # Product Requirements Document detalhado
├── PROJECT_SPEC.md             # Especificação Técnica Consolidada
├── AGENTS.md                   # Contratos, schemas Pydantic e Prompts dos Agentes
├── TASK.md                     # Roadmap granular e checklists de implementação
├── docs/                       # Documentação Viva Tri-língue (MkDocs)
│   ├── index.md                # Visão geral (Português - Padrão)
│   ├── index.en.md             # English Home Page
│   ├── index.es.md             # Página de inicio en Español
│   ├── prd.md                  # Requisitos de Produto
│   ├── architecture/           # Detalhes de arquitetura, gateways e FinOps
│   ├── agents/                 # Especificação e contratos dos agentes
│   └── runbooks/               # Runbooks operacionais de emergência
├── src/opsmesh/                # Código-Fonte Principal
│   ├── api/                    # FastAPI com Scalar Reference e Webhooks
│   ├── core/                   # Configurações, PII sanitizer e Circuit Breaker FinOps
│   ├── gateway/                # Universal Tool Gateway (MCP + OpenAI Tools)
│   ├── agents/                 # Implementação dos agentes LangGraph
│   ├── graph/                  # StateGraph LangGraph e Checkpointer Serverless
│   └── chaos/                  # Chaos Studio com os 4 cenários e modo Replay
└── tests/                      # Testes unitários, de integração e avaliação
```
