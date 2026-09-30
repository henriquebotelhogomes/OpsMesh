import React from 'react';
import { Activity, BookOpen, History, Flame, ExternalLink } from 'lucide-react';

export type AppTab = 'console' | 'guide' | 'audit';

interface NavigationTabsProps {
  activeTab: AppTab;
  onChangeTab: (tab: AppTab) => void;
  hasActiveCrisis?: boolean;
  isAwaitingApproval?: boolean;
  auditCount?: number;
}

export const NavigationTabs: React.FC<NavigationTabsProps> = ({
  activeTab,
  onChangeTab,
  hasActiveCrisis = false,
  isAwaitingApproval = false,
  auditCount = 0,
}) => {
  return (
    <div className="border-b border-brand-bronze/25 bg-sand-terminal/80 backdrop-blur-md sticky top-16 z-40 shadow-sm">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 flex items-center justify-between">
        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-2.5 overflow-x-auto py-1.5 scrollbar-none" aria-label="Tabs">
          {/* Tab 1: Console / Incident Command */}
          <button
            onClick={() => onChangeTab('console')}
            className={`flex items-center space-x-2 py-2 px-3 sm:px-4 rounded-lg text-xs sm:text-sm font-mono transition-all duration-150 relative ${
              activeTab === 'console'
                ? 'bg-gradient-to-b from-[#3E342B] to-[#2B231C] text-white font-bold border border-brand-gold/70 shadow-md shadow-black/50 ring-1 ring-brand-gold/40'
                : 'text-sand-muted hover:text-brand-ivory hover:bg-sand-surface/60 border border-transparent font-medium'
            }`}
          >
            <Activity
              className={`w-4 h-4 flex-shrink-0 ${
                activeTab === 'console'
                  ? 'text-brand-gold drop-shadow-[0_0_8px_rgba(206,176,126,0.6)]'
                  : 'text-sand-muted'
              }`}
            />
            <span>Central de Incidentes</span>
            {isAwaitingApproval && (
              <span className="flex h-2 w-2 relative flex-shrink-0">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-gold opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-gold"></span>
              </span>
            )}
            {hasActiveCrisis && !isAwaitingApproval && (
              <span className="flex h-2 w-2 relative flex-shrink-0">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-crimson opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-crimson"></span>
              </span>
            )}
          </button>

          {/* Tab 2: Guide & Architecture */}
          <button
            onClick={() => onChangeTab('guide')}
            className={`flex items-center space-x-2 py-2 px-3 sm:px-4 rounded-lg text-xs sm:text-sm font-mono transition-all duration-150 relative ${
              activeTab === 'guide'
                ? 'bg-gradient-to-b from-[#3E342B] to-[#2B231C] text-white font-bold border border-brand-gold/70 shadow-md shadow-black/50 ring-1 ring-brand-gold/40'
                : 'text-sand-muted hover:text-brand-ivory hover:bg-sand-surface/60 border border-transparent font-medium'
            }`}
          >
            <BookOpen
              className={`w-4 h-4 flex-shrink-0 ${
                activeTab === 'guide'
                  ? 'text-brand-gold drop-shadow-[0_0_8px_rgba(206,176,126,0.6)]'
                  : 'text-sand-muted'
              }`}
            />
            <span>Guia & Arquitetura</span>
            <span
              className={`hidden sm:inline-block px-1.5 py-0.5 rounded text-[10px] font-mono transition-colors ${
                activeTab === 'guide'
                  ? 'bg-brand-gold text-sand-terminal font-bold shadow-xs'
                  : 'bg-brand-gold/15 text-brand-gold border border-brand-gold/30'
              }`}
            >
              Como Funciona
            </span>
          </button>

          {/* Tab 3: History & Audit */}
          <button
            onClick={() => onChangeTab('audit')}
            className={`flex items-center space-x-2 py-2 px-3 sm:px-4 rounded-lg text-xs sm:text-sm font-mono transition-all duration-150 relative ${
              activeTab === 'audit'
                ? 'bg-gradient-to-b from-[#3E342B] to-[#2B231C] text-white font-bold border border-brand-gold/70 shadow-md shadow-black/50 ring-1 ring-brand-gold/40'
                : 'text-sand-muted hover:text-brand-ivory hover:bg-sand-surface/60 border border-transparent font-medium'
            }`}
          >
            <History
              className={`w-4 h-4 flex-shrink-0 ${
                activeTab === 'audit'
                  ? 'text-brand-gold drop-shadow-[0_0_8px_rgba(206,176,126,0.6)]'
                  : 'text-sand-muted'
              }`}
            />
            <span>Histórico & Auditoria</span>
            <span
              className={`px-2 py-0.5 rounded-full text-[10px] font-mono transition-colors ${
                activeTab === 'audit'
                  ? 'bg-brand-gold text-sand-terminal font-bold shadow-xs'
                  : 'bg-sand-terminal border border-brand-bronze/40 text-brand-gold'
              }`}
            >
              {auditCount}
            </span>
          </button>
        </nav>

        {/* Right Status Indicator */}
        <div className="hidden lg:flex items-center space-x-3 text-xs text-sand-muted font-mono">
          <span className="inline-flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-brand-emerald"></span>
            <span>Cloud Run: <strong>Online</strong></span>
          </span>
          <span className="text-brand-bronze/40">|</span>
          <a
            href="https://chaos-lab-197215016090.us-central1.run.app"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-1.5 hover:text-brand-ivory transition-colors group cursor-pointer"
            title="Abrir Simulador de Falhas Chaos Lab em nova aba"
          >
            <Flame className="w-3.5 h-3.5 text-brand-crimson group-hover:scale-110 transition-transform" />
            <span>Chaos Lab: <strong className="text-brand-gold group-hover:underline">Integrado</strong></span>
            <ExternalLink className="w-3 h-3 text-sand-muted group-hover:text-brand-ivory" />
          </a>
        </div>
      </div>
    </div>
  );
};
