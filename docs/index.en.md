# 🚨 OpsMesh — Autonomous Incident Commander

> **Autonomous Multi-Agent System for Critical Incident Response & SRE**  
> Built with **LangGraph**, **Model Context Protocol (MCP)**, **OpenAI Tools (DeepSeek / GPT / Llama)**, **PostgreSQL Serverless**, and **Human-in-the-Loop (HITL)**.

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
* **Universal Tool Gateway:** Seamless dual-support for **Anthropic MCP** and **OpenAI Function Calling (DeepSeek / GPT)**.
* **Living Documentation with Scalar:** State-of-the-art interactive API reference at `/docs` or `/scalar`.
