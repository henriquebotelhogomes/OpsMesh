# 🤖 OpsMesh — Contratos e Especificação dos Agentes (AGENTS.md)

> **Guia Normativo de Engenharia Multi-Agente**  
> **Versão:** 1.1.0  
> **Framework:** LangGraph (StateGraph) + Pydantic v2  
> **Protocolos de Ferramentas:** Anthropic MCP + OpenAI Tools (DeepSeek / GPT / Llama)  
> **Idioma Primário dos Prompts:** Português (PT-BR)  

---

## 1. Topologia da Rede de Agentes

A equipe do OpsMesh opera em uma topologia **Supervisor-Workers** hierárquica e determinística:

```mermaid
graph TD
    Alert[Alerta Ingerido + PII Sanitized] --> Supervisor[IncidentSupervisorAgent\nOrquestrador e Comandante]
    
    subgraph Specialists [Agentes Especialistas em Paralelo / Sequencial]
        Supervisor -->|Delegar Diagnóstico| LogAgent[LogTraceAnalystAgent\nLogs, Traces & LogHub]
        Supervisor -->|Delegar Infraestrutura| InfraAgent[DatabaseInfraAgent\nPostgres, Redis, K8s]
        Supervisor -->|Consultar Runbooks| RAGAgent[RunbookKnowledgeAgent\nRAG Híbrido Qdrant+BM25]
    end
    
    LogAgent --> Consolidation[Nó de Consolidação de Evidências]
    InfraAgent --> Consolidation
    RAGAgent --> Consolidation
    
    Consolidation --> RemediationAgent[RemediationEngineerAgent\nPlano de Ação & Diff]
    RemediationAgent --> HITL_Gate{HITL Gate: Ação Crítica?}
    
    HITL_Gate -->|interrupt_before| HumanApproval[Aprovação Humana Obrigatória\nSRE On-Call]
    HumanApproval --> ResumeExecution[Execução Controlada\nPOST /api/v1/incidents/{id}/resume]
    ResumeExecution --> AuditAgent[AuditPostMortemAgent\nTimeline, Auditoria e Relatório PDF]
```

---

## 2. Especificação do Estado Global (`IncidentState`)

Para evitar vazamento de contexto entre turnos de investigação, suportar execuções assíncronas paralelas com *Scale-to-Zero* e controlar o orçamento de tokens contra abusos (FinOps), o estado compartilhado utiliza reducers estritos com capacidade de reset explícito e controle orçamentário.

```python
from typing import Annotated, TypedDict, Literal
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field

def reduce_agent_results(current: dict | None, update: dict | None) -> dict:
    """Reducer com suporte a merge de resultados paralelos e reset via update={}."""
    if update is None:
        return current or {}
    if update == {}:
        return {}
    return {**(current or {}), **update}

def reduce_sources(current: list | None, update: list | None) -> list:
    """Reducer para fontes consultadas com desduplicação e reset via update=[]."""
    if update is None:
        return current or []
    if update == []:
        return []
    curr = current or []
    return curr + [s for s in update if s not in curr]

class IncidentState(TypedDict):
    # Metadados e Ciclo de Vida
    incident_id: str
    severity: Literal["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW"]
    status: Literal["INVESTIGATING", "AWAITING_APPROVAL", "MITIGATING", "RESOLVED", "FAILED"]
    raw_alert_sanitized: dict
    
    # Mensagens e Evidências Reduzidas
    messages: Annotated[list[AnyMessage], add_messages]
    agent_results: Annotated[dict, reduce_agent_results]
    retrieved_sources: Annotated[list, reduce_sources]
    
    # Diagnóstico e Plano Tipados
    root_cause_summary: str | None
    remediation_plan: dict | None  # Serializado a partir de RemediationPlan
    error_message: str | None
    
    # Portão Human-in-the-Loop (HITL)
    human_approved: bool | None
    approved_by: str | None
    approval_timestamp: str | None
    
    # Guardrails FinOps & Limites de Execução
    iteration_count: int
    max_iterations: int
    token_budget_limit: int
    total_tokens_consumed: int
    is_budget_exceeded: bool
    
    # Observabilidade e Rastreabilidade (LangSmith / Langfuse)
    trace_id: str | None
    langsmith_run_id: str | None
```

---

## 3. Catálogo e Contratos dos Agentes

### 3.1 IncidentSupervisorAgent (Comandante do Incidente)
* **Papel:** Receber o alerta higienizado, planejar a investigação cirúrgica, acionar especialistas e consolidar o veredito sem exceder limites de turnos.
* **Autonomia:** Alta (Orquestração e Roteamento). **Sem acesso a ferramentas de mutação**.
* **Guardrails de Execução:** `max_iterations = 4`. Se a investigação atingir 4 turnos sem conclusão, força a convergência para remediação ou escalada humana imediata.
* **Contrato de Saída Estruturada (`SupervisorDecision`):**

