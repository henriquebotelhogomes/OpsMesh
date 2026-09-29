import React, { useState } from 'react';
import {
  ShieldAlert,
  CheckCircle2,
  XCircle,
  Copy,
  Check,
  RotateCcw,
  Terminal,
  UserCheck,
  Zap,
  GitPullRequest,
  GitBranch,
  ExternalLink,
} from 'lucide-react';
import { RemediationPlan } from '../types';

interface HITLHeroCardProps {
  incidentId: string;
  rootCauseSummary: string | null | undefined;
  remediationPlan: RemediationPlan | null | undefined;
  isResuming: boolean;
  onApprove: (notes: string) => void;
  onReject: (notes: string) => void;
}

export const HITLHeroCard: React.FC<HITLHeroCardProps> = ({
  incidentId,
  rootCauseSummary,
  remediationPlan,
  isResuming,
  onApprove,
  onReject,
}) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [operatorNotes, setOperatorNotes] = useState('');

  if (!remediationPlan) return null;

  const handleCopyCommand = (cmd: string, idx: number) => {
    navigator.clipboard.writeText(cmd);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const renderDiffLines = (diff: string) => {
    return diff.split('\n').map((line, idx) => {
      if (line.startsWith('+')) {
        return (
          <div key={idx} className="diff-line-add px-3 py-0.5 font-mono text-xs">
            {line}
          </div>
        );
      } else if (line.startsWith('-')) {
        return (
          <div key={idx} className="diff-line-del px-3 py-0.5 font-mono text-xs">
            {line}
          </div>
        );
      }
      return (
        <div key={idx} className="px-3 py-0.5 font-mono text-xs text-sand-muted opacity-80">
          {line}
        </div>
      );
    });
  };

  return (
    <div className="glass-panel-elevated rounded-xl p-6 mb-8 border border-brand-gold/60 shadow-glow-gold relative overflow-hidden">
      {/* Decorative Accent Strip */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-brand-amber via-brand-gold to-brand-bronzeLight"></div>

      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6 pb-4 border-b border-brand-bronze/30">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-lg bg-sand-terminal border border-brand-gold/50 shadow-glow-gold animate-pulse-hitl">
            <ShieldAlert className="w-6 h-6 text-brand-gold" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-brand-ivory font-mono tracking-tight">
                Portão de Segurança Human-in-the-Loop (HITL)
              </h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-brand-crimson/20 text-brand-crimson border border-brand-crimson/40 uppercase">
                {remediationPlan.risk_level} RISK
              </span>
            </div>
            <p className="text-xs text-brand-gold/90 mt-0.5">
              Ação de mutação bloqueada no checkpoint do LangGraph. Aguardando assinatura técnica de SRE.
            </p>
          </div>
        </div>

        <div className="text-right">
          <span className="text-[11px] text-sand-muted block font-mono">ID do Incidente:</span>
          <span className="text-xs font-bold text-brand-ivory font-mono bg-sand-terminal px-2 py-1 rounded border border-brand-bronze/30">
            {incidentId}
          </span>
        </div>
      </div>

      {/* 1. Diagnóstico da Causa Raiz */}
      <div className="mb-5 bg-sand-terminal/80 rounded-lg p-4 border border-brand-bronze/30">
        <div className="flex items-center space-x-2 mb-2">
          <div className="w-2 h-2 rounded-full bg-brand-gold"></div>
          <h4 className="text-xs font-bold text-brand-ivory uppercase tracking-wider font-mono">
            Veredito da Causa Raiz (Comandante Supervisor)
          </h4>
        </div>
        <p className="text-xs text-sand-text leading-relaxed">
          {rootCauseSummary || 'Causa raiz isolada a partir da correlação de logs e infraestrutura.'}
        </p>
      </div>

      {/* 2. NÍVEL 1: Mitigação Imediata em Runtime */}
      <div className="mb-5 bg-sand-terminal/60 rounded-lg p-4 border border-brand-amber/30">
        <div className="flex items-center justify-between mb-3 pb-2 border-b border-brand-amber/20">
          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4 text-brand-amber animate-pulse" />
            <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-brand-amber/20 text-brand-amber border border-brand-amber/40 uppercase tracking-wider font-mono">
              Nível 1: Mitigação Runtime (&lt; 5s)
            </span>
          </div>
          <span className="text-[11px] text-sand-muted font-mono">
            Ação: <b className="text-brand-gold">{remediationPlan.tier_1_runtime?.action_type || remediationPlan.action_type}</b>
          </span>
        </div>

        <div className="space-y-2">
          {(remediationPlan.tier_1_runtime?.proposed_commands || remediationPlan.proposed_commands).map((cmd, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between bg-sand-terminal rounded-lg p-3 border border-brand-bronze/30 font-mono text-xs text-brand-ivory"
            >
              <div className="flex items-center space-x-2 truncate mr-3">
                <Terminal className="w-3.5 h-3.5 text-brand-amber flex-shrink-0" />
                <code className="truncate text-brand-gold/95">{cmd}</code>
              </div>
              <button
                onClick={() => handleCopyCommand(cmd, idx)}
                className="p-1.5 rounded hover:bg-sand-surface text-sand-muted hover:text-brand-gold transition-colors flex-shrink-0"
                title="Copiar comando"
              >
                {copiedIndex === idx ? (
                  <Check className="w-4 h-4 text-brand-emerald" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 3. NÍVEL 2: GitOps Pull Request Definitivo (GitHub) */}
      {(remediationPlan.patch_diff || remediationPlan.tier_2_gitops?.patch_diff) && (
        <div className="mb-5 bg-sand-terminal/60 rounded-lg p-4 border border-brand-emerald/40 shadow-glow-emerald">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3 pb-2 border-b border-brand-emerald/20">
            <div className="flex items-center space-x-2">
              <GitPullRequest className="w-4 h-4 text-brand-emerald" />
              <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-brand-emerald/20 text-brand-emerald border border-brand-emerald/40 uppercase tracking-wider font-mono">
                Nível 2: GitOps Pull Request (Definitivo)
              </span>
            </div>

            {/* GitHub Repo & Branch Badges */}
            <div className="flex items-center space-x-2 flex-wrap text-[11px] font-mono">
              <span className="text-sand-muted flex items-center space-x-1 bg-sand-surface px-2 py-0.5 rounded border border-brand-bronze/30">
                <GitBranch className="w-3 h-3 text-brand-emerald" />
                <b className="text-brand-ivory">
                  {remediationPlan.tier_2_gitops?.pr_branch_name || 'fix/opsmesh-conn-leak-8f3a'}
                </b>
              </span>
              <a
                href={`https://github.com/${remediationPlan.tier_2_gitops?.target_repo || 'henriquebotelhogomes/chaos-lab'}`}
                target="_blank"
                rel="noreferrer"
                className="text-brand-gold hover:underline flex items-center space-x-1 bg-sand-surface px-2 py-0.5 rounded border border-brand-bronze/30"
              >
                <span>{remediationPlan.tier_2_gitops?.target_repo || 'henriquebotelhogomes/chaos-lab'}</span>
                <ExternalLink className="w-3 h-3 ml-0.5" />
              </a>
            </div>
          </div>

          {/* PR Title Banner */}
          <div className="mb-2 text-xs font-mono text-sand-text">
            <span className="text-sand-muted">Título do PR: </span>
            <b className="text-brand-ivory">
              {remediationPlan.tier_2_gitops?.pr_title || 'fix(db): expand connection pool capacity from 10 to 30'}
            </b>
          </div>

          {/* Unified Diff */}
          <div className="bg-sand-terminal rounded-lg border border-brand-bronze/30 overflow-x-auto py-2">
            {renderDiffLines(remediationPlan.tier_2_gitops?.patch_diff || remediationPlan.patch_diff || '')}
          </div>
        </div>
      )}

      {/* 4. Garantia de Rollback */}
      <div className="mb-6 bg-sand-surface rounded-lg p-3 border border-brand-bronze/25 flex items-start space-x-2.5">
        <RotateCcw className="w-4 h-4 text-brand-steel flex-shrink-0 mt-0.5" />
        <div className="text-xs">
          <span className="font-bold text-brand-steel font-mono block">Estratégia de Rollback:</span>
          <span className="text-sand-muted leading-relaxed">{remediationPlan.rollback_plan}</span>
        </div>
      </div>


      {/* 5. Ações Humanas & Assinatura */}
      <div className="pt-4 border-t border-brand-bronze/30 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="w-full sm:w-auto flex-1">
          <div className="flex items-center space-x-2">
            <UserCheck className="w-4 h-4 text-sand-muted" />
            <input
              type="text"
              placeholder="Notas do SRE (opcional, ex.: 'Aprovado via canal de crise')"
              value={operatorNotes}
              onChange={(e) => setOperatorNotes(e.target.value)}
              className="w-full bg-sand-terminal rounded-md px-3 py-1.5 text-xs text-brand-ivory border border-brand-bronze/30 focus:outline-none focus:border-brand-gold placeholder:text-sand-muted/50"
            />
          </div>
        </div>

        <div className="flex items-center space-x-3 w-full sm:w-auto justify-end">
          <button
            onClick={() => onReject(operatorNotes)}
            disabled={isResuming}
            className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-sand-terminal hover:bg-sand-elevated text-brand-crimson border border-brand-crimson/40 hover:border-brand-crimson text-xs font-bold transition-all disabled:opacity-50"
          >
            <XCircle className="w-4 h-4" />
            <span>Rejeitar Mitigação</span>
          </button>

          <button
            onClick={() => onApprove(operatorNotes)}
            disabled={isResuming}
            className="flex items-center space-x-2 px-5 py-2 rounded-lg bg-gradient-to-r from-brand-gold to-brand-bronzeLight hover:from-brand-gold/90 hover:to-brand-bronzeLight/90 text-sand-terminal text-xs font-extrabold shadow-glow-gold transition-all disabled:opacity-50"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Autorizar Execução Cirúrgica</span>
          </button>
        </div>
      </div>
    </div>
  );
};
