<script>
  import { authState } from '../lib/auth.svelte.js';
  import { usersAPI } from '../services/api.js';
  import { addToast } from '../lib/toasts.svelte.js';

  let { navigate } = $props();

  // $state()
  let users     = $state([]);
  let loading   = $state(true);
  let search    = $state('');
  let confirmId = $state(null);

  // $derived()
  const filteredUsers = $derived(
    (() => {
      const q = search.trim().toLowerCase();
      if (!q) return users;
      return users.filter(u =>
        u.username.toLowerCase().includes(q) ||
        u.email.toLowerCase().includes(q) ||
        u.role.toLowerCase().includes(q)
      );
    })()
  );

  const adminCount = $derived(users.filter(u => u.role === 'admin').length);
  const userCount  = $derived(users.filter(u => u.role === 'user').length);

  // $effect() — redirige si no es admin
  $effect(() => {
    if (!authState.token) { navigate('login'); return; }
    if (authState.user?.role !== 'admin') { navigate('products'); return; }
    loadUsers();
  });

  async function loadUsers() {
    loading = true;
    try { users = await usersAPI.getAll(); }
    catch (err) { addToast(err.message, 'error'); }
    finally { loading = false; }
  }

  async function toggleRole(user) {
    const newRole = user.role === 'admin' ? 'user' : 'admin';
    try {
      const updated = await usersAPI.updateRole(user._id, newRole);
      users = users.map(u => u._id === updated._id ? updated : u);
      addToast(`${updated.username} ahora es ${newRole === 'admin' ? 'Archivista' : 'Explorador'}`);
    } catch (err) { addToast(err.message, 'error'); }
  }

  async function deleteUser(id) {
    try {
      await usersAPI.remove(id);
      users = users.filter(u => u._id !== id);
      confirmId = null;
      addToast('Explorador exiliado del Vault');
    } catch (err) { addToast(err.message, 'error'); }
  }

  const isSelf = (id) => id === authState.user?.id;

  function formatDate(d) {
    return new Date(d).toLocaleDateString('es-ES', { year:'numeric', month:'short', day:'numeric' });
  }
</script>

