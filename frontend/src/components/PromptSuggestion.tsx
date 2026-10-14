type PromptSuggestionProps = {
  prompt: string;
  onSelect: (prompt: string) => void;
};

export function PromptSuggestion({ prompt, onSelect }: PromptSuggestionProps) {
  return (
    <button
      className="flex min-h-16 w-full items-center rounded-control border border-primary/10 bg-surface/55 px-4 py-3 text-left text-sm leading-6 text-primary transition-colors hover:border-primary/25 hover:bg-surface focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary sm:text-[15px]"
      type="button"
      onClick={() => onSelect(prompt)}
    >
      {prompt}
    </button>
  );
}
