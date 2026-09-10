import React from 'react';
import { Shield, BookOpen, Activity, Zap } from 'lucide-react';

interface HeaderProps {
  tokensConsumed: number;
  isBudgetExceeded: boolean;
  activeProvider: string;
  historyCount?: number;
  onScrollToHistory?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  tokensConsumed,
  isBudgetExceeded,
  activeProvider,
  historyCount = 0,
  onScrollToHistory,
}) => {
  return (
    <header className="border-b border-brand-bronze/25 bg-sand-surface/90 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo & Brand Title */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-sand-terminal border border-brand-gold/40 flex items-center justify-center shadow-glow-gold">
            <Shield className="w-6 h-6 text-brand-gold" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold text-brand-ivory tracking-tight font-mono">
                OpsMesh
              </h1>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-brand-gold/15 text-brand-gold border border-brand-gold/30">
                v1.1.0
              </span>
            </div>
            <p className="text-xs text-sand-muted">
              Autonomous Incident Commander Multi-Agent Platform
            </p>
          </div>
        </div>

        {/* FinOps Shield & Telemetry Status */}
        <div className="hidden md:flex items-center space-x-3">
          {/* Provider Badge */}
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-sand-terminal/80 border border-brand-bronze/30 text-xs">
            <Zap className="w-3.5 h-3.5 text-brand-bronzeLight" />
            <span className="text-sand-muted">Engine:</span>
            <span className="text-brand-ivory font-mono uppercase text-[11px] font-semibold">
              {activeProvider}
            </span>
          </div>

          {/* Token & FinOps Circuit Breaker Monitor */}
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-sand-terminal/80 border border-brand-bronze/30 text-xs">
            <Activity className={`w-3.5 h-3.5 ${isBudgetExceeded ? 'text-brand-crimson animate-pulse' : 'text-brand-emerald'}`} />
            <span className="text-sand-muted">FinOps:</span>
            <span className="text-brand-gold font-mono font-medium">
              {tokensConsumed.toLocaleString()} / 12k
            </span>
          </div>

          {/* History Jump Button */}
          {onScrollToHistory && (
            <button
              onClick={onScrollToHistory}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-sand-terminal/90 hover:bg-sand-elevated border border-brand-gold/30 text-xs text-brand-gold hover:text-brand-ivory transition-all font-mono"
              title="Rolar para a tabela de histórico de incidentes"
            >
              <span>Auditoria ({historyCount})</span>
            </button>
          )}

          {/* Scalar Documentation Link (Global Standard) */}
          <a
            href="/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-brand-bronze/20 hover:bg-brand-bronze/35 text-brand-gold hover:text-brand-ivory border border-brand-bronze/40 transition-all text-xs font-medium"
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Scalar Docs</span>
          </a>
        </div>
      </div>
    </header>
  );
};
