import { useEffect, useRef } from 'react';
import type { ChatMessage } from '../types/chat';
import { AssistantResponseCard } from './AssistantResponseCard';
import { UserMessage } from './UserMessage';

type MessageListProps = {
  messages: ChatMessage[];
  children?: React.ReactNode;
};

export function MessageList({ messages, children }: MessageListProps) {
  const endRef = useRef<HTMLDivElement>(null);
  const wasNearBottomRef = useRef(true);

  useEffect(() => {
    if (wasNearBottomRef.current) {
      endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [children, messages]);

  function updateScrollIntent(): void {
    const distanceToBottom = document.documentElement.scrollHeight - window.scrollY - window.innerHeight;
    wasNearBottomRef.current = distanceToBottom < 160;
  }

  useEffect(() => {
    window.addEventListener('scroll', updateScrollIntent, { passive: true });
    return () => window.removeEventListener('scroll', updateScrollIntent);
  }, []);

  return (
    <div className="flex flex-col gap-6 py-8" aria-live="polite">
      {messages.map((message) =>
        message.role === 'user'
          ? <UserMessage key={message.id} message={message} />
          : <AssistantResponseCard key={message.id} message={message} />,
      )}
      {children}
      <div ref={endRef} />
    </div>
  );
}
