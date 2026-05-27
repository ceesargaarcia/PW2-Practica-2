<script>
  import { untrack } from 'svelte';

  // $props()
  let { product = null, onSave, onCancel } = $props();

  const GENRES = ['Acción','RPG','Aventura','Estrategia','Deportes','Terror','Simulación','Puzzle','Otros'];

  let form = $state(untrack(() => ({
    name:        product?.name        ?? '',
    description: product?.description ?? '',
    price:       product?.price       ?? '',
    category:    product?.category    ?? '',
    stock:       product?.stock       ?? 0,
    active:      product?.active      ?? true,
    imageUrl:    product?.imageUrl    ?? '',
  })));

  let errors  = $state({});
  let saving  = $state(false);

  // $derived()
  const title     = $derived(product ? 'Editar juego' : 'Añadir juego');
  const hasErrors = $derived(Object.keys(errors).length > 0);

  function validate() {
    const e = {};
    if (!form.name.trim())        e.name        = 'El título es obligatorio';
    if (!form.description.trim()) e.description = 'La descripción es obligatoria';
    if (form.price === '' || isNaN(Number(form.price)) || Number(form.price) < 0)
      e.price = 'Precio inválido (≥ 0)';
    if (!form.category)           e.category    = 'Selecciona un género';
    if (isNaN(Number(form.stock)) || Number(form.stock) < 0)
      e.stock = 'Stock inválido (≥ 0)';
    errors = e;
    return !hasErrors;
  }

  async function handleSubmit() {
    if (!validate()) return;
    saving = true;
    try {
      await onSave({
        ...form,
        price: Number(form.price),
        stock: Number(form.stock),
      });
    } finally {
      saving = false;
    }
  }
</script>

<div class="overlay" onclick={onCancel} role="presentation"></div>

