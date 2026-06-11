/**
 * J.A.R.V.I.S — Interface Web avec Orbe Three.js
 *
 * Se connecte au backend Python via WebSocket (ws://localhost:8765),
 * recoit les changements d'etat et pilote l'orbe en consequence.
 *
 * Etats: "idle" | "listening" | "thinking" | "speaking"
 */

import { createOrb, type OrbState } from "./orb";
import { injectVisionButton, captureFrame } from "./screen_capture";
import { initJarvisGlobe } from "./globe";
import { initWidgets, updateWeatherUI, updateMusicUI } from "./widgets";
import { cardManager } from "./cards";
import { initHoloClock } from "./holo_clock";
import { initHandTracking, toggleHandTracking, toggleArMirror } from "./hand_tracking";
import { activerHolo, desactiverHolo } from "./hologramme";
import { SpatialFileExplorer } from "./spatial_explorer";
import { DomoticMap } from "./domotic_map";
import { CortexMap } from "./cortex_map";

// Expose SpatialFileExplorer class globally for hologramme.js
(window as any).SpatialFileExplorer = SpatialFileExplorer;
(window as any).DomoticMap = DomoticMap;
(window as any).CortexMap = CortexMap;
import "./style.css";
import "./widgets.css";

// ── Config ────────────────────────────────────────────────────────────────────
const WS_URL = `ws://${window.location.hostname}:8765`;
const RECONNECT_INTERVAL_MS = 2_000;

// ── Boot sequence state ───────────────────────────────────────────────────────
let bootConnectedCallback: (() => void) | null = null;
let wsConnectedBeforeBoot = false;

// ── DOM refs ──────────────────────────────────────────────────────────────────
const canvas = document.getElementById("orb-canvas") as HTMLCanvasElement;
const statusEl = document.getElementById("status-text") as HTMLDivElement;
const errorEl = document.getElementById("error-text") as HTMLDivElement;
const badgeEl = document.getElementById("connection-badge") as HTMLDivElement;
const badgeLabelEl = document.getElementById(
  "connection-label"
) as HTMLSpanElement;
const muteButtonEl = document.getElementById("mute-button") as HTMLButtonElement;
const micBtnEl = document.getElementById("mic-btn") as HTMLButtonElement;
const gpuButtonEl = document.getElementById("gpu-button") as HTMLButtonElement;
const helpOverlayEl = document.getElementById("help-overlay") as HTMLDivElement;
const timerHudEl = document.getElementById("timer-hud") as HTMLDivElement;
const timerDisplayEl = document.getElementById("timer-display") as HTMLDivElement;
const timerProgressEl = document.getElementById("timer-progress") as HTMLDivElement;
const subtitleToggleButtonEl = document.getElementById("subtitle-toggle") as HTMLButtonElement;
const keyboardToggleButtonEl = document.getElementById("keyboard-toggle") as HTMLButtonElement;
const keyboardHudEl = document.getElementById("keyboard-hud") as HTMLDivElement;
const keyboardInputEl = document.getElementById("keyboard-input") as HTMLInputElement;
const visualizerHudEl = document.getElementById("visualizer-hud") as HTMLDivElement;

const settingsButtonEl = document.getElementById("settings-button") as HTMLButtonElement;
const settingsModalEl = document.getElementById("settings-modal") as HTMLDivElement;
const holoButtonEl = document.getElementById("holo-button") as HTMLButtonElement;
const settingsCloseBtn = document.getElementById("settings-close-btn") as HTMLSpanElement;
const settingsNameEl = document.getElementById("settings-name") as HTMLInputElement;
const settingsAgeEl = document.getElementById("settings-age") as HTMLInputElement;
const settingsAppsListEl = document.getElementById("settings-apps-list") as HTMLDivElement;
const appAddNameEl = document.getElementById("app-add-name") as HTMLInputElement;
const appAddPathEl = document.getElementById("app-add-path") as HTMLInputElement;
const appAddBtn = document.getElementById("app-add-btn") as HTMLButtonElement;
const settingsSaveBtn = document.getElementById("settings-save-btn") as HTMLButtonElement;

// New settings fields DOM refs
const settingsMicSelect = document.getElementById("settings-mic") as HTMLSelectElement;
const settingsCameraSelect = document.getElementById("settings-camera") as HTMLSelectElement;
const settingsMusiqueLien = document.getElementById("settings-musique-lien") as HTMLInputElement;
const haAddBtn = document.getElementById("ha-add-btn") as HTMLButtonElement;
const haAddNom = document.getElementById("ha-add-nom") as HTMLInputElement;
const haAddEntity = document.getElementById("ha-add-entity") as HTMLInputElement;
const haEntitiesListEl = document.getElementById("ha-entities-list") as HTMLDivElement;

let currentCustomApps: { id: string, label: string, exe_path: string }[] = [];
let currentCustomLights: { name: string, entity_id: string }[] = [];
let currentCustomPrises: { name: string, entity_id: string }[] = [];
let currentCustomCapteurs: { name: string, entity_id: string }[] = [];
let activeHaTab: "lumieres" | "prises" | "capteurs" = "lumieres";

let subtitlesEnabled = true;
let keyboardEnabled = false;

let timerInterval: number | null = null;
let timerSeconds = 0;
let timerTotalSeconds = 0;

const HELP_COMMANDS = [
  "Affiche la terre",
  "Où se trouve Tokyo ?",
  "Trace l'itinéraire Paris à Lyon",
  "Quelle heure est-il ?",
  "Ouvre Spotify",
  "Mets de la musique",
  "Prends une capture d'écran",
  "Mets en pause la lecture",
  "Augmente le volume",
  "Ferme le globe",
  "Lance une recherche sur YouTube",
  "Quelle est la météo ?",
  "Rappelle-moi de faire les courses",
  "Vérifie mes e-mails",
  "Raconte-moi une blague",
  "Lance le mode protocole",
  "Vérifie l'état du système",
  "Analyse les fichiers récents",
  "Active la vision",
  "Ouvre mon dossier Bureau",
  "Quel temps fait-il à New York ?",
  "Cherche sur Wikipédia l'intelligence artificielle",
  "Mets le volume à 50%",
  "Quelles sont les dernières news ?",
  "Lance le téléchargement",
  "Convertis ce fichier en PDF",
  "Ouvre mon TikTok",
  "Montre-moi les photos de vacances"
];

// ── Orb ───────────────────────────────────────────────────────────────────────
const orb = createOrb(canvas);
initHoloClock();

// Load and apply the saved color theme
const savedTheme = localStorage.getItem("jarvis-orb-theme") || "cyan";
orb.setTheme(savedTheme);

// Initialize select element value
const orbThemeSelect = document.getElementById("settings-orb-theme") as HTMLSelectElement;
if (orbThemeSelect) {
  orbThemeSelect.value = savedTheme;
}

// ── State labels (French) ────────────────────────────────────────────────────
const STATE_LABELS: Record<OrbState, string> = {
  idle: "",
  listening: "ecoute...",
  thinking: "reflexion...",
  speaking: "",
};

function applyState(state: OrbState): void {
  orb.setState(state);
  statusEl.textContent = STATE_LABELS[state];

  // Logic for the Visualizer Bar (guarded — element removed in V5)
  if (state === "listening" || state === "thinking") {
    visualizerHudEl?.classList.add("visible");
    visualizerHudEl?.classList.toggle("listening", state === "listening");
    visualizerHudEl?.classList.toggle("thinking", state === "thinking");
  } else {
    visualizerHudEl?.classList.remove("visible", "listening", "thinking");
  }
}

function setMuted(muted: boolean): void {
  // mic-btn reflects mic mute state (red = muted)
  if (micBtnEl) {
    micBtnEl.classList.toggle("is-muted", muted);
    micBtnEl.setAttribute("aria-pressed", String(muted));
    micBtnEl.title = muted ? "Micro coupé — Cliquez pour réactiver" : "Cliquez pour couper le micro";
  }
}

// ── Error toast ───────────────────────────────────────────────────────────────
let errorTimer: ReturnType<typeof setTimeout> | null = null;

