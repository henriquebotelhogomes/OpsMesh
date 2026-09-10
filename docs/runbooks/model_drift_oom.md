# Runbook: Vazamento de Memória e OOMKilled em Modelos ML

> **Código do SOP:** SOP-ML-004  
> **Serviço Alvo:** Recommendation Engine & Inference Workers  
> **Nível de Severidade:** P1 / P2  
> **Última Revisão:** 2026-09-09  

---

## 1. Descrição e Sintomas
Vazamento progressivo de memória nos processos de inferência (PyTorch/Transformers/ONNX) após deploy de novo modelo, levando o Kubelet a disparar OOMKilled (Exit Code 137) repetidamente nos Pods do Kubernetes.

**Sintomas Comuns nos Logs:**
- `RSS memory consumption crossed 92% of limit`
- `Out of memory: Kill process (python -m worker) score 950 or sacrifice child`
- `Container recommendation-engine in pod terminated with exitCode 137 (OOMKilled)`
- Status `CrashLoopBackOff` no Kubernetes.

---

## 2. Ações de Diagnóstico Recomendadas para o Agente
1. Inspecionar status dos Pods do deployment com `check_k8s_deployment_health`.
2. Avaliar taxa de reinício de containers e última saída de log de OOMKilled com `query_logs`.
3. Checar consumo de memória e vazamento de tensores no cluster.

---

## 3. Procedimento de Mitigação (Requer HITL)
1. **Rollback Imediato da Versão do Modelo:**
   - Executar rollback da tag da imagem Docker para a versão anterior estável (`v1.4.2`).
2. **Reinício Gradual de Pods:**
   - `kubectl rollout restart deployment recommendation-ml`
3. **Escalar Temporariamente o Limite de Memória:**
   - Se o rollback não for imediato, elevar o limit de memória de 4Gi para 8Gi no manifest K8s.
