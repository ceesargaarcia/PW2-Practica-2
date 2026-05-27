// Notificaciones toast globales con $state
export const toasts = $state([]);

let _id = 0;

export function addToast(message, type = 'success', duration = 3500) {
  const id = ++_id;
  toasts.push({ id, message, type });
  setTimeout(() => {
    const idx = toasts.findIndex(t => t.id === id);
    if (idx !== -1) toasts.splice(idx, 1);
  }, duration);
}
