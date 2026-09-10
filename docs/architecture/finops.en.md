# FinOps, Scale-to-Zero Architecture ($0/month) & Anti-Abuse Protection

OpsMesh was designed from day one with a **FinOps First** philosophy: guaranteeing **$0/month idle infrastructure cost** and **complete immunity against Denial of Wallet (DoW)** and token budget exhaustion when deployed publicly as open source.

---

## 1. Scale-to-Zero Serverless Principles

1. **Event-Driven Serverless Compute:**
   - Stateless control plane containerized and hosted on **Google Cloud Run** or **Azure Container Apps**.
   - `min_instances = 0` ensures zero active instances when no incidents occur ($0/month).
2. **Auto-Suspending PostgreSQL Serverless:**
   - LangGraph checkpoints and audit trails stored in serverless PostgreSQL (Neon / Supabase Free Tier) with auto-suspension after 5 minutes of inactivity.
3. **Embedded / Free-Tier Vector Store:**
   - Qdrant embedded in-file or Qdrant Cloud Free Tier (1GB perpetual).

---

## 2. 5-Layer Anti-Token Exhaustion Shield (Anti-DoW)

To offer a public online demo without financial risk:

1. **Edge Protection & Anti-DDoS:** Cloudflare Free Tier / Google Cloud Armor bot-fight rules.
2. **IP Rate Limiting (Sliding Window):** `slowapi` middleware enforcing max 5 req/min and 2 full incident runs per day per IP.
3. **Bring Your Own Key (BYOK):** Visitors can supply `X-OpenAI-API-Key` or `X-DeepSeek-API-Key` to test without consuming the server quota.
4. **Daily Cost Circuit Breaker:** Serverless counter (`daily_token_usage`) tripping at $1.00/day or 150k tokens/day, responding with `HTTP 429`.
5. **Zero-Token Replay Sandbox Mode:** Visitors can explore the 4 Chaos Studio scenarios using cached LogHub traces with zero paid LLM calls.
6. **LangGraph Agent Token Budget:** 12,000 token limit per incident, max 4 supervisor iterations, and 2,000-char tool output truncation.
