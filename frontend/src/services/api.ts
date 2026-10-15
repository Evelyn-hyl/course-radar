export type HealthStatus = 'checking' | 'connected' | 'unavailable';

type HealthResponse = {
  status: 'ok';
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export type AnswerCitationResponse = {
  chunk_id: string;
  document_id: string;
  document_title: string;
  page_start: number;
  page_end: number;
};

export type AnswerResponse = {
  answer: string;
  citations: AnswerCitationResponse[];
};

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

export async function askCourseQuestion(
  courseId: string,
  question: string,
  signal?: AbortSignal,
): Promise<AnswerResponse> {
  const response = await fetch(
    `${API_BASE_URL}/courses/${encodeURIComponent(courseId)}/ask`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
      signal,
    },
  );

  if (!response.ok) {
    const detail = await readErrorDetail(response);
    throw new Error(detail ?? `Answer request failed with status ${response.status}.`);
  }

  const data: unknown = await response.json();
  if (!isAnswerResponse(data)) {
    throw new Error('Answer request returned an unexpected response.');
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

function isAnswerResponse(value: unknown): value is AnswerResponse {
  if (
    typeof value !== 'object' ||
    value === null ||
    !('answer' in value) ||
    typeof value.answer !== 'string' ||
    !('citations' in value) ||
    !Array.isArray(value.citations)
  ) {
    return false;
  }

  return value.citations.every((citation: unknown) => (
    typeof citation === 'object' &&
    citation !== null &&
    'chunk_id' in citation && typeof citation.chunk_id === 'string' &&
    'document_id' in citation && typeof citation.document_id === 'string' &&
    'document_title' in citation && typeof citation.document_title === 'string' &&
    'page_start' in citation && typeof citation.page_start === 'number' &&
    'page_end' in citation && typeof citation.page_end === 'number'
  ));
}

async function readErrorDetail(response: Response): Promise<string | null> {
  try {
    const body: unknown = await response.json();
    if (
      typeof body === 'object' &&
      body !== null &&
      'detail' in body &&
      typeof body.detail === 'string'
    ) {
      return body.detail;
    }
  } catch {
    // Fall back to the status-based message when the body is not JSON.
  }
  return null;
}
