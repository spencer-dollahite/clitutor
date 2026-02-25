/** Simple toast notification system. */

let container: HTMLElement | null = null;

function ensureContainer(): HTMLElement {
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }
  return container;
}

export function showToast(
  message: string,
  type: "success" | "error" | "info" = "info",
  duration = 3000,
): void {
  const parent = ensureContainer();
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  parent.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, duration);
}