```python
class InvestigationStep(BaseModel):
    agent_name: Literal["LogTraceAnalystAgent", "DatabaseInfraAgent", "RunbookKnowledgeAgent"]
    reasoning: str = Field(description="Por que este agente precisa ser acionado.")
    input_directive: str = Field(description="Diretriz cirúrgica de pesquisa para o agente (máximo 200 caracteres).")

class SupervisorDecision(BaseModel):
    incident_severity: Literal["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW"]
    is_investigation_complete: bool = Field(description="True se a causa raiz foi comprovada ou se o orçamento de turnos esgotou.")
    next_steps: list[InvestigationStep] = Field(default_factory=list, description="Lista de passos para execução paralela ou sequencial.")
    root_cause_hypothesis: str | None = Field(default=None, description="Hipótese primária da causa raiz quando identificada.")
```

* **System Prompt Base:**
```text
Você é o IncidentSupervisorAgent, o Comandante de Incidentes de nível Staff SRE do OpsMesh.
Sua missão é liderar a resolução de crises em sistemas distribuídos de missão crítica, minimizando o MTTR com segurança absoluta.

DIRETRIZES FUNDAMENTAIS:
1. Você recebe alertas onde todo dado sensível (PII, tokens, senhas) já foi mascarado por governança de privacidade. IPs privados de redes internas (10.x, 172.16-31.x, 192.168.x) foram preservados para diagnóstico de pods e VPC.
2. Analise a anomalia descrita e planeje a investigação cirúrgica acionando seus especialistas:
   - LogTraceAnalystAgent para correlações de logs, stack traces e anomalias de erros.
   - DatabaseInfraAgent para checar conexões de banco, queries lentas, locks, memória Redis e pods K8s.
   - RunbookKnowledgeAgent para recuperar os procedimentos operacionais padrão (SOPs) aplicáveis.
3. Não faça suposições sem evidências técnicas auditáveis.
4. Mantenha as diretivas de pesquisa concisas para economizar tokens.
5. Quando as evidências convergirem para uma causa raiz comprovada, marque is_investigation_complete=True.
6. Comunique-se em Português técnico, claro e conciso.
```

---

### 3.2 LogTraceAnalystAgent (Especialista em Logs e Traces)
* **Papel:** Investigar logs estruturados e não-estruturados, clusters de stack traces e datasets do LogHub via servidores MCP e tools OpenAI.
* **Guardrail de Truncamento:** Ferramentas de log truncam o retorno para no máximo 2.000 caracteres por chamada para evitar explosão de contexto e custos.
* **Ferramentas Autorizadas:**
  * `query_logs(filter_query: str, time_range: str, limit: int = 50)` [MCP / OpenAI Tool]
  * `analyze_trace(trace_id: str)` [MCP / OpenAI Tool]
* **Contrato de Saída (`LogAnalysisResult`):**

```python
class LogAnomaly(BaseModel):
    error_pattern: str
    frequency: int
    first_seen: str
    last_seen: str
    sample_message: str

class LogAnalysisResult(BaseModel):
    found_anomalies: list[LogAnomaly]
    probable_origin_service: str
    error_spike_percentage: float
    summary: str
```

---

### 3.3 DatabaseInfraAgent (Especialista em Banco de Dados e Infraestrutura)
* **Papel:** Inspecionar métricas de saturação de banco de dados (PostgreSQL/MySQL), fila de locks, conexões ativas, uso de memória em Redis e estado de pods/deployments no Kubernetes.
* **Princípio de Menor Privilégio:** Acesso estritamente de leitura (`SELECT`, `GET`, `LIST`). Proibido qualquer comando de escrita ou alteração direta nesta fase.
* **Ferramentas Autorizadas:**
  * `inspect_pg_stat_activity()` [MCP / OpenAI Tool] — Read-Only
  * `check_k8s_deployment_health(service_name: str)` [MCP / OpenAI Tool] — Read-Only
  * `inspect_redis_memory(cluster_id: str)` [MCP / OpenAI Tool] — Read-Only
* **Contrato de Saída (`InfraAnalysisResult`):**

```python
class InfraAnalysisResult(BaseModel):
    database_pool_utilization_pct: float
    active_long_running_queries: int
    pod_restart_count: int
    is_resource_exhausted: bool
    diagnostic_evidence: str
```

---

