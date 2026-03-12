const API_BASE = '/api';

export async function fetchLiveStats() {
  const res = await fetch(`${API_BASE}/stats/live/`);
  if (!res.ok) throw new Error('Failed to fetch live stats');
  return res.json();
}

export async function fetchHourlyStats() {
  const res = await fetch(`${API_BASE}/stats/hourly/`);
  if (!res.ok) throw new Error('Failed to fetch hourly stats');
  return res.json();
}

export async function fetchRecentEvents(limit = 50) {
  const res = await fetch(`${API_BASE}/events/recent/?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch recent events');
  return res.json();
}

export async function fetchVehicleClasses() {
  const res = await fetch(`${API_BASE}/vehicle-classes/`);
  if (!res.ok) throw new Error('Failed to fetch vehicle classes');
  return res.json();
}

export async function uploadVideo(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/upload/video/`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to upload video');
  return res.json();
}
