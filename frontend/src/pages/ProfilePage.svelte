<script>
  import { authState } from '../lib/auth.svelte.js';
  import { usersAPI } from '../services/api.js';
  import { addToast } from '../lib/toasts.svelte.js';

  let { navigate } = $props();

  // $state()
  let profile = $state(null);
  let loading = $state(true);

  // $derived()
  const isAdmin  = $derived(authState.user?.role === 'admin');
  const initial  = $derived((profile?.username ?? '?').charAt(0).toUpperCase());
  const joinDate = $derived(
    profile?.createdAt
      ? new Date(profile.createdAt).toLocaleDateString('es-ES', { year:'numeric', month:'long', day:'numeric' })
      : '—'
  );

  // $effect()
  $effect(() => {
    if (!authState.token) { navigate('login'); return; }
    usersAPI.getMe()
      .then(d => { profile = d; })
      .catch(err => addToast(err.message, 'error'))
      .finally(() => { loading = false; });
  });
</script>

<div class="page">
  {#if loading}
    <div class="skeleton-hero"></div>
    <div class="skeleton-card"></div>
  {:else if profile}
    <div class="profile-wrap">

      <!-- Hero -->
      <div class="profile-hero">
        <div class="avatar-ring">
          <div class="avatar">{initial}</div>
        </div>
        <div class="hero-info">
          <h1>{profile.username}</h1>
          <p class="email">{profile.email}</p>
          <span class="role-badge role-badge--{isAdmin ? 'admin' : 'user'}">
            {isAdmin ? '👑 Archivista' : '⚔️ Explorador'}
          </span>
        </div>
      </div>

      <!-- Stats / info -->
      <div class="info-grid">
        <div class="info-card">
          <span class="info-icon">📅</span>
          <div>
            <span class="info-label">Miembro desde</span>
            <span class="info-value">{joinDate}</span>
          </div>
        </div>
        <div class="info-card">
          <span class="info-icon">🆔</span>
          <div>
            <span class="info-label">ID de explorador</span>
            <span class="info-value mono">{profile._id}</span>
          </div>
        </div>
        <div class="info-card">
          <span class="info-icon">{isAdmin ? '👑' : '🙋'}</span>
          <div>
            <span class="info-label">Rango</span>
            <span class="info-value">{isAdmin ? 'Archivista (Admin)' : 'Explorador'}</span>
          </div>
        </div>
      </div>

      {#if isAdmin}
        <div class="admin-banner">
          <span class="banner-icon">🔐</span>
          <div>
            <strong>Acceso de Archivista</strong>
            <p>Puedes gestionar el catálogo completo y administrar exploradores.</p>
          </div>
        </div>
      {/if}

    </div>
  {:else}
    <p class="err">No se pudo cargar el perfil del explorador.</p>
  {/if}
</div>

<style>
  .page { padding: 2rem; max-width: 600px; margin: 0 auto; }

  .profile-wrap { display: flex; flex-direction: column; gap: 1.25rem; }

  .profile-hero {
    background: var(--dusk-800);
    border-radius: var(--radius);
    padding: 2rem 2rem 2rem;
    display: flex; align-items: center; gap: 1.5rem;
    box-shadow: var(--shadow-lg);
    border: 1px solid var(--dusk-600);
    flex-wrap: wrap;
  }
  .avatar-ring {
    width: 88px; height: 88px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg, var(--ember-400), var(--sand-500));
    padding: 3px;
  }
  .avatar {
    width: 100%; height: 100%; border-radius: 50%;
    background: var(--dusk-700);
    color: var(--sand-200); font-family: 'Cinzel', serif;
    font-size: 2rem; font-weight: 900;
    display: flex; align-items: center; justify-content: center;
  }
  .hero-info { display: flex; flex-direction: column; gap: .4rem; }
  h1 { font-family: 'Cinzel', serif; font-size: 1.5rem; color: var(--sand-200); margin: 0; letter-spacing: .05em; }
  .email { color: var(--sand-500); font-size: .875rem; margin: 0; }
  .role-badge {
    display: inline-block; padding: .3rem .85rem; border-radius: 1rem;
    font-size: .8rem; font-weight: 700; width: fit-content; letter-spacing: .04em;
  }
  .role-badge--admin { background: linear-gradient(135deg, #92400e, #d97706); color: #fef3c7; }
  .role-badge--user  { background: rgba(212,180,131,0.2); color: var(--sand-400); border: 1px solid var(--dusk-500); }

  .info-grid { display: flex; flex-direction: column; gap: .75rem; }
  .info-card {
    background: var(--bone); border: 1px solid var(--sand-300);
    border-radius: var(--radius-sm); padding: 1rem 1.25rem;
    display: flex; align-items: center; gap: 1rem;
    box-shadow: var(--shadow-card);
  }
  .info-icon { font-size: 1.4rem; flex-shrink: 0; }
  .info-label { display: block; font-size: .72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: .08em; }
  .info-value { display: block; font-weight: 700; color: var(--dusk-600); font-size: .9rem; margin-top: .15rem; }
  .mono { font-family: monospace; font-size: .78rem; color: var(--text-secondary); word-break: break-all; }

  .admin-banner {
    background: linear-gradient(135deg, rgba(146,64,14,0.12), rgba(217,119,6,0.08));
    border: 1px solid rgba(217,119,6,0.3);
    border-radius: var(--radius-sm); padding: 1rem 1.25rem;
    display: flex; gap: .85rem; align-items: flex-start;
  }
  .banner-icon { font-size: 1.5rem; flex-shrink: 0; }
  .admin-banner strong { color: var(--dusk-600); font-size: .9rem; display: block; margin-bottom: .25rem; }
  .admin-banner p { color: var(--text-secondary); font-size: .85rem; margin: 0; }

  .skeleton-hero {
    height: 140px; border-radius: var(--radius);
    background: linear-gradient(90deg, var(--sand-200) 25%, var(--bone-dark) 50%, var(--sand-200) 75%);
    background-size: 200% 100%; animation: shimmer 1.5s infinite; margin-bottom: 1rem;
  }
  .skeleton-card {
    height: 180px; border-radius: var(--radius);
    background: linear-gradient(90deg, var(--sand-200) 25%, var(--bone-dark) 50%, var(--sand-200) 75%);
    background-size: 200% 100%; animation: shimmer 1.5s infinite;
  }
  @keyframes shimmer { to { background-position: -200% 0; } }
  .err { color: var(--ember-500); padding: 2rem; text-align: center; }
</style>
