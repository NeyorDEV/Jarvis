// ── Drag & Drop utilitaires (widgets HUD et panneaux) ───────────────────────
// Extrait de main.ts — comportement identique.

export function makeDraggable(el: HTMLElement): void {
  let dragging = false;
  let startMouseX = 0, startMouseY = 0;
  let startLeft = 0, startTop = 0;

  el.addEventListener("mousedown", (e: MouseEvent) => {
    // Ignorer les clics sur boutons, inputs, etc.
    if ((e.target as HTMLElement).closest("button, input, select, a, svg")) return;

    // Ignorer si on clique dans la zone de redimensionnement (coin inférieur droit)
    const rect = el.getBoundingClientRect();
    if (rect.right - e.clientX < 20 && rect.bottom - e.clientY < 20) return;

    e.preventDefault();
    dragging = true;

    // Convertir right/bottom en left/top absolus pour pouvoir déplacer librement
    el.style.transition = "none";
    el.style.animation  = "none";
    el.style.right      = "auto";
    el.style.bottom     = "auto";
    el.style.transform  = "none";
    el.style.position   = "fixed";
    el.style.left       = `${rect.left}px`;
    el.style.top        = `${rect.top}px`;
    el.style.zIndex     = "500";

    startMouseX = e.clientX;
    startMouseY = e.clientY;
    startLeft   = rect.left;
    startTop    = rect.top;

    document.body.style.userSelect = "none";
    el.style.cursor = "grabbing";
  });

  document.addEventListener("mousemove", (e: MouseEvent) => {
    if (!dragging) return;

    let newLeft = startLeft + (e.clientX - startMouseX);
    let newTop  = startTop  + (e.clientY - startMouseY);

    // Rester dans les limites de l'écran (20px de marge)
    newLeft = Math.max(10, Math.min(window.innerWidth  - el.offsetWidth  - 10, newLeft));
    newTop  = Math.max(10, Math.min(window.innerHeight - el.offsetHeight - 10, newTop));

    el.style.left = `${newLeft}px`;
    el.style.top  = `${newTop}px`;
  });

  document.addEventListener("mouseup", () => {
    if (!dragging) return;
    dragging = false;
    document.body.style.userSelect = "";
    el.style.cursor = "grab";
    el.style.zIndex = "70";
  });
}

export function makePanelDraggable(panel: HTMLElement, header: HTMLElement) {
  let isDragging = false;
  let offsetX = 0;
  let offsetY = 0;

  header.style.cursor = "grab";

  header.addEventListener("mousedown", (e) => {
    isDragging = true;
    const rect = panel.getBoundingClientRect();
    panel.style.left      = `${rect.left}px`;
    panel.style.top       = `${rect.top}px`;
    panel.style.right     = "auto";
    panel.style.bottom    = "auto";
    panel.style.transform = "none";
    offsetX = e.clientX - rect.left;
    offsetY = e.clientY - rect.top;
    header.style.cursor = "grabbing";
    e.preventDefault();
  });

  document.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    const newX = Math.max(0, Math.min(e.clientX - offsetX, window.innerWidth  - panel.offsetWidth));
    const newY = Math.max(0, Math.min(e.clientY - offsetY, window.innerHeight - panel.offsetHeight));
    panel.style.left = `${newX}px`;
    panel.style.top  = `${newY}px`;
  });

  document.addEventListener("mouseup", () => {
    if (isDragging) { isDragging = false; header.style.cursor = "grab"; }
  });
}
