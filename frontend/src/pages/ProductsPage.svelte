<script>
  import { authState } from '../lib/auth.svelte.js';
  import { productsAPI } from '../services/api.js';
  import { addToast } from '../lib/toasts.svelte.js';
  import ProductCard   from '../components/ProductCard.svelte';
  import ProductForm   from '../components/ProductForm.svelte';
  import ProductDetail from '../components/ProductDetail.svelte';

  let { navigate } = $props();

  // $state() — estado principal
  let products     = $state([]);
  let loading      = $state(true);
  let search       = $state('');
  let filterStatus = $state('all');
  let showForm     = $state(false);
  let editProduct  = $state(null);
  let detailProd   = $state(null);

  // $derived()
  const isAdmin = $derived(authState.user?.role === 'admin');

  const filteredProducts = $derived(
    (() => {
      let list = products;
      if (filterStatus === 'active')   list = list.filter(p => p.stock > 0);
      if (filterStatus === 'inactive') list = list.filter(p => p.stock === 0);     const q = search.trim().toLowerCase();
      if (q) list = list.filter(p =>
        p.name.toLowerCase().includes(q) ||
        (p.category ?? '').toLowerCase().includes(q) ||
        (p.description ?? '').toLowerCase().includes(q)
      );
      return list;
    })()
  );

  const totalCount = $derived(products.length);

  const activeCount = $derived(products.filter(p => p.stock > 0).length);

  const inactiveCount = $derived(products.filter(p => p.stock === 0).length);

  const visibleCount = $derived(filteredProducts.length);

  // $effect() — carga inicial + redirige si no autenticado
  $effect(() => {
    if (!authState.token) { navigate('login'); return; }
    loadProducts();
  });

  // $effect() — recarga si cambia el rol
  $effect(() => {
    const role = authState.user?.role;
    if (role) loadProducts();
  });

  async function loadProducts() {
    loading = true;
    try {
      products = await productsAPI.getAll();
    } catch (err) {
      addToast(err.message, 'error');
    } finally {
      loading = false;
    }
  }

  function openCreate() { editProduct = null; showForm = true; }
  function openEdit(p)  { editProduct = p;    showForm = true; }
  function closeForm()  { showForm = false; editProduct = null; }

  async function handleSave(data) {
    try {
      if (editProduct) {
        const updated = await productsAPI.update(editProduct._id, data);
        products = products.map(p => p._id === updated._id ? updated : p);
        addToast('Juego actualizado ✦');
      } else {
        const created = await productsAPI.create(data);
        products = [created, ...products];
        addToast('Juego publicado en el Vault ✦');
      }
      closeForm();
    } catch (err) {
      addToast(err.message, 'error');
      throw err;
    }
  }

  async function handleDelete(id) {
    try {
      await productsAPI.remove(id);
      products = products.filter(p => p._id !== id);
      addToast('Juego retirado del Vault');
    } catch (err) {
      addToast(err.message, 'error');
    }
  }
</script>

