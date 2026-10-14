import { useCallback, useEffect, useRef, useState } from 'react';
import type { ChatMessage, ChatService, RequestState } from '../types/chat';

export type UseChatResult = {
  messages: ChatMessage[];
  requestState: RequestState;
  acknowledgment: string | null;
  errorMessage: string | null;
  sendMessage: (prompt: string) => Promise<void>;
  retry: () => Promise<void>;
};

function createId(): string {
  return crypto.randomUUID();
}

function createAcknowledgment(prompt: string): string {
  const normalized = prompt.trim().replace(/\s+/g, ' ');
  const lowerPrompt = normalized.toLowerCase();

  if (lowerPrompt.includes(' vs ') || lowerPrompt.includes('compare')) {
    return "I'll compare the relevant explanations across your course materials.";
  }
  if (lowerPrompt.includes('example')) {
    return "I'll look for a course example that matches what you're exploring.";
  }
  if (lowerPrompt.includes('proof')) {
    return "I'll identify course concepts that may be relevant to that proof.";
  }

  return "I'll look into that question using your course materials.";
}

export function useChat(service: ChatService): UseChatResult {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [requestState, setRequestState] = useState<RequestState>('idle');
  const [acknowledgment, setAcknowledgment] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const lastPromptRef = useRef<string | null>(null);
  const activeControllerRef = useRef<AbortController | null>(null);

  const runRequest = useCallback(
    async (prompt: string, appendUserMessage: boolean): Promise<void> => {
      if (appendUserMessage) {
        setMessages((current) => [
          ...current,
          { id: createId(), role: 'user', content: prompt, createdAt: new Date().toISOString() },
        ]);
      }

      lastPromptRef.current = prompt;
      setErrorMessage(null);
      setAcknowledgment(createAcknowledgment(prompt));
      setRequestState('acknowledging');

      // Let React paint the immediate acknowledgment before moving into the pending state.
      await new Promise<void>((resolve) => window.requestAnimationFrame(() => resolve()));
      setRequestState('loading');

      const controller = new AbortController();
      activeControllerRef.current = controller;

      try {
        const response = await service.sendMessage(prompt, controller.signal);
        setMessages((current) => [
          ...current,
          {
            id: createId(),
            role: 'assistant',
            content: response.content,
            citations: response.citations,
            createdAt: new Date().toISOString(),
            isDemo: response.isDemo,
          },
        ]);
        setAcknowledgment(null);
        setRequestState('success');
      } catch (error: unknown) {
        if (error instanceof DOMException && error.name === 'AbortError') {
          return;
        }
        setErrorMessage('The response could not be prepared. Your question is still here, so you can retry.');
        setAcknowledgment(null);
        setRequestState('error');
      } finally {
        if (activeControllerRef.current === controller) {
          activeControllerRef.current = null;
        }
      }
    },
    [service],
  );

  const sendMessage = useCallback(
    async (prompt: string): Promise<void> => {
      if (requestState === 'acknowledging' || requestState === 'loading') {
        return;
      }
      await runRequest(prompt.trim(), true);
    },
    [requestState, runRequest],
  );

  const retry = useCallback(async (): Promise<void> => {
    if (lastPromptRef.current) {
      await runRequest(lastPromptRef.current, false);
    }
  }, [runRequest]);

  useEffect(() => () => activeControllerRef.current?.abort(), []);

  return { messages, requestState, acknowledgment, errorMessage, sendMessage, retry };
}
