export type IncidentSeverity = 'P0_CRITICAL' | 'P1_HIGH' | 'P2_MEDIUM' | 'P3_LOW';

export type IncidentStatus = 
  | 'INVESTIGATING'
  | 'AWAITING_APPROVAL'
  | 'MITIGATING'
  | 'RESOLVED'
  | 'FAILED';

export interface RemediationPlan {
  action_type: string;
  is_critical_action: boolean;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  proposed_commands: string[];
  patch_diff?: string | null;
  rollback_plan: string;
  justification: string;
}

export interface TimelineEvent {
  timestamp: string;
  event_type: string;
  description: string;
  actor: string;
}

export interface PostMortemReport {
  incident_id: string;
  incident_title: string;
  severity: IncidentSeverity;
  total_duration_minutes: number;
  estimated_cost_avoided_usd: number;
  root_cause_analysis: string;
  timeline: TimelineEvent[];
  mitigation_applied: string;
  rollback_instructions: string;
  human_signoff_by: string;
  signoff_timestamp: string;
  cryptographic_audit_hash: string;
}

export interface Incident {
  incident_id: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  service?: string;
  created_at?: string;
  message?: string;
  root_cause_summary?: string | null;
  remediation_plan?: RemediationPlan | null;
  retrieved_sources: string[];
  total_tokens_consumed: number;
  is_budget_exceeded: boolean;
  agent_results: Record<string, any>;
  human_approved?: boolean | null;
  approved_by?: string | null;
  approval_timestamp?: string | null;
}

export interface ChaosScenario {
  id: string;
  title: string;
  description: string;
  severity: string;
  service: string;
  expected_root_cause: string;
}
