# 🚨 OpsMesh — Autonomous Incident Commander

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/LangGraph-Multi--Agent-FF6F00?style=for-the-badge&logo=langchain&logoColor=white" alt="LangGraph" />
  <img src="https://img.shields.io/badge/FastAPI-REST_API-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/API_Docs-Scalar-6366F1?style=for-the-badge" alt="Scalar API" />
  <img src="https://img.shields.io/badge/Tools-MCP_%2B_OpenAI-000000?style=for-the-badge&logo=anthropic&logoColor=white" alt="MCP + OpenAI" />
  <img src="https://img.shields.io/badge/FinOps-Scale--to--Zero-22C55E?style=for-the-badge&logo=googlecloud&logoColor=white" alt="Scale-to-Zero" />
  <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge" alt="License Apache 2.0" />
</p>

---

## 📌 Visão Geral

O **OpsMesh** é um sistema multi-agente autônomo projetado para atuar como **Incident Commander (Comandante de Incidentes)** de nível Staff SRE em sistemas distribuídos de missão crítica. 

Quando alertas críticos disparam (Datadog, Prometheus, Grafana), o OpsMesh:
1. **Ingere e Sanitiza:** Mascara dados sensíveis (**LGPD / GDPR**), preservando a topologia de redes privadas RFC 1918 para diagnóstico de pods.
2. **Investiga em Paralelo:** Aciona agentes especialistas para correlacionar logs (Elastic/LogHub), inspecionar infraestrutura (Postgres, Redis, K8s) e consultar manuais de crise (**RAG Híbrido**).
3. **Gera Mitigação Segura com HITL:** Formula planos de remediação auditáveis com diffs de código e estratégia de rollback.
4. **Protege Ações Críticas:** Bloqueia execuções destrutivas com **Human-in-the-Loop (HITL)** persistido no **PostgreSQL Serverless** até a assinatura do engenheiro de plantão.
5. **Compila Post-Mortem:** Gera relatórios estruturados e PDFs auditáveis com hash criptográfico SHA-256.

---

## 💡 Por que o OpsMesh? (Comparativo com Datadog & Sentry)

Muitos engenheiros se perguntam: *"O OpsMesh substitui ou faz o mesmo que o Datadog e o Sentry?"*  
A resposta é **não — o OpsMesh complementa e expande a observabilidade moderna para o nível de Remediação Ativa e Prescritiva**:

* **Datadog e Sentry (Observabilidade Passiva):** São como os **alarmes de incêndio e termômetros** do edifício. Eles monitoram exceções no código, desenham gráficos e alertam quando algo quebrou (*"Alerta: Banco de dados com 98% de conexões travadas"*). Porém, **eles não resolvem o problema**. Às 3h da manhã, o engenheiro humano (SRE de plantão) é quem precisa acordar, ler wikis internas, abrir terminais e tentar descobrir os comandos corretos.
* **OpsMesh (Remediação Prescritiva com IA & Portão HITL):** É a **brigada de bombeiros inteligente**. Ele consome o alerta do Datadog/Sentry, aciona agentes para investigar logs e infraestrutura em paralelo, consulta os manuais da empresa (SOPs via RAG Híbrido) e entrega **a solução cirúrgica pronta** (comandos, diff de patch e rollback), aguardando apenas **1 clique de autorização humana** para resolver a crise.

```text
┌─────────────────────────────────────────┐       ┌──────────────────────────────────────────────┐
│       DATADOG / SENTRY / GRAFANA        │  ==>  │                   OPSMESH                    │
│        (Observabilidade Passiva)        │       │             (Remediação Ativa)               │
│                                         │       │                                              │
│  "Alerta: Erro 504 no Checkout e        │       │  1. Investiga logs, traces e pods em paralelo│
│   Pool PostgreSQL em 98% de saturação"  │       │  2. Consulta os Runbooks (SOPs) via RAG      │
│                                         │       │  3. Formula o plano exato de mitigação       │
│  (Para por aqui. Acorda o SRE on-call)  │       │  4. Portão HITL: SRE aprova com 1 clique     │
│                                         │       │  5. Emite relatório Post-Mortem em PDF       │
└─────────────────────────────────────────┘       └──────────────────────────────────────────────┘
```

