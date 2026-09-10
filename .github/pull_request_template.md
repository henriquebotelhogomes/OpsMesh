## 📋 Resumo das Alterações
<!-- Descreva de forma concisa o que este PR implementa ou corrige -->

## 🤖 Agentes e Componentes Impactados
- [ ] `IncidentSupervisorAgent` (Orquestração & Grafo LangGraph)
- [ ] `LogTraceAnalystAgent` (MCP / LogHub / Traces)
- [ ] `DatabaseInfraAgent` (Métricas de Banco & K8s)
- [ ] `RunbookKnowledgeAgent` (RAG Híbrido & Vector DB)
- [ ] `RemediationEngineerAgent` (Portão HITL & Patches)
- [ ] `AuditPostMortemAgent` (Post-Mortem & PDF)
- [ ] `API / Scalar Docs` (Endpoints FastAPI & Documentação)
- [ ] `Frontend SPA` (React + Vite Dashboard & Auditoria)

## 🛡️ Checklist de Governança & Qualidade
- [ ] `ruff check .` e `ruff format .` executados sem erros.
- [ ] `pytest` executado com 100% de aprovação.
- [ ] `npm run build` no frontend concluído com sucesso.
- [ ] Nenhuma credencial ou dado sensível exposto (Gitleaks / Sanitização de PII).
- [ ] Padrão de documentação de APIs mantido via **Scalar** (sem Swagger UI).
