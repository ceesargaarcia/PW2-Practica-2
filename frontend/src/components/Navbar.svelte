<script>
  import { authState, logout } from '../lib/auth.svelte.js';
  import { addToast } from '../lib/toasts.svelte.js';
  import { authAPI } from '../services/api.js';

  let { currentPage, navigate } = $props();

  // $derived() — valores calculados desde estado global
  const isAdmin  = $derived(authState.user?.role === 'admin');
  const username = $derived(authState.user?.username ?? '');
  const initial  = $derived(username.charAt(0).toUpperCase());

  const links = [
    { id: 'products', label: 'Catálogo',  icon: '🎮' },
    { id: 'profile',  label: 'Perfil',    icon: '⚔️' },
  ];

  async function handleLogout() {
    try { await authAPI.logout(); } catch { /* ignora */ }
    logout();
    navigate('login');
    addToast('Has abandonado el reino', 'info');
  }
</script>

<nav class="navbar">
  <button class="brand" onclick={() => navigate('products')}>
    <span class="brand-icon">🏜️</span>
    <span class="brand-text">DESERT<em>VAULT</em></span>
  </button>

  <div class="links">
    {#each links as link}
      <button
        class="nav-btn {currentPage === link.id ? 'nav-btn--active' : ''}"
        onclick={() => navigate(link.id)}
      >
        <span class="nav-icon">{link.icon}</span>
        <span>{link.label}</span>
      </button>
    {/each}
    {#if isAdmin}
      <button
        class="nav-btn {currentPage === 'admin' ? 'nav-btn--active' : ''} nav-btn--admin"
        onclick={() => navigate('admin')}
      >
        <span class="nav-icon">👑</span>
        <span>Admin</span>
      </button>
    {/if}
  </div>

  <div class="user-zone">
    {#if isAdmin}
      <span class="crown-badge">👑 ADMIN</span>
    {/if}
    <div class="avatar-wrap">
      <div class="avatar">{initial}</div>
      <span class="username">{username}</span>
    </div>
    <button class="logout-btn" onclick={handleLogout} title="Cerrar sesión">
      ⏻
    </button>
  </div>
</nav>

<style>
  .navbar {
    position: sticky; top: 0; z-index: 100;
    display: flex; align-items: center; gap: 1rem;
    padding: 0 1.5rem; height: 64px;
    background: var(--dusk-800);
    border-bottom: 1px solid var(--dusk-600);
    box-shadow: 0 2px 24px rgba(26,15,10,0.5);
  }

  .brand {
    display: flex; align-items: center; gap: .6rem;
    background: none; border: none; cursor: pointer;
    text-decoration: none; padding: 0; flex-shrink: 0;
  }
  .brand-icon { font-size: 1.5rem; }
  .brand-text {
    font-family: 'Cinzel', serif;
    font-size: 1.1rem; font-weight: 900;
    color: var(--sand-300);
    letter-spacing: 0.1em;
    line-height: 1;
  }
  .brand-text em {
    font-style: normal;
    color: var(--ember-400);
    display: block; font-size: .7rem; letter-spacing: 0.25em;
  }

  .links {
    display: flex; gap: .25rem; flex: 1;
    margin-left: 1.5rem;
  }

  .nav-btn {
    display: flex; align-items: center; gap: .4rem;
    background: transparent; border: none;
    color: var(--sand-400); padding: .5rem .9rem;
    border-radius: var(--radius-sm); cursor: pointer;
    font-size: .88rem; font-weight: 500;
    transition: all .15s; white-space: nowrap;
  }
  .nav-btn:hover { background: var(--dusk-700); color: var(--sand-200); }
  .nav-btn--active {
    background: var(--dusk-600);
    color: var(--sand-200);
    border-bottom: 2px solid var(--ember-400);
  }
  .nav-btn--admin { color: #f59e0b; }
  .nav-btn--admin:hover { color: #fbbf24; }
  .nav-icon { font-size: 1rem; }

  .user-zone {
    display: flex; align-items: center; gap: .75rem;
    margin-left: auto;
  }

  .crown-badge {
    font-size: .72rem; font-weight: 700; letter-spacing: .08em;
    background: linear-gradient(135deg, #92400e, #d97706);
    color: #fef3c7; padding: .2rem .65rem; border-radius: 1rem;
  }

  .avatar-wrap { display: flex; align-items: center; gap: .5rem; }
  .avatar {
    width: 32px; height: 32px; border-radius: 50%;
    background: linear-gradient(135deg, var(--dusk-500), var(--sand-600));
    border: 2px solid var(--sand-500);
    color: var(--sand-100); font-size: .85rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  .username { color: var(--sand-400); font-size: .85rem; }

  .logout-btn {
    background: none; border: 1px solid var(--dusk-500); color: var(--sand-500);
    width: 32px; height: 32px; border-radius: 50%;
    cursor: pointer; font-size: 1.1rem; display: flex; align-items: center; justify-content: center;
    transition: all .15s;
  }
  .logout-btn:hover { border-color: var(--ember-400); color: var(--ember-400); }

  @media (max-width: 640px) {
    .links { display: none; }
    .username, .crown-badge { display: none; }
  }
</style>