---

### 🕹️ Dois Modos de Operação: Demonstração (Chaos Studio) vs. Produção Real

| Modo | Como Funciona | Para Quem Serve | Custo |
| :--- | :--- | :--- | :--- |
| **Modo Sandbox / Chaos Studio** *(Botão "Simular Crise")* | O OpsMesh utiliza seu **emulador interno de telemetria** baseado em datasets reais do *LogHub*. Ele simula o envio de alertas no formato do Datadog/Prometheus sem necessidade de contas pagas ou servidores externos. | Recrutadores, Tech Leads, demonstrações de portfólio e testes locais. | **$0.00** *(Zero-Token Replay)* |
| **Modo Produção Corporativa** *(Webhook Universal)* | O OpsMesh expõe o endpoint `POST /api/v1/incidents/webhook`. Basta cadastrar essa URL nos Webhooks do seu **Datadog**, **Sentry**, **Grafana** ou **PagerDuty**. Quando um alerta real dispara, o OpsMesh inicia a investigação automaticamente. | Ambientes de staging e produção corporativa em nuvem (GCP, AWS, Azure, K8s). | Conforme tokens de LLM configurados |

---

### 📝 Exemplo Prático de Fluxo (Ponta a Ponta)

#### 1. O Alerta Chega (via Datadog ou Chaos Studio)
```json
POST /api/v1/incidents/webhook
{
  "service": "order-service",
  "severity": "P0_CRITICAL",
  "message": "FATAL: remaining connection slots are reserved on node 10.244.1.15",
  "details": { "active_connections": 98, "max_connections": 100 }
}
```

#### 2. O OpsMesh Investiga e Formula o Tratamento
A equipe de agentes correlaciona os logs, analisa o tráfego e consulta o manual `docs/runbooks/connection_pool.md` via RAG Híbrido, gerando o plano cirúrgico:
```yaml
Ação Proposta: DATABASE_TERMINATE_BACKENDS (Risco Alto)
Comandos Gerados:
  $ SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction' AND state_change < current_timestamp - INTERVAL '5 minutes';
  $ kubectl rollout restart deployment order-service -n production
Plano de Rollback: kubectl rollout restart deployment pgbouncer
```

#### 3. Portão Human-in-the-Loop (HITL)
O sistema **bloqueia qualquer ação destrutiva** e apresenta o diagnóstico completo na interface. O engenheiro revisa a causa raiz e clica em **"Aprovar Mitigação"** (`POST /api/v1/incidents/{id}/resume`).

#### 4. Auditoria Criptográfica & Post-Mortem
Após a mitigação, o sistema gera o Post-Mortem oficial com hash SHA-256 e download imediato em PDF.

---

## 🏛️ Topologia Arquitetural

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
        Supervisor -->|Diagnóstico de Logs| LogAgent[LogTraceAnalystAgent]
        Supervisor -->|Análise de Infra| InfraAgent[DatabaseInfraAgent]
        Supervisor -->|Manuais de Crise| RAGAgent[RunbookKnowledgeAgent]
        
        LogAgent <--> ToolGateway
        InfraAgent <--> ToolGateway
        
        LogAgent --> Synthesis[Nó de Síntese]
        InfraAgent --> Synthesis
        RAGAgent --> Synthesis
    end
    
    Synthesis --> RemediationPlan[RemediationEngineerAgent:\nGeração do Plano & Diff]
    
    RemediationPlan --> HITL_Gate{HITL Gate: Ação Crítica?}
    HITL_Gate -->|interrupt_before| PausedState[(LangGraph Checkpointer:\nPostgreSQL Serverless)]
    
    PausedState --> SRE_Notification([Engenheiro Humano de Plantão\nNotificação com Diff])
    
    SRE_Notification -->|Aprovar| ResumeEndpoint[POST /api/v1/incidents/{incident_id}/resume]
    ResumeEndpoint --> Execution[Execução Segura da Ação]
    Execution --> PostMortem[AuditPostMortemAgent: Relatório Estruturado & PDF]
