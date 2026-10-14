import type { ChatResponse, ChatService } from '../types/chat';

const PREVIEW_RESPONSE: ChatResponse = {
  content: [
    '### A preview of the response experience',
    '',
    'CourseRadar will use your uploaded materials to build a grounded answer here. A response can include readable mathematics such as',
    '',
    '$$P(A \\cap B) = P(A)P(B \\mid A)$$',
    '',
    '**Retrieval is not connected in M0**, so this preview does not claim to answer your question or cite real course evidence.',
  ].join('\n'),
  citations: [{ id: 'demo-source', label: 'Demo citation · Not a real source', isDemo: true }],
  isDemo: true,
};

const MOCK_RESPONSE_DELAY_MS = 900;

export const mockChatService: ChatService = {
  sendMessage: (_prompt: string, signal?: AbortSignal) =>
    new Promise<ChatResponse>((resolve, reject) => {
      const timeoutId = window.setTimeout(() => resolve(PREVIEW_RESPONSE), MOCK_RESPONSE_DELAY_MS);

      signal?.addEventListener(
        'abort',
        () => {
          window.clearTimeout(timeoutId);
          reject(new DOMException('Request aborted.', 'AbortError'));
        },
        { once: true },
      );
    }),
};