<div class="page">

  <!-- Header hero -->
  <div class="page-hero">
    <div class="hero-text">
      <h1>Desert Vault</h1>
      <p>Catálogo de reliquias digitales del desierto</p>
    </div>
    {#if isAdmin}
      <button class="btn-new" onclick={openCreate}>
        <span>＋</span> Nuevo juego
      </button>
    {/if}
  </div>

  <!-- Stats -->
  <div class="stats-bar">
    <div class="stat">
      <span class="stat-num">{totalCount}</span>
      <span class="stat-lbl">Total</span>
    </div>
    <div class="stat">
      <span class="stat-num">{activeCount}</span>
      <span class="stat-lbl">Disponibles</span>
    </div>
    <div class="stat">
      <span class="stat-num">{inactiveCount}</span>
      <span class="stat-lbl">Agotados</span>
    </div>
    <div class="stat">
      <span class="stat-num">{visibleCount}</span>
      <span class="stat-lbl">Visibles</span>
    </div>
  </div>

  <!-- Toolbar -->
  <div class="toolbar">
    <div class="search-wrap">
      <span class="search-icon">🔍</span>
      <input class="search-input" type="search"
        placeholder="Buscar por título, género…"
        bind:value={search} />
    </div>

    <div class="filter-group" role="group" aria-label="Filtrar por estado">
      {#each [['all','Todos'],['active','Disponibles'],['inactive','Agotados']] as [val, lbl]}
        <button
          class="filter-btn {filterStatus === val ? 'filter-btn--active' : ''}"
          onclick={() => filterStatus = val}
        >{lbl}</button>
      {/each}
    </div>
  </div>

  <!-- Grid o estados vacíos -->
  {#if loading}
    <div class="grid">
      {#each Array(6) as _}
        <div class="skeleton"></div>
      {/each}
    </div>
  {:else if filteredProducts.length === 0}
    <div class="empty">
      <span class="empty-icon">🏜️</span>
      <p>Ningún juego coincide con tu búsqueda</p>
      {#if search || filterStatus !== 'all'}
        <button class="btn-clear" onclick={() => { search = ''; filterStatus = 'all'; }}>
          Limpiar filtros
        </button>
      {/if}
    </div>
  {:else}
    <div class="grid">
      {#each filteredProducts as product (product._id)}
        <div onclick={() => detailProd = product} role="button" tabindex="0"
             onkeydown={(e) => e.key === 'Enter' && (detailProd = product)}>
          <ProductCard
            {product}
            {isAdmin}
            onEdit={(p) => openEdit(p)}
            onDelete={handleDelete}
          />
        </div>
      {/each}
    </div>
  {/if}
</div>

{#if showForm}
  <ProductForm product={editProduct} onSave={handleSave} onCancel={closeForm} />
{/if}

{#if detailProd}
  <ProductDetail product={detailProd} onClose={() => detailProd = null} />
{/if}

<style>
  .page { padding: 1.5rem; max-width: 1280px; margin: 0 auto; }

  .page-hero {
    display: flex; align-items: flex-end; justify-content: space-between;
    margin-bottom: 1.75rem; flex-wrap: wrap; gap: 1rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid var(--sand-300);
  }
  .hero-text h1 {
    font-family: 'Cinzel', serif;
    font-size: 2rem; font-weight: 900; color: var(--dusk-700);
    margin: 0 0 .2rem; letter-spacing: .05em;
  }
  .hero-text p { color: var(--text-muted); margin: 0; font-size: .9rem; font-style: italic; }

  .btn-new {
    display: flex; align-items: center; gap: .4rem;
    background: linear-gradient(135deg, var(--ember-400), var(--ember-500));
    border: none; color: #fff; padding: .65rem 1.4rem;
    border-radius: var(--radius-sm); cursor: pointer; font-size: .9rem; font-weight: 700;
    box-shadow: 0 4px 16px rgba(232,93,4,0.35);
    transition: all .2s; letter-spacing: .03em;
  }
  .btn-new:hover { filter: brightness(1.1); transform: translateY(-1px); }

  .stats-bar {
    display: flex; gap: .75rem; margin-bottom: 1.5rem; flex-wrap: wrap;
  }
  .stat {
    background: var(--bone); border: 1px solid var(--sand-300);
    border-radius: var(--radius-sm); padding: .65rem 1.25rem;
    display: flex; flex-direction: column; align-items: center; min-width: 75px;
    box-shadow: var(--shadow-card);
  }
  .stat-num { font-size: 1.4rem; font-weight: 800; color: var(--dusk-600); line-height: 1; }
  .stat-lbl { font-size: .72rem; color: var(--text-muted); margin-top: .2rem; text-transform: uppercase; letter-spacing: .06em; }

  .toolbar { display: flex; gap: .75rem; margin-bottom: 1.5rem; align-items: center; flex-wrap: wrap; }
  .search-wrap { position: relative; flex: 1; min-width: 200px; }
  .search-icon { position: absolute; left: .85rem; top: 50%; transform: translateY(-50%); pointer-events: none; }
  .search-input {
    width: 100%; padding: .6rem .85rem .6rem 2.5rem;
    border: 1.5px solid var(--sand-300); border-radius: var(--radius-sm);
    font-size: .9rem; background: var(--bone); color: var(--text-primary);
    transition: border-color .15s;
  }
  .search-input:focus { outline: none; border-color: var(--sand-500); }

  .filter-group { display: flex; gap: .25rem; }
  .filter-btn {
    background: var(--bone); border: 1.5px solid var(--sand-300);
    padding: .5rem .9rem; border-radius: var(--radius-sm);
    cursor: pointer; font-size: .82rem; color: var(--text-secondary);
    font-weight: 500; transition: all .15s;
  }
  .filter-btn:hover     { border-color: var(--sand-500); }
  .filter-btn--active   { background: var(--dusk-700); color: var(--sand-200); border-color: var(--dusk-700); }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(255px, 1fr));
    gap: 1.25rem;
  }

  .skeleton {
    height: 320px; border-radius: var(--radius);
    background: linear-gradient(90deg, var(--sand-200) 25%, var(--bone-dark) 50%, var(--sand-200) 75%);
    background-size: 200% 100%; animation: shimmer 1.5s infinite;
  }
  @keyframes shimmer { to { background-position: -200% 0; } }

  .empty {
    text-align: center; padding: 5rem 1rem; color: var(--text-muted);
    display: flex; flex-direction: column; align-items: center; gap: 1rem;
  }
  .empty-icon { font-size: 3.5rem; }
  .empty p { font-size: 1rem; margin: 0; }
  .btn-clear {
    background: transparent; border: 1.5px solid var(--sand-400);
    color: var(--text-secondary); padding: .5rem 1.2rem;
    border-radius: var(--radius-sm); cursor: pointer; font-size: .875rem;
    transition: all .15s;
  }
  .btn-clear:hover { background: var(--sand-200); }
</style>
