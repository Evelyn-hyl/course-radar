export function SoftLoader() {
  return (
    <div className="flex items-center gap-3 text-sm text-primary/60" role="status" aria-live="polite">
      <span className="soft-loader" aria-hidden="true">
        <span />
        <span />
        <span />
      </span>
      <span>Preparing response</span>
    </div>
  );
}
