// ── Dock carrousel 3D des boutons HUD (boucle infinie, drag, molette) ──
// Extrait de main.ts. Tout est encapsulé dans initCarouselDock() pour
// conserver exactement l'ordre d'initialisation d'origine.

// Contrôles de la flèche exposés au mode hologramme (renseignés par initCarouselDock)
let _arrowControls: { hide: () => void; show: () => void } | null = null;

export function hideCarouselArrow(): void {
  _arrowControls?.hide();
}

export function showCarouselArrow(): void {
  _arrowControls?.show();
}

export function initCarouselDock(): void {
// ── Carousel toggle arrow ─────────────────────────────────────────────────────
const _carouselBar   = document.getElementById("hud-control-bar");
const _carouselArrow = document.getElementById("carousel-toggle-arrow") as HTMLButtonElement | null;

// Position JS directe — immunisé contre tout conflit CSS/stacking-context
// La flèche reste TOUJOURS à bottom:8px, seule son apparence change
function _positionArrow(open: boolean) {
  if (!_carouselArrow) return;
  const w = 36, h = 22;
  Object.assign(_carouselArrow.style, {
    position:   'fixed',
    left:       `${Math.round(window.innerWidth / 2 - w / 2)}px`,
    bottom:     open ? '32px' : '8px',
    width:      `${w}px`,
    height:     `${h}px`,
    zIndex:     '10010',
    display:    'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'rgba(0,8,20,0.75)',
    border:     `1px solid rgba(0,229,255,${open ? '0.7' : '0.35'})`,
    borderRadius: '4px',
    color:      open ? '#00e5ff' : 'rgba(0,229,255,0.6)',
    fontSize:   '16px',
    cursor:     'pointer',
    padding:    '0',
    lineHeight: '1',
    transform:  open ? 'rotate(180deg)' : 'none',
    transition: 'transform 0.25s ease, color 0.15s, border-color 0.15s',
  });
}

let _carouselOpen = false;

function _toggleCarousel(force?: boolean) {
  if (!_carouselBar) return;
  _carouselOpen = force !== undefined ? force : !_carouselOpen;
  _carouselBar.classList.toggle("carousel-hidden", !_carouselOpen);
  _positionArrow(_carouselOpen);
}

// Hover sur la flèche = toggle, debounce 300ms pour éviter le flash sur les bords
let _carouselLastToggle = 0;
_carouselArrow?.addEventListener("mouseenter", () => {
  const now = Date.now();
  if (now - _carouselLastToggle < 300) return;
  _carouselLastToggle = now;
  _toggleCarousel();
});

// Init — visible dès le départ (couvert par le boot overlay comme tous les autres éléments)
_positionArrow(false);
window.addEventListener("resize", () => _positionArrow(_carouselOpen));

// ── Carousel Controls for Button Bar (3D Dial / Cover Flow) ───────────────────
const track = document.getElementById("carousel-track");
const getCarouselButtons = () => Array.from(track ? track.getElementsByTagName("button") : []);

let activeIndex = 0;

function renderCarousel(progress = 0) {
  const buttons = getCarouselButtons();
  if (buttons.length === 0) return;

  // Index virtuel basé sur le drag ou scroll
  let virtualIndex = activeIndex - progress;
  
  // Limiter l'index pour ne pas défiler dans le vide
  virtualIndex = Math.max(0, Math.min(virtualIndex, buttons.length - 1));

  // Chaque bouton fait 120px de large + 15px de gap = 135px de décalage
  const buttonOffset = 135;
  const halfButtonWidth = 60; // 120px / 2

  if (track) {
    // Calcule la translation négative par rapport au left: 50% de la track
    track.style.transform = `translateX(-${(virtualIndex * buttonOffset) + halfButtonWidth}px)`;
  }

  // Arrondir l'index pour savoir quel bouton est actif visuellement
  const roundedActive = Math.round(virtualIndex);

  buttons.forEach((btn, idx) => {
    if (idx === roundedActive) {
      btn.classList.add("active");
      btn.style.opacity = "1";
    } else {
      btn.classList.remove("active");
      btn.style.opacity = "0.5";
    }
  });

  // Mettre à jour les points indicateurs
  const dots = document.querySelectorAll(".carousel-dot");
  const N = buttons.length / 3;
  dots.forEach((dot, idx) => {
    if (N > 0 && idx === (roundedActive % N)) {
      dot.classList.add("active");
    } else {
      dot.classList.remove("active");
    }
  });
}

function updateCarousel() {
  renderCarousel(0);
}

const indicatorsContainer = document.querySelector(".carousel-indicators");

function createIndicators() {
  if (!indicatorsContainer) return;
  indicatorsContainer.innerHTML = "";
  const buttons = getCarouselButtons();
  const N = buttons.length / 3;
  if (N === 0) return;

  for (let idx = 0; idx < N; idx++) {
    const dot = document.createElement("span");
    dot.className = `carousel-dot${(activeIndex % N) === idx ? " active" : ""}`;
    dot.setAttribute("data-page", idx.toString());
    dot.addEventListener("click", () => {
      activeIndex = N + idx; // Aligner sur la 2ème copie
      updateCarousel();
    });
    indicatorsContainer.appendChild(dot);
  }
}

const controlBar = document.getElementById("hud-control-bar");
let isPointerDown = false;
let startX = 0;
let wasDragging = false;

if (controlBar && track) {
  // Prevent native browser drag-and-drop and text selection on the carousel
  controlBar.addEventListener("dragstart", (e) => e.preventDefault());
  controlBar.addEventListener("selectstart", (e) => e.preventDefault());

  // 1. Capture click events in capture phase to prevent click action when dragging
  controlBar.addEventListener("click", (e) => {
    if (wasDragging) {
      e.preventDefault();
      e.stopPropagation();
      return;
    }

    const btn = (e.target as HTMLElement).closest("button");
    if (!btn) return;

    const buttons = getCarouselButtons();
    const idx = buttons.indexOf(btn);
    if (idx !== -1 && idx !== activeIndex) {
      activeIndex = idx;
      updateCarousel();
    }
  }, true); // Use capture phase!

  // 2. Pointer down listener (on controlBar)
  controlBar.addEventListener("pointerdown", (e) => {
    if (e.button !== 0) return; // Only trigger for primary click / touch
    isPointerDown = true;
    startX = e.clientX;
    wasDragging = false;
  });

  // 3. Pointer move listener (on document to avoid setPointerCapture issues blocking clicks)
  document.addEventListener("pointermove", (e) => {
    if (!isPointerDown) return;
    const dx = e.clientX - startX;
    if (Math.abs(dx) > 8) {
      if (!wasDragging) {
        wasDragging = true;
        // Disable transitions on buttons during drag for instant responsiveness
        const buttons = getCarouselButtons();
        buttons.forEach(btn => btn.style.transition = "none");
      }
    }
    if (wasDragging) {
      const progress = dx / 150; // swipe factor based on 150px spacing
      renderCarousel(progress);
    }
  });

  // 4. Pointer up listener (on document)
  document.addEventListener("pointerup", (e) => {
    if (!isPointerDown) return;
    isPointerDown = false;

    // Re-enable CSS transitions on buttons for smooth snapback
    const buttons = getCarouselButtons();
    buttons.forEach(btn => btn.style.transition = "");

    const dx = e.clientX - startX;
    const len = buttons.length;

    if (len > 0 && wasDragging) {
      const progress = dx / 150;
      const offset = Math.round(-progress);
      activeIndex = (activeIndex + offset) % len;
      if (activeIndex < 0) activeIndex += len;
    }

    updateCarousel();

    if (wasDragging) {
      // Delay resetting wasDragging slightly to ensure click event is blocked
      setTimeout(() => {
        wasDragging = false;
      }, 50);
    }
  });

  // 5. Pointer cancel listener (on document)
  document.addEventListener("pointercancel", () => {
    isPointerDown = false;
    const buttons = getCarouselButtons();
    buttons.forEach(btn => btn.style.transition = "");
    updateCarousel();
    wasDragging = false;
  });

  // 6. Scroll wheel listener (on controlBar)
  controlBar.addEventListener("wheel", (e) => {
    e.preventDefault();
    const buttons = getCarouselButtons();
    const len = buttons.length;
    if (len === 0) return;
    if (e.deltaY > 0) {
      activeIndex = (activeIndex + 1) % len;
    } else {
      activeIndex = (activeIndex - 1 + len) % len;
    }
    updateCarousel();
    setTimeout(() => checkInfiniteBoundaries(), 400);
  }, { passive: false });
}

// ── FONCTIONS POUR LA BOUCLE INFINIE DU CAROUSEL (3 COPIES) ──
function checkInfiniteBoundaries() {
  const buttons = getCarouselButtons();
  const N = buttons.length / 3;
  if (N === 0) return;
  
  let snapped = false;
  if (activeIndex < N) {
    activeIndex += N;
    snapped = true;
  } else if (activeIndex >= 2 * N) {
    activeIndex -= N;
    snapped = true;
  }
  
  if (snapped && track) {
    const prevTransition = track.style.transition;
    track.style.transition = "none";
    const buttonOffset = 135;
    const halfButtonWidth = 60;
    track.style.transform = `translateX(-${(activeIndex * buttonOffset) + halfButtonWidth}px)`;
    track.offsetHeight; // Forcer reflow
    track.style.transition = prevTransition;
  }
}

function initInfiniteCarousel() {
  if (!track) return;
  const originalButtons = Array.from(track.children) as HTMLButtonElement[];
  const N = originalButtons.length;
  if (N === 0) return;

  // Assigner l'attribut data-original-id
  originalButtons.forEach(btn => {
    btn.setAttribute("data-original-id", btn.id);
  });

  // Vider et dupliquer en 3 copies
  track.innerHTML = "";
  for (let c = 0; c < 3; c++) {
    originalButtons.forEach(btn => {
      const clone = btn.cloneNode(true) as HTMLButtonElement;
      track.appendChild(clone);
    });
  }

  // Démarrer au début de la 2ème copie
  activeIndex = N;

  // Gérer la fin de transition pour le snap invisible
  track.addEventListener("transitionend", () => {
    checkInfiniteBoundaries();
  });
}

// Initialize
initInfiniteCarousel();
createIndicators();
updateCarousel();

// Exposer les contrôles de la flèche pour le mode hologramme
_arrowControls = {
  hide: () => { if (_carouselArrow) _carouselArrow.style.display = "none"; },
  show: () => { if (_carouselArrow) { _carouselArrow.style.display = "flex"; _positionArrow(_carouselOpen); } },
};


}
