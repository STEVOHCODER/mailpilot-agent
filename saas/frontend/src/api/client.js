const API = '/api';

async function request(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API}${path}`, { ...options, headers });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Request failed');
  return data;
}

export const auth = {
  register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  me: () => request('/auth/me'),
};

export const email = {
  list: () => request('/email/connections'),
  connect: (data) => request('/email/connect', { method: 'POST', body: JSON.stringify(data) }),
  disconnect: (id) => request(`/email/connections/${id}`, { method: 'DELETE' }),
};

export const whatsapp = {
  get: () => request('/whatsapp/connection'),
  connect: (data) => request('/whatsapp/connect', { method: 'POST', body: JSON.stringify(data) }),
  disconnect: () => request('/whatsapp/connection', { method: 'DELETE' }),
  test: () => request('/whatsapp/test', { method: 'POST' }),
};

export const rules = {
  list: () => request('/rules/'),
  create: (data) => request('/rules/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => request(`/rules/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => request(`/rules/${id}`, { method: 'DELETE' }),
};

export const dashboard = {
  get: () => request('/dashboard/'),
  messages: () => request('/dashboard/messages'),
  subscription: () => request('/dashboard/subscription'),
  usage: () => request('/dashboard/usage'),
};

export const admin = {
  stats: () => request('/admin/stats'),
  users: () => request('/admin/users'),
  toggleUser: (id) => request(`/admin/users/${id}/toggle`, { method: 'POST' }),
};
