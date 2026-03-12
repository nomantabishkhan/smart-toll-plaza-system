import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

export async function fetchLiveStats() {
  const { data } = await api.get('/stats/live/');
  return data;
}

export async function fetchHourlyStats() {
  const { data } = await api.get('/stats/hourly/');
  return data;
}

export async function fetchRecentEvents(limit = 50) {
  const { data } = await api.get('/events/recent/', { params: { limit } });
  return data;
}

export async function fetchVehicleClasses() {
  const { data } = await api.get('/vehicle-classes/');
  return data;
}

export async function uploadVideo(file, onUploadProgress) {
  const form = new FormData();
  form.append('file', file);
  const { data } = await api.post('/upload/video/', form, {
    onUploadProgress: onUploadProgress
      ? (e) => onUploadProgress(Math.round((e.loaded * 100) / (e.total || 1)))
      : undefined,
  });
  return data;
}

export async function fetchUploadStatus(id) {
  const { data } = await api.get('/upload/status/', { params: { id } });
  return data;
}