function showError(msg: string): void {
  errorEl.textContent = msg;
  errorEl.style.opacity = "1";
  if (errorTimer) clearTimeout(errorTimer);
  errorTimer = setTimeout(() => {
    errorEl.style.opacity = "0";
  }, 4_000);
}

// ── Connection badge ──────────────────────────────────────────────────────────
function setConnected(ok: boolean): void {
  badgeEl.classList.toggle("connected", ok);
  badgeEl.classList.toggle("disconnected", !ok);
  badgeLabelEl.textContent = ok ? "connecte" : "reconnexion";
  muteButtonEl.disabled = !ok;
  if (micBtnEl) micBtnEl.disabled = !ok;
}



// ── Virtual Cursor for Dynamic HUD Automation ──────────────────────────────────
let virtualCursorHideTimeout: ReturnType<typeof setTimeout> | null = null;

function initVirtualCursor(): HTMLDivElement | null {
  let cursor = document.getElementById("virtual-cursor") as HTMLDivElement;
  if (!cursor) {
    cursor = document.createElement("div");
    cursor.id = "virtual-cursor";
    document.body.appendChild(cursor);
  }
  return cursor;
}

function getElementCoordinates(el: HTMLElement): Promise<{x: number, y: number}> {
  return new Promise((resolve) => {
    let attempts = 0;
    const check = () => {
      const r = el.getBoundingClientRect();
      if ((r.width > 0 && r.height > 0) || (r.left > 0 || r.top > 0) || attempts > 15) {
        resolve({
          x: r.left + r.width / 2 + window.scrollX,
          y: r.top + r.height / 2 + window.scrollY
        });
      } else {
        attempts++;
        setTimeout(check, 50);
      }
    };
    check();
  });
}

function animateVirtualCursorTo(element: HTMLElement): Promise<void> {
  return new Promise(async (resolve) => {
    const cursor = initVirtualCursor();
    if (!cursor) {
      resolve();
      return;
    }

    if (virtualCursorHideTimeout) {
      clearTimeout(virtualCursorHideTimeout);
      virtualCursorHideTimeout = null;
    }

    if (cursor.style.display !== "block") {
      cursor.style.left = `${window.innerWidth / 2}px`;
      cursor.style.top = `${window.innerHeight / 2}px`;
      cursor.style.display = "block";
      // FORCE UN REFLOW pour garantir que la position de départ (milieu) soit peinte et prise en compte
      cursor.offsetHeight;
    }

    const coords = await getElementCoordinates(element);

    setTimeout(() => {
      cursor.style.left = `${coords.x}px`;
      cursor.style.top = `${coords.y}px`;
      
      setTimeout(resolve, 800);
    }, 50);
  });
}

// ── WebSocket with auto-reconnect ─────────────────────────────────────────────
let ws: WebSocket | null = null;
let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

