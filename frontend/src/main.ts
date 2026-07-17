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
import { initHADashboard, handleHAMessage } from "./ha_dashboard";
import { ChessMap } from "./chess_map";
import { NetworkRadar } from "./network_radar";
import { initIPTVPlayer, handleIPTVMessage, updateIPTVWS } from "./iptv_player";
import { wsRef } from "./ws_link";
import { makeDraggable, makePanelDraggable } from "./ui/draggable";
import { initDynamicUserTips } from "./ui/tips";
import { initDynamicAmbientGlow, initMagneticButtons } from "./ui/effects";
import { initCarouselDock, hideCarouselArrow, showCarouselArrow } from "./ui/carousel";
import { showImageHUD, showImagePanel } from "./panels/image_panels";
import { openAntivirusPanel, handleAntivirusWSMessage } from "./panels/antivirus_panel";
import { setShoppingList, openShoppingPanel } from "./panels/shopping_panel";
import { openUninstallerPanel, closeUninstallerPanel, handleInstalledPrograms, updateUninstallProgress, showUninstallComplete, showCleanComplete } from "./panels/uninstaller_panel";
import { openWingetPanel, handleWingetUpgrades, appendWingetProgress } from "./panels/winget_panel";

// Expose SpatialFileExplorer class globally for hologramme.js
(window as any).SpatialFileExplorer = SpatialFileExplorer;
(window as any).DomoticMap = DomoticMap;
(window as any).CortexMap = CortexMap;
(window as any).ChessMap = ChessMap;
(window as any).NetworkRadar = NetworkRadar;

import "./css/index.css";
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
const jarvisMenuBtn = document.getElementById("jarvis-menu-btn") as HTMLButtonElement;
const jarvisMenuDropdown = document.getElementById("jarvis-menu-dropdown") as HTMLDivElement;
const apiKeysButtonEl = document.getElementById("api-keys-button") as HTMLButtonElement;
const apiKeysModalEl = document.getElementById("api-keys-modal") as HTMLDivElement;
const apiKeysCloseBtn = document.getElementById("api-keys-close-btn") as HTMLSpanElement;
const apiKeysSaveBtn = document.getElementById("api-keys-save-btn") as HTMLButtonElement;
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
const haToggleBtn = document.getElementById("ha-toggle-btn") as HTMLButtonElement;
const haPanel = document.getElementById("ha-panel") as HTMLDivElement;
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
const appDetectBtn = document.getElementById("app-detect-btn") as HTMLButtonElement;
const appDetectSelect = document.getElementById("app-detect-select") as HTMLSelectElement;

// (Refs courses extraites dans panels/shopping_panel.ts)
// Swarm HUD DOM refs (Minimal)
const devSwarmHud = document.getElementById("dev-swarm-hud") as HTMLDivElement;
const swarmCloseBtn = document.getElementById("swarm-close-btn") as HTMLButtonElement;
const swarmProgressAgent = document.getElementById("swarm-progress-agent") as HTMLSpanElement;
const swarmProgressBarFill = document.getElementById("swarm-progress-bar-fill") as HTMLDivElement;
const swarmProgressMsg = document.getElementById("swarm-progress-msg") as HTMLSpanElement;

// (Refs winget extraites dans panels/winget_panel.ts)

// (Refs désinstallateur extraites dans panels/uninstaller_panel.ts)


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
  // Heure & Date
  "Quelle heure est-il ?",
  "On est quel jour ?",
  "Quelle date sommes-nous ?",
  "C'est quel mois ?",
  "Quelle année est-ce ?",
  "J'ai quel âge ?",
  
  // Système PC
  "Niveau de la batterie",
  "Niveau de charge du PC",
  "Utilisation du CPU",
  "Charge du processeur",
  "Utilisation de la RAM",
  "Mémoire vive disponible",
  "Allumé depuis combien de temps ?",
  "PC allumé depuis quand ?",
  "Uptime système",
  "Volume monte",
  "Volume baisse",
  "Coupe le son",
  "Volume à 50%",
  "Remets le son",
  "Prends une capture d'écran",
  "Prends un screenshot",
  "Vide la corbeille",
  "Nettoie la corbeille",
  "Éteins le PC dans 5 minutes",
  "Redémarre le PC",
  "Mets le PC en veille",
  "Verrouille le PC",
  "Annule l'arrêt",

  // Gestion des Fichiers & Dossiers
  "Ouvre mon Bureau",
  "Ouvre mes Documents",
  "Ouvre mes Téléchargements",
  "Ouvre mes Images",
  "Ouvre le dossier Documents",
  "Ouvre le fichier photo.jpg",
  "Range mes dossiers",
  "Mosaïque dossiers",
  "Trie mes fichiers par type",
  "Trie mes fichiers par date",
  "Crée le dossier Projets",
  "Renomme ancien_dossier en nouveau_dossier",
  "Déplace photo.jpg vers Images",
  "Analyse le fichier de notes",

  // Applications & Jeux
  "Ouvre la calculatrice",
  "Ouvre Notepad",
  "Ouvre Paint",
  "Ouvre Chrome",
  "Ouvre le gestionnaire de tâches",
  "Ferme la calculatrice",
  "Mode Boulot !",
  "Mode Gaming",
  "On joue !",
  "On joue à Rocket League",

  // Contrôle de l'Interface Graphique (HUD)
  "Ouvre les paramètres",
  "Ferme les paramètres",
  "Boost le GPU",
  "Active l'accélération graphique",
  "Active les sous-titres",
  "Active le clavier",
  "Ferme la météo",
  "Montre le widget Calendrier",
  "Active le mode hologramme",
  "Active le mode AR",
  "Active le miroir holo",

  // Minuteurs Interactifs
  "Mets un minuteur de 10 minutes",
  "Lance un timer de 5 minutes",
  "Ajoute 2 minutes au minuteur",
  "Retire 1 minute au minuteur",
  "Annule le minuteur",
  "Combien de temps reste-t-il ?",

  // Explorateur Spatial 3D & Carte 3D
  "Ouvre l'explorateur spatial",
  "Affiche mes fichiers en 3D",
  "Affiche ma maison en 3D",
  "Affiche la carte domotique 3D",

  // Cortex Neuronal 3D
  "Affiche ton cortex",
  "Ouvre le cortex neuronal",
  "Cherche dans mon cortex la musique",
  "Trouve dans le cortex la météo",
  "Lis ce souvenir",
  "Raconte cette mémoire",

  // Échecs 3D
  "On joue aux échecs",
  "Lance une partie d'échecs",
  "Lance la partie avec les noirs",
  "Réinitialise la partie d'échecs",
  "Quitte les échecs",
  "Lance la partie niveau moyen",
  "Lance la partie sans chrono",

  // Globe Terrestre 3D
  "Affiche la Terre",
  "Vue depuis l'espace",
  "Zoom sur la Terre",
  "Vol vers Tokyo",
  "Affiche ma position",
  "Où suis-je ?",
  "Trajet de Paris à Lyon",
  "Ferme le globe",

  // Télévision & Multimédia
  "Allume la télé",
  "Éteins la télé",
  "Lance Netflix sur la télé",
  "Mets du rock sur YouTube (Télé)",
  "Pause la télé",
  "Reprends la télé",
  "Monte le son de la télé",

  // Musique Spotify & Deezer
  "Lance Spotify",
  "Joue Billie Jean sur Spotify",
  "Suivant sur Spotify",
  "Volume Spotify monte",
  "Ouvre Deezer",
  "Recherche Michael Jackson sur Deezer",
  "Mets de la musique sur YouTube (PC)",

  // HomePod Mini & Audio Casque
  "Passe ta voix sur le HomePod",
  "Bascule sur le casque",
  "Règle le volume du HomePod à 50%",
  "Pause le HomePod",

  // Autopilote Web & Vision IA
  "Cherche un hôtel à Annecy sur Booking",
  "Cherche une PS5 moins de 400€ à Lyon",
  "Cherche les vols Paris-Barcelone sur Kayak",
  "Ferme le navigateur",
  "Lance l'autopilote OS",

  // Domotique Home Assistant
  "Allume la lumière du Salon",
  "Éteins la lumière du Bureau",
  "Mets la lumière en Bleu",
  "Règle la luminosité à 80%",
  "Quelle est la température dans le Salon ?",
  "Quel est le taux d'humidité dans le Bureau ?",
  "Combien d'abonnés sur TikTok ?",
  "Anniversaires du jour",
  "Active la scène Cinéma",
  "Désactive l'alarme",
  "Verrouille la porte",
  "Aspire la maison",
  "Retour à la base de l'aspirateur",

  // Intelligence & Assistance IA
  "Recherche approfondie sur l'intelligence artificielle",
  "Analyse mon écran",
  "Aide-moi",
  "Lance la caméra",
  "Regarde-moi",
  "Génère une image d'un coucher de soleil",
  "Dessine-moi une voiture de sport",
  "Tape le texte dicté",
  "Souviens-toi que j'aime le café",
  "Qu'est-ce que tu sais sur moi ?",
  "Liste ma mémoire",
  "Cherche dans mes souvenirs l'anniversaire",

  // Google Workspace
  "Crée un Google Doc intitulé Réunion",
  "Lis le contenu de mon Google Doc",
  "Lis mes nouveaux emails",
  "Lis le détail du dernier email",
  "Envoie un email à mylane@example.com",
  "Montre mon agenda",
  "Quels sont mes événements ?",
  "Ouvre mon Google Drive",
  "Ajoute une tâche faire les courses",

  // Sécurité & Mises à Jour
  "Analyse mon PC",
  "Lance le scan antivirus",
  "Active la protection en temps réel",
  "Mets à jour mes logiciels",
  "Lance winget",

  // Compétences Dynamiques / Démonstrations
  "Crée la compétence recherche_web",
  "Liste toutes tes compétences",
  "Lance la démo",
  "Écris le mot JARVIS",

  // Configuration & Flux
  "Prends la voix d'homme",
  "Prends la voix de femme",
  "Active le mode Iron Man",
  "Silence !",
  "Tais-toi !"
];

