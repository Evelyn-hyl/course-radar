import type { HealthStatus } from '../services/api';

type ConnectionStatusProps = {
  status: HealthStatus;
};

const labels: Record<HealthStatus, string> = {
  checking: 'Checking connection',
  connected: 'API connected',
  unavailable: 'Working in preview mode',
};

export function ConnectionStatus({ status }: ConnectionStatusProps) {
  return (
    <div className="flex items-center gap-2 text-xs font-medium text-primary/60" role="status">
      <span
        className={`h-2 w-2 rounded-full ${status === 'connected' ? 'bg-emerald-600' : 'bg-citation'}`}
        aria-hidden="true"
      />
      <span>{labels[status]}</span>
    </div>
  );
}
