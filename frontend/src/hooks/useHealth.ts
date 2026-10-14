import { useEffect, useState } from 'react';
import { checkHealth, type HealthStatus } from '../services/api';

export function useHealth(): HealthStatus {
  const [status, setStatus] = useState<HealthStatus>('checking');

  useEffect(() => {
    const controller = new AbortController();

    checkHealth(controller.signal)
      .then(() => setStatus('connected'))
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === 'AbortError') {
          return;
        }
        setStatus('unavailable');
      });

    return () => controller.abort();
  }, []);

  return status;
}