// ── Orb ───────────────────────────────────────────────────────────────────────
const orb = createOrb(canvas);
initHoloClock();

// Load and apply the saved color theme / orb style
const savedOrbStyle = localStorage.getItem("jarvis-orb-style") || "cyan";
orb.setTheme(savedOrbStyle);

// Initialize select element value
const orbStyleSelect = document.getElementById("settings-orb-style") as HTMLSelectElement;
if (orbStyleSelect) {
  orbStyleSelect.value = savedOrbStyle;
}

// ── State labels (French) ────────────────────────────────────────────────────
const STATE_LABELS: Record<OrbState, string> = {
  idle: "",
  listening: "ecoute...",
  thinking: "reflexion...",
  speaking: "",
  searching: "recherche..."
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
  wsRef.current = ws;
  (window as any)._jarvisWs = ws;
  updateIPTVWS(ws);

  ws.addEventListener("open", () => {
    setConnected(true);
    // Demander la liste de courses courante
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "get_shopping_list" }));
    }
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

      // ── Image Search ──
      if (data.type === "show_images") {
        showImagePanel((data as any).query || "IMAGE_SCAN", (data as any).images || []);
        return;
      }

      // ── Antivirus WS Messages ──
      if (data.type === "av_open") {
        openAntivirusPanel();
        return;
      }

      if (data.type === "av_start" || data.type === "av_progress" || data.type === "av_threat_detected" || data.type === "av_complete" || data.type === "av_cancel" || data.type === "av_action_result") {
        handleAntivirusWSMessage(data);
        return;
      }

      // ── Uninstaller WS Messages ──
      if (data.action === "uninstaller_open" || data.type === "uninstaller_open") {
        openUninstallerPanel();
        return;
      }

      if (data.type === "installed_programs" && (data as any).programs) {
        handleInstalledPrograms((data as any).programs);
        return;
      }

      if (data.type === "uninstall_progress") {
        updateUninstallProgress(data);
        return;
      }

      if (data.type === "uninstall_complete") {
        showUninstallComplete(data);
        return;
      }

      if (data.type === "clean_complete") {
        showCleanComplete(data);
        return;
      }

      // ── Winget WS Messages ──
      if (data.action === "winget_open" || data.type === "winget_open") {
        openWingetPanel();
        return;
      }

      if (data.type === "winget_upgrades" && (data as any).upgrades) {
        handleWingetUpgrades((data as any).upgrades);
        return;
      }

      if (data.type === "winget_upgrade_progress") {
        appendWingetProgress(data as any);
        return;
      }


      // —— NAVIGATEUR SÉCURISÉ ——
      if (data.action === "browser_state" && data.state) {
        if ((window as any).updateBrowserUIState) {
          (window as any).updateBrowserUIState(data.state);
        }
        return;
      }

      // ── Autonomous Dev Swarm HUD (Minimal Progress) ──
      if (data.action === "dev_swarm_update") {
        const swarmData = data as any;
        if (devSwarmHud) {
          devSwarmHud.classList.remove("hidden");
        }
        if (swarmProgressAgent) {
          swarmProgressAgent.textContent = `AGENT: ${swarmData.agent || 'SYSTEM'}`;
        }
        if (swarmProgressMsg) {
          swarmProgressMsg.textContent = swarmData.message || '';
        }
        if (swarmProgressBarFill) {
          let pct = 0;
          swarmProgressBarFill.classList.remove("success", "failure");
          if (swarmData.status === "success") {
            pct = 100;
            swarmProgressBarFill.classList.add("success");
          } else if (swarmData.status === "failure") {
            pct = 100;
            swarmProgressBarFill.classList.add("failure");
          } else {
            if (swarmData.agent === "PM") {
              pct = 20;
            } else if (swarmData.agent === "DEV") {
              pct = 60;
            } else if (swarmData.agent === "QA") {
              pct = 90;
            } else {
              pct = 10;
            }
          }
          swarmProgressBarFill.style.width = `${pct}%`;
        }
        // Auto-fermeture progressive du HUD après 8 secondes si terminé
        if (swarmData.status === "success" || swarmData.status === "failure") {
          setTimeout(() => {
            devSwarmHud?.classList.add("hidden");
          }, 8000);
        }
        return;
      }

      // ── Chess Map 3D ──
      if (data.action === "chess_start") {
        if (!_holoActive) {
          _openHolo();
        }
        setTimeout(() => {
          const app = (window as any)._holoApp;
          if (app) {
            if (!app.chessMap) {
              app.toggleChess();
            }
            setTimeout(() => {
              const chess = (window as any)._chessMap;
              if (chess) {
                // Si la commande provient du serveur avec des paramètres de configuration
                const anyData = data as any;
                if (anyData.difficulty) {
                  const diffSelect = document.getElementById('chess-config-difficulty') as HTMLSelectElement | null;
                  if (diffSelect) diffSelect.value = anyData.difficulty;
                }
                if (anyData.player_color) {
                  const colorSelect = document.getElementById('chess-config-color') as HTMLSelectElement | null;
                  if (colorSelect) colorSelect.value = anyData.player_color;
                }
                if (anyData.use_timer) {
                  const timerSelect = document.getElementById('chess-config-timer') as HTMLSelectElement | null;
                  if (timerSelect) timerSelect.value = anyData.use_timer;
                }

                // Démarrer la partie avec les paramètres si fournis
                if (anyData.difficulty && anyData.player_color && anyData.use_timer) {
                  chess.startFromConfig(anyData.difficulty, anyData.player_color, anyData.use_timer === 'yes');
                }

                chess.handleGameState(data.state);
              }
            }, 100);
          }
        }, 150);
        return;
      }

      if (data.action === "chess_reset") {
        const chess = (window as any)._chessMap;
        if (chess) {
          chess.resetGame(true); // reset forcé (sans confirm prompt)
        }
        return;
      }

      if (data.action === "chess_stop") {
        const app = (window as any)._holoApp;
        if (app && app.chessMap) {
          app.toggleChess();
        }
        return;
      }

      if (data.action === "chess_game_state") {
        const chess = (window as any)._chessMap;
        if (chess) {
          chess.handleGameState(data.state, (data as any).last_move);
        }
        return;
      }

      if (data.action === "chess_thinking") {
        const chess = (window as any)._chessMap;
        if (chess) {
          chess.handleThinking((data as any).thinking);
        }
        return;
      }

      // ── Network Radar 3D ──
      if (data.action === "network_radar_show") {
        if (!_holoActive) _openHolo();
        setTimeout(() => {
          const app = (window as any)._holoApp;
          if (app && !app.networkRadar) app.toggleNetworkRadar?.();
          const connections = (data as any).connections;
          if (connections) {
            setTimeout(() => {
              const radar = (window as any)._networkRadar;
              if (radar) radar.handleRadarUpdate(connections);
            }, 200);
          }
        }, 150);
        return;
      }
      if (data.action === "network_radar_update") {
        const radar = (window as any)._networkRadar;
        if (radar) radar.handleRadarUpdate((data as any).connections || []);
        return;
      }
      if (data.action === "network_radar_hide") {
        const app = (window as any)._holoApp;
        if (app?.networkRadar) app.toggleNetworkRadar?.();
        return;
      }
      if (data.action === "blocked_ips") {
        const radar = (window as any)._networkRadar;
        if (radar) radar.handleBlockedIps((data as any).ips || []);
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

      if (data.action === "domotic_audio_route_animation") {
        if (!_holoActive) {
          _openHolo();
        }
        setTimeout(() => {
          const app = (window as any)._holoApp;
          if (app && !app.domoticMap) {
            app.toggleDomotic();
          }
          setTimeout(() => {
            const domMap = (window as any)._domoticMap;
            if (domMap) domMap.handleServerResponse(data);
          }, 250);
        }, 200);
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

      if (data.action === "orb_write_word" && (data as any).word) {
        if (orb) {
          orb.writeWord((data as any).word);
        }
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

      // ── Shopping List ────────────────────────────────────────────────────
      if (data.type === "shopping_list" && (data as any).items !== undefined) {
        setShoppingList((data as any).items);
        return;
      }
      if (data.type === "shopping_open") {
        openShoppingPanel();
        return;
      }

      // ── IPTV Player WS Messages ──
      if (data.type === "iptv_open" || data.type === "iptv_stream_ready" || data.type === "iptv_playlist" || data.type === "iptv_direct_stream" || data.type === "iptv_playlist_error") {
        handleIPTVMessage(data);
        return;
      }

      // ── Home Assistant WS Messages ──
      if (data.type === "ha_states" || data.type === "ha_state_changed" || data.type === "ha_service_result") {
        handleHAMessage(data);
        return;
      }

      if (data.type === "detected_apps" && (data as any).apps) {
        if (appDetectSelect && appDetectBtn) {
          appDetectSelect.innerHTML = '<option value="">-- Sélectionner une application détectée --</option>';
          const appsList = (data as any).apps as {nom: string, chemin: string}[];
          appsList.forEach(app => {
            const opt = document.createElement("option");
            opt.value = app.chemin;
            opt.textContent = app.nom;
            appDetectSelect.appendChild(opt);
          });
          appDetectBtn.textContent = `🔍 APPS (${appsList.length})`;
        }
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
        // Orb Style & Antivirus Live
        const settingsOrbStyleEl = document.getElementById("settings-orb-style") as HTMLSelectElement;
        if (settingsOrbStyleEl) {
          settingsOrbStyleEl.value = settings.orb_style || "default";
          orb.setTheme(settingsOrbStyleEl.value);
          localStorage.setItem("jarvis-orb-style", settingsOrbStyleEl.value);
        }
        const settingsAvLiveEl = document.getElementById("settings-av-live") as HTMLInputElement;
        if (settingsAvLiveEl) {
          settingsAvLiveEl.checked = settings.av_live_protection === true;
        }

        // Remplissage des clés API
        if (settings.api_keys) {
          const geminiKeyEl = document.getElementById("settings-api-gemini-key") as HTMLInputElement;
          const groqKeyEl = document.getElementById("settings-api-groq-key") as HTMLInputElement;
          const youtubeKeyEl = document.getElementById("settings-api-youtube-key") as HTMLInputElement;
          const grokKeyEl = document.getElementById("settings-api-grok-key") as HTMLInputElement;
          const serpapiKeyEl = document.getElementById("settings-api-serpapi-key") as HTMLInputElement;
          const anthropicKeyEl = document.getElementById("settings-api-anthropic-key") as HTMLInputElement;
          const mistralKeyEl = document.getElementById("settings-api-mistral-key") as HTMLInputElement;

          if (geminiKeyEl) geminiKeyEl.value = settings.api_keys.GEMINI_API_KEY || "";
          if (groqKeyEl) groqKeyEl.value = settings.api_keys.GROQ_API_KEY || "";
          if (youtubeKeyEl) youtubeKeyEl.value = settings.api_keys.YOUTUBE_API_KEY || "";
          if (grokKeyEl) grokKeyEl.value = settings.api_keys.XAI_API_KEY || "";
          if (serpapiKeyEl) serpapiKeyEl.value = settings.api_keys.SERPAPI_API_KEY || "";
          if (anthropicKeyEl) anthropicKeyEl.value = settings.api_keys.ANTHROPIC_API_KEY || "";
          if (mistralKeyEl) mistralKeyEl.value = settings.api_keys.MISTRAL_API_KEY || "";
        }
        
        // Remplissage des checkboxes d'activation API
        const geminiEnabledEl = document.getElementById("settings-api-gemini-enabled") as HTMLInputElement;
        const groqEnabledEl = document.getElementById("settings-api-groq-enabled") as HTMLInputElement;
        const youtubeEnabledEl = document.getElementById("settings-api-youtube-enabled") as HTMLInputElement;
        const grokEnabledEl = document.getElementById("settings-api-grok-enabled") as HTMLInputElement;
        const serpapiEnabledEl = document.getElementById("settings-api-serpapi-enabled") as HTMLInputElement;
        const anthropicEnabledEl = document.getElementById("settings-api-anthropic-enabled") as HTMLInputElement;
        const mistralEnabledEl = document.getElementById("settings-api-mistral-enabled") as HTMLInputElement;
        
        if (geminiEnabledEl) geminiEnabledEl.checked = settings.api_gemini_enabled !== false;
        if (groqEnabledEl) groqEnabledEl.checked = settings.api_groq_enabled !== false;
        if (youtubeEnabledEl) youtubeEnabledEl.checked = settings.api_youtube_enabled !== false;
        if (grokEnabledEl) grokEnabledEl.checked = settings.api_grok_enabled !== false;
        if (serpapiEnabledEl) serpapiEnabledEl.checked = settings.api_serpapi_enabled !== false;
        if (anthropicEnabledEl) anthropicEnabledEl.checked = settings.api_anthropic_enabled !== false;
        if (mistralEnabledEl) mistralEnabledEl.checked = settings.api_mistral_enabled !== false;

        // Mise à jour visuelle du bouton de protection live dans le menu unifié
        const menuAvLiveBtn = document.getElementById("menu-av-live-btn");
        if (menuAvLiveBtn) {
          const enabled = settings.av_live_protection === true;
          menuAvLiveBtn.setAttribute("aria-pressed", String(enabled));
          menuAvLiveBtn.innerHTML = enabled
            ? `<span class="btn-icon">🛡️</span> PROT. TEMPS RÉEL : ON`
            : `<span class="btn-icon">🛡️</span> PROT. TEMPS RÉEL : OFF`;
          if (enabled) {
            menuAvLiveBtn.classList.add("active");
            menuAvLiveBtn.style.color = "#00ffcc";
            menuAvLiveBtn.style.borderColor = "#00ffcc";
          } else {
            menuAvLiveBtn.classList.remove("active");
            menuAvLiveBtn.style.color = "";
            menuAvLiveBtn.style.borderColor = "";
          }
        }
        
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
let hudLogs: string[] = [];

function showSubtitles(text: string) {
  const container = document.getElementById("subtitle-hud")!;
  const textEl = document.getElementById("subtitle-text")!;
  const metaEl = document.getElementById("subtitle-meta")!;

  if (textEl) {
    textEl.style.fontStyle = "normal";
    textEl.style.color = "#00e5ff";
  }

  // Si c'est un message du HUD de compilation (Iron Man Matrix)
  if (text.startsWith("[HUD]")) {
    if (subtitleTypeInterval) {
      clearInterval(subtitleTypeInterval);
      subtitleTypeInterval = null;
    }
    if (subtitleTimer) {
      clearTimeout(subtitleTimer);
      subtitleTimer = null;
    }
    container.style.display = "block";
    metaEl.textContent = "COMPILING_SKILL_MATRIX...";
    metaEl.style.color = "#ffaa00"; // Orange néon
    
    // Style type console / terminal
    if (textEl) {
      textEl.style.display = "block";
      textEl.style.textAlign = "left";
      textEl.style.whiteSpace = "pre-wrap";
      textEl.style.fontSize = "11px";
      textEl.style.lineHeight = "1.5";
      textEl.style.maxHeight = "120px";
      textEl.style.overflowY = "hidden";
      textEl.style.fontFamily = "'Courier New', monospace";
    }
    
    const cleanText = text.replace("[HUD] ", "").replace("[HUD]", "");
    
    // Réinitialiser les logs au début du processus
    if (cleanText.includes("COMPILING NEW SKILL") || cleanText.includes("SYSTEM: ALLOCATING")) {
      hudLogs = [];
    }
    
    // Filtrer les codes de couleur console ANSI éventuels
    const filteredText = cleanText.replace(/\u001b\[\d+m/g, '').replace(/\[0m/g, '').replace(/\[9\dm/g, '');
    
    if (filteredText.trim()) {
      hudLogs.push(filteredText);
      // Garder au maximum les 6 dernières lignes de logs à l'écran
      if (hudLogs.length > 6) {
        hudLogs.shift();
      }
    }
    
    if (textEl) {
      textEl.textContent = hudLogs.join("\n");
    }
    return;
  }

  // Restauration du style d'origine pour les sous-titres ordinaires de Jarvis
  if (textEl) {
    textEl.style.display = "inline";
    textEl.style.textAlign = "center";
    textEl.style.whiteSpace = "normal";
    textEl.style.fontSize = "18px";
    textEl.style.lineHeight = "1.4";
  }
  hudLogs = []; // Vider la console

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
// ── Unified Menu Event Listeners ─────────────────────────────────────────────
if (jarvisMenuBtn && jarvisMenuDropdown) {
  jarvisMenuBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    const isOpen = !jarvisMenuDropdown.classList.contains("hidden");
    if (isOpen) {
      jarvisMenuDropdown.classList.add("hidden");
      jarvisMenuBtn.classList.remove("active");
    } else {
      jarvisMenuDropdown.classList.remove("hidden");
      jarvisMenuBtn.classList.add("active");
    }
  });

  // Close menu when clicking outside of it
  document.addEventListener("click", (e) => {
    const target = e.target as HTMLElement;
    if (!jarvisMenuDropdown.classList.contains("hidden")) {
      if (!jarvisMenuDropdown.contains(target) && target !== jarvisMenuBtn) {
        jarvisMenuDropdown.classList.add("hidden");
        jarvisMenuBtn.classList.remove("active");
      }
    }
  });

  // Close menu when panel-opening buttons are clicked
  jarvisMenuDropdown.querySelectorAll(".menu-action-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.id;
      if (id === "menu-settings-btn" || id === "shopping-toggle-btn" || id === "menu-uninstaller-toggle-btn" || id === "winget-toggle-btn" || id === "menu-holo-btn" || id === "menu-iptv-toggle-btn" || id === "menu-ha-toggle-btn" || id === "browser-btn" || id === "menu-keyboard-toggle" || id === "clear-cache-btn" || id === "api-keys-button" || id === "menu-av-scan-btn" || id === "menu-av-live-btn") {
        jarvisMenuDropdown.classList.add("hidden");
        jarvisMenuBtn.classList.remove("active");
      }
    });
  });

  // Liaison des clics du menu unifié vers les boutons jumeaux originaux (évite les doublons d'IDs)
  const menuGpuBtn = document.getElementById("menu-gpu-btn");
  if (menuGpuBtn && gpuButtonEl) {
    menuGpuBtn.addEventListener("click", () => gpuButtonEl.click());
  }

  const menuSubtitleToggle = document.getElementById("menu-subtitle-toggle");
  if (menuSubtitleToggle && subtitleToggleButtonEl) {
    menuSubtitleToggle.addEventListener("click", () => subtitleToggleButtonEl.click());
  }

  const menuHoloBtn = document.getElementById("menu-holo-btn");
  if (menuHoloBtn && holoButtonEl) {
    menuHoloBtn.addEventListener("click", () => holoButtonEl.click());
  }

  const menuIptvToggleBtn = document.getElementById("menu-iptv-toggle-btn");
  if (menuIptvToggleBtn) {
    menuIptvToggleBtn.addEventListener("click", () => {
      const p = document.getElementById("iptv-panel");
      if (!p) return;
      if (p.classList.contains("hidden")) {
        p.classList.remove("hidden");
        menuIptvToggleBtn.setAttribute("aria-pressed", "true");
        menuIptvToggleBtn.classList.add("active");
      } else {
        p.classList.add("hidden");
        menuIptvToggleBtn.setAttribute("aria-pressed", "false");
        menuIptvToggleBtn.classList.remove("active");
        const vid = document.getElementById("iptv-video") as HTMLVideoElement | null;
        if (vid && !vid.paused) vid.pause();
      }
    });
  }

  const menuUninstallerToggleBtn = document.getElementById("menu-uninstaller-toggle-btn");
  if (menuUninstallerToggleBtn) {
    menuUninstallerToggleBtn.addEventListener("click", () => {
      const uninstallerPanel = document.getElementById("uninstaller-panel");
      if (!uninstallerPanel) return;
      const isHidden = uninstallerPanel.classList.contains("hidden");
      if (isHidden) {
        openUninstallerPanel();
        menuUninstallerToggleBtn.setAttribute("aria-pressed", "true");
        menuUninstallerToggleBtn.classList.add("active");
      } else {
        closeUninstallerPanel();
        menuUninstallerToggleBtn.setAttribute("aria-pressed", "false");
        menuUninstallerToggleBtn.classList.remove("active");
      }
    });
  }

  const menuHaToggleBtn = document.getElementById("menu-ha-toggle-btn");
  if (menuHaToggleBtn) {
    menuHaToggleBtn.addEventListener("click", () => {
      if (!haPanel) return;
      const isHidden = haPanel.classList.contains("hidden");
      if (isHidden) {
        haPanel.classList.remove("hidden");
        menuHaToggleBtn.setAttribute("aria-pressed", "true");
        menuHaToggleBtn.classList.add("active");
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: "ha_get_states" }));
        }
      } else {
        haPanel.classList.add("hidden");
        menuHaToggleBtn.setAttribute("aria-pressed", "false");
        menuHaToggleBtn.classList.remove("active");
      }
    });
  }

  const menuSettingsBtn = document.getElementById("menu-settings-btn");
  if (menuSettingsBtn) {
    menuSettingsBtn.addEventListener("click", () => {
      // Masquer le menu déroulant
      if (jarvisMenuDropdown) jarvisMenuDropdown.classList.add("hidden");
      if (jarvisMenuBtn) jarvisMenuBtn.classList.remove("active");
      
      // Désactiver le clavier visuel s'il est ouvert pour éviter la superposition
      if (keyboardEnabled && keyboardToggleButtonEl && keyboardHudEl) {
        keyboardEnabled = false;
        keyboardToggleButtonEl.setAttribute("aria-pressed", "false");
        keyboardHudEl.style.display = "none";
      }

      // Ouvrir directement le modal paramètres
      if (settingsModalEl) {
        settingsModalEl.classList.add("visible");
      }
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "get_settings" }));
      }

      // Énumération autonome des caméras
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
  }

  const menuKeyboardToggle = document.getElementById("menu-keyboard-toggle");
  const keyboardToggle = document.getElementById("keyboard-toggle");
  if (menuKeyboardToggle && keyboardToggle) {
    menuKeyboardToggle.addEventListener("click", () => keyboardToggle.click());
  }

  // ── Antivirus Scan / Live Protection dans le menu unifié ──
  const menuAvScanBtn = document.getElementById("menu-av-scan-btn");
  const settingsAvScanBtn = document.getElementById("settings-av-scan-btn");
  if (menuAvScanBtn && settingsAvScanBtn) {
    menuAvScanBtn.addEventListener("click", () => {
      // Fermer le menu déroulant et déclencher le scan antivirus
      if (jarvisMenuDropdown) jarvisMenuDropdown.classList.add("hidden");
      if (jarvisMenuBtn) jarvisMenuBtn.classList.remove("active");
      settingsAvScanBtn.click();
    });
  }

  const menuAvLiveBtn = document.getElementById("menu-av-live-btn");
  const settingsAvLive = document.getElementById("settings-av-live") as HTMLInputElement;
  if (menuAvLiveBtn && settingsAvLive) {
    menuAvLiveBtn.addEventListener("click", () => {
      if (jarvisMenuDropdown) jarvisMenuDropdown.classList.add("hidden");
      if (jarvisMenuBtn) jarvisMenuBtn.classList.remove("active");
      settingsAvLive.click();
    });
  }

  // ── Bouton Vider Cache / Recharger ──
  const clearCacheBtn = document.getElementById("clear-cache-btn") as HTMLButtonElement;
  if (clearCacheBtn) {
    clearCacheBtn.addEventListener("click", () => {
      if (jarvisMenuDropdown) jarvisMenuDropdown.classList.add("hidden");
      if (jarvisMenuBtn) jarvisMenuBtn.classList.remove("active");
      clearCacheBtn.disabled = true;
      clearCacheBtn.innerHTML = '<span class="btn-icon">⏳</span> NETTOYAGE EN COURS...';
      const banner = document.getElementById("update-banner");
      if (banner) {
        banner.style.display = "block";
        banner.style.cursor = "default";
        banner.textContent = "⏳ NETTOYAGE DU CACHE EN COURS...";
        banner.style.background = "linear-gradient(90deg, rgba(0,30,80,0.95), rgba(0,100,180,0.85))";
      }
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "clear_cache" }));
      } else {
        setTimeout(() => location.reload(), 1500);
      }
    });
  }

  // ── Bouton Liste des Commandes ──
  const commandsBtn = document.getElementById("commands-btn");
  if (commandsBtn) {
    commandsBtn.addEventListener("click", () => {
      if (jarvisMenuDropdown) jarvisMenuDropdown.classList.add("hidden");
      if (jarvisMenuBtn) jarvisMenuBtn.classList.remove("active");
      showHelpHUD();
    });
  }

  // ── Bouton de configuration des clés API ──
  if (apiKeysButtonEl && apiKeysModalEl) {
    apiKeysButtonEl.addEventListener("click", () => {
      if (jarvisMenuDropdown) jarvisMenuDropdown.classList.add("hidden");
      if (jarvisMenuBtn) jarvisMenuBtn.classList.remove("active");
      apiKeysModalEl.style.display = "flex";
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "get_settings" }));
      }
    });
  }

  if (apiKeysCloseBtn && apiKeysModalEl) {
    apiKeysCloseBtn.addEventListener("click", () => {
      apiKeysModalEl.style.display = "none";
    });
  }

  if (apiKeysSaveBtn && apiKeysModalEl) {
    apiKeysSaveBtn.addEventListener("click", () => {
      const geminiEnabledEl = document.getElementById("settings-api-gemini-enabled") as HTMLInputElement;
      const groqEnabledEl = document.getElementById("settings-api-groq-enabled") as HTMLInputElement;
      const youtubeEnabledEl = document.getElementById("settings-api-youtube-enabled") as HTMLInputElement;
      const grokEnabledEl = document.getElementById("settings-api-grok-enabled") as HTMLInputElement;
      const serpapiEnabledEl = document.getElementById("settings-api-serpapi-enabled") as HTMLInputElement;
      const anthropicEnabledEl = document.getElementById("settings-api-anthropic-enabled") as HTMLInputElement;
      const mistralEnabledEl = document.getElementById("settings-api-mistral-enabled") as HTMLInputElement;

      const geminiKeyEl = document.getElementById("settings-api-gemini-key") as HTMLInputElement;
      const groqKeyEl = document.getElementById("settings-api-groq-key") as HTMLInputElement;
      const youtubeKeyEl = document.getElementById("settings-api-youtube-key") as HTMLInputElement;
      const grokKeyEl = document.getElementById("settings-api-grok-key") as HTMLInputElement;
      const serpapiKeyEl = document.getElementById("settings-api-serpapi-key") as HTMLInputElement;
      const anthropicKeyEl = document.getElementById("settings-api-anthropic-key") as HTMLInputElement;
      const mistralKeyEl = document.getElementById("settings-api-mistral-key") as HTMLInputElement;

      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: "update_settings",
          settings: {
            api_gemini_enabled: geminiEnabledEl ? geminiEnabledEl.checked : true,
            api_groq_enabled: groqEnabledEl ? groqEnabledEl.checked : true,
            api_youtube_enabled: youtubeEnabledEl ? youtubeEnabledEl.checked : true,
            api_grok_enabled: grokEnabledEl ? grokEnabledEl.checked : true,
            api_serpapi_enabled: serpapiEnabledEl ? serpapiEnabledEl.checked : true,
            api_anthropic_enabled: anthropicEnabledEl ? anthropicEnabledEl.checked : true,
            api_mistral_enabled: mistralEnabledEl ? mistralEnabledEl.checked : true,
            api_keys: {
              GEMINI_API_KEY: geminiKeyEl ? geminiKeyEl.value.trim() : "",
              GROQ_API_KEY: groqKeyEl ? groqKeyEl.value.trim() : "",
              YOUTUBE_API_KEY: youtubeKeyEl ? youtubeKeyEl.value.trim() : "",
              XAI_API_KEY: grokKeyEl ? grokKeyEl.value.trim() : "",
              SERPAPI_API_KEY: serpapiKeyEl ? serpapiKeyEl.value.trim() : "",
              ANTHROPIC_API_KEY: anthropicKeyEl ? anthropicKeyEl.value.trim() : "",
              MISTRAL_API_KEY: mistralKeyEl ? mistralKeyEl.value.trim() : ""
            }
          }
        }));
      }
      apiKeysModalEl.style.display = "none";
    });
  }
}


