export interface LLMModelOption {
  id: string;
  name: string;
  provider: 'DeepSeek' | 'Anthropic' | 'OpenAI' | 'Google Gemini' | 'Meta & Qwen';
  badge: string;
  isReasoning?: boolean;
}

export const OPENCODE_GO_MODELS: LLMModelOption[] = [
  // DeepSeek
  {
    id: 'deepseek-chat',
    name: 'DeepSeek-V3 (671B)',
    provider: 'DeepSeek',
    badge: 'Flagship V3',
  },
  {
    id: 'deepseek-reasoner',
    name: 'DeepSeek-R1 (Reasoning)',
    provider: 'DeepSeek',
    badge: 'R1 CoT',
    isReasoning: true,
  },

  // Anthropic Claude (OpenCode Go)
  {
    id: 'claude-3-7-sonnet',
    name: 'Claude 3.7 Sonnet',
    provider: 'Anthropic',
    badge: 'Hybrid CoT',
    isReasoning: true,
  },
  {
    id: 'claude-3-5-sonnet',
    name: 'Claude 3.5 Sonnet v2',
    provider: 'Anthropic',
    badge: 'SRE Lead',
  },
  {
    id: 'claude-3-5-haiku',
    name: 'Claude 3.5 Haiku',
    provider: 'Anthropic',
    badge: 'Ultra Fast',
  },

  // OpenAI (OpenCode Go / Direct)
  {
    id: 'gpt-4o',
    name: 'GPT-4o (Omni)',
    provider: 'OpenAI',
    badge: 'Multimodal',
  },
  {
    id: 'gpt-4o-mini',
    name: 'GPT-4o Mini',
    provider: 'OpenAI',
    badge: 'Fast / Low Cost',
  },
  {
    id: 'o3-mini',
    name: 'OpenAI o3-mini',
    provider: 'OpenAI',
    badge: 'Deep Reasoning',
    isReasoning: true,
  },

  // Google Gemini (Gemini Pro / OpenCode Go)
  {
    id: 'gemini-2.0-flash',
    name: 'Gemini 2.0 Flash',
    provider: 'Google Gemini',
    badge: 'Next-Gen',
  },
  {
    id: 'gemini-1.5-pro',
    name: 'Gemini 1.5 Pro',
    provider: 'Google Gemini',
    badge: '2M Context',
  },
  {
    id: 'gemini-1.5-flash',
    name: 'Gemini 1.5 Flash',
    provider: 'Google Gemini',
    badge: 'Fast & Lean',
  },

  // Meta & Open Source (OpenCode Go)
  {
    id: 'llama-3.3-70b',
    name: 'Llama 3.3 70B Instruct',
    provider: 'Meta & Qwen',
    badge: 'Open Weight',
  },
  {
    id: 'qwen-2.5-72b',
    name: 'Qwen 2.5 72B Instruct',
    provider: 'Meta & Qwen',
    badge: 'Alibaba Cloud',
  },
];
