# FinOps, Arquitectura Scale-to-Zero ($0/mes) y Protección Anti-Abuso

OpsMesh fue concebido desde el primer día con una filosofía **FinOps First**: garantizar **$0/mes de infraestructura ociosa** e **inmunidad contra ataques de Denial of Wallet (DoW)** y agotamiento de saldo de tokens al desplegarse como código abierto en la nube.

---

## 1. Principios de Scale-to-Zero Serverless

1. **Cómputo Serverless Orientado a Eventos:**
   - Plano de control stateless en contenedores en **Google Cloud Run** o **Azure Container Apps**.
   - Configuración `min_instances = 0`: sin alertas activas, no hay instancias facturando CPU/RAM ($0/mes).
2. **PostgreSQL Serverless con Auto-Suspensión:**
   - Puntos de control de LangGraph y registros de auditoría en PostgreSQL Serverless (Neon / Supabase Free Tier) con suspensión automática a los 5 minutos de inactividad.
3. **Base Vectorial Embebida / Gratuita:**
   - Qdrant en modo embebido local o Qdrant Cloud Free Tier (1GB perpetuo).

---

## 2. Blindaje en 5 Capas contra Agotamiento de Tokens (Anti-DoW)

Para ofrecer una demo pública en la web sin riesgos financieros:

1. **Protección de Borde y Anti-DDoS:** Reglas de Cloudflare Free Tier / Google Cloud Armor contra bots y raspado.
2. **Límite de Frecuencia por IP (Sliding Window):** Middleware `slowapi` con un máximo de 5 req/min y 2 incidentes completos por día por IP en la cuota pública.
3. **Traiga su Propia Clave (BYOK):** Los visitantes pueden proporcionar `X-OpenAI-API-Key` o `X-DeepSeek-API-Key` para pruebas ilimitadas a costo cero para el mantenedor.
4. **Disyuntor Diario de Costos (Daily Circuit Breaker):** Contador en PostgreSQL Serverless que salta al superar $1.00/día o 150.000 tokens/día, respondiendo con `HTTP 429`.
5. **Modo Sandbox "Replay Zero-Token":** Los 4 escenarios de crisis de Chaos Studio pueden ejecutarse con trazas grabadas de LogHub sin realizar llamadas de pago.
6. **Presupuesto de Tokens en LangGraph:** Máximo 12.000 tokens por incidente, límite de 4 iteraciones del supervisor y truncado de salidas de logs a 2.000 caracteres.
