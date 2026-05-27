const BASE = '/api';

function getToken() {
  return localStorage.getItem('token');
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${getToken()}`,
  };
}

async function request(method, path, body) {
  const opts = { method, headers: authHeaders() };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const res = await fetch(BASE + path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.message || data.error || `HTTP ${res.status}`);
  return data;
}

// Auth
export const authAPI = {
  login:    (body) => request('POST', '/auth/login', body),
  register: (body) => request('POST', '/auth/register', body),
  logout:   ()     => request('POST', '/auth/logout'),
};

// Products
export const productsAPI = {
  getAll:  ()         => request('GET',    '/products'),
  getOne:  (id)       => request('GET',    `/products/${id}`),
  create:  (body)     => request('POST',   '/products', body),
  update:  (id, body) => request('PUT',    `/products/${id}`, body),
  remove:  (id)       => request('DELETE', `/products/${id}`),
};

// Users (admin)
export const usersAPI = {
  getAll:     ()           => request('GET',    '/users'),
  getMe:      ()           => request('GET',    '/users/me'),
  updateRole: (id, role)   => request('PUT',    `/users/${id}/role`, { role }),
  remove:     (id)         => request('DELETE', `/users/${id}`),
};
