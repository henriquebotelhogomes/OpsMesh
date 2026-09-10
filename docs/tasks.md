# Roadmap e Backlog de Tarefas

> Esta página apresenta a visão consolidada do backlog de engenharia. Para o checklist dinâmico de execução, consulte também o arquivo [TASK.md](file:///d:/OpsMesh/TASK.md).

---

## Fases do Projeto

```mermaid
graph TD
    F0[Fase 0: Arquitetura & Governança] --> F1[Fase 1: Setup & Dependências]
    F1 --> F2[Fase 2: Núcleo de Estado & PII]
    F2 --> F3[Fase 3: Universal Tool Gateway]
    F3 --> F4[Fase 4: Agentes Especialistas]
    F4 --> F5[Fase 5: Grafo LangGraph & Checkpoint]
    F5 --> F6[Fase 6: API FastAPI & Scalar]
    F6 --> F7[Fase 7: Chaos Studio & Testes]
    F7 --> F8[Fase 8: FinOps Scale-to-Zero]
    F8 --> F9[Fase 9: Benchmarks & Docs i18n]
```

---

## Status Resumido

- **Fase 0 (Arquitetura e Contratos):** Concluída com sucesso (PRD, Especificação Técnica, AGENTS, Pre-commit, MkDocs e Scalar definidos).
- **Fase 1 a 9:** Prontas para execução progressiva via *Vibe Coding*.
