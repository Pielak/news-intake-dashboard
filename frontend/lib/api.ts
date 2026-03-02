const API_URL = 'http://localhost:8000/api';

export async function getTrends(region = 'BR') {
  const res = await fetch(`${API_URL}/trends/?region=${region}`);
  return res.json();
}

export async function collectNow(region = 'BR') {
  const res = await fetch(`${API_URL}/admin/collect-now?region=${region}`, { method: 'POST' });
  return res.json();
}

export async function getArticles(trendId?: number) {
  const url = trendId ? `${API_URL}/articles/?trend_id=${trendId}` : `${API_URL}/articles/`;
  const res = await fetch(url);
  return res.json();
}

export async function getArticle(id: number) {
  const res = await fetch(`${API_URL}/articles/${id}`);
  return res.json();
}

export async function getSources(status?: string) {
  const url = status ? `${API_URL}/sources/?status=${status}` : `${API_URL}/sources/`;
  const res = await fetch(url);
  return res.json();
}

export async function createSource(data: any) {
  const res = await fetch(`${API_URL}/sources/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return res.json();
}

export async function approveSource(id: number) {
  const res = await fetch(`${API_URL}/admin/sources/${id}/approve`, { method: 'POST' });
  return res.json();
}

export async function blockSource(id: number) {
  const res = await fetch(`${API_URL}/admin/sources/${id}/block`, { method: 'POST' });
  return res.json();
}

export async function getDashboard() {
  const res = await fetch(`${API_URL}/admin/dashboard`);
  return res.json();
}

export async function getLogs() {
  const res = await fetch(`${API_URL}/admin/logs`);
  return res.json();
}

export async function getRegions() {
  const res = await fetch(`${API_URL}/trends/regions`);
  return res.json();
}
