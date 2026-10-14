export type HealthStatus = 'checking' | 'connected' | 'unavailable';

type HealthResponse = {
  status: 'ok';
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export async function checkHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`, { signal });

  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}.`);
  }

  const data: unknown = await response.json();
  if (!isHealthResponse(data)) {
    throw new Error('Health check returned an unexpected response.');
  }

  return data;
}

function isHealthResponse(value: unknown): value is HealthResponse {
  return (
    typeof value === 'object' &&
    value !== null &&
    'status' in value &&
    value.status === 'ok'
  );
}