muteButtonEl.addEventListener("click", () => {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;

  // Envoi du signal stop au backend
  ws.send(JSON.stringify({ type: "stop_audio" }));

  // Feedback immédiat sur l'orbe
  applyState("idle");
});

gpuButtonEl?.addEventListener("click", () => {
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

subtitleToggleButtonEl?.addEventListener("click", () => {
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
    // Réinitialiser la position pour le centrer au cas où il a été glissé précédemment
    keyboardHudEl.style.left = "";
    keyboardHudEl.style.top = "";
    keyboardHudEl.style.right = "";
    keyboardHudEl.style.bottom = "";
    keyboardHudEl.style.transform = "";
    setTimeout(() => keyboardInputEl.focus(), 100);
  }
});

// Rendre le clavier HUD déplaçable par son en-tête
const keyboardHeaderEl = keyboardHudEl?.querySelector(".keyboard-hud-header") as HTMLElement | null;
if (keyboardHudEl && keyboardHeaderEl) {
  makePanelDraggable(keyboardHudEl, keyboardHeaderEl);
}

let keyboardDecryptTimeout: any = null;
keyboardInputEl.addEventListener("input", () => {
  const statusLabel = document.getElementById("keyboard-status-label");
  if (!statusLabel) return;

  // Effet de décryptage dynamique
  const chars = "0123456789ABCDEFXYZ//_#◈";
  let randomStr = "";
  for (let i = 0; i < 6; i++) {
    randomStr += chars[Math.floor(Math.random() * chars.length)];
  }
  statusLabel.textContent = `DECRYPTING: [ ${randomStr} ]`;
  statusLabel.style.color = "#ff8a1a"; // Orange pendant le décryptage
  statusLabel.style.textShadow = "0 0 8px rgba(255, 138, 26, 0.5)";

  if (keyboardDecryptTimeout) clearTimeout(keyboardDecryptTimeout);
  keyboardDecryptTimeout = setTimeout(() => {
    statusLabel.textContent = "AWAITING_COMMAND...";
    statusLabel.style.color = "#00e5ff"; // Retour au cyan JARVIS
    statusLabel.style.textShadow = "0 0 8px rgba(0, 229, 255, 0.4)";
  }, 400);
});

keyboardInputEl.addEventListener("keydown", (e) => {
  const statusLabel = document.getElementById("keyboard-status-label");
  if (e.key === "Enter") {
    const val = keyboardInputEl.value.trim();
    if (val && ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "user_input", text: val }));
      keyboardInputEl.value = "";
      
      // Flash de statut d'envoi réussi
      if (statusLabel) {
        statusLabel.textContent = "COMMAND_TRANSMITTED";
        statusLabel.style.color = "#00ff88"; // Vert de validation
        statusLabel.style.textShadow = "0 0 10px rgba(0, 255, 136, 0.6)";
        if (keyboardDecryptTimeout) clearTimeout(keyboardDecryptTimeout);
        keyboardDecryptTimeout = setTimeout(() => {
          statusLabel.textContent = "AWAITING_COMMAND...";
          statusLabel.style.color = "#00e5ff";
          statusLabel.style.textShadow = "0 0 8px rgba(0, 229, 255, 0.4)";
        }, 1200);
      }
    }
  }
});

