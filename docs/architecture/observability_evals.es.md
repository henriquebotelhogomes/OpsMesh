# Observabilidad de LLMs y Evaluación Continua (LangSmith, Langfuse y Ragas)

En OpsMesh, los sistemas multi-agente que gestionan incidentes críticos de infraestructura no pueden ser una caja negra. Es obligatorio rastrear cada decisión, calcular costos en tiempo real y validar cuantitativamente que los planes de mitigación no contengan alucinaciones.

---

## 1. Rastreo de Ejecución: LangSmith vs Langfuse

* **LangSmith (Nativo):** Integración nativa sin código con LangGraph (`LANGSMITH_TRACING=true`). Rastreabilidade completa de nodos, latencia, recuento de tokens, costos por llamada y captura del feedback humano en el portón HITL.
* **Langfuse (Código Abierto):** Alternativa flexible para despliegues locales o autoalojados via callbacks de LiteLLM.

---

## 2. Quality Gate Continuo con Ragas

OpsMesh valida la precisión del diagnóstico y la calidad de la remediación mediante **Ragas** evaluado contra los 4 escenarios de Chaos Studio:
1. **Faithfulness ($\ge 0.85$):** Garantiza que los comandos y diffs de mitigación provengan estrictamente de los logs y manuales sin alucinaciones.
2. **Answer Relevancy ($\ge 0.80$):** Valida que la acción propuesta solucione quirúrgicamente la causa raíz.
3. **Context Precision & Recall:** Comprueba que el agente de runbooks recupere el procedimiento operativo estándar exacto.

---

## 3. Documentación Interactiva de APIs: Scalar

* OpsMesh **elimina el uso del Swagger UI tradicional**.
* Toda la documentación viva de endpoints se expone exclusivamente mediante **Scalar** (`scalar-fastapi`) en `/docs` y `/scalar`.
