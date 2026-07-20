// ── Effets visuels du HUD (auras ambiantes, boutons magnétiques) — extrait de main.ts ──

// ── Dynamic Ambient Glow Management ──────────────────────────────────────────
export function initDynamicAmbientGlow() {
  const container = document.querySelector(".ambient-glow-auras") as HTMLDivElement | null;
  if (!container) return;

  // Couleurs d'auras possibles
  const GLOW_COLORS = [
    "rgba(0, 229, 255, 0.16)", // Cyan
    "rgba(0, 110, 255, 0.14)", // Bleu électrique
    "rgba(189, 83, 237, 0.12)", // Violet
    "rgba(0, 255, 136, 0.11)"  // Vert émeraude
  ];

  function spawnAura() {
    if (!container) return;
    // Si on a déjà 3 auras actives, on ne fait rien
    if (container.children.length >= 3) return;

    const aura = document.createElement("div");
    aura.className = "glow-aura";
    
    // Propriétés aléatoires de taille et d'effet
    const size = Math.floor(Math.random() * 350) + 550; // Entre 550px et 900px
    const color = GLOW_COLORS[Math.floor(Math.random() * GLOW_COLORS.length)];
    const blur = Math.floor(Math.random() * 35) + 85; // Entre 85px et 120px
    
    // Position initiale aléatoire (sur tout l'écran)
    const startX = Math.random() * window.innerWidth;
    const startY = Math.random() * window.innerHeight;
    
    // Destination aléatoire pour la dérive
    const destX = Math.random() * window.innerWidth;
    const destY = Math.random() * window.innerHeight;
    
    // Application des styles initiaux
    aura.style.width = `${size}px`;
    aura.style.height = `${size}px`;
    aura.style.left = `${startX - size / 2}px`;
    aura.style.top = `${startY - size / 2}px`;
    aura.style.background = `radial-gradient(circle, ${color} 0%, rgba(0,0,0,0) 70%)`;
    aura.style.filter = `blur(${blur}px)`;
    aura.style.opacity = "0";
    
    // Transition fluide (8s pour le fondu, 55s pour le déplacement)
    aura.style.transition = "opacity 8s ease-in-out, transform 55s cubic-bezier(0.1, 0.25, 0.1, 1)";
    
    container.appendChild(aura);
    
    // 1. Débuter l'apparition et la dérive après injection
    setTimeout(() => {
      aura.style.opacity = "0.9";
      aura.style.transform = `translate(${destX - startX}px, ${destY - startY}px) scale(${Math.random() * 0.4 + 0.8})`;
    }, 100);
    
    // 2. Cycle de vie : fondu sortant après une durée de vie aléatoire (20 à 38 secondes)
    const lifeTime = (Math.random() * 18 + 20) * 1000;
    
    setTimeout(() => {
      aura.style.opacity = "0";
      // Retirer du DOM une fois le fondu terminé
      setTimeout(() => {
        aura.remove();
      }, 8500);
    }, lifeTime);
  }

  // Intervalle régulateur : décide s'il faut ajuster les auras vers une cible aléatoire (0 à 3)
  setInterval(() => {
    if (!container) return;
    const targetCount = Math.floor(Math.random() * 4); // 0, 1, 2 ou 3 auras
    const currentCount = container.children.length;
    
    if (currentCount < targetCount) {
      spawnAura();
    }
  }, 7000);

  // Instancier 1 à 2 auras initiales pour donner vie directement à l'écran
  const initCount = Math.floor(Math.random() * 2) + 1; // 1 ou 2 auras
  for (let i = 0; i < initCount; i++) {
    spawnAura();
  }
}

// ── Magnetic Buttons (Micro-Interactions Aimantées à distance) ────────────────
export function initMagneticButtons() {
  const buttons = document.querySelectorAll(
    ".carousel-track > button, #jarvis-menu-btn, #mic-btn, .menu-action-btn, #keyboard-toggle, #gestures-mirror, #fullscreen-btn"
  );

  const MAGNET_RADIUS = 60; // Zone d'attraction magnétique plus serrée (60px)

  document.addEventListener("mousemove", (e) => {
    const mouseX = e.clientX;
    const mouseY = e.clientY;

    buttons.forEach(btn => {
      const button = btn as HTMLElement;
      // Ne pas magnetiser si le bouton est caché
      if (button.offsetWidth === 0 || button.offsetHeight === 0) return;

      const rect = button.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      // Distance euclidienne entre la souris et le centre du bouton
      const dx = mouseX - centerX;
      const dy = mouseY - centerY;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < MAGNET_RADIUS) {
        // Le curseur est entré dans le rayon magnétique
        const proximity = 1 - distance / MAGNET_RADIUS; // Entre 0 (bord) et 1 (centre)
        const strength = proximity * 0.18; // Attraction très subtile de 18% max de la distance

        // Transition ultra-courte pendant le mouvement pour fluidifier le glissement
        button.style.transition = "transform 0.12s cubic-bezier(0.25, 1, 0.5, 1)";
        button.style.transform = `translate(${dx * strength}px, ${dy * strength}px) scale(${1 + proximity * 0.03})`;
        button.setAttribute("data-magnetized", "true");
      } else {
        // En dehors du champ, on réinitialise s'il était actif
        if (button.getAttribute("data-magnetized") === "true") {
          button.style.transition = "transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)";
          button.style.transform = "translate(0px, 0px) scale(1)";
          button.removeAttribute("data-magnetized");
        }
      }
    });
  });
}

