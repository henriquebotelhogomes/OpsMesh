import React from 'react';
import {
  Flame,
  Database,
  ShoppingCart,
  CreditCard,
  Cpu,
  Sparkles,
  RefreshCw,
  Info,
  Zap,
} from 'lucide-react';
import { ChaosScenario } from '../types';

interface ChaosBarProps {
  scenarios: ChaosScenario[];
  selectedScenarioId: string;
  isSimulating: boolean;
  replayMode: boolean;
  onSelectScenario: (scenarioId: string) => void;
  onToggleReplayMode: (enabled: boolean) => void;
  onTriggerCrisis: () => void;
}

export const ChaosBar: React.FC<ChaosBarProps> = ({
  scenarios,
  selectedScenarioId,
  isSimulating,
  replayMode,
  onSelectScenario,
  onToggleReplayMode,
  onTriggerCrisis,
}) => {
  const getIcon = (id: string) => {
    switch (id) {
      case 'postgres-pool':
        return <Database className="w-4 h-4 text-brand-steel" />;
      case 'checkout-timeout':
        return <ShoppingCart className="w-4 h-4 text-brand-crimson" />;
      case 'payment-latency':
        return <CreditCard className="w-4 h-4 text-brand-amber" />;
      case 'model-drift-oom':
        return <Cpu className="w-4 h-4 text-brand-gold" />;
      default:
        return <Flame className="w-4 h-4 text-brand-gold" />;
    }
  };

  const getScenarioSubtitle = (id: string) => {
    switch (id) {
      case 'postgres-pool':
        return 'Saturação de Pool (P0)';
      case 'checkout-timeout':
        return 'Cascata de 504 no Checkout (P0)';
      case 'payment-latency':
        return 'Latência no Gateway (P1)';
      case 'model-drift-oom':
        return 'Vazamento OOMKilled K8s (P1)';
      default:
        return 'Incidente';
    }
  };

  return (
    <div className="glass-panel rounded-xl p-5 mb-6 shadow-card-depth space-y-4">
      {/* Top Header & Mode Toggle */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-brand-bronze/20 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <Flame className="w-5 h-5 text-brand-amber animate-pulse" />
            <h2 className="text-sm font-bold text-brand-ivory uppercase tracking-wider font-mono">
              Chaos Studio — Injetor de Incidentes & Falhas em Produção
            </h2>
          </div>
          <p className="text-xs text-sand-muted mt-0.5">
            Selecione uma falha canônica para testar como os agentes de IA diagnosticam e formulam a mitigação.
          </p>
        </div>

        {/* Replay vs Live Toggle with Clear Explanations */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2">
          <span className="text-[11px] text-sand-muted font-mono">Modo de Execução:</span>
          <div className="flex items-center bg-sand-terminal rounded-lg p-1 border border-brand-bronze/35">
            <button
              onClick={() => onToggleReplayMode(true)}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                replayMode
                  ? 'bg-brand-bronze/40 text-brand-gold font-bold shadow-glow-gold'
                  : 'text-sand-muted hover:text-sand-text'
              }`}
              title="Modo Demonstração: reproduz telemetria real em cache a custo zero ($0)."
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Zero-Token Replay ($0)</span>
            </button>
            <button
              onClick={() => onToggleReplayMode(false)}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                !replayMode
                  ? 'bg-brand-bronze/40 text-brand-ivory font-bold shadow-glow-bronze'
                  : 'text-sand-muted hover:text-sand-text'
              }`}
              title="Modo Real: invoca chamadas de LLM (OpenAI/DeepSeek) e executa o LangGraph ao vivo."
            >
              <Zap className="w-3.5 h-3.5 text-brand-gold" />
              <span>Live Agent Workflow</span>
            </button>
          </div>
        </div>
      </div>

      {/* Explanatory Help Callout about current active mode */}
      <div className={`p-3 rounded-lg border text-xs flex items-start space-x-2.5 ${
        replayMode
          ? 'bg-sand-terminal/80 border-brand-gold/30 text-sand-text'
          : 'bg-sand-terminal/80 border-brand-amber/30 text-sand-text'
      }`}>
        <Info className="w-4 h-4 text-brand-gold flex-shrink-0 mt-0.5" />
        <div className="text-[11px] leading-relaxed">
          {replayMode ? (
            <span>
              <b className="text-brand-gold font-mono">Modo Zero-Token Replay ($0) Ativo:</b> Este modo reproduz traces e dados de telemetria reais do repositório acadêmico <b>LogHub</b> em cache. Permite que você teste o fluxo de ponta a ponta (diagnóstico, diffs e aprovação no portão HITL) <b>sem gastar créditos de API</b>. Ideal para demonstrações de portfólio.
            </span>
          ) : (
            <span>
              <b className="text-brand-ivory font-mono">Modo Live Agent Workflow Ativo:</b> O sistema executará o grafo do <b>LangGraph em tempo real</b>, realizando chamadas aos modelos de linguagem configurados (DeepSeek/OpenAI/Gemini) e consumindo tokens da sua cota.
            </span>
          )}
        </div>
      </div>

      {/* Scenario Buttons Grid & Trigger CTA */}
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-3 pt-1">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 flex-1">
          {scenarios.map((sc) => {
            const isSelected = sc.id === selectedScenarioId;
            const isP0 = sc.severity === 'P0_CRITICAL';
            return (
              <button
                key={sc.id}
                onClick={() => onSelectScenario(sc.id)}
                className={`p-2.5 rounded-lg text-left border transition-all flex flex-col justify-between ${
                  isSelected
                    ? 'bg-sand-elevated border-brand-gold text-brand-ivory shadow-glow-bronze'
                    : 'bg-sand-terminal/80 border-brand-bronze/25 text-sand-muted hover:border-brand-bronze/50 hover:text-sand-text'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center space-x-2">
                    {getIcon(sc.id)}
                    <span className="font-mono text-xs font-bold truncate text-brand-ivory">
                      {sc.id}
                    </span>
                  </div>
                  <span
                    className={`text-[9px] px-1.5 py-0.2 rounded font-mono font-bold ${
                      isP0
                        ? 'bg-brand-crimson/20 text-brand-crimson border border-brand-crimson/30'
                        : 'bg-brand-amber/20 text-brand-amber border border-brand-amber/30'
                    }`}
                  >
                    {isP0 ? 'P0' : 'P1'}
                  </span>
                </div>
                <span className="text-[11px] text-sand-muted truncate block">
                  {getScenarioSubtitle(sc.id)}
                </span>
              </button>
            );
          })}
        </div>

        {/* Trigger Button */}
        <button
          onClick={onTriggerCrisis}
          disabled={isSimulating}
          className="lg:w-48 px-5 py-3 rounded-lg bg-brand-crimson hover:bg-brand-crimson/90 disabled:opacity-50 text-brand-ivory text-xs font-extrabold font-mono tracking-wider shadow-glow-crimson transition-all flex items-center justify-center space-x-2"
        >
          {isSimulating ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Simulando...</span>
            </>
          ) : (
            <>
              <Flame className="w-4 h-4" />
              <span>Injetar Crise</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