### 3.4 RunbookKnowledgeAgent (Especialista em Runbooks e RAG de Crise)
* **Papel:** Recuperar conhecimento operacional corporativo (procedimentos de emergência, políticas de failover, guias de migração) armazenados em Markdown.
* **Técnica:** RAG Híbrido em 4 estágios (Vetorial Densa com Qdrant + BM25 Léxico + Fusão RRF + Cross-Encoder Re-ranker).
* **Contrato de Saída (`RunbookRetrievalResult`):**

```python
class RunbookRecommendation(BaseModel):
    runbook_title: str
    section: str
    recommended_procedure: str
    source_file: str
    confidence_score: float

class RunbookRetrievalResult(BaseModel):
    recommendations: list[RunbookRecommendation]
    synthesis: str
```

---

### 3.5 RemediationEngineerAgent (Engenheiro de Remediação & Patches)
* **Papel:** Formular o plano de mitigação seguro, criar os diffs de configuração/scripts de correção e definir a estratégia de rollback caso a ação falhe.
* **Contrato de Saída (`RemediationPlan`):**

```python
class RemediationPlan(BaseModel):
    action_type: Literal[
        "DATABASE_CONNECTION_SCALE",
        "DATABASE_TERMINATE_BACKENDS",
        "POD_ROLLOUT_RESTART",
        "CONFIG_ROLLBACK",
        "TRAFFIC_DRAIN",
        "CIRCUIT_BREAKER_ACTIVATE",
        "SCHEMA_HOTFIX"
    ]
    is_critical_action: bool = Field(default=True, description="True se exigir portão HITL obrigatório antes da execução.")
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    proposed_commands: list[str] = Field(description="Comandos exatos a serem executados.")
    patch_diff: str | None = Field(default=None, description="Diff unificado (git patch ou yaml diff) da alteração proposta.")
    rollback_plan: str = Field(description="Procedimento exato para desfazer a ação caso o problema se agrave.")
    justification: str = Field(description="Racional técnico de por que esta ação resolve a causa raiz.")
```

---

### 3.6 AuditPostMortemAgent (Auditoria & Relatório Post-Mortem)
* **Papel:** Consolidar toda a trilha de eventos do incidente em conformidade com governança e regulação (EU AI Act, LGPD), gerando o relatório final pós-incidente estruturado e em PDF.
* **Contrato de Saída Estruturada (`PostMortemReport`):**

```python
class TimelineEvent(BaseModel):
    timestamp: str
    event_type: Literal["ALERT_INGESTED", "INVESTIGATION_STARTED", "ROOT_CAUSE_IDENTIFIED", "PLAN_PROPOSED", "HUMAN_APPROVED", "ACTION_EXECUTED", "INCIDENT_RESOLVED"]
    description: str
    actor: str  # Nome do agente ou e-mail do engenheiro aprovador

class PreventativeAction(BaseModel):
    title: str
    action_item: str
    owner_team: str
    priority: Literal["P0", "P1", "P2"]

class PostMortemReport(BaseModel):
    incident_id: str
    incident_title: str
    severity: Literal["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW"]
    total_duration_minutes: float
    estimated_cost_avoided_usd: float
    root_cause_analysis: str
    timeline: list[TimelineEvent]
    mitigation_applied: str
    rollback_instructions: str
    preventative_actions: list[PreventativeAction]
    human_signoff_by: str
    signoff_timestamp: str
    cryptographic_audit_hash: str
```

---

## 4. Guardrails e Protocolo de Segurança Operacional

1. **Princípio do Menor Privilégio (*Least Privilege*):** Agentes de diagnóstico possuem acesso estritamente de leitura (`SELECT`, `GET`, `LIST`).
2. **Portão HITL Inviolável:** A execução de `proposed_commands` no agente de remediação é bloqueada no grafo por `interrupt_before=["execute_remediation_node"]`.
3. **Audit Trail Não-Repudiável:** Cada decisão inclui ID de thread do LangGraph, checkpoint no PostgreSQL Serverless e hash criptográfico SHA-256 do plano proposto e da assinatura do engenheiro autorizador.
4. **Política de PII Cirúrgica:**
   - **IPs Públicos / WAN:** Mascarados como `[REDACTED_PUBLIC_IP]`.
   - **IPs Privados RFC 1918 (10.x, 172.16-31.x, 192.168.x) e Hostnames de Cluster K8s:** Preservados para manter a rastreabilidade da topologia de rede e diagnóstico de pods.
5. **Token Budget & Turn Guardrail:**
   - Limite por incidente: 12.000 tokens.
   - Máximo de 4 iterações do Supervisor (`max_iterations = 4`). Se esgotar, encerra a investigação e despacha síntese parcial para revisão humana.
