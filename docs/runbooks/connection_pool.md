# Runbook: Saturação e Esgotamento do Pool de Conexões (PostgreSQL)

> **Código do SOP:** SOP-DB-002  
> **Serviço Alvo:** Cluster Principal PostgreSQL / PgBouncer  
> **Nível de Severidade:** P0 / P1  
> **Última Revisão:** 2026-09-09  

---

## 1. Descrição e Sintomas
Ocorre quando o número de conexões ativas atinge o limite máximo configurado em `max_connections` no PostgreSQL ou quando o pooler intermediário (PgBouncer) esgota o pool para uma base de dados específica.

**Sintomas Comuns nos Logs:**
- `FATAL: remaining connection slots are reserved for non-replication superuser connections`
- `FATAL: sorry, too many clients already`
- `server conn crashed? (PgBouncer)`
- Picos de latência (p99 > 5000ms) nas APIs de microsserviços.

---

## 2. Ações de Diagnóstico Recomendadas para o Agente

1. **Inspecionar Conexões Ativas por Aplicação:**
   ```sql
   SELECT client_addr, usename, datname, state, count(*) 
   FROM pg_stat_activity 
   GROUP BY client_addr, usename, datname, state 
   ORDER BY count(*) DESC;
   ```
2. **Identificar Queries Travadas ou Ociosas em Transação:**
   ```sql
   SELECT pid, now() - query_start AS duration, query, state 
   FROM pg_stat_activity 
   WHERE state = 'idle in transaction' 
     AND now() - query_start > interval '60 seconds'
   ORDER BY duration DESC;
   ```

---

## 3. Procedimento de Mitigação (Requer HITL)

1. **Terminar Conexões Ociosas em Transação:**
   ```sql
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle in transaction'
     AND now() - query_start > interval '120 seconds'
     AND usename != 'postgres';
   ```
2. **Reiniciar Pods de Microsserviços com Conexões Zumbis:**
   - Efetuar `rollout restart` seguro em lotes (*rolling update*) para não indisponibilizar a aplicação.
3. **Rollback:**
   - Se o pico tiver sido disparado por um deploy recente com vazamento de conexão no pool (ex.: falta de `conn.close()` em bloco try/finally), executar rollback imediato para a versão anterior da imagem Docker.