<div class="page">
  <div class="page-hero">
    <div>
      <h1>Exploradores</h1>
      <p>Gestión de acceso al Vault</p>
    </div>
    <div class="hero-stats">
      <span class="hstat hstat--admin">👑 {adminCount} archivistas</span>
      <span class="hstat hstat--user">⚔️ {userCount} exploradores</span>
    </div>
  </div>

  <div class="search-wrap">
    <span class="search-icon">🔍</span>
    <input class="search-input" type="search"
      placeholder="Buscar explorador…" bind:value={search} />
  </div>

  {#if loading}
    <div class="skeletons">
      {#each Array(5) as _}
        <div class="skeleton-row"></div>
      {/each}
    </div>
  {:else if filteredUsers.length === 0}
    <div class="empty">🏜️ <p>Ningún explorador coincide con la búsqueda</p></div>
  {:else}
    <div class="table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>Explorador</th>
            <th>Email</th>
            <th>Rango</th>
            <th>Registro</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {#each filteredUsers as user (user._id)}
            <tr class="{isSelf(user._id) ? 'row--self' : ''}">
              <td>
                <div class="user-cell">
                  <div class="avatar">{user.username.charAt(0).toUpperCase()}</div>
                  <span class="username">{user.username}</span>
                  {#if isSelf(user._id)}<span class="you-tag">tú</span>{/if}
                </div>
              </td>
              <td class="email-cell">{user.email}</td>
              <td>
                <span class="role-badge role-badge--{user.role}">
                  {user.role === 'admin' ? '👑 Archivista' : '⚔️ Explorador'}
                </span>
              </td>
              <td class="date-cell">{formatDate(user.createdAt)}</td>
              <td>
                {#if !isSelf(user._id)}
                  <div class="actions">
                    <button class="btn-role" onclick={() => toggleRole(user)}>
                      🔄 {user.role === 'admin' ? '→ Explorador' : '→ Archivista'}
                    </button>
                    {#if confirmId === user._id}
                      <button class="btn-confirm" onclick={() => deleteUser(user._id)}>¿Exiliar?</button>
                      <button class="btn-cancel"  onclick={() => confirmId = null}>✕</button>
                    {:else}
                      <button class="btn-del" onclick={() => confirmId = user._id}>🗑</button>
                    {/if}
                  </div>
                {:else}
                  <span class="dash">—</span>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<style>
  .page { padding: 1.5rem; max-width: 1100px; margin: 0 auto; }

  .page-hero {
    display: flex; align-items: flex-end; justify-content: space-between;
    flex-wrap: wrap; gap: .75rem; margin-bottom: 1.5rem;
    padding-bottom: 1.25rem; border-bottom: 1px solid var(--sand-300);
  }
  h1 { font-family: 'Cinzel', serif; font-size: 1.75rem; font-weight: 900; color: var(--dusk-700); margin: 0 0 .2rem; }
  .page-hero p { color: var(--text-muted); margin: 0; font-size: .875rem; font-style: italic; }

  .hero-stats { display: flex; gap: .6rem; flex-wrap: wrap; }
  .hstat {
    padding: .35rem 1rem; border-radius: 1rem;
    font-size: .82rem; font-weight: 700; letter-spacing: .04em;
  }
  .hstat--admin { background: linear-gradient(135deg, #92400e, #d97706); color: #fef3c7; }
  .hstat--user  { background: var(--dusk-600); color: var(--sand-300); }

  .search-wrap { position: relative; margin-bottom: 1.25rem; max-width: 380px; }
  .search-icon { position: absolute; left: .85rem; top: 50%; transform: translateY(-50%); pointer-events: none; }
  .search-input {
    width: 100%; padding: .6rem .85rem .6rem 2.5rem;
    border: 1.5px solid var(--sand-300); border-radius: var(--radius-sm);
    font-size: .9rem; background: var(--bone); color: var(--text-primary);
  }
  .search-input:focus { outline: none; border-color: var(--sand-500); }

  .table-wrap { overflow-x: auto; }
  .table {
    width: 100%; border-collapse: collapse; background: var(--bone);
    border-radius: var(--radius); overflow: hidden;
    box-shadow: var(--shadow-card); border: 1px solid var(--sand-300);
  }
  .table thead { background: var(--sand-200); }
  .table th {
    padding: .85rem 1rem; text-align: left;
    font-size: .72rem; color: var(--text-secondary);
    text-transform: uppercase; letter-spacing: .07em;
    font-weight: 700; border-bottom: 1px solid var(--sand-300);
  }
  .table td {
    padding: .85rem 1rem; border-bottom: 1px solid var(--sand-200);
    vertical-align: middle;
  }
  .table tbody tr:last-child td { border-bottom: none; }
  .table tbody tr:hover { background: var(--sand-100); }
  .row--self { background: rgba(212,180,131,0.08); }

  .user-cell { display: flex; align-items: center; gap: .6rem; }
  .avatar {
    width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg, var(--dusk-500), var(--sand-600));
    color: var(--sand-100); font-size: .8rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
  }
  .username { font-weight: 600; color: var(--dusk-700); }
  .you-tag {
    font-size: .7rem; background: var(--sand-300); color: var(--dusk-600);
    padding: .1rem .45rem; border-radius: 1rem; font-weight: 600;
  }
  .email-cell { color: var(--text-muted); font-size: .85rem; }
  .date-cell  { color: var(--text-muted); font-size: .8rem; white-space: nowrap; }
  .dash       { color: var(--sand-400); }

  .role-badge {
    padding: .2rem .7rem; border-radius: 1rem;
    font-size: .78rem; font-weight: 700; white-space: nowrap;
  }
  .role-badge--admin { background: linear-gradient(135deg, #92400e, #d97706); color: #fef3c7; }
  .role-badge--user  { background: var(--sand-200); color: var(--dusk-600); border: 1px solid var(--sand-300); }

  .actions { display: flex; gap: .35rem; flex-wrap: wrap; align-items: center; }
  .btn-role, .btn-del, .btn-confirm, .btn-cancel {
    cursor: pointer; border: none; border-radius: var(--radius-sm);
    font-size: .78rem; font-weight: 600; padding: .3rem .7rem; transition: all .15s;
  }
  .btn-role    { background: var(--sand-200); color: var(--dusk-600); }
  .btn-role:hover { background: var(--sand-300); }
  .btn-del     { background: transparent; border: 1px solid #dc2626; color: #dc2626; }
  .btn-del:hover { background: #dc2626; color: #fff; }
  .btn-confirm { background: #dc2626; color: #fff; }
  .btn-confirm:hover { background: #b91c1c; }
  .btn-cancel  { background: var(--sand-200); color: var(--text-secondary); }

  .skeletons { display: flex; flex-direction: column; gap: .6rem; }
  .skeleton-row {
    height: 56px; border-radius: var(--radius-sm);
    background: linear-gradient(90deg, var(--sand-200) 25%, var(--bone-dark) 50%, var(--sand-200) 75%);
    background-size: 200% 100%; animation: shimmer 1.5s infinite;
  }
  @keyframes shimmer { to { background-position: -200% 0; } }
  .empty {
    text-align: center; padding: 3rem; color: var(--text-muted);
    display: flex; flex-direction: column; align-items: center; gap: .5rem; font-size: 2rem;
  }
  .empty p { font-size: .95rem; margin: 0; }
</style>