// ── Settings UI Logic ────────────────────────────────────────────────────────
settingsButtonEl?.addEventListener("click", () => {
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

swarmCloseBtn?.addEventListener("click", () => {
  devSwarmHud?.classList.add("hidden");
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
  hideCarouselArrow();
  activerHolo();
}
(window as any)._openHolo = _openHolo;

function _closeHolo() {
  _holoActive = false;
  desactiverHolo();
  if (_holoOverlay) _holoOverlay.style.display = "none";
  if (holoButtonEl) holoButtonEl.setAttribute("aria-pressed", "false");
  const orbCanvas = document.getElementById("orb-canvas");
  if (orbCanvas) orbCanvas.style.display = "block";
  showCarouselArrow();
}
(window as any)._closeHolo = _closeHolo;

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

if (appDetectBtn) {
  appDetectBtn.addEventListener("click", () => {
    appDetectBtn.textContent = "🔍 SCAN...";
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "detect_apps" }));
    }
  });
}

if (appDetectSelect) {
  appDetectSelect.addEventListener("change", () => {
    const selectedPath = appDetectSelect.value;
    const selectedText = appDetectSelect.options[appDetectSelect.selectedIndex].text;
    if (selectedPath && selectedText) {
      const alreadyExists = currentCustomApps.some(app => app.exe_path === selectedPath);
      if (!alreadyExists) {
        const id = selectedText.toLowerCase().replace(/[^a-z0-9]/g, "_");
        currentCustomApps.push({ id, label: selectedText, exe_path: selectedPath });
        renderCustomApps();
      }
      appDetectSelect.value = "";
    }
  });
}