function connect(): void {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }

  ws = new WebSocket(WS_URL);
  (window as any)._jarvisWs = ws;

  ws.addEventListener("open", () => {
    setConnected(true);
    // Notifie la séquence de boot que le serveur est prêt
    if (bootConnectedCallback) {
      bootConnectedCallback();
      bootConnectedCallback = null;
    } else {
      wsConnectedBeforeBoot = true;
    }
  });

  // ── DOM Automation Queue to prevent race conditions ───────────────────────────
  const domActionQueue: any[] = [];
  let domActionProcessing = false;

  async function executeSingleDomAction(domAction: any): Promise<void> {
    // Cas dom_sequence : exécuter chaque step dans l'ordre avec délai
    if (domAction.action === "dom_sequence") {
      const steps: any[] = domAction.steps || [];
      for (const step of steps) {
        const delay = (step.delay || 0.5) * 1000;
        await new Promise(r => setTimeout(r, delay));
        // Convertir step (action_type) en format domAction (action)
        await executeSingleDomAction({
          action: step.action_type,
          selector: step.selector,
          text: step.text,
          class_name: step.class_name,
        });
      }
      return;
    }

    const element = domAction.selector ? document.querySelector(domAction.selector) as HTMLElement : null;
    if (!element) return;

    // Scroll automatique : amener l'élément dans la zone visible avant toute interaction
    element.scrollIntoView({ behavior: "smooth", block: "center", inline: "nearest" });
    await new Promise(r => setTimeout(r, 300)); // Laisser le scroll se terminer

    const cursor = initVirtualCursor();

    if (domAction.action === "click") {
      await animateVirtualCursorTo(element);
      if (cursor) {
        cursor.classList.add("clicking");
        await new Promise(r => setTimeout(r, 200));
      }
      element.click();
      if (cursor) {
        cursor.classList.remove("clicking");
        await new Promise(r => setTimeout(r, 500)); // Pacing de 500ms post-clic
      }
    } else if (domAction.action === "type") {
      await animateVirtualCursorTo(element);
      element.focus();
      await new Promise(r => setTimeout(r, 200));
      
      const text = domAction.text || "";
      const input = element as HTMLInputElement;
      input.value = "";
      for (let i = 0; i < text.length; i++) {
        input.value += text[i];
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        // Vitesse clavier à 100ms
        await new Promise(r => setTimeout(r, 100));
      }
      await new Promise(r => setTimeout(r, 500)); // Pacing de 500ms post-saisie
    } else if (domAction.action === "focus") {
      await animateVirtualCursorTo(element);
      element.focus();
      await new Promise(r => setTimeout(r, 500)); // Pacing de 500ms post-focus
    } else if (domAction.action === "select") {
      await animateVirtualCursorTo(element);
      (element as HTMLSelectElement).value = domAction.text || "";
      element.dispatchEvent(new Event('change', { bubbles: true }));
      await new Promise(r => setTimeout(r, 500)); // Pacing de 500ms post-sélection
    } else if (domAction.action === "add_class") {
      element.classList.add(domAction.class_name || "");
    } else if (domAction.action === "remove_class") {
      element.classList.remove(domAction.class_name || "");
    }

    // Effacer le curseur virtuel après 2 secondes d'inactivité en retournant d'abord au centre
    if (virtualCursorHideTimeout) clearTimeout(virtualCursorHideTimeout);
    virtualCursorHideTimeout = setTimeout(() => {
      if (cursor) {
        cursor.style.left = `${window.innerWidth / 2}px`;
        cursor.style.top = `${window.innerHeight / 2}px`;
        setTimeout(() => {
          cursor.style.display = "none";
        }, 800);
      }
    }, 2000);
  }

  async function processDomActionQueue() {
    if (domActionProcessing || domActionQueue.length === 0) return;
    domActionProcessing = true;
    
    while (domActionQueue.length > 0) {
      const nextAction = domActionQueue.shift();
      try {
        await executeSingleDomAction(nextAction);
      } catch (e) {
        console.error("Erreur d'action DOM dans la queue:", e);
      }
    }
    
    domActionProcessing = false;
  }

  ws.addEventListener("message", async (event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data as string) as {
        state?: string;
        action?: string;
        muted?: boolean;
        volume?: number;
        id?: string;
        duration?: number;
        text?: string;
        type?: string;
        version?: string;
        url?: string;
        cpu?: number;
        ram?: number;
        prompt?: string;
        title?: string;
        icon?: string;
        weather?: any;
        weather_type?: string;
        status_text?: string;
        data?: Record<string, any>;
      };



      // ── OS Autopilot & Virtual Cursor ──
      if (data.action === "draw_virtual_cursor" && (data as any).x !== undefined && (data as any).y !== undefined) {
        const cursor = document.getElementById("virtual-cursor");
        if (cursor) {
          const wasHidden = cursor.style.display === "none";
          const animDuration = data.duration || 0.8;
          
          // Injecter la durée de transition dynamique
          cursor.style.transition = `left ${animDuration}s cubic-bezier(0.25, 0.8, 0.25, 1), top ${animDuration}s cubic-bezier(0.25, 0.8, 0.25, 1), transform 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275)`;
          
          if (wasHidden) {
            // Positionner initialement au centre pour un premier déplacement fluide
            cursor.style.left = "50%";
            cursor.style.top = "50%";
            cursor.style.display = "block";
            
            // Attendre deux ticks du moteur de rendu pour appliquer le display: block
            requestAnimationFrame(() => {
              requestAnimationFrame(() => {
                cursor.style.left = `${(data as any).x}%`;
                cursor.style.top = `${(data as any).y}%`;
              });
            });
          } else {
            cursor.style.left = `${(data as any).x}%`;
            cursor.style.top = `${(data as any).y}%`;
          }
          
          const duration = animDuration * 1000;
          
          // Nettoyer les anciens timeouts de clic et de masquage
          if ((cursor as any).vcClickTimeout) clearTimeout((cursor as any).vcClickTimeout);
          if ((cursor as any).vcHideTimeout) clearTimeout((cursor as any).vcHideTimeout);
          
          (cursor as any).vcClickTimeout = setTimeout(() => {
            cursor.classList.add("clicking");
            
            const wave = document.createElement("div");
            wave.className = "vc-click-wave";
            cursor.appendChild(wave);
            
            setTimeout(() => {
              cursor.classList.remove("clicking");
              wave.remove();
            }, 600);
          }, duration);
          
          // Masquer le curseur après 3 secondes d'inactivité
          (cursor as any).vcHideTimeout = setTimeout(() => {
            cursor.style.display = "none";
          }, duration + 3000);
        }
        return;
      }

      if (data.action === "os_agent_status") {
        const banner = document.getElementById("os-autopilot-banner");
        const logEl = document.getElementById("os-autopilot-log");
        if (banner && logEl) {
          if ((data as any).active) {
            banner.style.display = "flex";
            logEl.textContent = (data as any).log || "[JARVIS OS AUTOPILOT] ACTIF";
          } else {
            banner.style.display = "none";
            // Cacher le curseur virtuel quand l'autopilote est terminé
            const cursor = document.getElementById("virtual-cursor");
            if (cursor) {
              if ((cursor as any).vcHideTimeout) clearTimeout((cursor as any).vcHideTimeout);
              cursor.style.display = "none";
            }
          }
        }
        return;
      }

      if (data.action === "request_screen_capture") {
        const frame = await captureFrame();
        if (frame && ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({
            type: "screen_frame",
            id: data.id,
            data: frame,
          }));
        } else if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({
            type: "screen_frame",
            id: data.id,
            error: "no_stream",
          }));
        }
        return;
      }

      // ── Spatial File Explorer 3D ──
      if (data.type === "spatial_result") {
        const explorer = (window as any)._spatialExplorer;
        if (explorer) explorer.handleServerResponse(data);
        return;
      }

      // ── Domotic Map 3D ──
      if (data.action === "domotic_map_update") {
        const domMap = (window as any)._domoticMap;
        if (domMap) domMap.handleServerResponse(data);
        return;
      }

      // ── Cortex Neuronal 3D ──
      if (data.action === "cortex_list" || 
          data.action === "cortex_update" || 
          data.action === "cortex_new_memory" || 
          data.action === "cortex_link_created" ||
          data.action === "cortex_link_removed" ||
          data.action === "cortex_edit_success") {
        const cortex = (window as any)._cortexMap;
        if (cortex) cortex.handleServerResponse(data);
        return;
      }

      if (data.action === "cortex_search") {
        if (!_holoActive) {
          _openHolo();
        }
        const app = (window as any)._holoApp;
        if (app && !app.cortexMap) {
          app.toggleCortex();
        }
        
        setTimeout(() => {
          const cortex = (window as any)._cortexMap;
          if (cortex && typeof (data as any).query === "string") {
            cortex.searchCortex((data as any).query);
          }
        }, 250);
        return;
      }

      if (data.action === "cortex_vocal_speak_request") {
        const cortex = (window as any)._cortexMap;
        if (cortex) {
          cortex.handleVocalSpeakRequest();
        }
        return;
      }

      if (data.action === "open_spatial_explorer") {
        if (!_holoActive) {
          _openHolo();
        }
        setTimeout(() => {
          const app = (window as any)._holoApp;
          if (app) {
            if (!app.spatialExplorer) {
              app.toggleExplorer();
            }
          }
        }, 150);
        return;
      }

      if (data.action === "open_domotic_map") {
        if (!_holoActive) {
          _openHolo();
        }
        setTimeout(() => {
          const app = (window as any)._holoApp;
          if (app) {
            if (!app.domoticMap) {
              app.toggleDomotic();
            }
          }
        }, 150);
        return;
      }

      if (data.action === "open_cortex") {
        if (!_holoActive) {
          _openHolo();
        }
        setTimeout(() => {
          const app = (window as any)._holoApp;
          if (app) {
            if (!app.cortexMap) {
              app.toggleCortex();
            }
          }
        }, 150);
        return;
      }

      if (data.action === "display_image" && data.url) {
        showImageHUD(data.url, data.prompt || "--");
        return;
      }
      if (data.action === "ctx_card") {
        cardManager.showCard({
          title: data.title || "INFORMATION",
          content: data.text || "",
          type: data.type as any,
          duration: data.duration,
          icon: data.icon
        });
        return;
      }
      if (data.action === "weather_update" && data.weather) {
        updateWeatherUI(data.weather, data.weather_type as 'local' | 'monistrol');
        return;
      }
      if (data.action === "music_update" && data.data) {
        updateMusicUI(data.data);
        return;
      }

      if (data.type === "settings_data" && data.data) {
        const settings = data.data as any;
        if (settings.user_name) settingsNameEl.value = settings.user_name;
        if (settings.user_age) settingsAgeEl.value = settings.user_age;
        
        // Microphone dropdown select
        if (settingsMicSelect) {
          settingsMicSelect.innerHTML = '<option value="">-- Détection automatique --</option>';
          if (settings.mic_list) {
            settings.mic_list.forEach((mic: { index: number, name: string }) => {
              const opt = document.createElement("option");
              opt.value = String(mic.index);
              opt.textContent = `[INDEX ${mic.index}] ${mic.name}`;
              if (settings.mic_device_index !== undefined && settings.mic_device_index !== null && Number(settings.mic_device_index) === mic.index) {
                opt.selected = true;
              }
              settingsMicSelect.appendChild(opt);
            });
          }
        }
        
        // Music link
        if (settingsMusiqueLien) {
          settingsMusiqueLien.value = settings.musique_lien || "";
        }

        // Custom Apps
        if (settings.custom_apps) {
          currentCustomApps = settings.custom_apps;
          renderCustomApps();
        }

        // Home Assistant Lists
        currentCustomLights = settings.custom_lights || [];
        currentCustomPrises = settings.custom_prises || [];
        currentCustomCapteurs = settings.custom_capteurs || [];
        renderHaEntities();
        
        return;
      }

      if (data.type === "dom_action") {
        domActionQueue.push(data);
        processDomActionQueue();
        return;
      }

      if (data.action === "help") {
        showHelpHUD();
        return;
      }
      if (data.action === "timer_start") {
        startTimer(data.duration || 0);
        return;
      }
      if (data.action === "timer_stop") {
        stopTimer();
        return;
      }
      if (data.action === "timer_add") {
        addTimer(data.duration || 60);
        return;
      }
      if (data.action === "timer_remove") {
        removeTimer(data.duration || 60);
        return;
      }
      if (data.action === "demo") {
        orb.triggerDemo();
        return;
      }
      // ── Globe 3D Navigation ─────────────────────────────────────────
      if (data.action === "jarvis_globe") {
        if (typeof (window as any).jarvisGlobe === "function") {
          (window as any).jarvisGlobe(data);
        }
        return;
      }
      if (data.action === "set_volume" && typeof data.volume === "number") {
        orb.setVolume(data.volume);
        return;
      }
      if (data.action === "jarvis_text" && typeof data.text === "string") {
        showSubtitles(data.text);
        return;
      }
      if (data.action === "interim_speech" && typeof data.text === "string") {
        const container = document.getElementById("subtitle-hud")!;
        const textEl = document.getElementById("subtitle-text")!;
        const metaEl = document.getElementById("subtitle-meta")!;
        if (container && textEl && metaEl) {
          container.style.display = "block";
          textEl.textContent = data.text;
          textEl.style.fontStyle = "italic";
          textEl.style.color = "rgba(0, 229, 255, 0.85)";
          metaEl.textContent = "DECRYPTING_SPEECH_STREAM...";
          metaEl.style.color = "rgba(0, 229, 255, 0.6)";
        }
        return;
      }
      if (data.type === "update_available") {
        const banner = document.getElementById("update-banner");
        if (banner) {
          banner.style.display = "block";
          banner.textContent = `SYSTEM_UPDATE_AVAILABLE_V${data.version}`;
          banner.onclick = () => {
            window.open(data.url, "_blank");
          };
        }
        return;
      }

      if (data.action === "system_stats") {
        const cpuVal = document.getElementById("cpu-value");
        const ramVal = document.getElementById("ram-value");
        const cpuHud = document.getElementById("cpu-hud");
        const ramHud = document.getElementById("ram-hud");
        const cpuBar = document.getElementById("cpu-bar-fill") as HTMLDivElement | null;
        const ramBar = document.getElementById("ram-bar-fill") as HTMLDivElement | null;

        if (cpuVal && typeof data.cpu === "number") {
          cpuVal.textContent = `${Math.round(data.cpu)}%`;
          cpuHud?.classList.toggle("stat-critical", data.cpu > 90);
          if (cpuBar) cpuBar.style.width = `${Math.min(100, data.cpu)}%`;
        }
        if (ramVal && typeof data.ram === "number") {
          ramVal.textContent = `${Math.round(data.ram)}%`;
          ramHud?.classList.toggle("stat-critical", data.ram > 90);
          if (ramBar) ramBar.style.width = `${Math.min(100, data.ram)}%`;
        }
        return;
      }

      if (data.action === "temp_panel" && data.data) {
        showTempPanel(data.data as Parameters<typeof showTempPanel>[0]);
      }

      if (data.action === "weather_panel" && data.data) {
        showWeatherPanel(data.data as Parameters<typeof showWeatherPanel>[0]);
      }

      if (data.type === "show_recipe") {
        const modal = document.getElementById("recipe-modal");
        const titleEl = document.getElementById("recipe-title");
        const ingListEl = document.getElementById("recipe-ingredients-list");
        const instListEl = document.getElementById("recipe-instructions-list");

        if (modal && titleEl && ingListEl && instListEl) {
          titleEl.textContent = (data as any).titre || "RECETTE J.A.R.V.I.S";

          ingListEl.innerHTML = "";
          const ingredients = (data as any).ingredients || [];
          ingredients.forEach((ing: string) => {
            const li = document.createElement("li");
            li.textContent = ing;
            ingListEl.appendChild(li);
          });

          instListEl.innerHTML = "";
          const instructions = (data as any).instructions || [];
          instructions.forEach((inst: string) => {
            const li = document.createElement("li");
            li.textContent = inst;
            instListEl.appendChild(li);
          });

          modal.classList.remove("hidden");
        }
        return;
      }

      if (data.state) {
        applyState(data.state as OrbState);
        if (data.status_text && statusEl) {
          statusEl.textContent = data.status_text;
        }
      }
      if (typeof data.volume === "number") {
        orb.setVolume(data.volume);
      }
      if (typeof data.muted === "boolean") {
        setMuted(data.muted);
      }
    } catch {
      // ignore malformed messages
    }
  });

  ws.addEventListener("close", () => {
    setConnected(false);
    applyState("idle");
    scheduleReconnect();
  });

  ws.addEventListener("error", () => {
    setConnected(false);
  });
}

