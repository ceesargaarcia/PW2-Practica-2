<script>
  import { toasts } from '../lib/toasts.svelte.js';
</script>

<div class="toast-container" aria-live="polite">
  {#each toasts as toast (toast.id)}
    <div class="toast toast--{toast.type}" role="alert">
      <span class="toast-icon">
        {#if toast.type === 'success'}✦{:else if toast.type === 'error'}✕{:else}◈{/if}
      </span>
      <span class="toast-msg">{toast.message}</span>
    </div>
  {/each}
</div>

<style>
  .toast-container {
    position: fixed; bottom: 1.5rem; right: 1.5rem;
    display: flex; flex-direction: column; gap: .5rem; z-index: 9999;
  }
  .toast {
    display: flex; align-items: center; gap: .6rem;
    padding: .75rem 1.25rem; border-radius: var(--radius-sm);
    font-size: .875rem; font-weight: 500;
    box-shadow: var(--shadow-lg);
    animation: slide-in .2s ease;
    max-width: 340px; border: 1px solid transparent;
  }
  .toast--success {
    background: var(--dusk-700); color: var(--sand-200);
    border-color: var(--sand-600);
  }
  .toast--error {
    background: #450a0a; color: #fca5a5;
    border-color: var(--ember-600);
  }
  .toast--info {
    background: var(--dusk-700); color: var(--sand-300);
    border-color: var(--dusk-500);
  }
  .toast-icon { font-size: .9rem; flex-shrink: 0; opacity: .8; }
  @keyframes slide-in {
    from { opacity: 0; transform: translateX(40px); }
    to   { opacity: 1; transform: translateX(0); }
  }
</style>