<dialog open class="modal" aria-modal="true" aria-labelledby="form-title">
  <div class="modal-header">
    <h2 id="form-title">{title}</h2>
    <button class="close-btn" onclick={onCancel} aria-label="Cerrar">✕</button>
  </div>

  <div class="form-body">
    <div class="field">
      <label for="f-name">Título del juego *</label>
      <input id="f-name" bind:value={form.name} placeholder="Ej: Desert Raiders II" />
      {#if errors.name}<p class="err">{errors.name}</p>{/if}
    </div>

    <div class="field">
      <label for="f-desc">Descripción *</label>
      <textarea id="f-desc" rows="3" bind:value={form.description} placeholder="Describe la aventura…"></textarea>
      {#if errors.description}<p class="err">{errors.description}</p>{/if}
    </div>

    <div class="row">
      <div class="field">
        <label for="f-price">Precio (€) *</label>
        <input id="f-price" type="number" min="0" step="0.01" bind:value={form.price} placeholder="0.00" />
        {#if errors.price}<p class="err">{errors.price}</p>{/if}
      </div>
      <div class="field">
        <label for="f-stock">Unidades en stock *</label>
        <input id="f-stock" type="number" min="0" bind:value={form.stock} />
        {#if errors.stock}<p class="err">{errors.stock}</p>{/if}
      </div>
    </div>

    <div class="field">
      <label for="f-cat">Género *</label>
      <select id="f-cat" bind:value={form.category}>
        <option value="" disabled>Selecciona un género…</option>
        {#each GENRES as g}
          <option value={g}>{g}</option>
        {/each}
      </select>
      {#if errors.category}<p class="err">{errors.category}</p>{/if}
    </div>

    <div class="field">
      <label for="f-img">URL de carátula</label>
      <input id="f-img" bind:value={form.imageUrl} placeholder="https://…" />
    </div>

    <label class="toggle-wrap">
      <input id="f-active" type="checkbox" bind:checked={form.active} class="sr-only" />
      <div class="toggle {form.active ? 'toggle--on' : ''}">
        <div class="toggle-thumb"></div>
      </div>
      <span>{form.active ? 'Juego disponible' : 'No disponible'}</span>
    </label>
  </div>

  <div class="modal-footer">
    <button class="btn-cancel" onclick={onCancel} disabled={saving}>Cancelar</button>
    <button class="btn-save" onclick={handleSubmit} disabled={saving}>
      {#if saving}
        <span class="spinner"></span> Guardando…
      {:else}
        {product ? '✦ Actualizar' : '✦ Publicar juego'}
      {/if}
    </button>
  </div>
</dialog>

<style>
  .overlay { position: fixed; inset: 0; background: rgba(26,15,10,.65); z-index: 200; backdrop-filter: blur(4px); }
  .modal {
    position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
    z-index: 201; background: var(--bone); border: 1px solid var(--sand-300);
    border-radius: var(--radius); border: none;
    padding: 0; width: min(540px, 95vw); max-height: 90vh; overflow-y: auto;
    box-shadow: var(--shadow-lg);
  }
  .modal-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.5rem 1.5rem 0;
  }
  h2 { font-family: 'Cinzel', serif; font-size: 1.15rem; color: var(--dusk-700); margin: 0; }
  .close-btn {
    background: none; border: none; font-size: 1rem; cursor: pointer;
    color: var(--text-muted); width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
  }
  .close-btn:hover { background: var(--sand-200); }

  .form-body { padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: .9rem; }
  .field { display: flex; flex-direction: column; gap: .3rem; }
  label { font-size: .8rem; font-weight: 600; color: var(--text-secondary); letter-spacing: .04em; text-transform: uppercase; }
  input, textarea, select {
    padding: .6rem .8rem; border: 1.5px solid var(--sand-300);
    border-radius: var(--radius-sm); font-size: .92rem;
    background: #fff; color: var(--text-primary);
    width: 100%; transition: border-color .15s;
  }
  input:focus, textarea:focus, select:focus { outline: none; border-color: var(--sand-500); }
  select option { background: #fff; color: var(--text-primary); }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
  .err { color: var(--ember-500); font-size: .78rem; margin: 0; }

  .sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); }
  .toggle-wrap {
    display: flex; align-items: center; gap: .75rem; cursor: pointer;
    font-size: .875rem; color: var(--text-secondary); font-weight: 500;
    text-transform: none; letter-spacing: 0;
  }
  .toggle {
    width: 42px; height: 24px; border-radius: 12px;
    background: var(--sand-300); position: relative; transition: background .2s; flex-shrink: 0;
  }
  .toggle--on { background: #16a34a; }
  .toggle-thumb {
    position: absolute; top: 2px; left: 2px;
    width: 20px; height: 20px; border-radius: 50%; background: #fff;
    transition: transform .2s; box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  }
  .toggle--on .toggle-thumb { transform: translateX(18px); }

  .modal-footer {
    display: flex; justify-content: flex-end; gap: .75rem;
    padding: 1rem 1.5rem 1.5rem;
    border-top: 1px solid var(--sand-200);
  }
  .btn-cancel {
    background: transparent; border: 1.5px solid var(--sand-300);
    color: var(--text-secondary); padding: .6rem 1.25rem;
    border-radius: var(--radius-sm); cursor: pointer; font-size: .9rem;
  }
  .btn-cancel:hover:not(:disabled) { background: var(--sand-200); }
  .btn-save {
    background: linear-gradient(135deg, var(--ember-400), var(--ember-500));
    border: none; color: #fff; padding: .6rem 1.5rem;
    border-radius: var(--radius-sm); cursor: pointer; font-size: .9rem; font-weight: 700;
    box-shadow: 0 4px 16px rgba(232,93,4,0.35);
    display: flex; align-items: center; gap: .5rem; transition: all .2s;
  }
  .btn-save:hover:not(:disabled) { filter: brightness(1.1); transform: translateY(-1px); }
  .btn-save:disabled, .btn-cancel:disabled { opacity: .6; cursor: not-allowed; }

  .spinner {
    width: 14px; height: 14px; border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff;
    animation: spin .7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