// ── Subtitles HUD Logic ──────────────────────────────────────────────────────
let subtitleTimer: number | null = null;
let subtitleTypeInterval: number | null = null;

function showSubtitles(text: string) {
  const container = document.getElementById("subtitle-hud")!;
  const textEl = document.getElementById("subtitle-text")!;
  const metaEl = document.getElementById("subtitle-meta")!;

  if (textEl) {
    textEl.style.fontStyle = "normal";
    textEl.style.color = "#00e5ff";
  }

  // Clear any existing animation
  if (subtitleTimer) clearTimeout(subtitleTimer);
  if (subtitleTypeInterval) clearInterval(subtitleTypeInterval);

  if (!subtitlesEnabled || text === "") {
    container.style.display = "none";
    return;
  }

  container.style.display = "block";
  textEl.textContent = "";
  metaEl.textContent = "DECRYPTING_RESPONSE...";
  metaEl.style.color = "rgba(0, 229, 255, 0.4)";

  let i = 0;
  // Faster for long text (news), slower for short phrases
  const speed = text.length > 100 ? 15 : 25;

  subtitleTypeInterval = window.setInterval(() => {
    if (i < text.length) {
      // Add a bit of "glitch" feel by sometimes adding random chars before the real one
      textEl.textContent += text.charAt(i);
      i++;

      // Auto-scroll if it's long? (The box is fixed width/max-width)
    } else {
      if (subtitleTypeInterval) clearInterval(subtitleTypeInterval);
      metaEl.textContent = "DECRYPTION_COMPLETE [STABLE]";
      metaEl.style.color = "#22c55e";

      // Hide after a delay proportional to text length
      const delay = Math.max(3000, text.length * 50);
      subtitleTimer = window.setTimeout(() => {
        container.style.display = "none";
      }, delay);
    }
  }, speed);
}

function scheduleReconnect(): void {
  if (reconnectTimer) return;
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;
    connect();
  }, RECONNECT_INTERVAL_MS);
}

// ── Events ──────────────────────────────────────────────────────────────────
muteButtonEl.addEventListener("click", () => {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;

  // Envoi du signal stop au backend
  ws.send(JSON.stringify({ type: "stop_audio" }));

  // Feedback immédiat sur l'orbe
  applyState("idle");
});

gpuButtonEl.addEventListener("click", () => {
  const isPressed = gpuButtonEl.getAttribute("aria-pressed") === "true";
  const newState = !isPressed;
  gpuButtonEl.setAttribute("aria-pressed", newState.toString());

  if (newState) {
    orb.setQuality("high");
    // Feedback visuel / textuel
    console.log("GPU Acceleration Enabled");
  } else {
    orb.setQuality("low");
    console.log("GPU Acceleration Disabled");
  }
});

subtitleToggleButtonEl.addEventListener("click", () => {
  subtitlesEnabled = !subtitlesEnabled;
  subtitleToggleButtonEl.setAttribute("aria-pressed", subtitlesEnabled.toString());
  subtitleToggleButtonEl.textContent = subtitlesEnabled ? "HUD TEXT" : "TEXT OFF";

  if (!subtitlesEnabled) {
    document.getElementById("subtitle-hud")!.style.display = "none";
  }
});

keyboardToggleButtonEl.addEventListener("click", () => {
  keyboardEnabled = !keyboardEnabled;
  keyboardToggleButtonEl.setAttribute("aria-pressed", keyboardEnabled.toString());
  keyboardHudEl.style.display = keyboardEnabled ? "block" : "none";

  if (keyboardEnabled) {
    setTimeout(() => keyboardInputEl.focus(), 100);
  }
});

keyboardInputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    const val = keyboardInputEl.value.trim();
    if (val && ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "user_input", text: val }));
      keyboardInputEl.value = "";
      // Optionnel: masquer après envoi ? Non, on laisse si l'utilisateur veut continuer à taper
    }
  }
});

