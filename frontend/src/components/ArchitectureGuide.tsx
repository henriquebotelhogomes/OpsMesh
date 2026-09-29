import React from 'react';
import {
  ShieldAlert,
  Bot,
  UserCheck,
  FileCheck,
  PlayCircle,
  Layers,
  DollarSign,
  Zap,
  Server,
  BookOpen,
  ArrowRight,
  ShieldCheck,
  Cpu,
} from 'lucide-react';

interface ArchitectureGuideProps {
  onNavigateToConsole?: () => void;
}

export const ArchitectureGuide: React.FC<ArchitectureGuideProps> = ({ onNavigateToConsole }) => {
  return (
    <div className="space-y-8 pb-12 animate-in fade-in duration-300">
      {/* Hero / Overview Header */}
      <div className="glass-panel p-6 sm:p-8 rounded-xl border border-brand-bronze/35 shadow-card-depth bg-gradient-to-br from-sand-surface/90 via-sand-surface/60 to-sand-terminal/80">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3 max-w-3xl">
            <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-full bg-brand-gold/15 border border-brand-gold/30 text-brand-gold text-xs font-mono font-medium">
              <BookOpen className="w-3.5 h-3.5" />
              <span>Guia Normativo & Arquitetura da Plataforma</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-brand-ivory font-mono tracking-tight">
              Como Funciona o OpsMesh?
            </h1>
            <p className="text-sm text-sand-muted leading-relaxed">
              Plataforma multi-agente autônoma para orquestração, diagnóstico e remediação segura
              de crises em sistemas distribuídos de missão crítica, com portão de aprovação humana inviolável.
            </p>
          </div>

          {onNavigateToConsole && (
            <button
              onClick={onNavigateToConsole}
              className="flex items-center justify-center space-x-2 px-5 py-3 rounded-lg bg-brand-gold hover:bg-brand-goldLight text-sand-terminal font-semibold text-sm shadow-glow-gold hover:shadow-glow-gold transition-all flex-shrink-0 active:scale-95"
            >
              <span>Testar na Central de Incidentes</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Foundation Section: Datadog/Sentry + OpsMesh Prescription */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-xl border border-brand-bronze/30 bg-sand-surface/50 space-y-3">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-brand-bronze/20 border border-brand-bronze/40 flex items-center justify-center">
              <Server className="w-5 h-5 text-brand-gold" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-brand-ivory font-mono">
                Fundação Indispensável (Datadog & Sentry)
              </h2>
              <span className="text-[11px] text-sand-muted">Os Olhos e Ouvidos da Produção</span>
            </div>
          </div>
          <p className="text-xs text-sand-text leading-relaxed">
            O OpsMesh <strong className="text-brand-gold">depende 100% da telemetria, métricas APM e rastreamento de exceções</strong> fornecidos por plataformas consagradas como Datadog e Sentry. Sem os monitores, métricas de latência e traces distribuídos dessas ferramentas, o OpsMesh não existiria.
          </p>
          <div className="pt-2 flex flex-wrap gap-2 text-[11px] font-mono">
            <span className="px-2 py-1 rounded bg-sand-terminal border border-brand-bronze/30 text-sand-muted">
              Webhook: /api/v1/incidents/webhook
            </span>
            <span className="px-2 py-1 rounded bg-sand-terminal border border-brand-bronze/30 text-sand-muted">
              Datadog Site: us5.datadoghq.com
            </span>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl border border-brand-gold/30 bg-sand-surface/50 space-y-3 shadow-glow-gold">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-brand-gold/20 border border-brand-gold/40 flex items-center justify-center">
              <Cpu className="w-5 h-5 text-brand-gold" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-brand-ivory font-mono">
                Onde o OpsMesh vai além?
              </h2>
              <span className="text-[11px] text-brand-gold">O Cérebro Investigativo e Braço Prescritivo</span>
            </div>
          </div>
          <p className="text-xs text-sand-text leading-relaxed">
            Ao receber um alerta de incidente, o OpsMesh entra em ação imediatamente: comanda uma equipe multi-agente para correlacionar logs, inspecionar banco de dados, recuperar procedimentos de emergência (SOPs) via RAG Híbrido e entregar um <strong className="text-brand-gold">plano de mitigação em dois níveis pronto</strong>, reduzindo o MTTR de horas para minutos.
          </p>
          <div className="pt-2 flex items-center space-x-2 text-[11px] font-mono text-brand-emerald">
            <ShieldCheck className="w-4 h-4" />
            <span>Redução de MTTR comprovada com 0 mutações sem sign-off</span>
          </div>
        </div>
      </div>

      {/* 4-Stage Lifecycle Pipeline */}
      <div className="glass-panel p-6 sm:p-7 rounded-xl border border-brand-bronze/30 space-y-6">
        <div>
          <div className="flex items-center space-x-2 mb-1">
            <Layers className="w-4 h-4 text-brand-gold" />
            <h2 className="text-base font-bold text-brand-ivory font-mono uppercase tracking-wide">
              Ciclo de Vida de um Incidente no OpsMesh
            </h2>
          </div>
          <p className="text-xs text-sand-muted">
            Da detecção do alarme até a emissão do relatório post-mortem auditável
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Step 1 */}
          <div className="bg-sand-terminal/80 p-4 rounded-xl border border-brand-bronze/30 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-brand-crimson/20 text-brand-crimson font-mono">
                  ETAPA 1
                </span>
                <ShieldAlert className="w-5 h-5 text-brand-crimson" />
              </div>
              <h3 className="text-sm font-bold text-brand-ivory mb-1.5 font-mono">
                Ingestão & Sanitização
              </h3>
              <p className="text-xs text-sand-muted leading-relaxed">
                O alarme do Datadog/Sentry é recebido via Webhook autenticado. Senhas, tokens e PII são <strong>mascarados</strong> preventivamente antes de qualquer inferência de LLM, mantendo IPs RFC 1918 para diagnóstico de VPC e pods.
              </p>
            </div>
            <div className="text-[10px] font-mono text-brand-steel border-t border-brand-bronze/20 pt-2">
              🛡️ Zero Vazamento de PII
            </div>
          </div>

          {/* Step 2 */}
          <div className="bg-sand-terminal/80 p-4 rounded-xl border border-brand-bronze/30 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-brand-bronze/30 text-brand-gold font-mono">
                  ETAPA 2
                </span>
                <Bot className="w-4 h-4 text-brand-gold" />
              </div>
              <h3 className="text-sm font-bold text-brand-ivory mb-1.5 font-mono">
                Investigação Especializada
              </h3>
              <p className="text-xs text-sand-muted leading-relaxed">
                O <strong>Supervisor</strong> aciona especialistas em paralelo: correlaciona clusters de logs (LogHub), inspeciona banco de dados e K8s em modo estritamente Read-Only e busca SOPs operacionais via <strong>RAG Híbrido</strong>.
              </p>
            </div>
            <div className="text-[10px] font-mono text-brand-gold border-t border-brand-bronze/20 pt-2">
              ⚡ Execução Paralela Cirúrgica
            </div>
          </div>

          {/* Step 3 */}
          <div className="bg-sand-terminal/80 p-4 rounded-xl border border-brand-gold/50 shadow-glow-gold flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-brand-gold/20 text-brand-gold font-mono animate-pulse">
                  ETAPA 3 • HERO
                </span>
                <UserCheck className="w-5 h-5 text-brand-gold" />
              </div>
              <h3 className="text-sm font-bold text-brand-gold mb-1.5 font-mono">
                Portão HITL Inviolável
              </h3>
              <p className="text-xs text-sand-text leading-relaxed">
                <strong>A IA nunca aplica mutações sozinha em produção.</strong> O plano de mitigação e o patch diff são congelados aguardando a <strong>aprovação expressa com assinatura eletrônica do engenheiro SRE</strong> on-call.
              </p>
            </div>
            <div className="text-[10px] font-mono text-brand-emerald border-t border-brand-bronze/20 pt-2">
              🔒 Portão Human-in-the-Loop
            </div>
          </div>

          {/* Step 4 */}
          <div className="bg-sand-terminal/80 p-4 rounded-xl border border-brand-bronze/30 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-brand-emerald/20 text-brand-emerald font-mono">
                  ETAPA 4
                </span>
                <FileCheck className="w-5 h-5 text-brand-emerald" />
              </div>
              <h3 className="text-sm font-bold text-brand-ivory mb-1.5 font-mono">
                Auditoria & Post-Mortem
              </h3>
              <p className="text-xs text-sand-muted leading-relaxed">
                Após aprovação, os comandos são executados com rollback garantido. Um <strong>Hash SHA-256 não-repudiável</strong> e um <strong>relatório PDF auditável</strong> são emitidos automaticamente para conformidade regulatória.
              </p>
            </div>
            <div className="text-[10px] font-mono text-brand-emerald border-t border-brand-bronze/20 pt-2">
              📜 Hash SHA-256 & PDF Pronto
            </div>
          </div>
        </div>
      </div>

      {/* Two-Tier Remediation Deep Dive */}
      <div className="glass-panel p-6 sm:p-7 rounded-xl border border-brand-bronze/30 space-y-6">
        <div>
          <div className="flex items-center space-x-2 mb-1">
            <Zap className="w-4 h-4 text-brand-gold" />
            <h2 className="text-base font-bold text-brand-ivory font-mono uppercase tracking-wide">
              Remediação em Dois Níveis (Padrão Ouro de Engenharia)
            </h2>
          </div>
          <p className="text-xs text-sand-muted">
            Como o OpsMesh equilibra a recuperação imediata do SLA com a sustentabilidade do código-fonte
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Tier 1 Box */}
          <div className="bg-sand-terminal/90 p-5 rounded-xl border border-brand-amber/35 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold px-2.5 py-1 rounded bg-brand-amber/15 text-brand-amber border border-brand-amber/30 font-mono">
                ⚡ Nível 1: Mitigação Runtime (&lt; 5s)
              </span>
              <span className="text-[11px] text-sand-muted font-mono">Objetivo: Salvar o SLA</span>
            </div>
            <p className="text-xs text-sand-text leading-relaxed">
              Ação operacional imediata executada diretamente no cluster de produção (Chaos Lab) após o sign-off do SRE. Não altera arquivos em disco nem faz builds demorados.
            </p>
            <div className="bg-sand-base/80 p-3 rounded-lg border border-brand-bronze/20 text-xs font-mono space-y-1 text-sand-muted">
              <div><strong className="text-brand-ivory">Endpoint Alvo:</strong> POST /operations/mitigate</div>
              <div><strong className="text-brand-ivory">Ações Comuns:</strong> Escalonamento de pool, matar conexões idle, ativação de circuit breaker, kill de threads travadas.</div>
              <div><strong className="text-brand-ivory">Tempo Médio:</strong> &lt; 15 milissegundos</div>
            </div>
          </div>

          {/* Tier 2 Box */}
          <div className="bg-sand-terminal/90 p-5 rounded-xl border border-brand-emerald/35 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold px-2.5 py-1 rounded bg-brand-emerald/15 text-brand-emerald border border-brand-emerald/30 font-mono">
                🌿 Nível 2: GitOps Pull Request Definitivo
              </span>
              <span className="text-[11px] text-sand-muted font-mono">Objetivo: Eliminar a Causa Raiz</span>
            </div>
            <p className="text-xs text-sand-text leading-relaxed">
              O OpsMesh sintetiza uma correção definitiva no código-fonte ou IaC, abre uma branch isolada e submete um Pull Request completo no GitHub para revisão por pares e CI/CD.
            </p>
            <div className="bg-sand-base/80 p-3 rounded-lg border border-brand-bronze/20 text-xs font-mono space-y-1 text-sand-muted">
              <div><strong className="text-brand-ivory">Repositório:</strong> henriquebotelhogomes/chaos-lab</div>
              <div><strong className="text-brand-ivory">Branch Isolada:</strong> fix/opsmesh-conn-leak-8f3a</div>
              <div><strong className="text-brand-ivory">Arquivos Reais:</strong> src/core/config.py, src/chaos/state.py</div>
              <div><strong className="text-brand-ivory">Pipeline:</strong> Passa pelo CI/CD antes de entrar na branch main</div>
            </div>
          </div>
        </div>
      </div>

      {/* Multi-Agent Catalog */}
      <div className="glass-panel p-6 sm:p-7 rounded-xl border border-brand-bronze/30 space-y-6">
        <div>
          <div className="flex items-center space-x-2 mb-1">
            <Bot className="w-4 h-4 text-brand-gold" />
            <h2 className="text-base font-bold text-brand-ivory font-mono uppercase tracking-wide">
              Catálogo da Rede Multi-Agente
            </h2>
          </div>
          <p className="text-xs text-sand-muted">
            Topologia hierárquica Supervisor-Workers com papéis e ferramentas delimitadas
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-sand-terminal/80 border border-brand-bronze/25 space-y-2">
            <div className="text-xs font-bold text-brand-gold font-mono">IncidentSupervisorAgent</div>
            <p className="text-xs text-sand-muted">
              Comandante de Incidentes. Prioriza o modelo ultrarrápido <strong>Jev First</strong> para decisões categóricas e convergência booleana, delegando para LLMs a síntese da hipótese.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-sand-terminal/80 border border-brand-bronze/25 space-y-2">
            <div className="text-xs font-bold text-brand-ivory font-mono">LogTraceAnalystAgent</div>
            <p className="text-xs text-sand-muted">
              Analisa clusters de stack traces, correlaciona logs históricos no LogHub e inspeciona arquivos de código na branch main via GitHub REST API.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-sand-terminal/80 border border-brand-bronze/25 space-y-2">
            <div className="text-xs font-bold text-brand-ivory font-mono">DatabaseInfraAgent</div>
            <p className="text-xs text-sand-muted">
              Especialista em saturação de conexões Postgres, filas de locks, uso de memória Redis e pods Kubernetes em modo estritamente Read-Only.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-sand-terminal/80 border border-brand-bronze/25 space-y-2">
            <div className="text-xs font-bold text-brand-ivory font-mono">RunbookKnowledgeAgent</div>
            <p className="text-xs text-sand-muted">
              Recupera procedimentos operacionais padrão (SOPs) corporativos através de RAG Híbrido em 4 estágios (Qdrant Densa + BM25 + Reciprocal Rank Fusion + Re-ranker).
            </p>
          </div>

          <div className="p-4 rounded-lg bg-sand-terminal/80 border border-brand-bronze/25 space-y-2">
            <div className="text-xs font-bold text-brand-ivory font-mono">RemediationEngineerAgent</div>
            <p className="text-xs text-sand-muted">
              Estrutura a mitigação em dois níveis (Nível 1 Runtime e Nível 2 GitOps PR), elabora o plano de rollback e aciona o portão HITL de segurança.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-sand-terminal/80 border border-brand-bronze/25 space-y-2">
            <div className="text-xs font-bold text-brand-ivory font-mono">AuditPostMortemAgent</div>
            <p className="text-xs text-sand-muted">
              Consolida a timeline do incidente, calcula o custo evitado em USD, gera o hash criptográfico SHA-256 e compila o relatório oficial em PDF.
            </p>
          </div>
        </div>
      </div>

      {/* Quickstart Call to Action */}
      <div className="bg-sand-terminal/90 rounded-xl p-6 border border-brand-gold/40 shadow-glow-gold flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2 text-sm font-bold text-brand-ivory font-mono">
            <PlayCircle className="w-5 h-5 text-brand-emerald" />
            <span>Como testar uma crise controlada agora:</span>
          </div>
          <p className="text-xs text-sand-muted">
            1. Acesse a <strong>Central de Incidentes</strong> ➔ 2. Escolha um cenário no Chaos Studio ➔ 3. Clique em <strong>"Disparar Análise"</strong> ➔ 4. Audite os dois níveis e autorize a mitigação!
          </p>
        </div>

        <div className="flex items-center space-x-3 flex-shrink-0">
          <div className="flex items-center space-x-1.5 text-xs text-brand-gold bg-sand-surface px-3 py-1.5 rounded-lg border border-brand-bronze/30 font-mono">
            <DollarSign className="w-3.5 h-3.5 text-brand-emerald" />
            <span>Modo Replay = 100% Gratuito</span>
          </div>
          {onNavigateToConsole && (
            <button
              onClick={onNavigateToConsole}
              className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-brand-gold hover:bg-brand-goldLight text-sand-terminal font-semibold text-xs transition-all active:scale-95 shadow-sm"
            >
              <span>Ir para o Console</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