settingsSaveBtn.addEventListener("click", () => {
  const selectedMic = settingsMicSelect.value;

  // Sauvegarde du style de l'orbe dans le localStorage et application instantanée
  const orbStyleSelect = document.getElementById("settings-orb-style") as HTMLSelectElement;
  if (orbStyleSelect) {
    const selectedStyle = orbStyleSelect.value;
    localStorage.setItem("jarvis-orb-style", selectedStyle);
    orb.setTheme(selectedStyle);
  }
  
  // Sauvegarde de la caméra sélectionnée dans le localStorage
  if (settingsCameraSelect) {
    localStorage.setItem("jarvis-camera-id", settingsCameraSelect.value);
  }

  const settingsAvLiveEl = document.getElementById("settings-av-live") as HTMLInputElement;

  const settings = {
    user_name: settingsNameEl.value.trim(),
    user_age: settingsAgeEl.value.trim(),
    mic_device_index: selectedMic === "" ? null : parseInt(selectedMic, 10),
    musique_lien: settingsMusiqueLien.value.trim(),
    custom_apps: currentCustomApps,
    custom_lights: currentCustomLights,
    custom_prises: currentCustomPrises,
    custom_capteurs: currentCustomCapteurs,
    orb_style: orbStyleSelect ? orbStyleSelect.value : "default",
    av_live_protection: settingsAvLiveEl ? settingsAvLiveEl.checked : false
  };
  
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "update_settings", settings }));
  }
  
  settingsModalEl.classList.remove("visible");
});

