export interface LLMModelOption {
  id: string;
  name: string;
  badge: string;
  provider?: string;
  quotaInfo?: string;
}

export const DEFAULT_MODEL_ID = 'deepseek-v4.1-flash';

export const OPENCODE_GO_MODELS: LLMModelOption[] = [
  {
    id: 'deepseek-v4.1-flash',
    name: 'DeepSeek 4.1 - Flash',
    badge: 'Padrão',
    provider: 'DeepSeek',
    quotaInfo: '26.000 req / 5h',
  },
  {
    id: 'glm-5.3-flash',
    name: 'GLM 5.3 - Flash',
    badge: 'Fast',
    provider: 'GLM / Zhipu',
    quotaInfo: '6.320 req / 5h',
  },
  {
    id: 'gpt-5.6-luna',
    name: 'GPT 5.6 Lua',
    badge: 'Frontier',
    provider: 'OpenAI',
    quotaInfo: '2.050 req / 5h',
  },
  {
    id: 'muse-spark-1.3-contributor',
    name: 'Muse Spark 1.3',
    badge: 'Throughput',
    provider: 'Muse',
    quotaInfo: '45.300 req / 5h',
  },
];

