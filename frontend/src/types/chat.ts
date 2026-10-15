export type Citation = {
  id: string;
  label: string;
  documentId: string;
  pageStart: number;
  pageEnd: number;
  isDemo?: boolean;
};

export type ChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  createdAt: string;
  isDemo?: boolean;
};

export type RequestState = 'idle' | 'acknowledging' | 'loading' | 'success' | 'error';

export type ChatResponse = {
  content: string;
  citations: Citation[];
  isDemo?: boolean;
};

export type ChatService = {
  sendMessage: (prompt: string, signal?: AbortSignal) => Promise<ChatResponse>;
};
