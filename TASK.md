# 📋 OpsMesh — Backlog de Tarefas & Roadmap (TASK.md)

> **Controle de Execução e Checklist de Engenharia para Vibe Coding**  
> **Status Geral:** Em Andamento (Fase 0 Concluída e Revisada)  
> **Padrão de Qualidade:** Senior / Lead AI Agent Engineer  

---

## 🧭 Legenda de Status
- [ ] A Fazer / Pendente
- [/] Em Andamento
- [x] Concluído

---

## 📦 Fase 0: Arquitetura, Governança, Proteção FinOps & Documentação Viva (Fundação)
- [x] Criação do `PRD.md` com requisitos de negócio, personas, SLAs de SRE, blindagem contra estouro de tokens (Anti-DoW) e conformidade (LGPD/EU AI Act).
- [x] Criação do `AGENTS.md` com contratos Pydantic (incluindo `PostMortemReport`), topologia hierárquica, reducers de estado, limites de turnos (`max_iterations = 4`) e orçamentos de tokens.
- [x] Atualização do `PROJECT_SPEC.md` com Universal Tool Gateway (MCP + OpenAI/DeepSeek), blindagem FinOps em 5 camadas (Circuit Breaker, BYOK, Replay Zero-Token), PostgreSQL Serverless e Scalar API Docs.
- [x] Detalhamento da matriz dos 4 cenários canônicos do Chaos Studio (Checkout, Conexões Postgres, Latência Pagamentos, Model Drift).
- [x] Configuração do `.pre-commit-config.yaml` com Ruff, Mypy/Pyright e detecção de credenciais (Gitleaks).
- [x] Configuração do `mkdocs.yml` com tema Material, suporte i18n (Português padrão, Inglês, Espanhol) e páginas iniciais em `docs/`.
- [x] Estruturação do `TASK.md` com roadmap granular para Vibe Coding.

---

## 🛠️ Fase 1: Setup do Ambiente e Gestão de Dependências
- [x] Criação do `pyproject.toml` moderno com gerenciador `uv`:
  - Dependências centrais: `langgraph`, `langchain-core`, `pydantic>=2.7.0`, `fastapi`, `scalar-fastapi`, `uvicorn`, `slowapi`.
  - Provedores, Ferramentas & Observabilidade: `openai`, `mcp`, `langgraph-checkpoint-postgres`, `asyncpg`, `psycopg-pool`, `langsmith`, `langfuse`.
  - RAG, Dados & Avaliação: `qdrant-client`, `rank-bm25`, `sentence-transformers`, `ragas`, `datasets`.
  - Qualidade: `ruff`, `mypy`, `pytest`, `pytest-asyncio`, `reportlab`.
- [x] Criação de `.env.example` com placeholders seguros para OpenAI, DeepSeek, Neon/Supabase PostgreSQL, Qdrant, LangSmith (`LANGSMITH_API_KEY`) e Langfuse.
- [x] Configuração de `.gitignore` abrangente (bloqueando `.env`, chaves de API, caches e arquivos de log).

---

## 🛡️ Fase 2: Núcleo de Segurança, FinOps Anti-Abuso e Sanitização PII (LGPD)
- [x] Implementação de `src/opsmesh/core/pii_sanitizer.py`:
  - Mascaramento determinístico via Regex para CPFs, CNPJs, Cartões de Crédito (Luhn), Tokens de Autenticação (Bearer/JWT), Passwords e IPs públicos.
  - **Preservação estrita de IPs de redes privadas RFC 1918** (`10.x`, `172.16-31.x`, `192.168.x`) e hostnames internos de Pods K8s para viabilizar o diagnóstico de infraestrutura.
- [x] Implementação do **Disjuntor Diário de Custos (Daily Cost Circuit Breaker)** em `src/opsmesh/core/circuit_breaker.py`:
  - Tabela `daily_token_usage` no PostgreSQL Serverless para controle agregado de gastos.
  - Teto configurável (ex.: $1.00/dia ou 150k tokens/dia) com desarme automático e retorno de `HTTP 429`.
