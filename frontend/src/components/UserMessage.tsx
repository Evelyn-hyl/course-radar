import type { ChatMessage } from '../types/chat';

type UserMessageProps = {
  message: ChatMessage;
};

export function UserMessage({ message }: UserMessageProps) {
  return (
    <div className="ml-auto max-w-[88%] rounded-card rounded-br-md bg-primary px-4 py-3 text-[15px] leading-6 whitespace-pre-wrap text-background sm:max-w-[76%]">
      {message.content}
    </div>
  );
}
