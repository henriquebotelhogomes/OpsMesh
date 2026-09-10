import React, { useState } from 'react';
import {
  ShieldAlert,
  Bot,
  UserCheck,
  FileCheck,
  ChevronDown,
  ChevronUp,
  HelpCircle,
  PlayCircle,
  Layers,
  DollarSign,
  Lock,
} from 'lucide-react';

export const ExplainerBanner: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState<boolean>(true);

  return (
    <div className="glass-panel rounded-xl mb-6 border border-brand-bronze/35 shadow-card-depth overflow-hidden transition-all">
      {/* Header bar with collapse button */}
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="px-5 py-3.5 bg-sand-terminal/90 border-b border-brand-bronze/25 flex items-center justify-between cursor-pointer hover:bg-sand-terminal transition-colors"
      >
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-brand-gold/15 border border-brand-gold/40 flex items-center justify-center">
            <HelpCircle className="w-4 h-4 text-brand-gold" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-bold text-brand-ivory font-mono tracking-tight">
                Como Funciona o OpsMesh?
              </h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-brand-bronze/20 text-brand-bronzeLight border border-brand-bronze/40">
                Guia Rápido & Arquitetura
              </span>
            </div>
            <p className="text-xs text-sand-muted">
              Plataforma autônoma que investiga incidentes em segundos com segurança Human-in-the-Loop inviolável.
            </p>
          </div>
        </div>

        <button className="text-sand-muted hover:text-brand-gold transition-colors p-1">
          {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="p-5 space-y-5 bg-sand-surface/60">
          {/* Executive Purpose & Datadog/Sentry Foundation */}
          <div className="text-xs text-sand-text leading-relaxed border-b border-brand-bronze/20 pb-4 space-y-2">
            <div>
              <b className="text-brand-ivory">Fundação Indispensável (Datadog & Sentry):</b> O OpsMesh <b className="text-brand-gold">depende 100% da telemetria, APM e rastreamento de exceções do Datadog e Sentry</b> — plataformas consagradas que atuam como os <b>olhos e ouvidos</b> dos sistemas em produção. Sem eles, o OpsMesh não existiria.
            </div>
            <div>
              <b className="text-brand-gold">Onde o OpsMesh vai além?</b> O OpsMesh assume o papel de <b>cérebro e braço prescritivo</b>: ao receber o alerta dessas ferramentas, uma equipe multi-agente de IA investiga logs e infraestrutura em paralelo, consulta os manuais de crise (SOPs) via RAG Híbrido e entrega o <b>plano de mitigação cirúrgico pronto</b>, reduzindo o MTTR de horas para minutos com <b>aprovação humana obrigatória (HITL)</b>.
            </div>
          </div>

          {/* 4-Step Visual Lifecycle Pipeline */}
          <div>
            <h3 className="text-xs font-bold text-brand-ivory uppercase tracking-wider font-mono mb-3 flex items-center space-x-2">
              <Layers className="w-3.5 h-3.5 text-brand-gold" />
              <span>Ciclo de Vida de um Incidente no OpsMesh</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              {/* Step 1 */}
              <div className="bg-sand-terminal/80 p-3.5 rounded-lg border border-brand-bronze/25 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-brand-crimson/20 text-brand-crimson font-mono">
                      ETAPA 1
                    </span>
                    <ShieldAlert className="w-4 h-4 text-brand-crimson" />
                  </div>
                  <h4 className="text-xs font-bold text-brand-ivory mb-1">Ingestão (Datadog/Sentry) & Sanitização</h4>
                  <p className="text-[11px] text-sand-muted leading-relaxed">
                    O alerta é gerado pelo <b>Datadog ou Sentry</b> e recebido via Webhook. Senhas, CPFs e dados sensíveis são <b>mascarados</b>, preservando IPs RFC 1918 para diagnóstico de rede.
                  </p>
                </div>
              </div>

              {/* Step 2 */}
              <div className="bg-sand-terminal/80 p-3.5 rounded-lg border border-brand-bronze/25 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-brand-bronze/30 text-brand-gold font-mono">
                      ETAPA 2
                    </span>
                    <Bot className="w-4 h-4 text-brand-gold" />
                  </div>
                  <h4 className="text-xs font-bold text-brand-ivory mb-1">Investigação Especializada</h4>
                  <p className="text-[11px] text-sand-muted leading-relaxed">
                    O <b>Supervisor</b> comanda 3 especialistas em paralelo: correlaciona logs do LogHub, inspeciona Postgres/K8s em modo Read-Only e busca SOPs via <b>RAG Híbrido</b>.
                  </p>
                </div>
              </div>

              {/* Step 3 */}
              <div className="bg-sand-terminal/80 p-3.5 rounded-lg border border-brand-gold/40 shadow-glow-gold flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-brand-gold/20 text-brand-gold font-mono animate-pulse">
                      ETAPA 3 • HERO
                    </span>
                    <UserCheck className="w-4 h-4 text-brand-gold" />
                  </div>
                  <h4 className="text-xs font-bold text-brand-gold mb-1">Portão Human-in-the-Loop (HITL)</h4>
                  <p className="text-[11px] text-sand-text leading-relaxed">
                    <b>A IA nunca aplica mutações sozinha.</b> O plano de mitigação e o diff de código são congelados aguardando a <b>aprovação expressa do engenheiro SRE</b>.
                  </p>
                </div>
              </div>

              {/* Step 4 */}
              <div className="bg-sand-terminal/80 p-3.5 rounded-lg border border-brand-bronze/25 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-brand-emerald/20 text-brand-emerald font-mono">
                      ETAPA 4
                    </span>
                    <FileCheck className="w-4 h-4 text-brand-emerald" />
                  </div>
                  <h4 className="text-xs font-bold text-brand-ivory mb-1">Auditoria & Post-Mortem PDF</h4>
                  <p className="text-[11px] text-sand-muted leading-relaxed">
                    Após aprovação, os comandos são executados com rollback garantido. Um <b>Hash SHA-256 não-repudiável</b> e um <b>relatório PDF auditável</b> são emitidos.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Quickstart Guide for Visitors / Evaluators */}
          <div className="bg-sand-terminal/90 rounded-lg p-3.5 border border-brand-bronze/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center space-x-2.5">
              <PlayCircle className="w-4 h-4 text-brand-emerald flex-shrink-0" />
              <div>
                <span className="font-bold text-brand-ivory">Como testar esta demonstração agora:</span>
                <span className="text-sand-muted ml-1.5">
                  1. Selecione um dos 4 cenários no Chaos Studio abaixo ➔ 2. Clique em <b>"Injetar Caos"</b> ➔ 3. Veja os agentes investigarem ➔ 4. No card do <b>Portão HITL</b>, audite o diff e clique em <b>"Autorizar Execução Cirúrgica"</b>!
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-2 flex-shrink-0">
              <span className="flex items-center space-x-1 text-[11px] text-brand-gold bg-sand-surface px-2.5 py-1 rounded border border-brand-bronze/30">
                <DollarSign className="w-3 h-3 text-brand-emerald" />
                <span>Modo Replay = 100% Gratuito</span>
              </span>
              <span className="flex items-center space-x-1 text-[11px] text-brand-steel bg-sand-surface px-2.5 py-1 rounded border border-brand-bronze/30">
                <Lock className="w-3 h-3 text-brand-steel" />
                <span>Zero Mutação Acidental</span>
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