// ── Settings UI Logic ────────────────────────────────────────────────────────
settingsButtonEl.addEventListener("click", () => {
  if (keyboardEnabled) {
    keyboardEnabled = false;
    keyboardToggleButtonEl.setAttribute("aria-pressed", "false");
    keyboardHudEl.style.display = "none";
  }

  settingsModalEl.classList.add("visible");
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "get_settings" }));
  }

  // Énumération des caméras détectées
  if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
    navigator.mediaDevices.enumerateDevices()
      .then(devices => {
        const cameras = devices.filter(d => d.kind === "videoinput");
        if (settingsCameraSelect) {
          settingsCameraSelect.innerHTML = '<option value="">-- Détection automatique --</option>';
          cameras.forEach((cam, index) => {
            const opt = document.createElement("option");
            opt.value = cam.deviceId;
            opt.textContent = cam.label || `Caméra ${index + 1} (${cam.deviceId.substring(0, 5)}...)`;
            settingsCameraSelect.appendChild(opt);
          });
          const savedCam = localStorage.getItem("jarvis-camera-id") || "";
          settingsCameraSelect.value = savedCam;
        }
      })
      .catch(err => {
        console.error("Erreur lors de l'énumération des caméras:", err);
      });
  }
});

settingsCloseBtn.addEventListener("click", () => {
  settingsModalEl.classList.remove("visible");
});

// ── Hologramme mode toggle ────────────────────────────────────────────────────
let _holoActive = false;
const _holoOverlay = document.getElementById("holo-overlay") as HTMLDivElement;

function _openHolo() {
  _holoActive = true;
  if (_holoOverlay) _holoOverlay.style.display = "block";
  if (holoButtonEl) holoButtonEl.setAttribute("aria-pressed", "true");
  const orbCanvas = document.getElementById("orb-canvas");
  if (orbCanvas) orbCanvas.style.display = "none";
  activerHolo();
}

function _closeHolo() {
  _holoActive = false;
  desactiverHolo();
  if (_holoOverlay) _holoOverlay.style.display = "none";
  if (holoButtonEl) holoButtonEl.setAttribute("aria-pressed", "false");
  const orbCanvas = document.getElementById("orb-canvas");
  if (orbCanvas) orbCanvas.style.display = "block";
}

holoButtonEl?.addEventListener("click", () => {
  if (_holoActive) _closeHolo(); else _openHolo();
});

document.getElementById("holo-close-btn")?.addEventListener("click", _closeHolo);

function renderCustomApps() {
  settingsAppsListEl.innerHTML = "";
  currentCustomApps.forEach((app, index) => {
    const div = document.createElement("div");
    div.className = "settings-app-item";
    div.innerHTML = `
      <div><strong>${app.label}</strong> <br> <span style="font-size:10px;color:rgba(0,229,255,0.5)">${app.exe_path.replace(/\\/g, '\\\\')}</span></div>
      <div class="settings-app-remove" data-index="${index}">[ X ]</div>
    `;
    settingsAppsListEl.appendChild(div);
  });

  document.querySelectorAll(".settings-app-remove").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const idx = parseInt((e.target as HTMLElement).getAttribute("data-index") || "0", 10);
      currentCustomApps.splice(idx, 1);
      renderCustomApps();
    });
  });
}

appAddBtn.addEventListener("click", () => {
  const name = appAddNameEl.value.trim();
  const path = appAddPathEl.value.trim();
  if (name && path) {
    const id = name.toLowerCase().replace(/[^a-z0-9]/g, "_");
    currentCustomApps.push({ id, label: name, exe_path: path });
    appAddNameEl.value = "";
    appAddPathEl.value = "";
    renderCustomApps();
  }
});

settingsSaveBtn.addEventListener("click", () => {
  const selectedMic = settingsMicSelect.value;

  // Sauvegarde du thème de l'orbe dans le localStorage et application instantanée
  const orbThemeSelect = document.getElementById("settings-orb-theme") as HTMLSelectElement;
  if (orbThemeSelect) {
    const selectedTheme = orbThemeSelect.value;
    localStorage.setItem("jarvis-orb-theme", selectedTheme);
    orb.setTheme(selectedTheme);
  }
  
  // Sauvegarde de la caméra sélectionnée dans le localStorage
  if (settingsCameraSelect) {
    localStorage.setItem("jarvis-camera-id", settingsCameraSelect.value);
  }

  const settings = {
    user_name: settingsNameEl.value.trim(),
    user_age: settingsAgeEl.value.trim(),
    mic_device_index: selectedMic === "" ? null : parseInt(selectedMic, 10),
    musique_lien: settingsMusiqueLien.value.trim(),
    custom_apps: currentCustomApps,
    custom_lights: currentCustomLights,
    custom_prises: currentCustomPrises,
    custom_capteurs: currentCustomCapteurs
  };
  
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "update_settings", settings }));
  }
  
  settingsModalEl.classList.remove("visible");
});

function renderHaEntities() {
  if (!haEntitiesListEl) return;
  haEntitiesListEl.innerHTML = "";
  
  let currentList: { name: string, entity_id: string }[] = [];
  if (activeHaTab === "lumieres") currentList = currentCustomLights;
  else if (activeHaTab === "prises") currentList = currentCustomPrises;
  else if (activeHaTab === "capteurs") currentList = currentCustomCapteurs;
  
  if (currentList.length === 0) {
    haEntitiesListEl.innerHTML = '<div style="font-size:11px;color:rgba(0,229,255,0.4);text-align:center;padding:12px;">AUCUN APPAREIL PERSO</div>';
    return;
  }
  
  currentList.forEach((ent, index) => {
    const div = document.createElement("div");
    div.className = "settings-app-item";
    div.innerHTML = `
      <div><strong>${ent.name}</strong> <br> <span style="font-size:10px;color:rgba(0,229,255,0.5)">${ent.entity_id}</span></div>
      <div class="ha-entity-remove" data-index="${index}">[ X ]</div>
    `;
    haEntitiesListEl.appendChild(div);
  });
  
  document.querySelectorAll(".ha-entity-remove").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const idx = parseInt((e.target as HTMLElement).getAttribute("data-index") || "0", 10);
      if (activeHaTab === "lumieres") currentCustomLights.splice(idx, 1);
      else if (activeHaTab === "prises") currentCustomPrises.splice(idx, 1);
      else if (activeHaTab === "capteurs") currentCustomCapteurs.splice(idx, 1);
      renderHaEntities();
    });
  });
}

if (haAddBtn) {
  haAddBtn.addEventListener("click", () => {
    const name = haAddNom.value.trim();
    const entity = haAddEntity.value.trim();
    if (name && entity) {
      const item = { name, entity_id: entity };
      if (activeHaTab === "lumieres") currentCustomLights.push(item);
      else if (activeHaTab === "prises") currentCustomPrises.push(item);
      else if (activeHaTab === "capteurs") currentCustomCapteurs.push(item);
      haAddNom.value = "";
      haAddEntity.value = "";
      renderHaEntities();
    }
  });
}

