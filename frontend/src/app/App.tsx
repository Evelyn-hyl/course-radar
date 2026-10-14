import { useCallback, useState } from 'react';
import { ChatComposer } from '../components/ChatComposer';
import { ChatLayout } from '../components/ChatLayout';
import { ErrorNotice } from '../components/ErrorNotice';
import { MessageList } from '../components/MessageList';
import { RequestAcknowledgment } from '../components/RequestAcknowledgment';
import { WelcomeState } from '../components/WelcomeState';
import { useChat } from '../hooks/useChat';
import { useHealth } from '../hooks/useHealth';
import { mockChatService } from '../services/chatAdapter';

const SUGGESTIONS = [
  'Walk through an example we learned in class that uses multinomial coefficients.',
  'How are Hamiltonian cycles explained in lectures vs in the textbook?',
] as const;

export function App() {
  const healthStatus = useHealth();
  const { messages, requestState, acknowledgment, errorMessage, sendMessage, retry } = useChat(mockChatService);
  const [selectedPrompt, setSelectedPrompt] = useState<string | null>(null);
  const hasConversation = messages.length > 0;
  const isPending = requestState === 'acknowledging' || requestState === 'loading';
  const clearSelection = useCallback(() => setSelectedPrompt(null), []);

  const composer = (
    <ChatComposer
      selectedPrompt={selectedPrompt}
      isPending={isPending}
      onSubmit={sendMessage}
      onSelectionApplied={clearSelection}
    />
  );

  return (
    <ChatLayout status={healthStatus} composer={composer}>
      {!hasConversation && !isPending && (
        <WelcomeState suggestions={SUGGESTIONS} onSelectSuggestion={setSelectedPrompt} />
      )}
      {(hasConversation || isPending) && (
        <MessageList messages={messages}>
          {acknowledgment && (
            <RequestAcknowledgment message={acknowledgment} isLoading={requestState === 'loading'} />
          )}
          {requestState === 'error' && errorMessage && (
            <ErrorNotice message={errorMessage} onRetry={retry} />
          )}
        </MessageList>
      )}
    </ChatLayout>
  );
}
