import type { ChatMessage } from '../types/chat';
import { CitationPill } from './CitationPill';
import { MarkdownMathRenderer } from './MarkdownMathRenderer';

type AssistantResponseCardProps = {
  message: ChatMessage;
};

export function AssistantResponseCard({ message }: AssistantResponseCardProps) {
  return (
    <article className="rounded-card border border-primary/10 bg-surface p-5 text-primary shadow-soft sm:p-7">
      {message.isDemo && (
        <div className="mb-5 inline-flex rounded-full bg-warm/25 px-3 py-1 text-xs font-semibold tracking-wide text-rust">
          M0 preview
        </div>
      )}
      <MarkdownMathRenderer content={message.content} />
      {message.citations && message.citations.length > 0 && (
        <div className="mt-6 flex flex-wrap gap-2" aria-label="Citations">
          {message.citations.map((citation) => <CitationPill key={citation.id} citation={citation} />)}
        </div>
      )}
    </article>
  );
}