```

---

## ⚡ Diferenciais de Engenharia

| Pilar | Detalhes Técnicos |
| :--- | :--- |
| **Universal Tool Gateway** | Suporta simultaneamente **Anthropic MCP** (stdio/SSE) e **OpenAI Function Calling** (DeepSeek V3/R1, GPT-4o, Llama 3 via Ollama/vLLM). |
| **FinOps & Scale-to-Zero** | Elegível para **Google Cloud Run** e **Azure Container Apps** com `min_instances = 0` (**$0/mês ocioso**). |
| **Blindagem Anti-DoW** | Disjuntor diário de gastos ($1.00/dia), Rate Limiting por IP, padrão **BYOK** (`X-OpenAI-API-Key`, `X-DeepSeek-API-Key`) e Modo Replay Zero-Token. |
| **Observabilidade de LLMs** | Tracing nativo do LangGraph com **LangSmith** e suporte a **Langfuse** (self-hosted). |
| **Quality Gate com Ragas** | Avaliação contínua no CI/CD com LLM-as-a-Judge: *Faithfulness $\ge 0.85$* e *Answer Relevancy $\ge 0.80$*. |
| **API Moderna com Scalar** | Documentação interativa e cliente HTTP embutido em `/docs` e `/scalar` (Swagger UI descontinuado). |
| **Documentação Tri-língue** | Portal **MkDocs Material** com seletor de idiomas: Português (padrão), Inglês e Espanhol. |

---

## 🧪 Chaos Studio: 4 Cenários Canônicos

1. **Checkout Schema Mismatch:** Coluna ausente após deploy em microsserviço -> Hotfix SQL ou rollback.
2. **PostgreSQL Connection Pool:** Queries ociosas travando conexões (`CPU 95%`) -> `pg_terminate_backend()` seguro.
3. **Payment Gateway Latency:** Timeout externo p99 > 15s -> Ativação de circuit breaker e rota de contingência.
4. **Model Drift Crítico:** Queda súbita de 52% na conversão -> Rollback do deployment de inferência.

---

## 🚀 Quickstart

### Pré-requisitos
* Python 3.12+
* Gerenciador [UV](https://github.com/astral-sh/uv) instalado (`pip install uv` ou `cargo install uv`)

### Instalação
```bash
# 1. Clonar o repositório
git clone https://github.com/OpsMesh/OpsMesh.git
cd OpsMesh

# 2. Sincronizar o ambiente virtual com uv
uv sync

# 3. Configurar variáveis de ambiente
cp .env.example .env

# 4. Ativar os hooks de pre-commit
uv run pre-commit install
```

### Executando a API e a Documentação Viva
```bash
# Iniciar a API com Scalar Docs
uv run uvicorn src.opsmesh.api.app:app --reload --port 8000

# Acessar a documentação viva da API:
# 👉 http://localhost:8000/docs ou http://localhost:8000/scalar

# Iniciar o portal de documentação MkDocs com i18n
uv run mkdocs serve --dev-addr 127.0.0.1:8080
# 👉 http://localhost:8080 (Português, Inglês e Espanhol)
```

---

## 📚 Base Documental Viva

* [**`PRD.md`**](PRD.md): Product Requirements Document (Personas, SLAs, Casos de Uso, NFRs).
* [**`PROJECT_SPEC.md`**](PROJECT_SPEC.md): Especificação técnica e topologia do sistema.
* [**`AGENTS.md`**](AGENTS.md): Contratos dos agentes, schemas Pydantic v2 e system prompts.
* [**`TASK.md`**](TASK.md): Backlog granular de tarefas em checklist por fases de engenharia.
* [**`.pre-commit-config.yaml`**](.pre-commit-config.yaml): Hooks de qualidade (Ruff, Mypy, Gitleaks, Prettier).