if (haAddEntity) {
  haAddEntity.addEventListener("input", () => {
    let val = haAddEntity.value;
    // Remplace les espaces et tirets par des underscores, minuscule, et filtre les caracteres invalides
    val = val.toLowerCase()
             .replace(/[\s-]+/g, "_")
             .replace(/[^a-z0-9_.]/g, "");
    if (haAddEntity.value !== val) {
      haAddEntity.value = val;
      haAddEntity.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
}

document.querySelectorAll(".ha-tab-btn").forEach(btn => {
  btn.addEventListener("click", (e) => {
    document.querySelectorAll(".ha-tab-btn").forEach(b => b.classList.remove("active"));
    const target = e.currentTarget as HTMLButtonElement;
    target.classList.add("active");
    activeHaTab = target.getAttribute("data-tab") as any;
    
    if (activeHaTab === "lumieres") {
      haAddNom.placeholder = "Nom vocal (ex: escalier)";
      haAddEntity.placeholder = "entity_id (ex: light.escalier)";
    } else if (activeHaTab === "prises") {
      haAddNom.placeholder = "Nom vocal (ex: cafetiere)";
      haAddEntity.placeholder = "entity_id (ex: switch.cafetiere)";
    } else if (activeHaTab === "capteurs") {
      haAddNom.placeholder = "Nom vocal (ex: salon)";
      haAddEntity.placeholder = "entity_id (ex: sensor.salon_temp)";
    }
    
    renderHaEntities();
  });
});

// ── Boot Sequence ─────────────────────────────────────────────────────────────
function runBootSequence(): void {
  const overlay    = document.getElementById("boot-overlay") as HTMLDivElement;
  const modulesEl  = document.getElementById("boot-modules") as HTMLDivElement;
  const progressBar = document.getElementById("boot-progress-bar") as HTMLDivElement;
  const progressLbl = document.getElementById("boot-progress-label") as HTMLDivElement;
  const statusText  = document.getElementById("boot-status-text") as HTMLDivElement;
  const finalText   = document.getElementById("boot-final-text") as HTMLDivElement;
  const buildYear   = document.getElementById("boot-build-year") as HTMLSpanElement;

  if (!overlay) return;
  if (buildYear) buildYear.textContent = new Date().getFullYear().toString();

  const MODULES = [
    "NEURAL_NETWORK_CORE",
    "SPEECH_RECOGNITION",
    "KNOWLEDGE_DATABASE",
    "VISION_SYSTEM",
    "AUDIO_SYNTHESIS_TTS",
    "HOME_AUTOMATION_LINK",
    "COMM_PROTOCOLS",
  ];

  const TOTAL = MODULES.length + 1; // +1 pour la connexion serveur
  let done = 0;

  function setProgress(n: number) {
    const pct = Math.round((n / TOTAL) * 100);
    progressBar.style.width = `${pct}%`;
    progressLbl.textContent = `CHARGEMENT... ${pct}%`;
  }

  function addLine(name: string): HTMLDivElement {
    const div = document.createElement("div");
    div.className = "boot-module-line";
    div.innerHTML = `
      <span class="boot-module-name">${name}</span>
      <span class="boot-module-dots"></span>
      <span class="boot-module-status pending">INITIALISATION</span>
    `;
    modulesEl.appendChild(div);
    return div;
  }

  function setLineOnline(line: HTMLDivElement, mode: "ok" | "wait" = "ok") {
    const s = line.querySelector(".boot-module-status") as HTMLSpanElement;
    s.classList.remove("pending");
    if (mode === "ok") {
      s.textContent = "[ ONLINE ]";
      s.classList.add("online");
      done++;
      setProgress(done);
    } else {
      s.textContent = "[ EN ATTENTE ]";
      s.classList.add("waiting");
    }
  }

  function finishBoot() {
    setProgress(TOTAL);
    progressLbl.textContent = "CHARGEMENT... 100%";
    statusText.textContent = "SYSTÈMES OPÉRATIONNELS — BONNE JOURNÉE";
    finalText.style.opacity = "1";
    finalText.style.transform = "scale(1)";

    setTimeout(() => {
      overlay.style.opacity = "0";
      setTimeout(() => { overlay.style.display = "none"; }, 900);
    }, 1600);
  }

  // Défilement des modules locaux (~280 ms entre chaque)
  MODULES.forEach((name, i) => {
    const delay = 250 + i * 280;
    setTimeout(() => {
      const line = addLine(name);
      setTimeout(() => setLineOnline(line, "ok"), 200);
    }, delay);
  });

  // Module serveur — attend la connexion WebSocket
  const serverDelay = 250 + MODULES.length * 280;
  setTimeout(() => {
    const line = addLine("SERVER_CONNECTION");
    statusText.textContent = "CONNEXION AU SERVEUR EN COURS...";

    if (wsConnectedBeforeBoot) {
      // WS déjà connecté avant cette étape
      setTimeout(() => { setLineOnline(line, "ok"); setTimeout(finishBoot, 350); }, 250);
    } else {
      setLineOnline(line, "wait");
      bootConnectedCallback = () => {
        const s = line.querySelector(".boot-module-status") as HTMLSpanElement;
        s.classList.remove("waiting");
        s.textContent = "[ ONLINE ]";
        s.classList.add("online");
        done++;
        setTimeout(finishBoot, 350);
      };
      // Sécurité : ferme le boot après 25 s si le serveur ne répond pas
      setTimeout(() => {
        if (bootConnectedCallback) {
          bootConnectedCallback = null;
          overlay.style.opacity = "0";
          setTimeout(() => { overlay.style.display = "none"; }, 900);
        }
      }, 25_000);
    }
  }, serverDelay);
}

// ── Boot ──────────────────────────────────────────────────────────────────────
setConnected(false);
applyState("idle");
setMuted(false);
injectVisionButton();
initJarvisGlobe();
initHandTracking();
runBootSequence();

// Masquer le message d'aide après 10 secondes
setTimeout(() => {
  const tip = document.getElementById("user-tip");
  if (tip) {
    tip.style.opacity = "0";
    setTimeout(() => { tip.style.display = "none"; }, 1000);
  }
}, 10000);
// ── Help HUD Logic ───────────────────────────────────────────────────────────
function showHelpHUD() {
  helpOverlayEl.style.display = "block";
  helpOverlayEl.innerHTML = "";

  // Select 16 random commands
  const shuffled = [...HELP_COMMANDS].sort(() => 0.5 - Math.random());
  const selected = shuffled.slice(0, 16);

  selected.forEach((cmd, i) => {
    const isRight = i % 2 === 1;
    const widget = document.createElement("div");
    widget.className = `help-widget ${isRight ? 'right' : ''}`;

    // Grid-like positioning with random offsets (starting lower to avoid the tip)
    const row = Math.floor(i / 2);
    const top = 160 + (row * 95) + (Math.random() * 15);
    widget.style.top = `${top}px`;

    // Position them more towards the center to "fill around"
    const sideOffset = 30 + (Math.random() * 40);
    if (isRight) widget.style.right = `${sideOffset}px`;
    else widget.style.left = `${sideOffset}px`;

    // Faster reveal and varied animations
    widget.style.animation = `float ${2 + Math.random() * 2}s ease-in-out infinite`;
    widget.style.animationDelay = `${Math.random() * 1}s`;

    widget.innerHTML = `
      <div class="help-widget-title" style="display:flex; justify-content: space-between;">
        <span>CAPACITÉ ${Math.floor(Math.random() * 999)}</span>
        <span style="opacity:0.3">[SYNC]</span>
      </div>
      <div class="help-widget-cmd">"${cmd}"</div>
    `;

    helpOverlayEl.appendChild(widget);

    // Cinematic reveal synchronized with speech (one widget every 800ms)
    setTimeout(() => widget.classList.add("visible"), i * 800);
  });

  // Auto-hide after 20 seconds
  setTimeout(() => {
    const widgets = document.querySelectorAll(".help-widget");
    widgets.forEach((w, i) => {
      setTimeout(() => w.classList.remove("visible"), i * 100);
    });
    setTimeout(() => helpOverlayEl.style.display = "none", 2000);
  }, 20000);
}

// ── Timer Logic ─────────────────────────────────────────────────────────────
function startTimer(duration: number) {
  stopTimer();
  timerSeconds = duration;
  timerTotalSeconds = duration;
  timerHudEl.style.display = "block";
  updateTimerDisplay();

  timerInterval = window.setInterval(() => {
    timerSeconds--;
    updateTimerDisplay();
    if (timerSeconds <= 0) {
      timerDisplayEl.textContent = "FINISH";
      timerDisplayEl.style.color = "#ff3d00";
      setTimeout(() => stopTimer(), 3000);
    }
  }, 1000);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  timerHudEl.style.display = "none";
}

function addTimer(extraSeconds: number) {
  timerSeconds += extraSeconds;
  timerTotalSeconds += extraSeconds;
  updateTimerDisplay();
}

function removeTimer(lessSeconds: number) {
  timerSeconds = Math.max(0, timerSeconds - lessSeconds);
  updateTimerDisplay();
}

function updateTimerDisplay() {
  const mins = Math.floor(timerSeconds / 60);
  const secs = timerSeconds % 60;
  timerDisplayEl.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

  const progress = ((timerTotalSeconds - timerSeconds) / timerTotalSeconds) * 100;
  timerProgressEl.style.width = `${progress}%`;

  // Flash effect if near end
  if (timerSeconds <= 10) {
    timerDisplayEl.style.color = (timerSeconds % 2 === 0) ? "#ff3d00" : "#00e5ff";
  } else {
    timerDisplayEl.style.color = "#00e5ff";
  }
}

connect();

// ── Clock Logic ─────────────────────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  const timeStr = now.toLocaleTimeString('fr-FR', { hour12: false });

  // Globe overlay clock (existing)
  const clockEl = document.getElementById("globe-clock");
  if (clockEl) clockEl.textContent = timeStr;

  // Orb HUD clock (top of screen, always visible)
  const orbTime = document.getElementById("orb-time-display");
  if (orbTime) orbTime.textContent = timeStr;

  const orbDate = document.getElementById("orb-date-display");
  if (orbDate) {
    orbDate.textContent = now.toLocaleDateString('fr-FR', {
      day: '2-digit', month: '2-digit', year: 'numeric'
    });
  }
}
setInterval(updateClock, 1000);
updateClock();

// Silence unused-import warning for showError
void showError;

// ── Temp Panel (left side — Home Assistant interior) ────────────────────────

const TEMP_DURATION_MS = 3 * 60 * 1000; // 3 minutes

// Comfort scale: 10°C → 30°C maps to 0% → 100%
function tempToPercent(t: number): number {
  return Math.min(100, Math.max(0, ((t - 10) / 20) * 100));
}

let _tpTimer: ReturnType<typeof setInterval> | null = null;
let _tpHideTimer: ReturnType<typeof setTimeout> | null = null;
let _tpEndTime = 0;

function showTempPanel(d: {
  piece: string; temperature: string; humidite?: string | null;
}) {
  const panel = document.getElementById("temp-panel");
  if (!panel) return;

  const temp = parseFloat(d.temperature) || 0;

  (document.getElementById("tp-piece") as HTMLElement).textContent = d.piece.toUpperCase();
  (document.getElementById("tp-temp") as HTMLElement).textContent = String(Math.round(temp));

  const humRow = document.getElementById("tp-hum-row") as HTMLElement;
  if (d.humidite) {
    (document.getElementById("tp-hum") as HTMLElement).textContent = d.humidite;
    humRow.style.display = "flex";
  } else {
    humRow.style.display = "none";
  }

  const pct = tempToPercent(temp);
  const marker = document.getElementById("tp-marker") as HTMLElement;
  marker.style.left = `${pct}%`;

  if (_tpTimer) clearInterval(_tpTimer);
  if (_tpHideTimer) clearTimeout(_tpHideTimer);

  panel.classList.add("tp-visible");
  _tpEndTime = Date.now() + TEMP_DURATION_MS;

  const progress = document.getElementById("tp-progress") as HTMLElement;
  const timerEl  = document.getElementById("tp-timer") as HTMLElement;

  _tpTimer = setInterval(() => {
    const remaining = Math.max(0, _tpEndTime - Date.now());
    const fraction  = remaining / TEMP_DURATION_MS;
    progress.style.transform = `scaleX(${fraction})`;
    const secs = Math.ceil(remaining / 1000);
    timerEl.textContent = `${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, "0")}`;
    if (remaining <= 0) hideTempPanel();
  }, 1000);

  _tpHideTimer = setTimeout(hideTempPanel, TEMP_DURATION_MS);
}

function hideTempPanel() {
  const panel = document.getElementById("temp-panel");
  if (!panel) return;
  panel.classList.remove("tp-visible");
  if (_tpTimer) { clearInterval(_tpTimer); _tpTimer = null; }
  if (_tpHideTimer) { clearTimeout(_tpHideTimer); _tpHideTimer = null; }
}

document.getElementById("tp-close-btn")?.addEventListener("click", hideTempPanel);

// ── Weather Panel ────────────────────────────────────────────────────────────

const WEATHER_DURATION_MS = 2 * 60 * 1000; // 2 minutes

const WEATHER_ICONS: Record<number, string> = {
  0: "☀️", 1: "🌤", 2: "⛅", 3: "☁️",
  45: "🌫", 48: "🌫",
  51: "🌦", 53: "🌦", 55: "🌧",
  61: "🌧", 63: "🌧", 65: "🌧",
  71: "🌨", 73: "🌨", 75: "❄️", 77: "🌨",
  80: "🌦", 81: "🌦", 82: "⛈",
  85: "🌨", 86: "❄️",
  95: "⛈", 96: "⛈", 99: "⛈",
};

let _wpTimer: ReturnType<typeof setInterval> | null = null;
let _wpHideTimer: ReturnType<typeof setTimeout> | null = null;
let _wpEndTime = 0;

function showWeatherPanel(d: {
  ville: string; temperature: number; ressenti: number;
  humidite: number; vent: number; code: number; description: string;
}) {
  const panel = document.getElementById("weather-panel");
  if (!panel) return;

  (document.getElementById("wp-city") as HTMLElement).textContent = d.ville.toUpperCase();
  (document.getElementById("wp-temp") as HTMLElement).textContent = String(d.temperature);
  (document.getElementById("wp-desc") as HTMLElement).textContent = d.description.toUpperCase();
  (document.getElementById("wp-feels") as HTMLElement).textContent = String(d.ressenti);
  (document.getElementById("wp-humidity") as HTMLElement).textContent = String(d.humidite);
  (document.getElementById("wp-wind") as HTMLElement).textContent = String(d.vent);
  (document.getElementById("wp-icon") as HTMLElement).textContent = WEATHER_ICONS[d.code] ?? "🌡";

  // reset any existing timers
  if (_wpTimer) clearInterval(_wpTimer);
  if (_wpHideTimer) clearTimeout(_wpHideTimer);

  panel.classList.add("wp-visible");
  _wpEndTime = Date.now() + WEATHER_DURATION_MS;

  const progress = document.getElementById("wp-progress") as HTMLElement;
  const timerEl  = document.getElementById("wp-timer") as HTMLElement;

  _wpTimer = setInterval(() => {
    const remaining = Math.max(0, _wpEndTime - Date.now());
    const fraction  = remaining / WEATHER_DURATION_MS;
    progress.style.transform = `scaleX(${fraction})`;
    const secs = Math.ceil(remaining / 1000);
    timerEl.textContent = `${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, "0")}`;
    if (remaining <= 0) hideWeatherPanel();
  }, 1000);

  _wpHideTimer = setTimeout(hideWeatherPanel, WEATHER_DURATION_MS);
}

function hideWeatherPanel() {
  const panel = document.getElementById("weather-panel");
  if (!panel) return;
  panel.classList.remove("wp-visible");
  if (_wpTimer) { clearInterval(_wpTimer); _wpTimer = null; }
  if (_wpHideTimer) { clearTimeout(_wpHideTimer); _wpHideTimer = null; }
}

document.getElementById("wp-close-btn")?.addEventListener("click", hideWeatherPanel);

// ── Recipe Modal Logic ───────────────────────────────────────────────────────

const recipeModal = document.getElementById("recipe-modal");
const closeRecipeBtn = document.getElementById("close-recipe");
const recipeHeader = document.getElementById("recipe-header");

if (closeRecipeBtn && recipeModal) {
  closeRecipeBtn.addEventListener("click", () => {
    recipeModal.classList.add("hidden");
  });
}

// Drag & Drop for Recipe Modal
if (recipeModal && recipeHeader) {
  let isDragging = false;
  let offsetX = 0;
  let offsetY = 0;

  recipeHeader.addEventListener("mousedown", (e) => {
    isDragging = true;
    const rect = recipeModal.getBoundingClientRect();
    offsetX = e.clientX - rect.left;
    offsetY = e.clientY - rect.top;
    recipeModal.style.cursor = "grabbing";
  });

  document.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    
    // Prevent dragging outside the window
    let newX = e.clientX - offsetX;
    let newY = e.clientY - offsetY;
    
    // Boundaries
    const maxX = window.innerWidth - recipeModal.offsetWidth;
    const maxY = window.innerHeight - recipeModal.offsetHeight;
    
    newX = Math.max(0, Math.min(newX, maxX));
    newY = Math.max(0, Math.min(newY, maxY));

    recipeModal.style.left = `${newX}px`;
    recipeModal.style.top = `${newY}px`;
    recipeModal.style.transform = "none"; // disable original translation for dragging
  });

  document.addEventListener("mouseup", () => {
    if (isDragging) {
      isDragging = false;
      recipeModal.style.cursor = "default";
    }
  });
}

