## 🚀 OpsMesh v1.1.0 — Autonomous Incident Commander Platform

OpsMesh é uma plataforma multi-agente de nível Staff SRE projetada para orquestrar, diagnosticar e remediar incidentes em sistemas distribuídos de missão crítica, reduzindo o MTTR (Mean Time to Resolution) de horas para minutos sem abrir mão de segurança e governança.

> 🌐 **Ambiente Oficial Online (Google Cloud Run):**  
> 🔗 **Console SRE & Chaos Studio:** [https://opsmesh-197215016090.us-central1.run.app](https://opsmesh-197215016090.us-central1.run.app)  
> 📖 **Documentação Interativa de APIs (Scalar):** [https://opsmesh-197215016090.us-central1.run.app/docs](https://opsmesh-197215016090.us-central1.run.app/docs)  
> 🩺 **Health Check & Telemetria:** [https://opsmesh-197215016090.us-central1.run.app/health](https://opsmesh-197215016090.us-central1.run.app/health)

---

### 🌟 Destaques da Versão

#### 1. 🤖 Rede Multi-Agente Hierárquica (LangGraph StateGraph)
* **IncidentSupervisorAgent:** Comandante da crise que planeja a investigação cirúrgica e orquestra especialistas.
* **LogTraceAnalystAgent:** Diagnóstico de anomalias em logs estruturados e traces via Universal Tool Gateway (MCP + OpenAI Tools).
* **DatabaseInfraAgent:** Inspeção em tempo real de saturação de pools PostgreSQL/MySQL, locks ativos e saúde de pods Kubernetes.
* **RunbookKnowledgeAgent:** RAG Híbrido em 4 estágios (Qdrant vetorial + BM25 léxico + fusão Reciprocal Rank Fusion + Re-ranking).
* **RemediationEngineerAgent:** Elaboração de planos de contenção, diffs unificados de configuração e procedimentos de rollback.
* **AuditPostMortemAgent:** Linha do tempo auditável, hash criptográfico SHA-256 e geração de relatórios Post-Mortem em PDF (ReportLab).

#### 2. 🛡️ Portão Human-in-the-Loop (HITL) & Segurança Inviolável
* **Portão de Aprovação Obrigatório:** O grafo do LangGraph é pausado (`interrupt_before`) antes de qualquer comando de mutação ou remediação crítica, exigindo aprovação explícita do SRE On-Call.
* **Sanitização Cirúrgica de PII:** Mascaramento automático de IPs públicos e credenciais, preservando IPs privados RFC 1918 (10.x, 172.16-31.x, 192.168.x) para manter a rastreabilidade da topologia interna.

#### 3. 📜 Livro-Razão de Auditoria & Histórico de Incidentes
* Interface interativa no dashboard e endpoint `GET /api/v1/incidents` para auditoria detalhada de todos os erros tratados, evidências de log, telemetria de infraestrutura e downloads instantâneos do PDF Post-Mortem.

#### 4. 📚 Documentação Moderna de APIs via Scalar
* Em conformidade estrita com as diretrizes de governança, todos os endpoints REST são documentados via **Scalar** em `/docs` e `/scalar` (design moderno, client HTTP interativo embutido e snippets multilíngues).

#### 5. 💰 FinOps & Modos de Execução
* **Modo Replay Zero-Token ($0):** Permite simular e inspecionar diagnósticos e remediações pré-computados sem consumo de tokens de API.
* **Circuit Breaker FinOps:** Limites diários de custo e teto estrito de 12.000 tokens / 4 turnos por incidente para prevenir DoW (Denial of Wallet).
* **Multi-Provider:** Suporte transparente a Google Gemini Pro, OpenCode Go (DeepSeek R1/V3, Claude, GPT), LiteLLM e Ollama.

---

### 📦 Instalação Rápida

```bash
# Clonar o repositório
git clone https://github.com/henriquebotelhogomes/OpsMesh.git
cd OpsMesh

# Instalar dependências backend
pip install uv
uv pip install -e ".[dev]"

# Iniciar backend unificado com Scalar Docs e SPA
python -m uvicorn opsmesh.api.app:app --host 0.0.0.0 --port 8000 --reload
```

---

### 🐳 Imagem Docker
Disponível no GitHub Packages (GHCR):
```bash
docker pull ghcr.io/henriquebotelhogomes/opsmesh:v1.1.0
docker run -p 8000:8000 ghcr.io/henriquebotelhogomes/opsmesh:v1.1.0
```