// Toggle visibilité des mots de passe (oeil)
document.querySelectorAll(".toggle-password-eye").forEach(eye => {
  eye.addEventListener("click", () => {
    const targetId = eye.getAttribute("data-target");
    if (targetId) {
      const input = document.getElementById(targetId) as HTMLInputElement;
      if (input) {
        if (input.type === "password") {
          input.type = "text";
          eye.textContent = "🙈";
        } else {
          input.type = "password";
          eye.textContent = "👁️";
        }
      }
    }
  });
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
      // Retirer la protection anti-FOUC pour révéler l'interface
      document.body.classList.remove("loading");
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
initHADashboard(ws);
initIPTVPlayer(ws);
initDynamicAmbientGlow();
initMagneticButtons();
runBootSequence();

// ── Carrousel de conseils (extrait dans ui/tips.ts) ──
initDynamicUserTips();
// ── Help HUD Logic ───────────────────────────────────────────────────────────
function showHelpHUD() {
  helpOverlayEl.style.display = "block";
  helpOverlayEl.innerHTML = "";

  // Select 16 random commands (8 on each side) to keep them visible within the viewport
  const shuffled = [...HELP_COMMANDS].sort(() => 0.5 - Math.random());
  const selected = shuffled.slice(0, 16);

  selected.forEach((cmd, i) => {
    const isRight = i % 2 === 1;
    const widget = document.createElement("div");
    widget.className = `help-widget ${isRight ? 'right' : ''}`;

    // Grid-like positioning with absolute geometric alignment (no overlap)
    const row = Math.floor(i / 2);
    const top = 120 + (row * 84);
    widget.style.top = `${top}px`;

    // Position them on the left or right side with identical margins
    const sideOffset = 45;
    if (isRight) widget.style.right = `${sideOffset}px`;
    else widget.style.left = `${sideOffset}px`;

    // Cinematic reveal delay (shorter timeout for faster entrance)
    widget.style.transitionDelay = `${(i % 5) * 0.15}s`;

    widget.innerHTML = `
      <div class="help-widget-title" style="display:flex; justify-content: space-between;">
        <span>CAPACITÉ ${Math.floor(Math.random() * 999)}</span>
        <span style="opacity:0.3">[SYNC]</span>
      </div>
      <div class="help-widget-cmd">"${cmd}"</div>
    `;

    helpOverlayEl.appendChild(widget);

    // Cinematic reveal (set transition visible immediately or on next tick)
    requestAnimationFrame(() => {
      setTimeout(() => widget.classList.add("visible"), 50);
    });
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
// (showImageHUD extrait dans panels/image_panels.ts)

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

// ── Drag & Drop souris pour les widgets HUD (extrait dans ui/draggable.ts) ──
// Appliquer le drag à tous les widgets HUD au chargement (ils existent dans le DOM même si cachés)
["calendar-hud", "weather-hud", "music-hud", "dev-swarm-hud"].forEach(id => {
  const el = document.getElementById(id);
  if (el) makeDraggable(el);
});

// ── Dock carrousel (extrait dans ui/carousel.ts) ──
initCarouselDock();

// (Panneau antivirus extrait dans panels/antivirus_panel.ts)

// Lancement manuel du scan antivirus depuis le menu des paramètres
const settingsAvScanBtn = document.getElementById("settings-av-scan-btn") as HTMLButtonElement;
if (settingsAvScanBtn) {
  settingsAvScanBtn.addEventListener("click", () => {
    // Fermer le modal des paramètres
    if (settingsModalEl) {
      settingsModalEl.classList.remove("visible");
    }
    // Ouvrir le panneau antivirus et démarrer le scan
    openAntivirusPanel();
  });
}

// Raccourci ANTIVIRUS dans le menu principal
const menuAvScanBtn = document.getElementById("menu-av-scan-btn") as HTMLButtonElement;
if (menuAvScanBtn) {
  menuAvScanBtn.addEventListener("click", () => {
    // Fermer le menu déroulant (requête dynamique d'éléments)
    const dropdown = document.getElementById("jarvis-menu-dropdown");
    if (dropdown) dropdown.classList.add("hidden");
    const menuBtn = document.getElementById("jarvis-menu-btn");
    if (menuBtn) menuBtn.classList.remove("active");
    // Ouvrir le panneau antivirus
    openAntivirusPanel();
  });
}

// (Modal info antivirus extrait dans panels/antivirus_panel.ts)

// (Listeners désinstallateur extraits dans panels/uninstaller_panel.ts)

// ── LOGIQUE DU LECTEUR IPTV / VIDÉO ──
document.getElementById("iptv-toggle-btn")?.addEventListener("click", () => {
  const p = document.getElementById("iptv-panel");
  if (!p) return;
  const btn = document.getElementById("iptv-toggle-btn");
  if (p.classList.contains("hidden")) {
    p.classList.remove("hidden");
    btn?.setAttribute("aria-pressed", "true");
  } else {
    p.classList.add("hidden");
    btn?.setAttribute("aria-pressed", "false");
    const vid = document.getElementById("iptv-video") as HTMLVideoElement | null;
    if (vid && !vid.paused) vid.pause();
  }
});

// (Panneau courses extrait dans panels/shopping_panel.ts)

// ── LOGIQUE DU DASHBOARD DOMOTIQUE HOME ASSISTANT ────────────────────────────
haToggleBtn?.addEventListener("click", () => {
  if (!haPanel) return;
  const isHidden = haPanel.classList.contains("hidden");
  if (isHidden) {
    haPanel.classList.remove("hidden");
    haToggleBtn.setAttribute("aria-pressed", "true");
    haToggleBtn.classList.add("active");
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "ha_get_states" }));
    }
  } else {
    haPanel.classList.add("hidden");
    haToggleBtn.setAttribute("aria-pressed", "false");
    haToggleBtn.classList.remove("active");
  }
});


// (Panneaux images extraits dans panels/image_panels.ts)

// (Désinstallateur extrait dans panels/uninstaller_panel.ts)

// (Panneau winget extrait dans panels/winget_panel.ts)

// ══ NAVIGATEUR SÉCURISÉ CONTRÔLES & ÉVÉNEMENTS ══
(window as any).updateBrowserUIState = (state: string) => {
  const browserControls = document.getElementById("hud-browser-controls");
  const dockBtn = document.getElementById("hud-browser-dock-btn");
  if (state === "docked") {
    document.body.classList.add("browser-open");
    if (browserControls) browserControls.classList.remove("hidden");
    if (dockBtn) dockBtn.innerText = "⚡ DÉTACHER";
  } else if (state === "undocked") {
    document.body.classList.remove("browser-open");
    if (browserControls) browserControls.classList.remove("hidden");
    if (dockBtn) dockBtn.innerText = "🔗 ANCRER";
  } else if (state === "closed") {
    document.body.classList.remove("browser-open");
    if (browserControls) browserControls.classList.add("hidden");
  }
};

const browserBtnEl = document.getElementById("browser-btn") as HTMLButtonElement;
if (browserBtnEl) {
  browserBtnEl.addEventListener("click", () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "open_browser" }));
    }
  });
}