// ── Image HUD Logic ──────────────────────────────────────────────────────────
function showImageHUD(url: string, prompt: string) {
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

// ── Control Buttons Events ───────────────────────────────────────────────────
document.getElementById("fullscreen-btn")?.addEventListener("click", () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "toggle_fullscreen" }));
  }
});

const gesturesToggleBtn = document.getElementById("gestures-toggle") as HTMLButtonElement;
if (gesturesToggleBtn) {
  gesturesToggleBtn.addEventListener("click", async () => {
    const isPressed = gesturesToggleBtn.getAttribute("aria-pressed") === "true";
    const newState = !isPressed;

    gesturesToggleBtn.disabled = true;
    gesturesToggleBtn.textContent = newState ? "LANCEMENT..." : "MODE AR";

    const active = await toggleHandTracking(newState);

    gesturesToggleBtn.disabled = false;
    gesturesToggleBtn.setAttribute("aria-pressed", active.toString());
    gesturesToggleBtn.textContent = active ? "AR ACTIF" : "MODE AR";
    gesturesToggleBtn.classList.toggle("ar-active", active);
  });
}

const gesturesMirrorBtn = document.getElementById("gestures-mirror") as HTMLButtonElement;
if (gesturesMirrorBtn) {
  gesturesMirrorBtn.addEventListener("click", () => {
    const isMirrored = toggleArMirror();
    gesturesMirrorBtn.classList.toggle("active", isMirrored);
    gesturesMirrorBtn.textContent = isMirrored ? "AR MIROIR" : "AR DIRECT";
  });
}

