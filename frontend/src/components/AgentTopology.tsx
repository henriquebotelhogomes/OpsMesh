import React from 'react';
import {
  ShieldAlert,
  FileSearch,
  Server,
  BookOpen,
  Wrench,
  FileCheck2,
  CheckCircle2,
  Clock,
} from 'lucide-react';
import { IncidentStatus } from '../types';

interface AgentTopologyProps {
  status: IncidentStatus;
  agentResults: Record<string, any>;
  hasRemediationPlan: boolean;
}

export const AgentTopology: React.FC<AgentTopologyProps> = ({
  status,
  agentResults,
  hasRemediationPlan,
}) => {
  const isInvestigating = status === 'INVESTIGATING';
  const isAwaitingApproval = status === 'AWAITING_APPROVAL';
  const isResolved = status === 'RESOLVED';

  const agents = [
    {
      id: 'IncidentSupervisorAgent',
      name: 'SupervisorAgent',
      role: 'Comandante Staff SRE',
      description: 'Lidera a investigação, aciona especialistas e sintetiza a causa raiz (max 4 turnos).',
      icon: <ShieldAlert className="w-5 h-5 text-brand-gold" />,
      active: true,
      done: Boolean(agentResults['LogTraceAnalystAgent'] || hasRemediationPlan),
    },
    {
      id: 'LogTraceAnalystAgent',
      name: 'LogTraceAnalyst',
      role: 'Logs & Traces LogHub',
      description: 'Minera logs estruturados, calcula taxa de erro e isola o serviço de origem.',
      icon: <FileSearch className="w-5 h-5 text-brand-bronzeLight" />,
      active: isInvestigating || Boolean(agentResults['LogTraceAnalystAgent']),
      done: Boolean(agentResults['LogTraceAnalystAgent']),
    },
    {
      id: 'DatabaseInfraAgent',
      name: 'DatabaseInfra',
      role: 'Postgres, K8s & Locks',
      description: 'Inspeciona pool de banco de dados e pods OOMKilled com acesso estritamente Read-Only.',
      icon: <Server className="w-5 h-5 text-brand-steel" />,
      active: isInvestigating || Boolean(agentResults['DatabaseInfraAgent']),
      done: Boolean(agentResults['DatabaseInfraAgent']),
    },
    {
      id: 'RunbookKnowledgeAgent',
      name: 'RunbookKnowledge',
      role: 'RAG Híbrido de SOPs',
      description: 'Recupera procedimentos operacionais padrão (SOPs) em Markdown com alta precisão.',
      icon: <BookOpen className="w-5 h-5 text-brand-silver" />,
      active: isInvestigating || Boolean(agentResults['RunbookKnowledgeAgent']),
      done: Boolean(agentResults['RunbookKnowledgeAgent']),
    },
    {
      id: 'RemediationEngineerAgent',
      name: 'RemediationEngineer',
      role: 'Plano de Ação & Diff',
      description: 'Formula o patch diff e os comandos cirúrgicos de mitigação e estratégia de rollback.',
      icon: <Wrench className="w-5 h-5 text-brand-amber" />,
      active: hasRemediationPlan || isAwaitingApproval || isResolved,
      done: hasRemediationPlan,
    },
    {
      id: 'AuditPostMortemAgent',
      name: 'AuditPostMortem',
      role: 'Auditoria & PDF LGPD',
      description: 'Gera trilha auditável com Hash SHA-256 (não-repúdio) e relatório executivo em PDF.',
      icon: <FileCheck2 className="w-5 h-5 text-brand-emerald" />,
      active: isResolved,
      done: isResolved,
    },
  ];

  return (
    <div className="glass-panel rounded-xl p-5 mb-6 shadow-card-depth">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 border-b border-brand-bronze/20 pb-3 gap-2">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-brand-emerald animate-pulse"></span>
            <h3 className="text-sm font-bold text-brand-ivory uppercase tracking-wider font-mono">
              Rede de Agentes Especialistas (Topologia Hierárquica LangGraph)
            </h3>
          </div>
          <p className="text-xs text-sand-muted mt-0.5">
            Cada nó é um agente autônomo com responsabilidade e ferramentas delimitadas pelo princípio do menor privilégio.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs self-start sm:self-auto">
          <span className="text-sand-muted">Status do Grafo:</span>
          <span
            className={`px-2.5 py-1 rounded font-mono font-bold text-[11px] ${
              isAwaitingApproval
                ? 'bg-brand-gold/20 text-brand-gold border border-brand-gold/40 animate-pulse-hitl shadow-glow-gold'
                : isResolved
                ? 'bg-brand-emerald/20 text-brand-emerald border border-brand-emerald/40'
                : 'bg-brand-amber/20 text-brand-amber border border-brand-amber/40'
            }`}
          >
            {status}
          </span>
        </div>
      </div>

      {/* Grid of Agent Nodes with Responsibilities */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
        {agents.map((agent) => {
          return (
            <div
              key={agent.id}
              className={`p-3.5 rounded-lg border transition-all flex flex-col justify-between ${
                agent.done
                  ? 'bg-sand-terminal/90 border-brand-bronze/50 shadow-glow-bronze'
                  : agent.active
                  ? 'bg-sand-terminal/60 border-brand-gold/60 shadow-glow-gold animate-pulse-subtle'
                  : 'bg-sand-terminal/30 border-brand-bronze/20 opacity-60'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="p-1.5 rounded-md bg-sand-surface border border-brand-bronze/30">
                    {agent.icon}
                  </div>
                  {agent.done ? (
                    <span className="flex items-center space-x-1 text-[10px] font-bold text-brand-emerald font-mono bg-brand-emerald/10 px-1.5 py-0.5 rounded border border-brand-emerald/20">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>PRONTO</span>
                    </span>
                  ) : agent.active ? (
                    <span className="flex items-center space-x-1 text-[10px] font-bold text-brand-gold font-mono bg-brand-gold/10 px-1.5 py-0.5 rounded border border-brand-gold/20">
                      <Clock className="w-3 h-3 animate-spin" />
                      <span>AGINDO</span>
                    </span>
                  ) : (
                    <span className="text-[10px] text-sand-muted/60 font-mono">STANDBY</span>
                  )}
                </div>

                <p className="text-xs font-bold text-brand-ivory font-mono">
                  {agent.name}
                </p>
                <p className="text-[11px] text-brand-gold/90 font-medium mb-2">{agent.role}</p>
                <p className="text-[11px] text-sand-muted leading-relaxed line-clamp-3">
                  {agent.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
