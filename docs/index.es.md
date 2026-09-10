# 🚨 OpsMesh — Autonomous Incident Commander

> **Sistema Multi-Agente Autónomo de Respuesta a Incidentes Críticos y SRE**  
> Desarrollado con **LangGraph**, **Model Context Protocol (MCP)**, **OpenAI Tools (DeepSeek / GPT / Llama)**, **PostgreSQL Serverless** y **Human-in-the-Loop (HITL)**.

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
* **Documentación Viva con Scalar:** Explorador interactivo moderno para probar los endpoints de la API REST en tiempo real.
