import { PromptSuggestion } from './PromptSuggestion';

type WelcomeStateProps = {
  suggestions: readonly string[];
  onSelectSuggestion: (prompt: string) => void;
};

export function WelcomeState({ suggestions, onSelectSuggestion }: WelcomeStateProps) {
  return (
    <section className="mx-auto flex w-full max-w-3xl flex-1 flex-col justify-center py-10 text-center sm:py-16">
      <div className="mx-auto mb-6 flex h-12 w-12 items-center justify-center rounded-full border border-primary/15 bg-surface text-xl font-semibold text-primary shadow-soft" aria-hidden="true">
        C
      </div>
      <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-rust">CourseRadar</p>
      <h1 className="text-balance font-serif text-3xl leading-tight font-medium text-primary sm:text-4xl">
        What would you like to explore?
      </h1>
      <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-primary/65 sm:text-base">
        Ask a question about your course. Source-grounded retrieval will arrive in the next milestones.
      </p>
      <div className="mt-8 grid gap-3 sm:grid-cols-2">
        {suggestions.map((suggestion) => (
          <PromptSuggestion key={suggestion} prompt={suggestion} onSelect={onSelectSuggestion} />
        ))}
      </div>
    </section>
  );
}
