<script>
  // $props()
  let { product, onClose } = $props();

  const genreColors = {
    'Acción': '#e85d04', 'RPG': '#9333ea', 'Aventura': '#0891b2',
    'Estrategia': '#16a34a', 'Deportes': '#ca8a04', 'Terror': '#dc2626',
    'Simulación': '#2563eb', 'Puzzle': '#db2777',
  };
  const accent = genreColors[product.category] ?? '#a67c52';
</script>

<div class="overlay" onclick={onClose} role="presentation"></div>

<dialog open class="modal" aria-modal="true" aria-labelledby="detail-title" style="--accent:{accent}">
  <button class="close-btn" onclick={onClose} aria-label="Cerrar">✕</button>

  <div class="hero">
    <img src={product.imageUrl} alt={product.name} class="hero-img"
         onerror={(e) => e.target.src = 'https://placehold.co/600x300/2d1b0e/d4b483?text=No+Image'} />
    <div class="hero-grad"></div>
    <div class="hero-info">
      <span class="genre-tag">{product.category}</span>
      <h2 id="detail-title">{product.name}</h2>
    </div>
  </div>

  <div class="body">
    <p class="description">{product.description}</p>

    <div class="meta-grid">
      <div class="meta-item">
        <span class="meta-label">Precio</span>
        <span class="meta-value price">€{Number(product.price).toFixed(2)}</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Stock</span>
        <span class="meta-value">{product.stock} unidades</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Estado</span>
        <span class="meta-value">
          <span class="badge badge--{product.active ? 'active' : 'inactive'}">
            {product.active ? '✦ Disponible' : '✕ No disponible'}
          </span>
        </span>
      </div>
      {#if product.createdBy}
      <div class="meta-item">
        <span class="meta-label">Archivado por</span>
        <span class="meta-value">{product.createdBy.username ?? product.createdBy}</span>
      </div>
      {/if}
    </div>
  </div>

  <div class="accent-bottom"></div>
</dialog>

<style>
  .overlay { position: fixed; inset: 0; background: rgba(26,15,10,.7); z-index: 200; backdrop-filter: blur(4px); }
  .modal {
    position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
    z-index: 201; background: var(--bone); border: 1px solid var(--sand-300);
    border-radius: var(--radius); border: none;
    padding: 0; width: min(560px, 95vw); max-height: 90vh; overflow-y: auto;
    box-shadow: var(--shadow-lg);
  }
  .close-btn {
    position: absolute; top: .75rem; right: .75rem;
    background: rgba(26,15,10,.5); border: none; color: var(--sand-300);
    width: 2rem; height: 2rem; border-radius: 50%; cursor: pointer;
    font-size: .9rem; z-index: 1; display: flex; align-items: center; justify-content: center;
    transition: background .15s;
  }
  .close-btn:hover { background: rgba(26,15,10,.8); }

  .hero { position: relative; }
  .hero-img { width: 100%; height: 240px; object-fit: cover; display: block; }
  .hero-grad {
    position: absolute; inset: 0;
    background: linear-gradient(to top, rgba(26,15,10,.9) 0%, transparent 50%);
  }
  .hero-info {
    position: absolute; bottom: 1rem; left: 1.25rem;
    display: flex; flex-direction: column; gap: .4rem;
  }
  .genre-tag {
    display: inline-block; background: var(--accent); color: #fff;
    padding: .2rem .7rem; border-radius: 1rem;
    font-size: .75rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
    width: fit-content;
  }
  h2 {
    font-family: 'Cinzel', serif;
    margin: 0; font-size: 1.4rem; color: var(--sand-100);
    text-shadow: 0 2px 8px rgba(0,0,0,0.5);
  }

  .body { padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
  .description { color: var(--text-secondary); line-height: 1.7; margin: 0; }

  .meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
  .meta-item { display: flex; flex-direction: column; gap: .25rem; }
  .meta-label { font-size: .72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: .08em; }
  .meta-value { font-weight: 700; color: var(--dusk-600); font-size: .95rem; }
  .price { color: var(--ember-400); font-size: 1.25rem; }

  .badge { padding: .2rem .65rem; border-radius: 1rem; font-size: .8rem; font-weight: 600; }
  .badge--active   { background: #dcfce7; color: #16a34a; }
  .badge--inactive { background: #fee2e2; color: #dc2626; }

  .accent-bottom { height: 4px; background: linear-gradient(90deg, var(--accent), transparent); }
</style>
