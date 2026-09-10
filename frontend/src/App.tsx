import React, { useEffect, useState } from 'react';
import {
  checkHealth,
  fetchChaosScenarios,
  fetchIncidents,
  getPostMortemReport,
  resumeIncident,
  simulateCrisis,
} from './api';
import { AgentTopology } from './components/AgentTopology';
import { ChaosBar } from './components/ChaosBar';
import { EvidenceViewer } from './components/EvidenceViewer';
import { ExplainerBanner } from './components/ExplainerBanner';
import { Header } from './components/Header';
import { HITLHeroCard } from './components/HITLHeroCard';
import { IncidentHistory } from './components/IncidentHistory';
import { PostMortemViewer } from './components/PostMortemViewer';
import { ChaosScenario, Incident, PostMortemReport } from './types';

export const App: React.FC = () => {
  const [scenarios, setScenarios] = useState<ChaosScenario[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>('postgres-pool');
  const [replayMode, setReplayMode] = useState<boolean>(true);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [isResuming, setIsResuming] = useState<boolean>(false);
  const [activeIncident, setActiveIncident] = useState<Incident | null>(null);
  const [postMortemReport, setPostMortemReport] = useState<PostMortemReport | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>(() => {
    return localStorage.getItem('opsmesh_selected_model') || 'deepseek-chat';
  });
  const [incidentsHistory, setIncidentsHistory] = useState<Incident[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState<boolean>(false);

  const handleSelectModel = (modelId: string) => {
    setSelectedModel(modelId);
    localStorage.setItem('opsmesh_selected_model', modelId);
  };

  const loadHistory = async () => {
    setIsHistoryLoading(true);
    try {
      const list = await fetchIncidents();
      setIncidentsHistory(list);
    } catch (e) {
      console.warn('Failed to load incident history', e);
    } finally {
      setIsHistoryLoading(false);
    }
  };

  // Load initial health, scenarios & history
  useEffect(() => {
    async function init() {
      await checkHealth();

      const scList = await fetchChaosScenarios();
      setScenarios(scList);

      await loadHistory();

      // Auto-populate with initial Replay scenario for instant demo visualization
      try {
        const initial = await simulateCrisis('postgres-pool', 'replay');
        setActiveIncident(initial);
      } catch (e) {
        console.warn('Initial simulation error', e);
      }
    }
    init();
  }, []);

  const handleTriggerCrisis = async () => {
    setIsSimulating(true);
    setPostMortemReport(null);
    try {
      const mode = replayMode ? 'replay' : 'live';
      const result = await simulateCrisis(selectedScenarioId, mode, selectedModel);
      setActiveIncident(result);
      await loadHistory();
    } catch (err: any) {
      alert(`Falha ao simular crise: ${err.message}`);
    } finally {
      setIsSimulating(false);
    }
  };

  const handleApprove = async (notes: string) => {
    if (!activeIncident) return;
    setIsResuming(true);
    try {
      const updated = await resumeIncident(
        activeIncident.incident_id,
        true,
        'sre-commander@enterprise.org',
        notes
      );
      setActiveIncident(updated);

      // Fetch post-mortem report
      const report = await getPostMortemReport(activeIncident.incident_id);
      setPostMortemReport(report);
      await loadHistory();
    } catch (err: any) {
      alert(`Erro ao aprovar mitigação: ${err.message}`);
    } finally {
      setIsResuming(false);
    }
  };

  const handleReject = async (notes: string) => {
    if (!activeIncident) return;
    setIsResuming(true);
    try {
      const updated = await resumeIncident(
        activeIncident.incident_id,
        false,
        'sre-commander@enterprise.org',
        notes
      );
      setActiveIncident(updated);
      await loadHistory();
    } catch (err: any) {
      alert(`Erro ao rejeitar mitigação: ${err.message}`);
    } finally {
      setIsResuming(false);
    }
  };

  const handleSelectIncident = async (incident: Incident) => {
    setActiveIncident(incident);
    if (incident.status === 'RESOLVED') {
      try {
        const report = await getPostMortemReport(incident.incident_id);
        setPostMortemReport(report);
      } catch (e) {
        setPostMortemReport(null);
      }
    } else {
      setPostMortemReport(null);
    }
    window.scrollTo({ top: 350, behavior: 'smooth' });
  };

  const scrollToHistory = () => {
    document.getElementById('incident-history-section')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-sand-base relative overflow-x-hidden pb-16">
      {/* Ambient Lighting Background from Portfolio_Pessoal */}
      <div className="ambient-glow"></div>

      {/* Main Content Layout */}
      <div className="relative z-10">
        <Header
          tokensConsumed={activeIncident?.total_tokens_consumed || 0}
          isBudgetExceeded={activeIncident?.is_budget_exceeded || false}
          selectedModel={selectedModel}
          onSelectModel={handleSelectModel}
          historyCount={incidentsHistory.length}
          onScrollToHistory={scrollToHistory}
        />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
          {/* Executive & Architecture Explainer Guide */}
          <ExplainerBanner />

          {/* Chaos Studio Bar */}
          <ChaosBar
            scenarios={scenarios}
            selectedScenarioId={selectedScenarioId}
            isSimulating={isSimulating}
            replayMode={replayMode}
            onSelectScenario={(id) => setSelectedScenarioId(id)}
            onToggleReplayMode={(mode) => setReplayMode(mode)}
            onTriggerCrisis={handleTriggerCrisis}
          />

          {/* Multi-Agent Network Topology */}
          <AgentTopology
            status={activeIncident?.status || 'INVESTIGATING'}
            agentResults={activeIncident?.agent_results || {}}
            hasRemediationPlan={Boolean(activeIncident?.remediation_plan)}
          />

          {/* Human-in-the-Loop (HITL) Hero Card - Prominent when Awaiting Approval */}
          {activeIncident && activeIncident.status === 'AWAITING_APPROVAL' && (
            <HITLHeroCard
              incidentId={activeIncident.incident_id}
              rootCauseSummary={activeIncident.root_cause_summary}
              remediationPlan={activeIncident.remediation_plan}
              isResuming={isResuming}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          )}

          {/* Post-Mortem & Audit Trail Card - Displayed when Resolved */}
          {activeIncident && activeIncident.status === 'RESOLVED' && (
            <PostMortemViewer
              report={postMortemReport}
              incidentId={activeIncident.incident_id}
            />
          )}

          {/* Diagnostic Evidence Viewer (Logs, Infra, Runbooks) */}
          {activeIncident && (
            <EvidenceViewer
              agentResults={activeIncident.agent_results || {}}
              retrievedSources={activeIncident.retrieved_sources || []}
              incidentStatus={activeIncident.status}
            />
          )}

          {/* Historical Incidents & Error Audit Ledger */}
          <div id="incident-history-section">
            <IncidentHistory
              incidents={incidentsHistory}
              onSelectIncident={handleSelectIncident}
              onRefresh={loadHistory}
              isLoading={isHistoryLoading}
            />
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
