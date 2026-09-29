# 🚨 OpsMesh — Autonomous Incident Commander

> **Sistema Multi-Agente Autónomo de Respuesta a Incidentes Críticos y SRE**  
> Desarrollado con **LangGraph**, **Model Context Protocol (MCP)**, **OpenAI Tools (DeepSeek / GPT / Llama)**, **PostgreSQL Serverless** y **Human-in-the-Loop (HITL)**.

> 🌐 **Entorno Oficial en Producción (Google Cloud Run):**  
> 🔗 **Consola SRE y Chaos Studio:** [https://opsmesh-197215016090.us-central1.run.app](https://opsmesh-197215016090.us-central1.run.app)  
> 📖 **Documentación Interactiva de APIs (Scalar):** [https://opsmesh-197215016090.us-central1.run.app/docs](https://opsmesh-197215016090.us-central1.run.app/docs)  
> 🩺 **Chequeo de Salud y Telemetría:** [https://opsmesh-197215016090.us-central1.run.app/health](https://opsmesh-197215016090.us-central1.run.app/health)

---

## 🌟 ¿Qué es OpsMesh?

**OpsMesh** actúa como un Comandante de Incidentes (*Incident Commander*) de nivel Staff SRE para sistemas distribuidos en la nube. Cuando se disparan alertas en Datadog, Prometheus o Grafana, OpsMesh:

1. **Ingiere y Sanitiza:** Recibe la alerta y anonimiza información sensible (**LGPD / GDPR**) antes del análisis por IA.
2. **Investigación Forense en Paralelo:** Activa agentes especializados en registros (patrones en LogHub y Elastic) e infraestructura (Postgres, Redis, Kubernetes).
3. **Consulta la Base de Conocimiento:** Realiza **RAG Híbrido** sobre los manuales de emergencia (*runbooks*) de la empresa.
4. **Formula el Plan de Mitigación:** Determina la causa raíz y genera el *diff* de código/configuración necesario para detener la crisis.
5. **Aprobación Humana Obligatoria (HITL):** Las acciones críticas se pausan en el punto de control de PostgreSQL Serverless hasta la autorización explícita del ingeniero de guardia.
6. **Ejecución y Post-Mortem:** Aplica la mitigación aprobada y compila el informe post-incidente completo en PDF.

---

## 🚀 Puntos Clave de Ingeniería

* **FinOps Serverless ($0/mes ocioso):** Diseñado para **Scale-to-Zero** en Google Cloud Run y Azure Container Apps. Sin alertas activas, el costo de cómputo es estrictamente cero.
* **Universal Tool Gateway:** Compatibilidad nativa con herramientas **Anthropic MCP** y **OpenAI Function Calling (DeepSeek / GPT)**.
* **Modelos de Decisión Especializados (Jev First):** Ruteo y convergencia del Supervisor impulsados por **Jev (`typesafe/jev-latest` en OpenRouter)** con latencia sub-30ms, coste de salida $0.00 y primitivas nativas (`Choice`, `Noul`).
* **OpenRouter Gateway y Flota Free:** Acceso a la flota oficial de modelos gratuitos (`openrouter/free`, `nvidia/nemotron-3-ultra-550b-a55b:free`, `poolside/laguna-s-2.1:free`, `cohere/north-mini-code:free`) con cuotas ampliadas por saldo mantenido (> $10) y soporte BYOK (`X-OpenRouter-API-Key`).
* **Datadog Pro APM y Tracing Distribuido:** Instrumentación nativa (`ddtrace`) con propagación de contexto (`traceparent`, `x-datadog-trace-id`), conectando anomalías de Chaos Lab con los nodos de LangGraph.
* **Almacenamiento Zero-Daemon:** **LanceDB** para búsqueda vectorial híbrida en disco ($0 de infra) y **DuckDB + Parquet** para analítica instantánea de MTTR e incidentes históricos.
* **Red-Teaming Gate Automatizado (Promptfoo):** Pentesting continuo en GitHub Actions CI auditando contra inyecciones de prompt, desvío de HITL y fuga de credenciales.
* **Documentación Viva con Scalar:** Explorador interactivo moderno para probar los endpoints de la API REST en tiempo real.
* **Ecosistema Chaos Lab:** Aplicación compañera independiente (`d:\ChaosLab`) con inyección de fallos en tiempo real e instrumentación nativa con Datadog APM.
* **Inspección Quirúrgica vía GitHub API:** Lectura remota y stateless del archivo y línea exactos en la rama `main` indicados por el stack trace de Datadog.
* **Remediación en Dos Niveles:** Mitigación inmediata en runtime (< 5s) para recuperar el SLO + Apertura automática de Pull Request documentado en GitHub para la corrección definitiva de la causa raíz.
