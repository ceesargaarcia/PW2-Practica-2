<script>
  // $props() — comunicación hijo→padre mediante callbacks
  let { product, isAdmin = false, onEdit, onDelete } = $props();

  // $derived() — estado calculado
  const isActive    = $derived(product.active);
  const stockStatus = $derived(
    product.stock === 0 ? 'empty' : product.stock < 5 ? 'low' : 'ok'
  );
  const stockLabel  = $derived(
    product.stock === 0 ? 'Sin stock' :
    product.stock < 5   ? `Solo ${product.stock} left` :
                          `${product.stock} en stock`
  );
  const priceStr = $derived(`€${Number(product.price).toFixed(2)}`);

  // Mapeo de géneros a colores de acento
  const genreColors = {
    'Acción': '#e85d04', 'RPG': '#9333ea', 'Aventura': '#0891b2',
    'Estrategia': '#16a34a', 'Deportes': '#ca8a04', 'Terror': '#dc2626',
    'Simulación': '#2563eb', 'Puzzle': '#db2777',
  };
  const accentColor = $derived(genreColors[product.category] ?? '#a67c52');

  let confirmDelete = $state(false);

  function handleDelete(e) {
    e.stopPropagation();
    if (!confirmDelete) { confirmDelete = true; return; }
    onDelete(product._id);
  }
  function cancelDelete(e) { e.stopPropagation(); confirmDelete = false; }
  function handleEdit(e) { e.stopPropagation(); onEdit(product); }
</script>

<article class="card" style="--accent: {accentColor}">
  <div class="card-img-wrap">
    <img src={product.imageUrl} alt={product.name} class="card-img" loading="lazy"
         onerror={(e) => e.target.src = 'https://placehold.co/400x300/2d1b0e/d4b483?text=No+Image'} />

    <div class="card-overlay">
      <span class="genre-tag">{product.category}</span>
      {#if !isActive}
        <span class="unavailable-tag">No disponible</span>
      {/if}
    </div>

    <div class="stock-ribbon stock-ribbon--{stockStatus}">
      {stockLabel}
    </div>
  </div>

  <div class="card-body">
    <h3 class="card-title">{product.name}</h3>
    <p class="card-desc">{product.description}</p>

    <div class="card-footer">
      <span class="price">{priceStr}</span>
      <span class="status-dot status-dot--{isActive ? 'on' : 'off'}"
            title={isActive ? 'Disponible' : 'No disponible'}></span>
    </div>

    {#if isAdmin}
      <div class="card-actions">
        <button class="btn-edit" onclick={handleEdit}>✏ Editar</button>
        {#if confirmDelete}
          <button class="btn-confirm" onclick={handleDelete}>¿Seguro?</button>
          <button class="btn-cancel"  onclick={cancelDelete}>✕</button>
        {:else}
          <button class="btn-del" onclick={handleDelete}>🗑</button>
        {/if}
      </div>
    {/if}
  </div>

  <!-- Accent line at bottom -->
  <div class="accent-line"></div>
</article>

<style>
  .card {
    background: var(--bone);
    border: 1px solid var(--sand-300);
    border-radius: var(--radius);
    overflow: hidden;
    display: flex; flex-direction: column;
    box-shadow: var(--shadow-card);
    transition: transform .2s, box-shadow .2s;
    cursor: pointer; position: relative;
  }
  .card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(26,15,10,0.18);
  }

  .card-img-wrap { position: relative; }
  .card-img { width: 100%; height: 185px; object-fit: cover; display: block; }

  .card-overlay {
    position: absolute; top: .6rem; left: .6rem;
    display: flex; flex-direction: column; gap: .35rem; align-items: flex-start;
  }
  .genre-tag {
    background: var(--accent); color: #fff;
    padding: .2rem .65rem; border-radius: 1rem;
    font-size: .72rem; font-weight: 700; letter-spacing: .04em;
    text-transform: uppercase; text-shadow: 0 1px 2px rgba(0,0,0,0.3);
  }
  .unavailable-tag {
    background: rgba(26,15,10,0.75); color: var(--sand-300);
    padding: .15rem .55rem; border-radius: 1rem; font-size: .7rem;
  }

  .stock-ribbon {
    position: absolute; bottom: .6rem; right: .6rem;
    padding: .2rem .65rem; border-radius: var(--radius-sm);
    font-size: .72rem; font-weight: 600; letter-spacing: .03em;
  }
  .stock-ribbon--ok    { background: rgba(22,163,74,0.9);  color: #fff; }
  .stock-ribbon--low   { background: rgba(202,138,4,0.9);  color: #fff; }
  .stock-ribbon--empty { background: rgba(220,38,38,0.9);  color: #fff; }

  .card-body {
    padding: 1rem; display: flex; flex-direction: column; gap: .5rem; flex: 1;
  }
  .card-title {
    font-family: 'Cinzel', serif;
    font-size: .95rem; font-weight: 700; color: var(--dusk-700); margin: 0;
    line-height: 1.3;
  }
  .card-desc {
    font-size: .82rem; color: var(--text-secondary); line-height: 1.5; flex: 1;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  }

  .card-footer {
    display: flex; align-items: center; justify-content: space-between; margin-top: auto;
  }
  .price { font-size: 1.15rem; font-weight: 800; color: var(--dusk-600); }

  .status-dot {
    width: 10px; height: 10px; border-radius: 50%;
    box-shadow: 0 0 6px currentColor;
  }
  .status-dot--on  { background: #16a34a; color: #16a34a; }
  .status-dot--off { background: #dc2626; color: #dc2626; }

  .card-actions {
    display: flex; gap: .4rem; margin-top: .5rem; flex-wrap: wrap;
  }
  .btn-edit, .btn-del, .btn-confirm, .btn-cancel {
    cursor: pointer; border: none; border-radius: var(--radius-sm);
    padding: .35rem .75rem; font-size: .78rem; font-weight: 600;
    transition: all .15s;
  }
  .btn-edit    { background: var(--sand-200); color: var(--dusk-600); flex: 1; }
  .btn-edit:hover { background: var(--sand-300); }
  .btn-del     { background: transparent; border: 1px solid #dc2626; color: #dc2626; }
  .btn-del:hover { background: #dc2626; color: #fff; }
  .btn-confirm { background: #dc2626; color: #fff; flex: 1; }
  .btn-confirm:hover { background: #b91c1c; }
  .btn-cancel  { background: var(--sand-200); color: var(--text-secondary); }

  .accent-line {
    height: 3px;
    background: linear-gradient(90deg, var(--accent), transparent);
  }
</style>
