import React from 'react';
import { Shield, BookOpen, Activity, Cpu, ChevronDown } from 'lucide-react';
import { OPENCODE_GO_MODELS } from '../models';

interface HeaderProps {
  tokensConsumed: number;
  isBudgetExceeded: boolean;
  selectedModel: string;
  onSelectModel: (modelId: string) => void;
  historyCount?: number;
  onScrollToHistory?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  tokensConsumed,
  isBudgetExceeded,
  selectedModel,
  onSelectModel,
  historyCount = 0,
  onScrollToHistory,
}) => {
  return (
    <header className="border-b border-brand-bronze/25 bg-sand-surface/95 backdrop-blur-md sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-2.5 md:py-0 md:h-16 flex flex-col md:flex-row md:items-center md:justify-between gap-2 md:gap-4">
        {/* Row 1 on Mobile / Left Side on Desktop */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5 sm:space-x-3 min-w-0">
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-lg bg-sand-terminal border border-brand-gold/40 flex items-center justify-center shadow-glow-gold flex-shrink-0">
              <Shield className="w-5 h-5 sm:w-6 sm:h-6 text-brand-gold" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center space-x-2">
                <h1 className="text-lg sm:text-xl font-bold text-brand-ivory tracking-tight font-mono">
                  OpsMesh
                </h1>
                <span className="px-1.5 sm:px-2 py-0.5 rounded text-[9px] sm:text-[10px] font-semibold bg-brand-gold/15 text-brand-gold border border-brand-gold/30">
                  v1.1.0
                </span>
              </div>
              <p className="text-[10px] sm:text-xs text-sand-muted truncate">
                Autonomous Incident Commander Multi-Agent Platform
              </p>
            </div>
          </div>

          {/* Quick Action Links for Mobile (Auditoria & Docs) */}
          <div className="flex items-center space-x-1.5 md:hidden flex-shrink-0 ml-2">
            {onScrollToHistory && (
              <button
                onClick={onScrollToHistory}
                className="px-2 py-1 rounded bg-sand-terminal/90 border border-brand-gold/30 text-[10px] text-brand-gold font-mono active:scale-95 transition-transform"
                title="Auditoria de Erros e Incidentes"
              >
                Audit ({historyCount})
              </button>
            )}
            <a
              href="/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="p-1.5 rounded bg-brand-bronze/20 text-brand-gold border border-brand-bronze/40 active:scale-95 transition-transform"
              title="Documentação de APIs (Scalar)"
            >
              <BookOpen className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>

        {/* Row 2 on Mobile / Right Side on Desktop: Model Selector & FinOps Telemetry */}
        <div className="flex items-center justify-between md:justify-end gap-2 sm:gap-3 w-full md:w-auto">
          {/* Dynamic OpenCode Go Model Selector */}
          <div className="relative flex items-center flex-1 sm:flex-none min-w-0 max-w-full sm:max-w-xs">
            <div className="absolute left-2.5 pointer-events-none text-brand-gold flex items-center">
              <Cpu className="w-3.5 h-3.5" />
            </div>
            <select
              value={selectedModel}
              onChange={(e) => onSelectModel(e.target.value)}
              className="w-full sm:w-auto appearance-none bg-sand-terminal/95 hover:bg-sand-terminal text-brand-ivory text-[11px] sm:text-xs font-mono font-medium pl-7 sm:pl-8 pr-7 py-1.5 rounded-md border border-brand-gold/40 hover:border-brand-gold focus:outline-none focus:ring-1 focus:ring-brand-gold shadow-sm cursor-pointer transition-all truncate"
              title="Selecione o modelo ativo do OpenCode Go"
            >
              {OPENCODE_GO_MODELS.map((m) => (
                <option key={m.id} value={m.id} className="bg-sand-terminal text-brand-ivory font-normal">
                  {m.name}
                </option>
              ))}
            </select>
            <div className="absolute right-2 pointer-events-none text-sand-muted">
              <ChevronDown className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
            </div>
          </div>

          {/* Token & FinOps Circuit Breaker Monitor */}
          <div
            className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-md bg-sand-terminal/80 border border-brand-bronze/30 text-[11px] sm:text-xs flex-shrink-0"
            title="Consumo de Tokens FinOps e Disjuntor de Segurança"
          >
            <Activity className={`w-3 h-3 sm:w-3.5 sm:h-3.5 ${isBudgetExceeded ? 'text-brand-crimson animate-pulse' : 'text-brand-emerald'}`} />
            <span className="text-sand-muted hidden sm:inline">FinOps:</span>
            <span className="text-brand-gold font-mono font-medium">
              {tokensConsumed.toLocaleString()} / 12k
            </span>
          </div>

          {/* History Jump Button (Desktop) */}
          {onScrollToHistory && (
            <button
              onClick={onScrollToHistory}
              className="hidden md:flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-sand-terminal/90 hover:bg-sand-elevated border border-brand-gold/30 text-xs text-brand-gold hover:text-brand-ivory transition-all font-mono shadow-sm"
              title="Rolar para a tabela de histórico de incidentes"
            >
              <span>Auditoria ({historyCount})</span>
            </button>
          )}

          {/* Scalar Documentation Link (Desktop) */}
          <a
            href="/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden md:flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-brand-bronze/20 hover:bg-brand-bronze/35 text-brand-gold hover:text-brand-ivory border border-brand-bronze/40 transition-all text-xs font-medium shadow-sm"
            title="Abrir documentação interativa de endpoints no Scalar"
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Scalar Docs</span>
          </a>
        </div>
      </div>
    </header>
  );
};
