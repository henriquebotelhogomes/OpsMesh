import React from 'react';
import { Activity, BookOpen, History, Flame } from 'lucide-react';

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
        <nav className="flex space-x-1 sm:space-x-3 overflow-x-auto py-1 scrollbar-none" aria-label="Tabs">
          {/* Tab 1: Console / Incident Command */}
          <button
            onClick={() => onChangeTab('console')}
            className={`flex items-center space-x-2 py-2.5 px-3 sm:px-4 rounded-t-lg text-xs sm:text-sm font-mono font-medium transition-all relative ${
              activeTab === 'console'
                ? 'bg-sand-surface text-brand-gold border-t-2 border-brand-gold shadow-sm'
                : 'text-sand-muted hover:text-brand-ivory hover:bg-sand-surface/40'
            }`}
          >
            <Activity className="w-4 h-4 flex-shrink-0" />
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
            className={`flex items-center space-x-2 py-2.5 px-3 sm:px-4 rounded-t-lg text-xs sm:text-sm font-mono font-medium transition-all relative ${
              activeTab === 'guide'
                ? 'bg-sand-surface text-brand-gold border-t-2 border-brand-gold shadow-sm'
                : 'text-sand-muted hover:text-brand-ivory hover:bg-sand-surface/40'
            }`}
          >
            <BookOpen className="w-4 h-4 flex-shrink-0" />
            <span>Guia & Arquitetura</span>
            <span className="hidden sm:inline-block px-1.5 py-0.2 rounded text-[10px] bg-brand-gold/15 text-brand-gold border border-brand-gold/30">
              Como Funciona
            </span>
          </button>

          {/* Tab 3: History & Audit */}
          <button
            onClick={() => onChangeTab('audit')}
            className={`flex items-center space-x-2 py-2.5 px-3 sm:px-4 rounded-t-lg text-xs sm:text-sm font-mono font-medium transition-all relative ${
              activeTab === 'audit'
                ? 'bg-sand-surface text-brand-gold border-t-2 border-brand-gold shadow-sm'
                : 'text-sand-muted hover:text-brand-ivory hover:bg-sand-surface/40'
            }`}
          >
            <History className="w-4 h-4 flex-shrink-0" />
            <span>Histórico & Auditoria</span>
            <span className="px-1.5 py-0.5 rounded-full text-[10px] font-mono bg-sand-terminal border border-brand-bronze/40 text-brand-gold">
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
          <span className="inline-flex items-center space-x-1.5">
            <Flame className="w-3.5 h-3.5 text-brand-crimson" />
            <span>Chaos Lab: <strong>Integrado</strong></span>
          </span>
        </div>
      </div>
    </div>
  );
};