- [x] Implementação do `IncidentState` TypedDict em `src/opsmesh/core/state.py` com reducers de reset (`reduce_agent_results`, `reduce_sources`) e campos de token budget (`total_tokens_consumed`, `token_budget_limit`).
- [x] Implementação de todos os modelos Pydantic v2 em `src/opsmesh/core/schemas.py` (`SupervisorDecision`, `LogAnalysisResult`, `InfraAnalysisResult`, `RunbookRetrievalResult`, `RemediationPlan`, `PostMortemReport`).

---

## 🔌 Fase 3: Universal Tool Gateway (MCP + OpenAI Tools)
- [x] Implementação do adaptador de ferramentas em `src/opsmesh/gateway/adapter.py`:
  - Conversor bidirecional de schemas: MCP Tool Schema <-> OpenAI Function Calling Schema.
- [x] Implementação do cliente MCP em `src/opsmesh/gateway/mcp_client.py` com suporte a transporte `stdio` e `sse`.
- [x] Implementação do despachante universal em `src/opsmesh/gateway/dispatcher.py` unificando chamadas para DeepSeek, OpenAI ou Servidores MCP.
- [x] Criação de ferramentas mock de observabilidade com guardrail de truncamento (máximo 2.000 caracteres):
  - `query_logs` (Elasticsearch/Loki mock com dados LogHub).
  - `inspect_database_activity` (Postgres stat activity mock em modo Read-Only).
  - `check_k8s_deployment_health` (Kubernetes mock em modo Read-Only).

---

## 🧠 Fase 4: Implementação dos Agentes Especialistas
- [x] Implementação do `IncidentSupervisorAgent` em `src/opsmesh/agents/supervisor.py`:
  - Orquestração com `with_structured_output(SupervisorDecision)`.
  - Guardrail de turnos: `max_iterations = 4`.
- [x] Implementação do `LogTraceAnalystAgent` em `src/opsmesh/agents/log_analyst.py`.
- [x] Implementação do `DatabaseInfraAgent` em `src/opsmesh/agents/infra_analyst.py`.
- [x] Implementação do `RunbookKnowledgeAgent` em `src/opsmesh/agents/runbook_agent.py`:
  - Indexação híbrida de runbooks Markdown (Dense Qdrant + BM25 + RRF).
- [x] Implementação do `RemediationEngineerAgent` em `src/opsmesh/agents/remediation.py`:
  - Geração de planos de ação, patches diff e avaliação de risco (`is_critical_action`).
- [x] Implementação do `AuditPostMortemAgent` em `src/opsmesh/agents/post_mortem.py`:
  - Geração de `PostMortemReport` estruturado e exportação para PDF auditável.

---

## 🕸️ Fase 5: Grafo LangGraph, Checkpoint PostgreSQL & Tracing
- [x] Montagem do grafo orquestrador em `src/opsmesh/graph/builder.py`:
  - Arestas condicionais baseadas na decisão do Supervisor.
  - Portão HITL com `interrupt_before=["execute_remediation_node"]`.
- [x] Configuração do checkpointer persistente em `src/opsmesh/graph/checkpointer.py`:
  - Conexão assíncrona com PostgreSQL Serverless (`AsyncPostgresSaver`) com fallback para `MemorySaver`.
  - Auto-migração das tabelas de checkpoints.
- [x] Instrumentação de Observabilidade (LangSmith & Langfuse):
  - Injeção de rastreamento de traces de execução do grafo com `trace_id` e `langsmith_run_id`.
  - Captura do feedback humano de aprovação/rejeição no LangSmith.
- [x] Testes de interrupção e retomada de estado via thread ID.

---

## 🌐 Fase 6: API REST FastAPI, Scalar Docs, BYOK & Webhooks
- [x] Criação da aplicação FastAPI em `src/opsmesh/api/app.py`:
  - Configuração da documentação viva com **Scalar API Reference** em `/docs` e `/scalar` (proibido Swagger UI).
  - Middleware de **Rate Limiting por IP** via `slowapi` (5 req/min, 2 incidentes/dia).
  - Middleware de **Bring Your Own Key (BYOK)** extraindo `X-OpenAI-API-Key` e `X-DeepSeek-API-Key`.
