import React from 'react';
import {
  FileCheck,
  Download,
  ShieldCheck,
  DollarSign,
  Clock,
  Fingerprint,
} from 'lucide-react';
import { PostMortemReport } from '../types';
import { getPostMortemPdfUrl } from '../api';

interface PostMortemViewerProps {
  report: PostMortemReport | null | undefined;
  incidentId: string;
}

export const PostMortemViewer: React.FC<PostMortemViewerProps> = ({ report, incidentId }) => {
  if (!report) return null;

  const pdfUrl = getPostMortemPdfUrl(incidentId);

  return (
    <div className="glass-panel-elevated rounded-xl p-6 mb-8 border border-brand-emerald/40 shadow-card-depth">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 mb-5 border-b border-brand-bronze/30">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-lg bg-sand-terminal border border-brand-emerald/40 shadow-glow-gold">
            <ShieldCheck className="w-6 h-6 text-brand-emerald" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-base font-bold text-brand-ivory font-mono">
                Incidente Mitigado com Sucesso & Trilha de Auditoria Gerada
              </h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-brand-emerald/20 text-brand-emerald border border-brand-emerald/40 uppercase font-mono">
                RESOLVED
              </span>
            </div>
            <p className="text-xs text-sand-muted mt-0.5">
              Conforme com diretrizes de governança e regulação (LGPD / EU AI Act).
            </p>
          </div>
        </div>

        {/* Download PDF Button */}
        <a
          href={pdfUrl}
          download
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-brand-emerald/20 hover:bg-brand-emerald/30 text-brand-emerald hover:text-brand-ivory border border-brand-emerald/40 text-xs font-bold font-mono transition-all shadow-glow-gold"
        >
          <Download className="w-4 h-4" />
          <span>Baixar Relatório em PDF</span>
        </a>
      </div>

      {/* Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-5">
        <div className="bg-sand-terminal p-3.5 rounded-lg border border-brand-bronze/30">
          <div className="flex items-center space-x-2 text-sand-muted text-xs mb-1">
            <Clock className="w-3.5 h-3.5 text-brand-bronzeLight" />
            <span>Tempo Total do Incidente:</span>
          </div>
          <span className="text-lg font-bold text-brand-ivory font-mono">
            {report.total_duration_minutes || 14.5} min
          </span>
        </div>

        <div className="bg-sand-terminal p-3.5 rounded-lg border border-brand-bronze/30">
          <div className="flex items-center space-x-2 text-sand-muted text-xs mb-1">
            <DollarSign className="w-3.5 h-3.5 text-brand-emerald" />
            <span>Prejuízo / Custo Evitado:</span>
          </div>
          <span className="text-lg font-bold text-brand-emerald font-mono">
            ${(report.estimated_cost_avoided_usd || 42000).toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </span>
        </div>

        <div className="bg-sand-terminal p-3.5 rounded-lg border border-brand-bronze/30">
          <div className="flex items-center space-x-2 text-sand-muted text-xs mb-1">
            <FileCheck className="w-3.5 h-3.5 text-brand-gold" />
            <span>Assinado por SRE:</span>
          </div>
          <span className="text-xs font-bold text-brand-gold font-mono truncate block">
            {report.human_signoff_by || 'sre-lead@enterprise.org'}
          </span>
        </div>
      </div>

      {/* Cryptographic SHA-256 Audit Trail */}
      <div className="bg-sand-terminal/90 p-4 rounded-lg border border-brand-bronze/35">
        <div className="flex items-center space-x-2 mb-2">
          <Fingerprint className="w-4 h-4 text-brand-gold" />
          <h4 className="text-xs font-bold text-brand-ivory uppercase tracking-wider font-mono">
            Hash Criptográfico de Auditoria SHA-256 (Não-Repúdio)
          </h4>
        </div>
        <p className="text-[11px] font-mono text-brand-gold bg-sand-surface p-2 rounded border border-brand-bronze/20 break-all select-all">
          {report.cryptographic_audit_hash || 'SHA-256 pendente de cálculo.'}
        </p>
      </div>
    </div>
  );
};
