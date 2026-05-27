// Estado global de autenticación — $state de Svelte 5
// Persistencia en localStorage (requisito "Persistencia de sesión")

export const authState = $state({
  token: localStorage.getItem('token') || null,
  user:  JSON.parse(localStorage.getItem('user') || 'null'),
});

export function login(token, user) {
  authState.token = token;
  authState.user  = user;
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
}

export function logout() {
  authState.token = null;
  authState.user  = null;
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}