// mute-button = Stopper JARVIS (interrompre la parole)
muteButtonEl?.addEventListener("click", () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "stop_audio" }));
  }
  // Flash visuel rapide
  muteButtonEl.style.boxShadow = "0 0 25px rgba(0, 229, 255, 0.8)";
  setTimeout(() => { muteButtonEl.style.boxShadow = ""; }, 400);
});

// mic-btn = Couper/réactiver le microphone
micBtnEl?.addEventListener("click", () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "toggle_mic" }));
  }
  // Feedback visuel optimiste (l'état réel sera confirmé par mic_state)
  const isMuted = micBtnEl.classList.contains("is-muted");
  setMuted(!isMuted);
});

setTimeout(() => initWidgets(ws), 2000);

// ── Drag & Drop souris pour les widgets HUD ───────────────────────────────────
function makeDraggable(el: HTMLElement): void {
  let dragging = false;
  let startMouseX = 0, startMouseY = 0;
  let startLeft = 0, startTop = 0;

  el.addEventListener("mousedown", (e: MouseEvent) => {
    // Ignorer les clics sur boutons, inputs, etc.
    if ((e.target as HTMLElement).closest("button, input, select, a, svg")) return;

    e.preventDefault();
    dragging = true;

    // Convertir right/bottom en left/top absolus pour pouvoir déplacer librement
    const rect = el.getBoundingClientRect();
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

// Appliquer le drag à tous les widgets HUD au chargement (ils existent dans le DOM même si cachés)
["calendar-hud", "weather-hud", "music-hud"].forEach(id => {
  const el = document.getElementById(id);
  if (el) makeDraggable(el);
});

// ── Carousel Controls for Button Bar (3D Dial / Cover Flow) ───────────────────
const track = document.getElementById("carousel-track");
const getCarouselButtons = () => Array.from(track ? track.getElementsByTagName("button") : []);

let activeIndex = 0;

function interpolate(val: number, keyframes: [number, number][]) {
  if (val <= keyframes[0][0]) return keyframes[0][1];
  if (val >= keyframes[keyframes.length - 1][0]) return keyframes[keyframes.length - 1][1];
  for (let i = 0; i < keyframes.length - 1; i++) {
    const k1 = keyframes[i];
    const k2 = keyframes[i+1];
    if (val >= k1[0] && val <= k2[0]) {
      const pct = (val - k1[0]) / (k2[0] - k1[0]);
      return k1[1] + pct * (k2[1] - k1[1]);
    }
  }
  return keyframes[0][1];
}

const scaleKeyframes: [number, number][] = [
  [-3, 0.5],
  [-2, 0.65],
  [-1, 0.85],
  [0, 1.16],
  [1, 0.85],
  [2, 0.65],
  [3, 0.5]
];

const opacityKeyframes: [number, number][] = [
  [-3, 0],
  [-2, 0.5],
  [-1, 0.8],
  [0, 1],
  [1, 0.8],
  [2, 0.5],
  [3, 0]
];

const txKeyframes: [number, number][] = [
  [-3, -281],
  [-2, -207.5],
  [-1, -116.5],
  [0, 0],
  [1, 116.5],
  [2, 207.5],
  [3, 281]
];

function renderCarousel(progress = 0) {
  const buttons = getCarouselButtons();
  const len = buttons.length;
  if (len === 0) return;

  buttons.forEach((btn, idx) => {
    // 1. Calculate the base circular slot
    const diff = (idx - activeIndex + len) % len;
    let slot = diff;
    if (slot > Math.floor(len / 2)) {
      slot -= len;
    }

    // 2. Adjust slot by drag progress
    let currentSlot = slot + progress;

    // Wrap currentSlot to the range [-len/2, len/2] for infinite circular scrolling
    const halfLen = len / 2;
    while (currentSlot < -halfLen) {
      currentSlot += len;
    }
    while (currentSlot > halfLen) {
      currentSlot -= len;
    }

    // 3. Interpolate styles
    const scale = interpolate(currentSlot, scaleKeyframes);
    const opacity = interpolate(currentSlot, opacityKeyframes);
    const offset = interpolate(currentSlot, txKeyframes);
    const tx = -50 + offset;

    // Z-index based on rounded slot
    const roundedSlot = Math.round(currentSlot);
    let zIndex = 1;
    if (roundedSlot === 0) zIndex = 10;
    else if (Math.abs(roundedSlot) === 1) zIndex = 5;
    else if (Math.abs(roundedSlot) === 2) zIndex = 3;

    // Apply class names for CSS specific overrides (colors, etc.)
    btn.classList.remove("active", "prev", "next", "prev2", "next2", "hidden");
    
    if (roundedSlot === 0) {
      btn.classList.add("active");
      btn.setAttribute("aria-hidden", "false");
    } else if (roundedSlot === -1) {
      btn.classList.add("prev");
      btn.setAttribute("aria-hidden", "false");
    } else if (roundedSlot === -2) {
      btn.classList.add("prev2");
      btn.setAttribute("aria-hidden", "false");
    } else if (roundedSlot === 1) {
      btn.classList.add("next");
      btn.setAttribute("aria-hidden", "false");
    } else if (roundedSlot === 2) {
      btn.classList.add("next2");
      btn.setAttribute("aria-hidden", "false");
    } else {
      btn.classList.add("hidden");
      btn.setAttribute("aria-hidden", "true");
    }

    // Direct inline styles for fluid transition
    btn.style.transform = `translate(${tx}%, -50%) scale(${scale})`;
    btn.style.opacity = opacity.toString();
    btn.style.zIndex = zIndex.toString();
    btn.style.pointerEvents = Math.abs(currentSlot) > 2.2 ? "none" : "auto";
  });

  // Update dots active class
  const dots = document.querySelectorAll(".carousel-dot");
  dots.forEach((dot, idx) => {
    dot.classList.toggle("active", idx === activeIndex);
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
  buttons.forEach((_, idx) => {
    const dot = document.createElement("span");
    dot.className = `carousel-dot${idx === activeIndex ? " active" : ""}`;
    dot.setAttribute("data-page", idx.toString());
    dot.addEventListener("click", () => {
      activeIndex = idx;
      updateCarousel();
    });
    indicatorsContainer.appendChild(dot);
  });
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
  }, { passive: false });
}

// Initialize
createIndicators();
updateCarousel();
