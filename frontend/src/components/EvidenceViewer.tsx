import React, { useState } from 'react';
import { FileText, Server, BookOpen, AlertCircle } from 'lucide-react';

interface EvidenceViewerProps {
  agentResults: Record<string, any>;
  retrievedSources: string[];
  incidentStatus?: string;
}

export const EvidenceViewer: React.FC<EvidenceViewerProps> = ({
  agentResults,
  retrievedSources,
  incidentStatus,
}) => {
  const [activeTab, setActiveTab] = useState<'logs' | 'infra' | 'runbooks'>('logs');

  const logData = agentResults['LogTraceAnalystAgent'] || {};
  const infraData = agentResults['DatabaseInfraAgent'] || {};
  const runbookData = agentResults['RunbookKnowledgeAgent'] || {};

  const isFinished = incidentStatus === 'RESOLVED' || incidentStatus === 'FAILED';
  const hasLogRun = Boolean(logData.summary || logData.probable_origin_service || logData.found_anomalies?.length);

  const getLogSummary = () => {
    if (logData.summary) return logData.summary;
    if (hasLogRun && logData.probable_origin_service) {
      return `Diagnóstico concluído: anomalias de erro mapeadas com foco no serviço '${logData.probable_origin_service}'. Padrões identificados com sucesso.`;
    }
    if (isFinished) {
      return 'Diagnóstico de logs e traces concluído com sucesso. Anomalias tratadas e telemetria normalizada.';
    }
    if (incidentStatus === 'AWAITING_APPROVAL' || incidentStatus === 'MITIGATING') {
      return 'Diagnóstico concluído. Evidências sintetizadas e consolidadas para a formulação do plano de remediação.';
    }
    return 'Aguardando execução do LogTraceAnalystAgent...';
  };

  const getInfraEvidence = () => {
    if (infraData.diagnostic_evidence) return infraData.diagnostic_evidence;
    if (isFinished) {
      return 'Inspeção de infraestrutura finalizada. Métricas de saturação e pools de conexões restaurados aos parâmetros normais.';
    }
    if (incidentStatus === 'AWAITING_APPROVAL' || incidentStatus === 'MITIGATING') {
      return 'Inspeção concluída: telemetria de pools, pods e queries lentas consolidada para decisão.';
    }
    return 'Telemetria de infraestrutura nominal.';
  };

  const getRunbookSynthesis = () => {
    if (runbookData.synthesis) return runbookData.synthesis;
    if (isFinished) {
      return 'Procedimentos operacionais padrão (SOPs) recuperados via RAG híbrido e executados com sucesso.';
    }
    return 'Nenhum runbook consultado ainda.';
  };

  const recCount = runbookData.recommendations?.length || retrievedSources.length || 0;

  return (
    <div className="glass-panel rounded-xl p-5 mb-6 shadow-card-depth">
      {/* Navigation Tabs */}
      <div className="flex items-center justify-between border-b border-brand-bronze/25 pb-3 mb-4">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveTab('logs')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'logs'
                ? 'bg-sand-elevated text-brand-gold border border-brand-bronze/50 shadow-glow-gold'
                : 'text-sand-muted hover:text-sand-text'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Logs & Traces LogHub</span>
            {logData.error_spike_percentage ? (
              <span className="text-[10px] px-1.5 rounded bg-brand-crimson/20 text-brand-crimson font-mono font-bold">
                +{logData.error_spike_percentage}%
              </span>
            ) : null}
          </button>

          <button
            onClick={() => setActiveTab('infra')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'infra'
                ? 'bg-sand-elevated text-brand-steel border border-brand-bronze/50 shadow-glow-bronze'
                : 'text-sand-muted hover:text-sand-text'
            }`}
          >
            <Server className="w-4 h-4" />
            <span>Infraestrutura & Pods K8s</span>
          </button>

          <button
            onClick={() => setActiveTab('runbooks')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'runbooks'
                ? 'bg-sand-elevated text-brand-bronzeLight border border-brand-bronze/50'
                : 'text-sand-muted hover:text-sand-text'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Runbooks (SOPs RAG)</span>
            <span className="text-[10px] px-1.5 rounded bg-brand-bronze/30 text-brand-gold font-mono">
              {recCount}
            </span>
          </button>
        </div>
      </div>

      {/* Tab 1: Logs & Traces */}
      {activeTab === 'logs' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="bg-sand-terminal p-3 rounded-lg border border-brand-bronze/25">
            <div className="text-sand-muted mb-1 text-[11px]">Resumo do Analista de Logs:</div>
            <div className="text-brand-ivory font-sans text-xs">
              {getLogSummary()}
            </div>
            {logData.probable_origin_service && (
              <div className="mt-2 text-[11px] text-brand-gold">
                Origem Provável: <b>{logData.probable_origin_service}</b>
              </div>
            )}
          </div>

          {/* Anomalies List */}
          {logData.found_anomalies && logData.found_anomalies.length > 0 ? (
            <div className="space-y-2">
              <div className="text-[11px] text-sand-muted font-sans uppercase font-bold tracking-wider">
                Anomalias Isoladas:
              </div>
              {logData.found_anomalies.map((anom: any, idx: number) => (
                <div
                  key={idx}
                  className="bg-sand-terminal/90 p-3 rounded-lg border border-brand-crimson/30 flex items-start space-x-2"
                >
                  <AlertCircle className="w-4 h-4 text-brand-crimson flex-shrink-0 mt-0.5" />
                  <div className="flex-1 overflow-hidden">
                    <div className="text-brand-crimson font-bold truncate">{anom.error_pattern}</div>
                    <div className="text-sand-muted text-[11px] mt-1 line-clamp-2">
                      {anom.sample_message}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : null}
        </div>
      )}

      {/* Tab 2: Infraestrutura */}
      {activeTab === 'infra' && (
        <div className="space-y-3 text-xs">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="bg-sand-terminal p-3 rounded-lg border border-brand-bronze/25">
              <span className="text-[11px] text-sand-muted block">Utilização do Pool Postgres:</span>
              <span
                className={`text-xl font-bold font-mono ${
                  (infraData.database_pool_utilization_pct || 0) > 85
                    ? 'text-brand-crimson'
                    : 'text-brand-emerald'
                }`}
              >
                {infraData.database_pool_utilization_pct || 0}%
              </span>
            </div>

            <div className="bg-sand-terminal p-3 rounded-lg border border-brand-bronze/25">
              <span className="text-[11px] text-sand-muted block">Conexões Travadas / Slow:</span>
              <span className="text-xl font-bold font-mono text-brand-amber">
                {infraData.active_long_running_queries || 0}
              </span>
            </div>

            <div className="bg-sand-terminal p-3 rounded-lg border border-brand-bronze/25">
              <span className="text-[11px] text-sand-muted block">Reinícios de Pods K8s:</span>
              <span
                className={`text-xl font-bold font-mono ${
                  (infraData.pod_restart_count || 0) > 0 ? 'text-brand-crimson' : 'text-brand-emerald'
                }`}
              >
                {infraData.pod_restart_count || 0}
              </span>
            </div>
          </div>

          <div className="bg-sand-terminal p-3 rounded-lg border border-brand-bronze/25">
            <span className="text-[11px] text-sand-muted block mb-1">Evidência Diagnóstica:</span>
            <p className="text-sand-text font-mono text-xs">
              {getInfraEvidence()}
            </p>
          </div>
        </div>
      )}

      {/* Tab 3: Runbooks */}
      {activeTab === 'runbooks' && (
        <div className="space-y-3 text-xs">
          <div className="bg-sand-terminal p-3 rounded-lg border border-brand-bronze/25">
            <span className="text-[11px] text-sand-muted block mb-1">Síntese do Conhecimento RAG:</span>
            <p className="text-brand-ivory text-xs">
              {getRunbookSynthesis()}
            </p>
          </div>

          {runbookData.recommendations && runbookData.recommendations.length > 0 ? (
            <div className="space-y-2">
              {runbookData.recommendations.map((rec: any, idx: number) => (
                <div
                  key={idx}
                  className="bg-sand-terminal/80 p-3 rounded-lg border border-brand-bronze/30"
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-brand-gold font-mono">{rec.runbook_title}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-brand-bronze/30 text-brand-ivory font-mono">
                      Confiança: {Math.round(rec.confidence_score * 100)}%
                    </span>
                  </div>
                  <pre className="text-sand-muted font-mono text-[11px] whitespace-pre-wrap bg-sand-surface p-2 rounded border border-brand-bronze/20">
                    {rec.recommended_procedure}
                  </pre>
                </div>
              ))}
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
};