const hudBrowserDockBtn = document.getElementById("hud-browser-dock-btn") as HTMLButtonElement;
const hudBrowserCloseBtn = document.getElementById("hud-browser-close-btn") as HTMLButtonElement;

if (hudBrowserDockBtn) {
  hudBrowserDockBtn.addEventListener("click", () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      if (document.body.classList.contains("browser-open")) {
        ws.send(JSON.stringify({ type: "undock_browser" }));
      } else {
        ws.send(JSON.stringify({ type: "dock_browser" }));
      }
    }
  });
}

if (hudBrowserCloseBtn) {
  hudBrowserCloseBtn.addEventListener("click", () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "close_browser" }));
    }
  });
}

// (Effets ambiants extraits dans ui/effects.ts)

// ── BINDINGS D'ÉVÉNEMENTS POUR LE DOCK CAROUSEL OPERATIONAL (OPTION B) ──
const bindCarouselAction = (btnId: string, actionFn: () => void) => {
  const btn = document.getElementById(btnId);
  if (btn) btn.addEventListener("click", actionFn);
};

// 1. Vision (déjà liée à vision-button par ailleurs, mais on assure la compatibilité)
bindCarouselAction("vision-button", () => {
  const original = document.getElementById("vision-button");
  if (original && original !== document.activeElement) {
    // La logique de Vision s'active déjà sur son clic, aucun doublon requis.
  }
});