- [x] Endpoint de ingestão de alertas: `POST /api/v1/incidents/webhook`:
  - Tratamento de payloads Datadog, Prometheus e Grafana.
  - Disparo assíncrono em background do fluxo do LangGraph.
- [x] Endpoint de consulta de status: `GET /api/v1/incidents/{incident_id}`:
  - Retorno do estado atual do grafo, evidências e plano de ação pendente.
- [x] Endpoint de retomada HITL: `POST /api/v1/incidents/{incident_id}/resume`:
  - Recepção da aprovação humana para destravar o checkpoint.
- [x] Endpoint de download de post-mortem: `GET /api/v1/incidents/{incident_id}/post-mortem` (JSON e PDF auditável).

---

## 💥 Fase 7: Chaos Studio, Modo Replay Zero-Token & Evals com Ragas
- [x] Criação do módulo `src/opsmesh/chaos/studio.py`:
  - Carregador de amostras do repositório acadêmico LogHub (Linux, Hadoop, Spark, OpenStack).
  - Implementação dos 4 cenários canônicos (Checkout, Postgres Conexões, Latência Pagamentos, Model Drift).
- [x] Implementação do **Modo Replay Zero-Token** (`DEMO_MODE=replay`):
  - Execução dos 4 cenários da demo pública a partir de traces gravados em cache, permitindo que visitantes usem o sistema sem gerar custos de API para os mantenedores.
- [x] Pipeline de Avaliação Contínua com **Ragas** (`tests/evals/test_ragas_quality_gate.py`):
  - Validação de *Faithfulness* ($\ge 0.85$), *Answer Relevancy* ($\ge 0.80$) e *Context Precision* contra os 4 cenários de crise.
- [x] Suite de testes automatizados com `pytest` validando os 4 cenários ponta a ponta.

---

## 🎨 Fase 8: Console Frontend SRE (Paleta Nobre Areia & Bronze)
- [x] Criação da aplicação React 19 + Vite + TypeScript em `frontend/`:
  - Aplicação dos tokens de design extraídos de `Portfolio_Pessoal` (`sand.base`, `sand.surface`, `sand.terminal`, `brand.bronze`, `brand.gold`, `brand.steel`).
  - Efeitos glassmorphism `.glass-panel` e iluminação ambiente `.ambient-glow`.
- [x] Componentes do Centro de Comando:
  - `Header.tsx`: Monitoramento FinOps, quota de tokens diária e link Scalar API.
  - `ChaosBar.tsx`: Seletor dos 4 cenários canônicos de crise e toggle **Zero-Token Replay ($0)** vs Live.
  - `AgentTopology.tsx`: Grafo visual em tempo real dos 6 agentes especialistas.
  - `HITLHeroCard.tsx`: Portão Human-in-the-Loop hero card com visualizador de diff de código e botões de autorização.
  - `EvidenceViewer.tsx`: Navegador de evidências em abas (Logs LogHub, Infra K8s/Postgres, Runbooks SOPs).
  - `PostMortemViewer.tsx`: Painel de conformidade com hash criptográfico SHA-256 e download de PDF oficial.
- [x] Integração no FastAPI para servir o frontend SPA compilado via `/` e `/assets`.

---

## 🚀 Fase 9: FinOps, Conteinerização Scale-to-Zero & Deploy
- [x] Criação do `Dockerfile` multi-stage otimizado (Node Alpine builder + Python 3.12 slim com UV + non-root user).
- [x] Configuração de deploy serverless:
  - Manifesto para **Google Cloud Run** (`deploy/cloud-run.yaml`, `minScale: "0"`, startup CPU boost).
  - Manifesto para **Azure Container Apps** (`deploy/azure-container-app.bicep`, `minReplicas: 0`).
- [x] Validação de FinOps: auditoria de cold start (< 3s) e garantia de $0/mês em repouso.

---

## 📚 Fase 10: Documentação Viva MkDocs & Suporte Tri-língue
- [x] Validação das páginas de documentação em `docs/` com suporte i18n (Português padrão, Inglês e Espanhol).
- [x] Script de build e teste local da documentação (`python -m mkdocs build` validado sem erros).
