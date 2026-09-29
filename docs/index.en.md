# 🚨 OpsMesh — Autonomous Incident Commander

> **Autonomous Multi-Agent System for Critical Incident Response & SRE**  
> Built with **LangGraph**, **Model Context Protocol (MCP)**, **OpenAI Tools (DeepSeek / GPT / Llama)**, **PostgreSQL Serverless**, and **Human-in-the-Loop (HITL)**.

> 🌐 **Official Live Production Environment (Google Cloud Run):**  
> 🔗 **SRE Console & Chaos Studio:** [https://opsmesh-197215016090.us-central1.run.app](https://opsmesh-197215016090.us-central1.run.app)  
> 📖 **Interactive API Documentation (Scalar):** [https://opsmesh-197215016090.us-central1.run.app/docs](https://opsmesh-197215016090.us-central1.run.app/docs)  
> 🩺 **Health Check & Telemetry:** [https://opsmesh-197215016090.us-central1.run.app/health](https://opsmesh-197215016090.us-central1.run.app/health)

---

## 🌟 What is OpsMesh?

**OpsMesh** acts as a Staff SRE Incident Commander for distributed cloud environments. When monitoring alerts fire in Datadog, Prometheus, or Grafana, OpsMesh:

1. **Ingests & Sanitizes:** Receives alerts and redacts Personally Identifiable Information (**GDPR / LGPD**) before LLM processing.
2. **Parallel Forensic Investigation:** Spawns specialized agents for log analytics (LogHub datasets & Elasticsearch/Loki) and infrastructure (Postgres, Redis, Kubernetes).
3. **Retrieves Operational Knowledge:** Executes **Hybrid RAG** over standard operating procedures (SOPs) and runbooks.
4. **Synthesizes Remediation Plan:** Identifies root cause and generates config/code diffs and rollback plans.
5. **Enforces Human-in-the-Loop (HITL):** Critical actions pause execution at the PostgreSQL Serverless checkpoint until on-call engineer authorization.
6. **Safe Execution & Post-Mortem:** Executes verified patches and generates audit-ready PDF post-mortem reports.

---

## 🚀 Engineering Highlights

* **FinOps Serverless ($0/month):** Designed for **Scale-to-Zero** on Google Cloud Run and Azure Container Apps. When idle, computing costs are exactly zero.
* **Specialized Decision Models (Jev First):** Incident Supervisor routing and convergence powered by **Jev (`typesafe/jev-latest` on OpenRouter)** with sub-30ms latency, zero output cost, and native `Choice`/`Noul` primitives.
* **Universal Tool Gateway:** Seamless dual-support for **Anthropic MCP** and **OpenAI Function Calling (DeepSeek / GPT)**.
* **OpenRouter Gateway & Free Fleet:** Integrated access to the official free models fleet (`openrouter/free`, `nvidia/nemotron-3-ultra-550b-a55b:free`, `poolside/laguna-s-2.1:free`, `cohere/north-mini-code:free`) unlocked by positive balance (> $10) and full BYOK support (`X-OpenRouter-API-Key`).
* **Datadog Pro APM & Distributed Tracing:** Native instrumentation (`ddtrace`) with distributed context propagation (`traceparent`, `x-datadog-trace-id`), connecting Chaos Lab faults to LangGraph nodes.
* **Zero-Daemon Serverless Storage:** **LanceDB** for disk-based hybrid vector search ($0 infra) and **DuckDB + Parquet** for instant historical MTTR and incident analytics.
* **Automated Red-Teaming Gate (Promptfoo):** Continuous pentesting in GitHub Actions CI auditing against prompt injection, HITL bypass, and credential leakage.
* **Living Documentation with Scalar:** State-of-the-art interactive API reference at `/docs` or `/scalar`.
* **Chaos Lab Ecosystem:** Independent companion application (`d:\ChaosLab`) with live fault injection and native Datadog APM tracing.
* **Surgical Code Inspection via GitHub API:** Stateless remote retrieval of exact files/lines on the `main` branch pinpointed by Datadog's stack trace.
* **Two-Tier Remediation:** Immediate runtime stabilization (< 5s) to restore SLO + Automated GitHub Pull Request for permanent root cause code fix.


