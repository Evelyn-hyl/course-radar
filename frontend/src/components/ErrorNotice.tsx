type ErrorNoticeProps = {
  message: string;
  onRetry: () => Promise<void>;
};

export function ErrorNotice({ message, onRetry }: ErrorNoticeProps) {
  return (
    <div className="rounded-card border border-rust/25 bg-surface p-5" role="alert">
      <p className="text-sm leading-6 text-primary">{message}</p>
      <button
        className="mt-3 rounded-control border border-primary/20 px-3 py-2 text-sm font-semibold text-primary hover:bg-primary/5 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
        type="button"
        onClick={() => void onRetry()}
      >
        Retry
      </button>
    </div>
  );
}
