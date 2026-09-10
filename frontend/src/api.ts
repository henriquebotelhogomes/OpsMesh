import { ChaosScenario, Incident, PostMortemReport } from './types';

const API_BASE = '/api/v1';

export async function checkHealth(): Promise<{ status: string; default_llm_provider: string }> {
  try {
    const res = await fetch('/health');
    if (!res.ok) throw new Error('Health check failed');
    return await res.json();
  } catch (err) {
    return { status: 'offline', default_llm_provider: 'offline-sandbox' };
  }
}

export async function fetchChaosScenarios(): Promise<ChaosScenario[]> {
  try {
    const res = await fetch(`${API_BASE}/chaos/scenarios`);
    if (!res.ok) throw new Error('Failed to fetch scenarios');
    return await res.json();
  } catch (err) {
    console.warn('Backend unavailable, using fallback scenarios', err);
    return [
      {
        id: 'postgres-pool',
        title: 'Saturação e Esgotamento do Pool de Conexões PostgreSQL',
        description: 'Fila de requisições travada no order-service com 98% das conexões em idle in transaction.',
        severity: 'P0_CRITICAL',
        service: 'order-service',
        expected_root_cause: 'PostgreSQL connection pool exhausted',
      },
      {
        id: 'checkout-timeout',
        title: 'Timeout em Cascata e HTTP 504 no Checkout',
        description: 'Lentidão extrema no serviço de inventário upstream causa timeout durante reserva de estoque.',
        severity: 'P0_CRITICAL',
        service: 'checkout-api',
        expected_root_cause: 'Upstream inventory-service timeout',
      },
      {
        id: 'payment-latency',
        title: 'Degradação e Latência no Gateway de Pagamentos',
        description: 'Spike de latência externa no adquirente de cartão represando a fila de webhooks.',
        severity: 'P1_HIGH',
        service: 'payment-worker',
        expected_root_cause: 'External payment gateway latency spike',
      },
      {
        id: 'model-drift-oom',
        title: 'Vazamento de Memória e Pods OOMKilled no Recommendation Engine',
        description: 'Versão canary de modelo ML vaza tensores em memória, causando CrashLoopBackOff repetido.',
        severity: 'P1_HIGH',
        service: 'recommendation-ml',
        expected_root_cause: 'Tensor memory leak in v1.5.0 canary',
      },
    ];
  }
}

export async function simulateCrisis(
  scenarioId: string,
  mode: 'replay' | 'live' = 'replay',
  model?: string
): Promise<Incident> {
  const params = new URLSearchParams({ mode });
  if (model) {
    params.set('model', model);
  }
  const res = await fetch(`${API_BASE}/chaos/simulate/${scenarioId}?${params.toString()}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Simulation error' }));
    throw new Error(err.detail || 'Simulation failed');
  }
  return await res.json();
}

export async function getIncident(incidentId: string): Promise<Incident> {
  const res = await fetch(`${API_BASE}/incidents/${incidentId}`);
  if (!res.ok) throw new Error('Failed to fetch incident status');
  return await res.json();
}

export async function resumeIncident(
  incidentId: string,
  humanApproved: boolean,
  approvedBy: string,
  operatorNotes?: string
): Promise<Incident> {
  const res = await fetch(`${API_BASE}/incidents/${incidentId}/resume`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      human_approved: humanApproved,
      approved_by: approvedBy,
      operator_notes: operatorNotes || 'Aprovação manual do operador SRE',
    }),
  });
  if (!res.ok) throw new Error('Failed to resume incident');
  return await res.json();
}

export async function getPostMortemReport(incidentId: string): Promise<PostMortemReport> {
  const res = await fetch(`${API_BASE}/incidents/${incidentId}/post-mortem?format=json`);
  if (!res.ok) throw new Error('Failed to load post-mortem report');
  return await res.json();
}

export function getPostMortemPdfUrl(incidentId: string): string {
  return `${API_BASE}/incidents/${incidentId}/post-mortem?format=pdf`;
}

export async function fetchIncidents(severity?: string, status?: string): Promise<Incident[]> {
  const params = new URLSearchParams();
  if (severity) params.append('severity', severity);
  if (status) params.append('status', status);
  const query = params.toString() ? `?${params.toString()}` : '';
  const res = await fetch(`${API_BASE}/incidents${query}`);
  if (!res.ok) throw new Error('Failed to fetch incident history');
  return await res.json();
}

