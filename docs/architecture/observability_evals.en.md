# LLM Observability & Continuous Evaluation (LangSmith, Langfuse & Ragas)

In OpsMesh, multi-agent systems handling critical infrastructure crises cannot be a black box. Tracing every decision, monitoring costs in real time, and quantitatively verifying that remediation plans are hallucination-free is mandatory.

---

## 1. Execution Tracing: LangSmith vs Langfuse

* **LangSmith (Native):** Seamless zero-code integration with LangGraph (`LANGSMITH_TRACING=true`). Tracks the entire multi-agent tree, per-node latency, token counts, dollar costs, and captures human sign-off feedback from the HITL gate.
* **Langfuse (Open Source):** Flexible alternative for on-premise or self-hosted environments via LiteLLM callbacks.

---

## 2. Continuous Quality Gate with Ragas

OpsMesh validates diagnostic accuracy and mitigation quality using **Ragas** against the 4 canonical Chaos Studio scenarios:
1. **Faithfulness ($\ge 0.85$):** Ensures proposed mitigation diffs and commands stem strictly from retrieved logs and SOPs with zero hallucination.
2. **Answer Relevancy ($\ge 0.80$):** Validates that proposed actions surgically solve the specific root cause.
3. **Context Precision & Recall:** Verifies that the Runbook Knowledge Agent retrieves the exact emergency runbook for the crisis.

---

## 3. Interactive API Documentation: Scalar

* OpsMesh **bans traditional Swagger UI**.
* All interactive API documentation is served exclusively via **Scalar** (`scalar-fastapi`) at `/docs` and `/scalar`.
