// Proxy forwards /api/* to backend (see vite.config.ts)
const API_URL = '/api/query';

export interface QueryResponse {
  answer: string;
  sources: string[];
  cache_hit: boolean;
}

export async function sendQuery(question: string): Promise<QueryResponse> {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, doc_type: null }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Request failed: ${res.status}`);
  }
  return res.json();
}