// 2. IPTV / Lecteur Vidéo
bindCarouselAction("carousel-iptv-btn", () => {
  const p = document.getElementById("iptv-panel");
  if (!p) return;
  const isHidden = p.classList.contains("hidden");
  if (isHidden) {
    p.classList.remove("hidden");
    const btn = document.getElementById("carousel-iptv-btn");
    if (btn) { btn.classList.add("active"); btn.setAttribute("aria-pressed", "true"); }
  } else {
    p.classList.add("hidden");
    const btn = document.getElementById("carousel-iptv-btn");
    if (btn) { btn.classList.remove("active"); btn.setAttribute("aria-pressed", "false"); }
    const vid = document.getElementById("iptv-video") as HTMLVideoElement | null;
    if (vid && !vid.paused) vid.pause();
  }
});

// 3. Désinstallateur
bindCarouselAction("carousel-uninstaller-btn", () => {
  const uninstallerPanel = document.getElementById("uninstaller-panel");
  if (!uninstallerPanel) return;
  const isHidden = uninstallerPanel.classList.contains("hidden");
  if (isHidden) {
    // openUninstallerPanel est une fonction globale disponible dans main.ts
    // Déclenchons-la :
    const openBtn = document.getElementById("uninstaller-toggle-btn");
    if (openBtn) {
      openBtn.click();
    } else {
      uninstallerPanel.classList.remove("hidden");
    }
    const btn = document.getElementById("carousel-uninstaller-btn");
    if (btn) { btn.classList.add("active"); btn.setAttribute("aria-pressed", "true"); }
  } else {
    const closeBtn = document.getElementById("uninstaller-close-btn");
    if (closeBtn) {
      closeBtn.click();
    } else {
      uninstallerPanel.classList.add("hidden");
    }
    const btn = document.getElementById("carousel-uninstaller-btn");
    if (btn) { btn.classList.remove("active"); btn.setAttribute("aria-pressed", "false"); }
  }
});

// 4. Winget / Mises à jour
bindCarouselAction("carousel-winget-btn", () => {
  const wingetLogsPanel = document.getElementById("winget-logs-panel");
  if (!wingetLogsPanel) return;
  const isHidden = wingetLogsPanel.classList.contains("hidden");
  if (isHidden) {
    wingetLogsPanel.classList.remove("hidden");
    const btn = document.getElementById("carousel-winget-btn");
    if (btn) { btn.classList.add("active"); btn.setAttribute("aria-pressed", "true"); }
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "winget_get_logs" }));
    }
  } else {
    wingetLogsPanel.classList.add("hidden");
    const btn = document.getElementById("carousel-winget-btn");
    if (btn) { btn.classList.remove("active"); btn.setAttribute("aria-pressed", "false"); }
  }
});

// 5. Antivirus Scan
bindCarouselAction("carousel-av-scan-btn", () => {
  // Déclenche le scan antivirus en simulant le clic sur le bouton de configuration d'origine
  const settingsAvScanBtn = document.getElementById("settings-av-scan-btn");
  if (settingsAvScanBtn) {
    settingsAvScanBtn.click();
  }
});

// 6. Domotique (Home Assistant)
bindCarouselAction("carousel-ha-btn", () => {
  const haPanel = document.getElementById("ha-panel");
  if (!haPanel) return;
  const isHidden = haPanel.classList.contains("hidden");
  if (isHidden) {
    haPanel.classList.remove("hidden");
    const btn = document.getElementById("carousel-ha-btn");
    if (btn) { btn.classList.add("active"); btn.setAttribute("aria-pressed", "true"); }
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "ha_get_states" }));
    }
  } else {
    haPanel.classList.add("hidden");
    const btn = document.getElementById("carousel-ha-btn");
    if (btn) { btn.classList.remove("active"); btn.setAttribute("aria-pressed", "false"); }
  }
});

// 7. Navigateur Sécurisé
bindCarouselAction("carousel-browser-btn", () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "open_browser" }));
  }
});

// 8. Liste des commandes
bindCarouselAction("carousel-commands-btn", () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "open_commands_file" }));
  }
});

// 9. API Keys Modal
bindCarouselAction("carousel-api-btn", () => {
  const modal = document.getElementById("api-keys-modal");
  if (modal) {
    const isVisible = modal.classList.contains("visible");
    if (isVisible) {
      modal.classList.remove("visible");
    } else {
      modal.classList.add("visible");
    }
  }
});
