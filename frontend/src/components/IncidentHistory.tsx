import React, { useState } from 'react';
import {
  History,
  Search,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Download,
  ExternalLink,
  ShieldCheck,
  Terminal,
  Activity,
  RefreshCw,
} from 'lucide-react';
import { Incident } from '../types';
import { getPostMortemPdfUrl } from '../api';

interface IncidentHistoryProps {
  incidents: Incident[];
  onSelectIncident: (incident: Incident) => void;
  onRefresh: () => void;
  isLoading?: boolean;
}

export const IncidentHistory: React.FC<IncidentHistoryProps> = ({
  incidents,
  onSelectIncident,
  onRefresh,
  isLoading = false,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'RESOLVED' | 'AWAITING_APPROVAL' | 'P0'>('ALL');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedId(prev => (prev === id ? null : id));
  };

  const filteredIncidents = incidents.filter(inc => {
    const matchesSearch =
      inc.incident_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (inc.service && inc.service.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (inc.root_cause_summary && inc.root_cause_summary.toLowerCase().includes(searchTerm.toLowerCase()));

    if (!matchesSearch) return false;

    if (statusFilter === 'RESOLVED') return inc.status === 'RESOLVED';
    if (statusFilter === 'AWAITING_APPROVAL') return inc.status === 'AWAITING_APPROVAL';
    if (statusFilter === 'P0') return inc.severity === 'P0_CRITICAL';
    return true;
  });

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'P0_CRITICAL':
        return 'bg-brand-crimson/20 text-brand-crimson border-brand-crimson/40';
      case 'P1_HIGH':
        return 'bg-brand-amber/20 text-brand-amber border-brand-amber/40';
      case 'P2_MEDIUM':
        return 'bg-brand-gold/20 text-brand-gold border-brand-gold/40';
      default:
        return 'bg-sand-elevated text-sand-muted border-brand-bronze/30';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'RESOLVED':
        return {
          label: 'RESOLVIDO',
          classes: 'bg-brand-emerald/15 text-brand-emerald border-brand-emerald/30',
          icon: CheckCircle2,
        };
      case 'AWAITING_APPROVAL':
        return {
          label: 'AGUARDANDO HITL',
          classes: 'bg-brand-amber/15 text-brand-amber border-brand-amber/30 animate-pulse',
          icon: Clock,
        };
      case 'INVESTIGATING':
        return {
          label: 'INVESTIGANDO',
          classes: 'bg-brand-steel/15 text-brand-steel border-brand-steel/30',
          icon: Activity,
        };
      default:
        return {
          label: status,
          classes: 'bg-sand-elevated text-sand-muted border-brand-bronze/30',
          icon: AlertTriangle,
        };
    }
  };

  return (
    <section className="glass-panel rounded-xl p-5 mb-8 shadow-card-depth border border-brand-bronze/30">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-brand-bronze/25 pb-4 mb-5">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-sand-terminal border border-brand-gold/30 flex items-center justify-center shadow-glow-gold">
            <History className="w-5 h-5 text-brand-gold" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold text-brand-ivory font-mono tracking-tight">
                Histórico de Incidentes & Auditoria de Erros
              </h2>
              <span className="px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-brand-gold/15 text-brand-gold border border-brand-gold/30">
                {incidents.length} registrados
              </span>
            </div>
            <p className="text-xs text-sand-muted mt-0.5">
              Rastreabilidade de todas as crises tratadas, padrões de erro diagnosticados e mitigações HITL.
            </p>
          </div>
        </div>

        {/* Refresh Action */}
        <div className="flex items-center space-x-2">
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-sand-surface border border-brand-bronze/40 text-xs text-sand-text hover:text-brand-gold hover:border-brand-gold/40 transition-all disabled:opacity-50"
            title="Recarregar histórico de incidentes"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-brand-gold' : ''}`} />
            <span>Atualizar</span>
          </button>
        </div>
      </div>

      {/* Filters & Search Toolbar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 mb-4">
        {/* Search Input */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-sand-muted absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Buscar por serviço, ID ou causa raiz..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-sand-terminal border border-brand-bronze/30 text-xs text-brand-ivory placeholder-sand-muted/60 focus:outline-none focus:border-brand-gold/60 font-mono transition-all"
          />
        </div>

        {/* Status Filter Chips */}
        <div className="flex items-center space-x-1.5 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          {(
            [
              { key: 'ALL', label: 'Todos' },
              { key: 'RESOLVED', label: 'Resolvidos' },
              { key: 'AWAITING_APPROVAL', label: 'Aguardando SRE' },
              { key: 'P0', label: 'Críticos (P0)' },
            ] as const
          ).map(f => (
            <button
              key={f.key}
              onClick={() => setStatusFilter(f.key)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all whitespace-nowrap ${
                statusFilter === f.key
                  ? 'bg-sand-elevated text-brand-gold border border-brand-bronze/60 shadow-glow-gold'
                  : 'text-sand-muted hover:text-sand-text border border-transparent'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Incident List */}
      {filteredIncidents.length === 0 ? (
        <div className="text-center py-10 bg-sand-terminal/50 rounded-lg border border-brand-bronze/20">
          <AlertTriangle className="w-8 h-8 text-brand-bronzeLight mx-auto mb-2 opacity-50" />
          <p className="text-xs text-sand-muted">Nenhum incidente encontrado para os filtros selecionados.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredIncidents.map(incident => {
            const isExpanded = expandedId === incident.incident_id;
            const statusInfo = getStatusBadge(incident.status);
            const StatusIcon = statusInfo.icon;
            const logData = incident.agent_results?.LogTraceAnalystAgent || {};
            const infraData = incident.agent_results?.DatabaseInfraAgent || {};
            const remPlan = incident.remediation_plan;

            return (
              <div
                key={incident.incident_id}
                className={`rounded-xl border transition-all duration-200 overflow-hidden ${
                  isExpanded
                    ? 'bg-sand-surface border-brand-gold/40 shadow-card-depth'
                    : 'bg-sand-surface/60 border-brand-bronze/25 hover:border-brand-bronze/50'
                }`}
              >
                {/* Main Row Bar */}
                <div
                  onClick={() => toggleExpand(incident.incident_id)}
                  className="p-4 cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-3 select-none"
                >
                  {/* Left Metadata */}
                  <div className="flex items-start sm:items-center space-x-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${getSeverityBadge(
                        incident.severity
                      )}`}
                    >
                      {incident.severity.replace('_', ' ')}
                    </span>

                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-xs font-bold text-brand-ivory hover:text-brand-gold transition-colors">
                          {incident.incident_id}
                        </span>
                        {incident.service && (
                          <span className="px-1.5 py-0.5 rounded bg-sand-terminal text-[10px] font-mono text-brand-steel border border-brand-steel/30">
                            {incident.service}
                          </span>
                        )}
                        <span
                          className={`flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-medium border ${statusInfo.classes}`}
                        >
                          <StatusIcon className="w-3 h-3" />
                          <span>{statusInfo.label}</span>
                        </span>
                      </div>

                      <p className="text-xs text-sand-muted mt-1 line-clamp-1">
                        {incident.root_cause_summary || 'Diagnóstico de causa raiz em andamento...'}
                      </p>
                    </div>
                  </div>

                  {/* Right Actions & Expand Icon */}
                  <div className="flex items-center space-x-2 self-end md:self-center" onClick={e => e.stopPropagation()}>
                    <button
                      onClick={() => onSelectIncident(incident)}
                      className="flex items-center space-x-1 px-2.5 py-1 rounded bg-sand-terminal text-brand-gold border border-brand-gold/30 hover:bg-brand-gold/15 text-[11px] font-mono font-medium transition-all"
                      title="Carregar evidências e diagnóstico deste incidente no painel central"
                    >
                      <ExternalLink className="w-3 h-3" />
                      <span>Inspecionar</span>
                    </button>

                    {incident.status === 'RESOLVED' && (
                      <a
                        href={getPostMortemPdfUrl(incident.incident_id)}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center space-x-1 px-2.5 py-1 rounded bg-sand-terminal text-brand-emerald border border-brand-emerald/30 hover:bg-brand-emerald/15 text-[11px] font-mono font-medium transition-all"
                        title="Baixar Relatório Post-Mortem em PDF"
                      >
                        <Download className="w-3 h-3" />
                        <span>PDF</span>
                      </a>
                    )}

                    <button
                      onClick={() => toggleExpand(incident.incident_id)}
                      className="p-1.5 text-sand-muted hover:text-brand-ivory transition-colors"
                      aria-label="Expandir detalhes"
                    >
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Expanded Details Accordion */}
                {isExpanded && (
                  <div className="border-t border-brand-bronze/25 bg-sand-terminal/80 p-4 space-y-4 text-xs">
                    {/* Grid: 2 Columns - Error Details & Treatment Applied */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      {/* Left: Erro & Diagnóstico Técnico */}
                      <div className="space-y-3 bg-sand-surface p-3.5 rounded-lg border border-brand-bronze/30">
                        <div className="flex items-center justify-between border-b border-brand-bronze/20 pb-2">
                          <span className="font-bold text-brand-crimson flex items-center space-x-1.5">
                            <AlertTriangle className="w-4 h-4" />
                            <span>1. Erro Detectado & Causa Raiz</span>
                          </span>
                          {incident.created_at && (
                            <span className="text-[10px] font-mono text-sand-muted">
                              Disparado: {new Date(incident.created_at).toLocaleString('pt-BR')}
                            </span>
                          )}
                        </div>

                        <div>
                          <span className="text-[11px] text-sand-muted block mb-0.5">Diagnóstico Consolidado:</span>
                          <p className="text-brand-ivory font-sans leading-relaxed">
                            {incident.root_cause_summary || 'Nenhuma síntese disponível.'}
                          </p>
                        </div>

                        {/* Log Anomalies */}
                        {logData.found_anomalies && logData.found_anomalies.length > 0 && (
                          <div>
                            <span className="text-[11px] text-sand-muted block mb-1">
                              Padrões de Erro em Logs ({logData.found_anomalies.length}):
                            </span>
                            <div className="space-y-1.5">
                              {logData.found_anomalies.map((anom: any, idx: number) => (
                                <div
                                  key={idx}
                                  className="bg-sand-terminal p-2 rounded border border-brand-crimson/25 font-mono text-[11px]"
                                >
                                  <div className="text-brand-crimson font-bold truncate">{anom.error_pattern}</div>
                                  <div className="text-sand-muted text-[10px] mt-0.5 truncate">{anom.sample_message}</div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Infra Evidence */}
                        {infraData.diagnostic_evidence && (
                          <div>
                            <span className="text-[11px] text-sand-muted block mb-0.5">Métricas de Infraestrutura:</span>
                            <p className="text-sand-text font-mono text-[11px] bg-sand-terminal p-2 rounded border border-brand-bronze/25">
                              {infraData.diagnostic_evidence}
                            </p>
                          </div>
                        )}
                      </div>

                      {/* Right: Tratamento & Remediação Aplicada */}
                      <div className="space-y-3 bg-sand-surface p-3.5 rounded-lg border border-brand-bronze/30">
                        <div className="flex items-center justify-between border-b border-brand-bronze/20 pb-2">
                          <span className="font-bold text-brand-emerald flex items-center space-x-1.5">
                            <ShieldCheck className="w-4 h-4" />
                            <span>2. Tratamento & Mitigação Aplicada</span>
                          </span>
                          {remPlan && (
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-brand-emerald/15 text-brand-emerald border border-brand-emerald/30">
                              {remPlan.action_type}
                            </span>
                          )}
                        </div>

                        {remPlan ? (
                          <>
                            <div>
                              <span className="text-[11px] text-sand-muted block mb-0.5">Racional da Correção:</span>
                              <p className="text-brand-ivory leading-relaxed">{remPlan.justification}</p>
                            </div>

                            {/* Commands executed */}
                            {remPlan.proposed_commands && remPlan.proposed_commands.length > 0 && (
                              <div>
                                <span className="text-[11px] text-sand-muted block mb-1 flex items-center space-x-1">
                                  <Terminal className="w-3.5 h-3.5 text-brand-steel" />
                                  <span>Comandos Executados em Produção:</span>
                                </span>
                                <div className="space-y-1">
                                  {remPlan.proposed_commands.map((cmd: string, idx: number) => (
                                    <div
                                      key={idx}
                                      className="bg-sand-terminal p-2 rounded border border-brand-bronze/30 font-mono text-[11px] text-brand-gold overflow-x-auto"
                                    >
                                      $ {cmd}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Rollback Plan */}
                            <div>
                              <span className="text-[11px] text-sand-muted block mb-0.5">Plano de Rollback de Contingência:</span>
                              <p className="text-sand-muted font-mono text-[11px] bg-sand-terminal p-2 rounded border border-brand-bronze/20">
                                {remPlan.rollback_plan}
                              </p>
                            </div>
                          </>
                        ) : (
                          <p className="text-sand-muted">Nenhum plano de remediação formulado para este incidente.</p>
                        )}

                        {/* HITL Signoff details */}
                        <div className="pt-2 border-t border-brand-bronze/20 flex flex-wrap items-center justify-between text-[11px] text-sand-muted">
                          <div>
                            Assinado por:{' '}
                            <b className="text-brand-gold font-mono">
                              {incident.approved_by || 'Aguardando autorização humana'}
                            </b>
                          </div>
                          {incident.approval_timestamp && (
                            <div className="font-mono text-[10px]">
                              {new Date(incident.approval_timestamp).toLocaleString('pt-BR')}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Bottom Action Footer */}
                    <div className="flex items-center justify-between pt-1">
                      <div className="text-[11px] text-sand-muted">
                        Tokens consumidos:{' '}
                        <b className="text-brand-ivory font-mono">{incident.total_tokens_consumed.toLocaleString()}</b>
                      </div>

                      <button
                        onClick={() => onSelectIncident(incident)}
                        className="px-3 py-1.5 rounded-lg bg-sand-elevated text-brand-gold border border-brand-gold/40 hover:bg-brand-gold/20 text-xs font-mono font-bold transition-all shadow-glow-gold flex items-center space-x-1.5"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        <span>Carregar Incidente no Painel Central</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
};
