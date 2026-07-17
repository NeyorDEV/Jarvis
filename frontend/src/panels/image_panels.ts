// ── Panneaux images (HUD image générée + grilles de recherche flottantes) ──
// Extrait de main.ts.

import { makePanelDraggable } from "../ui/draggable";

export function showImageHUD(url: string, prompt: string) {
  const container = document.getElementById("image-hud")!;
  const img = document.getElementById("image-display") as HTMLImageElement;
  const promptEl = document.getElementById("image-prompt")!;
  const statusEl = document.getElementById("image-status")!;
  const scan = document.getElementById("image-scan")!;

  container.style.display = "block";
  img.style.opacity = "0";
  img.src = url;
  promptEl.textContent = `PROMPT: ${prompt}`;
  statusEl.textContent = "[RECONSTRUCTING_DATA...]";
  statusEl.style.color = "#ff3d00";
  scan.style.display = "block";

  // Scan animation
  let pos = 0;
  const scanInterval = setInterval(() => {
    pos += 5;
    scan.style.top = `${pos % 100}%`;
  }, 30);

  // Sécurité : Si l'image met trop de temps (15s), on arrête tout
  const timeout = setTimeout(() => {
    if (img.style.opacity === "0") {
      clearInterval(scanInterval);
      scan.style.display = "none";
      statusEl.textContent = "[ERROR: RECONSTRUCTION_FAILED]";
      statusEl.style.color = "#ff3d00";
      console.error("Timeout loading image:", url);
    }
  }, 15000);

  img.onload = () => {
    clearTimeout(timeout);
    setTimeout(() => {
      clearInterval(scanInterval);
      scan.style.display = "none";
      img.style.opacity = "1";
      statusEl.textContent = "[RECONSTRUCTION_COMPLETE]";
      statusEl.style.color = "#00e5ff";
    }, 2000);
  };

  img.onerror = () => {
    clearTimeout(timeout);
    clearInterval(scanInterval);
    scan.style.display = "none";
    statusEl.textContent = "[ERROR: SOURCE_UNREACHABLE]";
    statusEl.style.color = "#ff3d00";
    console.error("Failed to load image from URL:", url);
  };
}

document.getElementById("image-close")?.addEventListener("click", () => {
  document.getElementById("image-hud")!.style.display = "none";
});


// ── Image Panels Logic (Iron Man style floating panels) ──────────────────────
let imgPanelCount = 0;
let maxZIndex = 600;

export function showImagePanel(query: string, images: string[]) {
  const container = document.getElementById("image-panels-container");
  if (!container) return;

  const panel = document.createElement("div");
  panel.className = "img-panel";
  
  // Bring to front on mousedown
  panel.addEventListener("mousedown", () => {
    maxZIndex++;
    panel.style.zIndex = maxZIndex.toString();
  });

  // Calculate dynamic position with cascade offset
  const offset = (imgPanelCount % 6) * 30;
  const left = Math.max(20, (window.innerWidth - 420) / 2 + offset);
  const top = Math.max(20, (window.innerHeight - 380) / 2 + offset);
  panel.style.left = `${left}px`;
  panel.style.top = `${top}px`;
  imgPanelCount++;

  // Add scanlines, corners & structure
  panel.innerHTML = `
    <div class="img-panel-scanlines"></div>
    <div class="img-panel-corner-tr"></div>
    <div class="img-panel-corner-bl"></div>
    <div class="img-panel-header">
      <div class="img-panel-drag-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 9l7-7 7 7M5 15l7 7 7-7" />
        </svg>
      </div>
      <div class="img-panel-title">IMAGE_SCAN // ${query.toUpperCase()}</div>
      <button class="img-panel-close">&times;</button>
    </div>
    <div class="img-panel-status">
      <span>GRID STATUS: ACTIVE</span>
      <span class="img-panel-meta">FOUND: ${images.length} SECURE_NODES</span>
    </div>
    <div class="img-panel-grid"></div>
    <div class="img-panel-footer">
      <span>SYS.LOC: LOCAL_HUD</span>
      <span>JARVIS_V2.6</span>
    </div>
  `;

  // Populate grid
  const grid = panel.querySelector(".img-panel-grid") as HTMLElement;
  if (images.length === 0) {
    const empty = document.createElement("div");
    empty.style.gridColumn = "span 3";
    empty.style.padding = "20px";
    empty.style.textAlign = "center";
    empty.style.fontSize = "10px";
    empty.style.color = "rgba(0, 229, 255, 0.4)";
    empty.textContent = "NO SECURE NODE RESOLVED";
    grid.appendChild(empty);
  } else {
    images.forEach((url, index) => {
      const item = document.createElement("div");
      item.className = "img-panel-item";
      // Stagger animation delay
      item.style.animationDelay = `${index * 0.08}s`;
      
      const img = document.createElement("img");
      img.src = url;
      img.alt = query;
      img.loading = "lazy";
      
      // Handle image load error
      img.onerror = () => {
        img.src = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'><rect width='100' height='100' fill='rgba(0,8,20,0.8)'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-family='Courier, monospace' font-size='10' fill='%23ff3366'>LOAD_ERR</text></svg>";
      };

      item.appendChild(img);
      
      // Click for fullscreen zoom
      item.addEventListener("click", () => {
        showFullscreenImage(url, query);
      });

      grid.appendChild(item);
    });
  }

  // Setup close button
  const closeBtn = panel.querySelector(".img-panel-close") as HTMLElement;
  closeBtn.addEventListener("click", () => {
    panel.classList.remove("visible");
    setTimeout(() => {
      panel.remove();
    }, 400);
  });

  // Setup Drag & Drop
  const header = panel.querySelector(".img-panel-header") as HTMLElement;
  makePanelDraggable(panel, header);

  // Append & animate in
  container.appendChild(panel);
  
  // Trigger Reflow to animate opacity/scale
  void panel.offsetWidth;
  panel.classList.add("visible");
}

function showFullscreenImage(url: string, query: string) {
  const overlay = document.createElement("div");
  overlay.className = "img-zoom-overlay";

  overlay.innerHTML = `
    <button class="img-zoom-close">CLOSE [ESC]</button>
    <img src="${url}" alt="${query}" />
    <div class="img-zoom-label">RESOLVED NODE // ${query.toUpperCase()}</div>
  `;

  const closeOverlay = () => {
    overlay.remove();
    document.removeEventListener("keydown", handleEsc);
  };

  const handleEsc = (e: KeyboardEvent) => {
    if (e.key === "Escape") {
      closeOverlay();
    }
  };

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay || (e.target as HTMLElement).classList.contains("img-zoom-close")) {
      closeOverlay();
    }
  });

  document.addEventListener("keydown", handleEsc);
  document.body.appendChild(overlay);
}

