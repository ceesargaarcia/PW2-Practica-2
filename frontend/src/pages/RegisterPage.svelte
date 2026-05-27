<script>
  import { authAPI } from '../services/api.js';
  import { addToast } from '../lib/toasts.svelte.js';

  let { navigate } = $props();

  let username = $state('');
  let email    = $state('');
  let password = $state('');
  let role     = $state('user');
  let loading  = $state(false);
  let errorMsg = $state('');

  async function handleRegister() {
    if (!username.trim() || !email.trim() || !password.trim()) {
      errorMsg = 'Todos los campos son obligatorios para unirse al reino';
      return;
    }
    if (password.length < 6) {
      errorMsg = 'La contraseña debe tener al menos 6 caracteres';
      return;
    }
    loading = true; errorMsg = '';
    try {
      await authAPI.register({ username: username.trim(), email: email.trim(), password, role });
      addToast('¡Cuenta creada! Ahora inicia sesión ✦');
      navigate('login');
    } catch (err) {
      errorMsg = err.message || 'Error al registrarse';
    } finally {
      loading = false;
    }
  }
</script>

<div class="auth-bg">
  <svg class="dunes" viewBox="0 0 1200 200" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M0,120 C200,40 400,180 600,100 C800,20 1000,160 1200,80 L1200,200 L0,200 Z" fill="rgba(196,154,108,0.12)"/>
  </svg>

  <div class="auth-card">
    <header class="auth-header">
      <div class="logo">⚔️</div>
      <h1>Unirse al <span>Vault</span></h1>
      <p>Crea tu identidad de explorador</p>
    </header>

    {#if errorMsg}
      <div class="alert" role="alert"><span>⚠</span> {errorMsg}</div>
    {/if}

    <div class="form">
      <div class="field">
        <label for="username">Nombre de explorador</label>
        <input id="username" bind:value={username} placeholder="DuneRider99" disabled={loading} />
      </div>
      <div class="field">
        <label for="email">Correo</label>
        <input id="email" type="email" bind:value={email} placeholder="explorador@desierto.com" disabled={loading} />
      </div>
      <div class="field">
        <label for="password">Contraseña (mín. 6 caracteres)</label>
        <input id="password" type="password" bind:value={password} placeholder="••••••••" disabled={loading} />
      </div>
      <div class="field">
        <label for="role">Rango</label>
        <select id="role" bind:value={role} disabled={loading}>
          <option value="user">🙋 Explorador</option>
          <option value="admin">👑 Archivista (Admin)</option>
        </select>
      </div>

      <button class="btn-enter" onclick={handleRegister} disabled={loading}>
        {#if loading}
          <span class="spinner"></span> Forjando tu identidad…
        {:else}
          Crear cuenta ✦
        {/if}
      </button>
    </div>

    <footer class="auth-footer">
      ¿Ya eres explorador?
      <button class="link-btn" onclick={() => navigate('login')}>Inicia sesión</button>
    </footer>
  </div>
</div>

<style>
  .auth-bg {
    min-height: 100vh; display: flex; align-items: center; justify-content: center;
    background: linear-gradient(160deg, var(--dusk-800) 0%, var(--dusk-700) 40%, #3d1f0a 100%);
    padding: 1rem; position: relative; overflow: hidden;
  }
  .dunes { position: absolute; bottom: 0; left: 0; width: 100%; height: 200px; pointer-events: none; }
  .auth-card {
    background: rgba(253,246,227,0.04); backdrop-filter: blur(12px);
    border: 1px solid rgba(212,180,131,0.2); border-radius: 1.25rem;
    padding: 2.75rem 2.25rem; width: 100%; max-width: 420px;
    box-shadow: var(--shadow-lg); position: relative; z-index: 1;
  }
  .auth-header { text-align: center; margin-bottom: 2rem; }
  .logo { font-size: 2.5rem; margin-bottom: .5rem; }
  h1 { font-family: 'Cinzel', serif; font-size: 1.5rem; font-weight: 900; color: var(--sand-300); margin: 0 0 .4rem; letter-spacing: .1em; }
  h1 span { color: var(--ember-400); }
  .auth-header p { color: var(--sand-500); font-size: .875rem; margin: 0; font-style: italic; }

  .alert {
    background: rgba(157,2,8,0.3); border: 1px solid var(--ember-600);
    color: #fca5a5; border-radius: var(--radius-sm);
    padding: .75rem 1rem; font-size: .875rem; margin-bottom: 1.25rem;
    display: flex; gap: .5rem; align-items: center;
  }

  .form { display: flex; flex-direction: column; gap: 1rem; }
  .field { display: flex; flex-direction: column; gap: .35rem; }
  label { font-size: .8rem; font-weight: 600; color: var(--sand-400); letter-spacing: .05em; text-transform: uppercase; }
  input, select {
    width: 100%; padding: .7rem .9rem;
    background: rgba(26,15,10,0.4); border: 1px solid rgba(212,180,131,0.25);
    border-radius: var(--radius-sm); color: var(--sand-200); font-size: .95rem;
    transition: border-color .15s;
  }
  input::placeholder { color: var(--sand-600); }
  input:focus, select:focus { outline: none; border-color: var(--sand-400); }
  input:disabled, select:disabled { opacity: .5; }
  select option { background: var(--dusk-700); color: var(--sand-200); }

  .btn-enter {
    margin-top: .5rem; width: 100%; padding: .85rem; border: none;
    border-radius: var(--radius-sm);
    background: linear-gradient(135deg, var(--sand-600), var(--sand-500));
    color: var(--dusk-800); font-size: .95rem; font-weight: 700;
    letter-spacing: .05em; cursor: pointer;
    box-shadow: 0 4px 20px rgba(196,154,108,0.3);
    transition: all .2s; display: flex; align-items: center; justify-content: center; gap: .5rem;
  }
  .btn-enter:hover:not(:disabled) { filter: brightness(1.1); transform: translateY(-1px); }
  .btn-enter:disabled { opacity: .6; cursor: not-allowed; }

  .spinner {
    width: 16px; height: 16px; border-radius: 50%;
    border: 2px solid rgba(26,15,10,0.3); border-top-color: var(--dusk-800);
    animation: spin .7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  .auth-footer { text-align: center; margin-top: 1.5rem; font-size: .875rem; color: var(--sand-500); }
  .link-btn { background: none; border: none; color: var(--sand-300); cursor: pointer; font-size: inherit; font-weight: 600; text-decoration: underline; }
  .link-btn:hover { color: var(--ember-400); }
</style>
