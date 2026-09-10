# OpsMesh System Architecture

OpsMesh architecture is designed to be deterministic, auditable, resilient, and token-abuse protected (FinOps), utilizing a hierarchical topology powered by LangGraph and StateGraph.

---

## Topology Overview

```mermaid
graph TD
    Alert[Webhook: POST /api/v1/incidents/webhook] --> PII[PII Sanitizer Middleware\nMasks Public PII, Preserves RFC 1918]
    PII --> GuardrailCheck{Token Budget & Circuit Breaker?}
    
    GuardrailCheck -->|Quota Exceeded| 429[HTTP 429: Daily Quota Reached\nPrompt for BYOK or Local Docker]
    GuardrailCheck -->|Authorized / BYOK| Supervisor[Supervisor: Incident Commander]
    
    subgraph Specialists [Specialist Agents]
        Supervisor -->|Log Forensics| LogAgent[Log & Trace Analyst Agent]
        Supervisor -->|Infra Health| InfraAgent[Database & Infra Agent]
        Supervisor -->|SOP Retrieval| RAGAgent[Runbook Knowledge Agent]
        
        LogAgent --> Synthesis[Synthesis Node]
        InfraAgent --> Synthesis
        RAGAgent --> Synthesis
    end
    
    Synthesis --> Remediation[Remediation Engineer Agent]
    Remediation --> HITL{Critical Action?}
    
    HITL -->|interrupt_before| Checkpoint[(PostgreSQL Serverless Checkpointer)]
    Checkpoint --> SRE[On-Call SRE Notification]
    SRE -->|POST /api/v1/incidents/{id}/resume| Resume[Resume Graph]
    Resume --> Exec[Safe Mitigation Execution]
    Exec --> PostMortem[AuditPostMortemAgent: Structured PDF Report]
```

---

## Key Components

### 1. PII Sanitizer Middleware with RFC 1918 Preservation
- Redacts customer documents, credit cards (Luhn), API keys, JWTs, passwords, and public WAN IPs.
- **Preserves private RFC 1918 IP addresses (`10.x`, `172.16-31.x`, `192.168.x`)** and Kubernetes pod DNS hostnames to ensure infrastructure agents can trace service failures.

### 2. PostgreSQL Serverless Checkpointer
- Uses `AsyncPostgresSaver` with Neon/Supabase to store conversational checkpoints, ensuring stateless instances can scale-to-zero without losing investigation state.

### 3. FinOps & BYOK Token Guardrails
- 5-layer shield preventing Denial of Wallet (DoW) attacks on open source public deployments.
