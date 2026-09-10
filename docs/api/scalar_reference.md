# Documentação Viva de API com Scalar

O OpsMesh adota o **Scalar** como a interface oficial de documentação viva e teste interativo de API, substituindo o Swagger UI por uma experiência moderna de padrão internacional.

---

## 🌟 O que é o Scalar?

O **Scalar** (`scalar/fastapi` / `@scalar/api-reference`) é uma ferramenta de referência de API construída para desenvolvedores modernos, com:
- Design limpo e responsivo inspirado em plataformas como Stripe e Vercel.
- Cliente de teste de requisições interativo embutido (eliminando a necessidade de abrir o Postman ou Insomnia).
- Gerador automático de código de chamada em Python, cURL, JavaScript, Go e PHP.
- Modo claro e escuro sincronizado.

---

## 🚀 Como Acessar a Documentação no OpsMesh

Quando a API FastAPI do OpsMesh estiver em execução:

* **Endpoint Oficial do Scalar (Produção Online):**
  [https://opsmesh-197215016090.us-central1.run.app/docs](https://opsmesh-197215016090.us-central1.run.app/docs)
* **Endpoint Local de Desenvolvimento:**
  `http://localhost:8000/docs` ou `http://localhost:8000/scalar`
* **Especificação OpenAPI JSON (Produção):**
  [https://opsmesh-197215016090.us-central1.run.app/openapi.json](https://opsmesh-197215016090.us-central1.run.app/openapi.json)

---

## 📡 Principais Endpoints Expostos

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `POST` | `/api/v1/incidents/webhook` | Recebimento de alertas de monitoramento (Datadog, Prometheus, Grafana) |
| `GET` | `/api/v1/incidents/{incident_id}` | Consulta do status, evidências e plano de ação do incidente |
| `POST` | `/api/v1/incidents/{incident_id}/resume` | **HITL:** Retomada da execução do LangGraph após aprovação humana |
| `GET` | `/api/v1/incidents/{incident_id}/post-mortem` | Download do relatório pós-incidente em Markdown ou PDF |
| `GET` | `/health` | Checagem de integridade e prontidão para Scale-to-Zero |
