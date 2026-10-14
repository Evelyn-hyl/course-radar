import { useEffect, useRef, useState, type KeyboardEvent } from 'react';

type ChatComposerProps = {
  selectedPrompt: string | null;
  isPending: boolean;
  onSubmit: (prompt: string) => Promise<void>;
  onSelectionApplied: () => void;
};

export function ChatComposer({ selectedPrompt, isPending, onSubmit, onSelectionApplied }: ChatComposerProps) {
  const [draft, setDraft] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const canSubmit = draft.trim().length > 0 && !isPending;

  useEffect(() => {
    if (selectedPrompt === null) {
      return;
    }
    setDraft(selectedPrompt);
    onSelectionApplied();
    window.requestAnimationFrame(() => textareaRef.current?.focus());
  }, [onSelectionApplied, selectedPrompt]);

  async function submit(): Promise<void> {
    if (!canSubmit) {
      return;
    }
    const prompt = draft.trim();
    setDraft('');
    await onSubmit(prompt);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      void submit();
    }
  }

  return (
    <div className="rounded-card border border-primary/15 bg-surface p-2 shadow-soft focus-within:border-primary/30">
      <textarea
        ref={textareaRef}
        className="block max-h-44 min-h-20 w-full resize-none bg-transparent px-3 py-2 text-[15px] leading-6 text-primary outline-none placeholder:text-primary/45"
        value={draft}
        placeholder="Ask about your course materials..."
        rows={2}
        aria-label="Course question"
        onChange={(event) => setDraft(event.target.value)}
        onKeyDown={handleKeyDown}
      />
      <div className="flex items-center justify-between gap-4 px-2 pb-1">
        <span className="hidden text-xs text-primary/45 sm:inline">Enter to send · Shift+Enter for a new line</span>
        <span className="text-xs text-primary/45 sm:hidden">Shift+Enter for a new line</span>
        <button
          className="flex min-h-10 items-center gap-2 rounded-control bg-primary px-4 py-2 text-sm font-semibold text-background transition-colors hover:bg-primary/90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-not-allowed disabled:opacity-35"
          type="button"
          disabled={!canSubmit}
          onClick={() => void submit()}
        >
          <span>Send</span>
          <svg className="h-4 w-4" viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path d="m4 10 11-6-3.5 12-2.2-4.3L4 10Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
          </svg>
        </button>
      </div>
    </div>
  );
}
