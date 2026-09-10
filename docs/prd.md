# 📋 Requisitos de Produto (PRD)

> **Versão:** 1.1.0  
> **Status:** Aprovado  
> **Classificação:** Open Source Enterprise  

---

## 1. Visão de Negócio & O Problema do MTTR

Em arquiteturas distribuídas e microsserviços modernos, cada minuto de inatividade em panes P0/P1 custa milhares de dólares. O **OpsMesh** atua como um Comandante de Incidentes autônomo baseado em **LangGraph**, unificando:
- Ingestão de alertas de observabilidade (Datadog, Prometheus, Grafana).
- Diagnóstico paralelo em logs e infraestrutura via **Universal Tool Gateway** (Anthropic MCP + OpenAI Tools).
- RAG Híbrido sobre manuais operacionais (SOPs).
- Portão **Human-in-the-Loop (HITL)** para ações críticas.
- **FinOps Guardrails**: proteção contra estouro de tokens em demonstrações públicas na web.

---

## 2. Personas do Sistema

| Persona | Papel Primário | Benefício com OpsMesh |
| :--- | :--- | :--- |
| **SRE On-Call** | Primeiro respondente | Diagnóstico correlacionado em < 60s com sugestão exata de mitigação |
| **Incident Commander** | Liderança da crise | Painel em tempo real e geração automática de Post-Mortem |
| **Engenheiro DevOps** | Patches e correções | Diffs unificados e scripts idempotentes pré-validados |
| **Visitante / Avaliador** | Testes na demo pública | Execução gratuita via Modo Replay ou com chave própria (BYOK) |
| **Mantenedor do Projeto** | Governança e custos | $0/mês de computação ociosa e limite rígido diário de tokens |

---

## 3. Requisitos Funcionais Principais

* **FR-01:** Webhook padronizado `POST /api/v1/incidents/webhook`.
* **FR-02:** PII Sanitizer mascarando dados de clientes, preservando IPs privados RFC 1918 para diagnóstico de cluster.
* **FR-03:** LangGraph com `SupervisorDecision` e limite de 4 turnos (`max_iterations = 4`).
* **FR-04:** Universal Tool Gateway suportando simultaneamente servidores MCP e ferramentas OpenAI.
* **FR-05:** RAG Híbrido em 4 estágios (Qdrant + BM25 + RRF + Re-ranking).
* **FR-06:** Portão HITL com `interrupt_before` e retomada em `POST /api/v1/incidents/{incident_id}/resume`.
* **FR-07:** Persistência em PostgreSQL Serverless (Neon/Supabase) via `AsyncPostgresSaver`.
* **FR-08:** Documentação viva interativa de API via **Scalar** em `/docs` ou `/scalar`.
* **FR-09:** Chaos Studio com 4 cenários canônicos baseados em datasets do LogHub.
* **FR-10:** Suporte multilíngue nativo (Português, Inglês e Espanhol).
* **FR-11:** Padrão BYOK (`X-OpenAI-API-Key`, `X-DeepSeek-API-Key`).
* **FR-12:** Modo Sandbox Replay Zero-Token para exploração sem custos.

---

## 4. Requisitos Não Funcionais & FinOps

* **NFR-01:** Scale-to-Zero ($0/mês ocioso) no Google Cloud Run e Azure Container Apps.
* **NFR-02:** TTFT < 800ms em streaming de eventos.
* **NFR-03:** Resiliência com cascata de modelos e fallback automático.
* **NFR-04:** Pré-commit com Ruff, Mypy e Gitleaks.
* **NFR-05:** Disjuntor diário de gastos (Daily Cost Circuit Breaker) cortando chamadas pagas ao atingir o teto diário ($1.00/dia).
