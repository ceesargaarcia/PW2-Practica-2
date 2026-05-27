<script>
  import { authState, login } from '../lib/auth.svelte.js';
  import { authAPI } from '../services/api.js';
  import { addToast } from '../lib/toasts.svelte.js';

  let { navigate } = $props();

  // $state()
  let email    = $state('');
  let password = $state('');
  let loading  = $state(false);
  let errorMsg = $state('');

  // $effect() — redirigir si ya autenticado
  $effect(() => {
    if (authState.token) navigate('products');
  });

  async function handleLogin() {
    if (!email.trim() || !password.trim()) {
      errorMsg = 'Completa todos los campos para entrar al reino';
      return;
    }
    loading = true; errorMsg = '';
    try {
      const data = await authAPI.login({ email: email.trim(), password });
      login(data.token, data.user);
      addToast(`Bienvenido de vuelta, ${data.user.username} ⚔️`);
      navigate('products');
    } catch (err) {
      errorMsg = err.message || 'Credenciales incorrectas';
    } finally {
      loading = false;
    }
  }

  function onKey(e) { if (e.key === 'Enter') handleLogin(); }
</script>

<div class="auth-bg">
  <!-- Decorative dunes SVG -->
  <svg class="dunes" viewBox="0 0 1200 200" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M0,120 C200,40 400,180 600,100 C800,20 1000,160 1200,80 L1200,200 L0,200 Z" fill="rgba(196,154,108,0.12)"/>
    <path d="M0,160 C300,80 600,200 900,120 C1050,80 1150,140 1200,120 L1200,200 L0,200 Z" fill="rgba(196,154,108,0.08)"/>
  </svg>

  <div class="auth-card">
    <div class="card-glow"></div>

    <header class="auth-header">
      <div class="logo">🏜️</div>
      <h1>DESERT<span>VAULT</span></h1>
      <p>El santuario de los juegos perdidos</p>
    </header>

    {#if errorMsg}
      <div class="alert" role="alert">
        <span>⚠</span> {errorMsg}
      </div>
    {/if}

    <div class="form">
      <div class="field">
        <label for="email">Correo de explorador</label>
        <div class="input-wrap">
          <span class="input-icon">✉</span>
          <input id="email" type="email" bind:value={email}
            placeholder="explorador@desierto.com"
            autocomplete="email" onkeydown={onKey} disabled={loading} />
        </div>
      </div>

      <div class="field">
        <label for="password">Contraseña secreta</label>
        <div class="input-wrap">
          <span class="input-icon">🔑</span>
          <input id="password" type="password" bind:value={password}
            placeholder="••••••••"
            autocomplete="current-password" onkeydown={onKey} disabled={loading} />
        </div>
      </div>

      <button class="btn-enter" onclick={handleLogin} disabled={loading}>
        {#if loading}
          <span class="spinner"></span> Cruzando el desierto…
        {:else}
          Entrar al Vault ⚔️
        {/if}
      </button>
    </div>

    <footer class="auth-footer">
      ¿Primera vez en el desierto?
      <button class="link-btn" onclick={() => navigate('register')}>Crea tu cuenta</button>
    </footer>
  </div>
</div>

<style>
  .auth-bg {
    min-height: 100vh;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(160deg, var(--dusk-800) 0%, var(--dusk-700) 40%, #3d1f0a 100%);
    padding: 1rem; position: relative; overflow: hidden;
  }

  .dunes {
    position: absolute; bottom: 0; left: 0; width: 100%; height: 200px;
    pointer-events: none;
  }

  .auth-card {
    background: rgba(253,246,227,0.04);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(212,180,131,0.2);
    border-radius: 1.25rem; padding: 2.75rem 2.25rem;
    width: 100%; max-width: 420px;
    box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(253,246,227,0.06);
    position: relative; z-index: 1;
  }

  .card-glow {
    position: absolute; inset: -1px; border-radius: 1.25rem;
    background: linear-gradient(135deg, rgba(232,93,4,0.15), transparent 60%);
    pointer-events: none;
  }

  .auth-header { text-align: center; margin-bottom: 2rem; }
  .logo { font-size: 3rem; margin-bottom: .5rem; }
  h1 {
    font-family: 'Cinzel', serif;
    font-size: 1.75rem; font-weight: 900;
    color: var(--sand-300); margin: 0 0 .4rem;
    letter-spacing: .15em;
  }
  h1 span { color: var(--ember-400); }
  .auth-header p { color: var(--sand-500); font-size: .875rem; margin: 0; font-style: italic; }

  .alert {
    background: rgba(157,2,8,0.3); border: 1px solid var(--ember-600);
    color: #fca5a5; border-radius: var(--radius-sm);
    padding: .75rem 1rem; font-size: .875rem;
    margin-bottom: 1.25rem; display: flex; gap: .5rem; align-items: center;
  }

  .form { display: flex; flex-direction: column; gap: 1.1rem; }
  .field { display: flex; flex-direction: column; gap: .35rem; }
  label { font-size: .8rem; font-weight: 600; color: var(--sand-400); letter-spacing: .05em; text-transform: uppercase; }

  .input-wrap { position: relative; }
  .input-icon {
    position: absolute; left: .85rem; top: 50%; transform: translateY(-50%);
    color: var(--sand-500); font-size: .9rem; pointer-events: none;
  }
  input {
    width: 100%; padding: .7rem .85rem .7rem 2.5rem;
    background: rgba(26,15,10,0.4);
    border: 1px solid rgba(212,180,131,0.25);
    border-radius: var(--radius-sm);
    color: var(--sand-200); font-size: .95rem;
    transition: border-color .15s, box-shadow .15s;
  }
  input::placeholder { color: var(--sand-600); }
  input:focus { outline: none; border-color: var(--sand-400); box-shadow: 0 0 0 3px rgba(212,180,131,0.1); }
  input:disabled { opacity: .5; }

  .btn-enter {
    margin-top: .5rem; width: 100%;
    padding: .85rem; border: none; border-radius: var(--radius-sm);
    background: linear-gradient(135deg, var(--ember-400), var(--ember-500));
    color: #fff; font-size: .95rem; font-weight: 700;
    letter-spacing: .05em; cursor: pointer;
    box-shadow: 0 4px 20px rgba(232,93,4,0.4);
    transition: all .2s; display: flex; align-items: center; justify-content: center; gap: .5rem;
  }
  .btn-enter:hover:not(:disabled) {
    background: linear-gradient(135deg, #ff6b1a, var(--ember-400));
    box-shadow: 0 6px 28px rgba(232,93,4,0.55); transform: translateY(-1px);
  }
  .btn-enter:disabled { opacity: .6; cursor: not-allowed; transform: none; }

  .spinner {
    width: 16px; height: 16px; border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: #fff; animation: spin .7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  .auth-footer {
    text-align: center; margin-top: 1.5rem;
    font-size: .875rem; color: var(--sand-500);
  }
  .link-btn {
    background: none; border: none; color: var(--sand-300);
    cursor: pointer; font-size: inherit; font-weight: 600;
    text-decoration: underline; text-underline-offset: 2px;
  }
  .link-btn:hover { color: var(--ember-400); }
</style>
