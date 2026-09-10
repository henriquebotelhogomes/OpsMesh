# Especificação dos Agentes & Contratos Pydantic

> Esta página resume os papéis dos agentes no OpsMesh. Para os contratos completos e schemas de código, consulte o arquivo [AGENTS.md](file:///d:/OpsMesh/AGENTS.md).

---

## Papéis dos Agentes no LangGraph

### 1. IncidentSupervisorAgent
- **Responsabilidade:** Comandante do Incidente.
- **Saída Estruturada:** `SupervisorDecision` (Pydantic v2).
- **Guardrails:** Teto de 4 iterações (`max_iterations = 4`) e orçamento de até 12.000 tokens por incidente.
- **Ações:** Roteamento condicional de nós, determinação da gravidade (`P0` a `P3`) e encerramento da fase de investigação.

### 2. LogTraceAnalystAgent
- **Responsabilidade:** Especialista em logs e correlação forense.
- **Ferramentas:** Consultas a Elasticsearch, Loki e amostras reais do LogHub via MCP ou OpenAI Tools.
- **Guardrail de Truncamento:** Máximo de 2.000 caracteres por chamada de ferramenta de log.
- **Saída:** `LogAnalysisResult` com identificação do serviço causador e anomalias agrupadas.

### 3. DatabaseInfraAgent
- **Responsabilidade:** Especialista em infraestrutura e persistência.
- **Ferramentas:** Inspeção de conexões ativas (`pg_stat_activity`), memória Redis e pods Kubernetes em modo Read-Only.
- **Saída:** `InfraAnalysisResult` indicando saturação de recursos e queries travadas.

### 4. RunbookKnowledgeAgent
- **Responsabilidade:** Recuperador de manuais operacionais e procedimentos padrão (SOPs).
- **Método:** RAG Híbrido em 4 estágios (Vetorial denso + BM25 esparso + Fusão RRF + Re-ranking).
- **Saída:** `RunbookRetrievalResult` com recomendações e links para os arquivos fonte.

### 5. RemediationEngineerAgent
- **Responsabilidade:** Formulação de patches de mitigação e estratégia de rollback.
- **Controle:** Marcador `is_critical_action=True` para acionar o portão HITL no LangGraph.
- **Saída:** `RemediationPlan` tipado com diffs unificados e comandos de rollback.

### 6. AuditPostMortemAgent
- **Responsabilidade:** Governança, auditoria regulatória (EU AI Act) e post-mortem.
- **Saída:** `PostMortemReport` estruturado e exportação para PDF auditável com hash SHA-256 e timeline completa.
