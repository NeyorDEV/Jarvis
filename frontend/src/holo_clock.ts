/**
 * J.A.R.V.I.S — Sleek & Modern 2D Clock HUD
 * Version épurée minimale : Heures, minutes et secondes sur une ligne, avec deux traits décoratifs en dessous.
 */

export function initHoloClock(): void {
  const container = document.getElementById('holo-clock-canvas-wrap');
  if (!container) return;

  // Nettoyer l'ancien canvas Three.js s'il existe
  const oldCanvas = document.getElementById('holo-clock-canvas');
  if (oldCanvas) {
    oldCanvas.remove();
  }

  // Injecter la structure HTML de l'horloge minimale avec les deux traits décoratifs sous l'heure
  container.innerHTML = `
    <div class="refined-clock-hud">
      <div class="clock-time-display">
        <span id="refined-h">00</span>
        <span class="refined-colon">:</span>
        <span id="refined-m">00</span>
        <span class="refined-colon-sec">:</span>
        <span id="refined-s" class="refined-sec">00</span>
      </div>
      <div class="clock-decorations">
        <div class="clock-line-decor"></div>
        <span class="clock-status-dot"></span>
        <div class="clock-line-decor"></div>
      </div>
    </div>
  `;

  const hEl = document.getElementById('refined-h');
  const mEl = document.getElementById('refined-m');
  const sEl = document.getElementById('refined-s');
  const clockHud = container.querySelector('.refined-clock-hud') as HTMLDivElement | null;

  function updateClock() {
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');

    if (hEl && hEl.textContent !== h) hEl.textContent = h;
    if (mEl && mEl.textContent !== m) mEl.textContent = m;
    if (sEl && sEl.textContent !== s) sEl.textContent = s;

    // Synchroniser le thème de couleur avec l'orbe JARVIS
    if (clockHud) {
      const savedOrbStyle = localStorage.getItem("jarvis-orb-style") || "cyan";
      if (!clockHud.classList.contains(`theme-${savedOrbStyle}`)) {
        clockHud.className = "refined-clock-hud";
        clockHud.classList.add(`theme-${savedOrbStyle}`);
      }
    }
  }

  // Boucle de mise à jour légère (200ms)
  updateClock();
  setInterval(updateClock, 200);
}
