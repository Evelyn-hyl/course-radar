import type { Citation } from '../types/chat';

type CitationPillProps = {
  citation: Citation;
};

export function CitationPill({ citation }: CitationPillProps) {
  return (
    <span className="inline-flex min-h-8 items-center rounded-full bg-citation px-3 py-1 text-xs font-semibold text-primary">
      {citation.label}
    </span>
  );
}
