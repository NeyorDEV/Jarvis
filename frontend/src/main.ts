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

// Shopping Panel DOM refs
const shoppingPanel = document.getElementById("shopping-panel") as HTMLDivElement;
const shoppingCloseBtn = document.getElementById("shopping-panel-close-btn") as HTMLButtonElement;
const shoppingListContainer = document.getElementById("shopping-list-container") as HTMLDivElement;
const shoppingAddInput = document.getElementById("shopping-add-input") as HTMLInputElement;
const shoppingAddBtn = document.getElementById("shopping-add-btn") as HTMLButtonElement;
const shoppingClearBtn = document.getElementById("shopping-clear-btn") as HTMLButtonElement;
const shoppingHeader = document.getElementById("shopping-panel-header") as HTMLDivElement;

// Swarm HUD DOM refs (Minimal)
const devSwarmHud = document.getElementById("dev-swarm-hud") as HTMLDivElement;
const swarmCloseBtn = document.getElementById("swarm-close-btn") as HTMLButtonElement;
const swarmProgressAgent = document.getElementById("swarm-progress-agent") as HTMLSpanElement;
const swarmProgressBarFill = document.getElementById("swarm-progress-bar-fill") as HTMLDivElement;
const swarmProgressMsg = document.getElementById("swarm-progress-msg") as HTMLSpanElement;

// ── Winget Upgrade DOM Refs ────────────────────────────────────────────────
const wingetPanel = document.getElementById("winget-panel") as HTMLDivElement;
const wingetToggleBtn = document.getElementById("winget-toggle-btn") as HTMLButtonElement;
const wingetCloseBtn = document.getElementById("winget-panel-close-btn") as HTMLButtonElement;
const wingetHeader = document.getElementById("winget-panel-header") as HTMLDivElement;
const wingetSearchInput = document.getElementById("winget-search-input") as HTMLInputElement;
const wingetList = document.getElementById("winget-upgrades-list") as HTMLDivElement;
const wingetSelectAll = document.getElementById("winget-select-all") as HTMLInputElement;
const wingetRefreshBtn = document.getElementById("winget-refresh-btn") as HTMLButtonElement;
const wingetUpgradeSelectedBtn = document.getElementById("winget-upgrade-selected-btn") as HTMLButtonElement;
const wingetUpgradeAllBtn = document.getElementById("winget-upgrade-all-btn") as HTMLButtonElement;
const wingetLogsContainer = document.getElementById("winget-logs-container") as HTMLDivElement;
const wingetConsole = document.getElementById("winget-console") as HTMLPreElement;
const wingetCloseLogsBtn = document.getElementById("winget-close-logs-btn") as HTMLButtonElement;
const wingetCountBadge = document.getElementById("winget-count-badge") as HTMLSpanElement;

interface WingetUpgradeItem {
  name: string;
  id: string;
  version: string;
  available: string;
  source: string;
}

let allWingetUpgrades: WingetUpgradeItem[] = [];

// ── Uninstaller DOM Refs ───────────────────────────────────────────────────
const uninstallerPanel = document.getElementById("uninstaller-panel") as HTMLDivElement;
const uninstallerToggleBtn = document.getElementById("uninstaller-toggle-btn") as HTMLButtonElement;
const uninstallerCloseBtn = document.getElementById("uninstaller-panel-close-btn") as HTMLButtonElement;
const uninstallerHeader = document.getElementById("uninstaller-panel-header") as HTMLDivElement;
const uninstallerSearchInput = document.getElementById("uninstaller-search-input") as HTMLInputElement;
const uninstallerAppsList = document.getElementById("uninstaller-apps-list") as HTMLDivElement;
const uninstallerListView = document.getElementById("uninstaller-list-view") as HTMLDivElement;
const uninstallerActionView = document.getElementById("uninstaller-action-view") as HTMLDivElement;
const uninstallerStatusMsg = document.getElementById("uninstaller-status-msg") as HTMLDivElement;
const uninstallerRadarContainer = document.getElementById("uninstaller-radar-container") as HTMLDivElement;
const uninstallerLeftoversContainer = document.getElementById("uninstaller-leftovers-container") as HTMLDivElement;
const uninstallerLeftoversList = document.getElementById("uninstaller-leftovers-list") as HTMLDivElement;
const uninstallerSelectAll = document.getElementById("uninstaller-select-all") as HTMLInputElement;
const uninstallerCleanBtn = document.getElementById("uninstaller-clean-btn") as HTMLButtonElement;
const uninstallerSkipBtn = document.getElementById("uninstaller-skip-btn") as HTMLButtonElement;

let allInstalledPrograms: Array<{
  name: string;
  subkey: string;
  publisher: string;
  version: string;
  uninstall_string: string;
  install_location: string;
  icon_path: string;
  hive: string;
}> = [];
let currentLeftovers: Array<{
  type: string;
  path: string;
  desc: string;
  hive?: string;
}> = [];

let currentShoppingList: string[] = [];
let shoppingInitialLoaded = false;

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
        allInstalledPrograms = (data as any).programs;
        renderInstalledPrograms(allInstalledPrograms);
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
        allWingetUpgrades = (data as any).upgrades;
        renderWingetUpgrades(allWingetUpgrades);
        return;
      }

      if (data.type === "winget_upgrade_progress") {
        const progressData = data as any;
        if (wingetConsole) {
          if (progressData.status === "running") {
            wingetConsole.textContent += progressData.log;
            wingetConsole.scrollTop = wingetConsole.scrollHeight;
          } else if (progressData.status === "complete") {
            wingetConsole.textContent += `\n[JARVIS] Processus de mise à jour terminé (Code: ${progressData.returncode}).\n`;
            wingetConsole.scrollTop = wingetConsole.scrollHeight;
          }
        }
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
        currentShoppingList = (data as any).items;
        renderShoppingList();
        return;
      }
      if (data.type === "shopping_open") {
        if (shoppingPanel) {
          shoppingPanel.classList.remove("hidden");
          shoppingPanel.classList.add("visible");
        }
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
  if (_carouselArrow) _carouselArrow.style.display = "none";
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
  if (_carouselArrow) { _carouselArrow.style.display = "flex"; _positionArrow(_carouselOpen); }
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

// ── Dynamic Quick Tips Carousel (Option 2) ──────────────────────────
const QUICK_TIPS = [
  "DEMANDEZ : 'ACTIVE LE MODE IRON MAN'",
  "DEMANDEZ : 'LANCE LE SCAN ANTIVIRUS'",
  "DEMANDEZ : 'ALLUME LA LUMIERE DU SALON'",
  "DEMANDEZ : 'LANCE UNE PARTIE D'ECHECS'",
  "DEMANDEZ : 'LANCE LE DESSIN DE JARVIS'",
  "DEMANDEZ : 'LANCE LE LECTEUR IPTV'",
  "CONSEIL : SURVOLEZ LES BOUTONS POUR L'ATTRACTION MAGNETIQUE",
  "SAISIE DIRECTE : CLIQUEZ SUR CLAVIER POUR LES COMMANDES TEXTE",
  "CONFIGURATION : COMMANDE 'METS LA VOIX D'HOMME / DE FEMME'"
];

function initDynamicUserTips() {
  const tipPanelEl = document.getElementById("user-tip");
  const tipTextEl = document.getElementById("user-tip-text");
  if (!tipPanelEl || !tipTextEl) return;

  let currentTipIndex = 0;
  let typingInterval: number | null = null;
  let collapseTimeout: number | null = null;
  let isCollapsed = false;

  function typeText(text: string, callback: () => void) {
    let charIndex = 0;
    tipTextEl!.textContent = "";
    
    if (typingInterval) clearInterval(typingInterval);
    
    typingInterval = window.setInterval(() => {
      if (charIndex < text.length) {
        tipTextEl!.textContent += text.charAt(charIndex);
        charIndex++;
      } else {
        if (typingInterval) {
          clearInterval(typingInterval);
          typingInterval = null;
        }
        callback();
      }
    }, 35); // 35ms par lettre
  }

  function collapsePanel() {
    isCollapsed = true;
    tipPanelEl!.classList.add("collapsed");
    // Changer le texte en "?" après un léger délai pour coller à la transition CSS (200ms)
    setTimeout(() => {
      if (isCollapsed) {
        tipTextEl!.textContent = "?";
      }
    }, 200);
  }

  function expandPanel() {
    if (!isCollapsed) return; // Déjà déplié
    isCollapsed = false;
    tipPanelEl!.classList.remove("collapsed");

    // Choisir le conseil suivant
    currentTipIndex = (currentTipIndex + 1) % QUICK_TIPS.length;
    
    // Attendre la fin de l'expansion CSS (300ms) puis dactylographier
    setTimeout(() => {
      if (!isCollapsed) {
        typeText(QUICK_TIPS[currentTipIndex], () => {
          // Relancer le timer de disparition automatique (5s)
          resetCollapseTimer(5000);
        });
      }
    }, 300);
  }

  function resetCollapseTimer(delay: number) {
    if (collapseTimeout) clearTimeout(collapseTimeout);
    collapseTimeout = window.setTimeout(() => {
      collapsePanel();
    }, delay);
  }

  // Événements d'interaction
  tipPanelEl.addEventListener("mouseenter", () => {
    if (isCollapsed) {
      expandPanel();
    } else {
      // Si l'utilisateur survole alors qu'il est déjà étendu, on garde ouvert
      if (collapseTimeout) clearTimeout(collapseTimeout);
    }
  });

  tipPanelEl.addEventListener("mouseleave", () => {
    if (!isCollapsed) {
      // S'il quitte la zone, on replie après 5 secondes d'inactivité
      resetCollapseTimer(5000);
    }
  });

  tipPanelEl.addEventListener("click", () => {
    if (isCollapsed) {
      expandPanel();
    } else {
      // Si déjà ouvert, un clic force le passage directement à l'astuce suivante
      currentTipIndex = (currentTipIndex + 1) % QUICK_TIPS.length;
      typeText(QUICK_TIPS[currentTipIndex], () => {
        resetCollapseTimer(5000);
      });
    }
  });

  // Cycle initial : Dactylographie la première astuce, puis se replie au bout de 5 secondes
  typeText(QUICK_TIPS[currentTipIndex], () => {
    resetCollapseTimer(5000);
  });
}

// Initialiser le carrousel d'astuces
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

// Appliquer le drag à tous les widgets HUD au chargement (ils existent dans le DOM même si cachés)
["calendar-hud", "weather-hud", "music-hud", "dev-swarm-hud"].forEach(id => {
  const el = document.getElementById(id);
  if (el) makeDraggable(el);
});

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


// ── Drag & Drop utility for Antivirus Panel ─────────────────────────────────
function makePanelDraggable(panel: HTMLElement, header: HTMLElement) {
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

// ── Antivirus HUD Logic ──────────────────────────────────────────────────────
const avPanelEl       = document.getElementById("av-panel") as HTMLDivElement;
const avHeaderEl      = document.getElementById("av-panel-header") as HTMLDivElement;
const avCloseBtn      = document.getElementById("av-panel-close-btn") as HTMLButtonElement;
const avCancelBtn     = document.getElementById("av-cancel-btn") as HTMLButtonElement;
const avProgressFill  = document.getElementById("av-progress-bar-fill") as HTMLDivElement;
const avProgressPct   = document.getElementById("av-progress-percent") as HTMLDivElement;
const avStatusLabel   = document.getElementById("av-status-label") as HTMLSpanElement;
const avThreatsCount  = document.getElementById("av-threats-count") as HTMLSpanElement;
const avCurrentFile   = document.getElementById("av-current-file") as HTMLDivElement;
const avConsole       = document.getElementById("av-console") as HTMLDivElement;

let avScanInProgress = false;
let avThreatsList: any[] = [];
let avResolvedThreatsCount = 0;

// Setup Drag & Drop
if (avPanelEl && avHeaderEl) {
  makePanelDraggable(avPanelEl, avHeaderEl);
}

function openAntivirusPanel() {
  if (!avPanelEl) return;

  // Initial positioning
  const left = Math.max(20, (window.innerWidth - 460) / 2);
  const top = Math.max(20, (window.innerHeight - 420) / 2);
  avPanelEl.style.left = `${left}px`;
  avPanelEl.style.top = `${top}px`;
  avPanelEl.style.right = "auto";
  avPanelEl.style.bottom = "auto";
  avPanelEl.style.transform = "none";

  // Reset UI elements
  avPanelEl.classList.remove("threat-detected");
  avPanelEl.classList.remove("hidden");
  void avPanelEl.offsetWidth; // Reflow
  avPanelEl.classList.add("visible");

  if (avStatusLabel) avStatusLabel.textContent = "SYS_STATUS: INITIALISATION";
  if (avThreatsCount) avThreatsCount.textContent = "MENACES DÉTECTÉES: 0";
  if (avProgressFill) avProgressFill.style.width = "0%";
  if (avProgressPct) avProgressPct.textContent = "0%";
  if (avCurrentFile) avCurrentFile.textContent = "CONNEXION AU NOYAU DE SÉCURITÉ...";
  if (avConsole) avConsole.innerHTML = '<div class="av-console-line info">[INFO] Initialisation du système de sécurité JARVIS v2.6...</div>';
  
  // Clean active threats state
  avThreatsList = [];
  avResolvedThreatsCount = 0;
  const listContainer = document.getElementById("av-threats-list");
  if (listContainer) {
    listContainer.innerHTML = "";
    listContainer.classList.add("hidden");
  }
  
  // Show radar and progress controls
  const radarCont = avPanelEl.querySelector(".av-radar-container") as HTMLElement;
  const progressCont = avPanelEl.querySelector(".av-progress-bar-container") as HTMLElement;
  const currentFileCont = document.getElementById("av-current-file") as HTMLElement;
  if (radarCont) radarCont.style.display = "";
  if (progressCont) progressCont.style.display = "";
  if (currentFileCont) currentFileCont.style.display = "";

  if (avCancelBtn) {
    avCancelBtn.textContent = "ANNULER";
    avCancelBtn.disabled = false;
  }
  avScanInProgress = true;

  // Send start scan to backend
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "av_scan_start" }));
  }
}

function closeAntivirusPanel() {
  if (!avPanelEl) return;
  
  if (avScanInProgress) {
    cancelAvScan();
  }

  avPanelEl.classList.remove("visible");
  setTimeout(() => {
    avPanelEl.classList.add("hidden");
  }, 400);
}

function cancelAvScan() {
  avScanInProgress = false;
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "av_scan_cancel" }));
  }
  if (avCancelBtn) {
    avCancelBtn.textContent = "FERMER";
  }
}

if (avCloseBtn) {
  avCloseBtn.addEventListener("click", closeAntivirusPanel);
}

if (avCancelBtn) {
  avCancelBtn.addEventListener("click", () => {
    if (avScanInProgress) {
      cancelAvScan();
    } else {
      closeAntivirusPanel();
    }
  });
}

function handleAntivirusWSMessage(data: any) {
  if (!avConsole) return;

  if (data.type === "av_start") {
    const line = document.createElement("div");
    line.className = "av-console-line info";
    line.textContent = `[NOYAU] ${data.message || 'Moteur antivirus démarré.'}`;
    avConsole.appendChild(line);
    avConsole.scrollTop = avConsole.scrollHeight;
  }
  
  else if (data.type === "av_progress") {
    // Update progress bar
    if (data.percent !== undefined && avProgressFill && avProgressPct) {
      avProgressFill.style.width = `${data.percent}%`;
      avProgressPct.textContent = `${data.percent}%`;
    }
    
    if (data.step && avStatusLabel) {
      avStatusLabel.textContent = `SYS_STATUS: ${data.step.toUpperCase()}_SCAN`;
    }
    
    if (data.threats_found !== undefined && avThreatsCount) {
      avThreatsCount.textContent = `MENACES DÉTECTÉES: ${data.threats_found}`;
    }
    
    if (data.message) {
      if (avCurrentFile) avCurrentFile.textContent = data.message;
      
      const line = document.createElement("div");
      line.className = "av-console-line";
      
      if (data.step === "registry") {
        line.textContent = `[REGISTRE] ${data.message}`;
      } else if (data.step === "processes") {
        line.textContent = `[PROCESSUS] ${data.message}`;
      } else {
        line.textContent = `[FICHIER] ${data.message}`;
      }
      
      avConsole.appendChild(line);
      avConsole.scrollTop = avConsole.scrollHeight;
    }
  }
  
  else if (data.type === "av_threat_detected" && data.threat) {
    avThreatsList.push(data.threat);
    if (avPanelEl) avPanelEl.classList.add("threat-detected");
    
    const line = document.createElement("div");
    line.className = "av-console-line threat";
    line.textContent = `[DANGER] Menace détectée : ${data.threat.class} -> ${data.threat.name} (${data.threat.desc})`;
    avConsole.appendChild(line);
    avConsole.scrollTop = avConsole.scrollHeight;
  }
  
  else if (data.type === "av_complete") {
    avScanInProgress = false;
    if (avCancelBtn) avCancelBtn.textContent = "FERMER";
    if (avProgressFill && avProgressPct) {
      avProgressFill.style.width = "100%";
      avProgressPct.textContent = "100%";
    }
    
    const line = document.createElement("div");
    if (data.status === "infected") {
      if (avPanelEl) {
        avPanelEl.classList.add("threat-detected");
        avStatusLabel.textContent = "SYS_STATUS: VULNÉRABLE";
      }
      line.className = "av-console-line threat";
      line.textContent = `[TERMINE] Analyse terminée. Menaces détectées : ${data.threats ? data.threats.length : avThreatsList.length}. Système vulnérable.`;
      
      // Store threats list
      avThreatsList = data.threats || avThreatsList;
      avResolvedThreatsCount = 0;
      
      // Render the threat controls
      renderThreatsList();
    } else if (data.status === "error") {
      if (avStatusLabel) avStatusLabel.textContent = "SYS_STATUS: ERREUR";
      line.className = "av-console-line threat";
      line.textContent = `[ERREUR] ${data.message || 'Une erreur système est survenue pendant le scan.'}`;
    } else {
      if (avPanelEl) avPanelEl.classList.remove("threat-detected");
      if (avStatusLabel) avStatusLabel.textContent = "SYS_STATUS: SAIN";
      line.className = "av-console-line success";
      line.textContent = `[TERMINE] Analyse terminée. Aucune menace détectée. Système entièrement sécurisé.`;
    }
    avConsole.appendChild(line);
    avConsole.scrollTop = avConsole.scrollHeight;
  }
  
  else if (data.type === "av_cancel") {
    avScanInProgress = false;
    if (avCancelBtn) avCancelBtn.textContent = "FERMER";
    if (avStatusLabel) avStatusLabel.textContent = "SYS_STATUS: INTERROMPU";
    
    const line = document.createElement("div");
    line.className = "av-console-line info";
    line.textContent = `[INTERROMPU] ${data.message || "L'analyse antivirus a été annulée."}`;
    avConsole.appendChild(line);
    avConsole.scrollTop = avConsole.scrollHeight;
  }

  else if (data.type === "av_action_result") {
    const idx = avThreatsList.findIndex(t => t.target === data.threat_target);
    const line = document.createElement("div");
    if (data.success) {
      line.className = "av-console-line success";
      line.textContent = `[RÉSOLU] Action '${data.action.toUpperCase()}' : ${data.message}`;
      
      if (idx !== -1) {
        const itemEl = document.getElementById(`av-threat-${idx}`);
        if (itemEl && !itemEl.classList.contains("resolved")) {
          itemEl.classList.add("resolved");
          const buttons = itemEl.querySelectorAll(".av-action-btn") as NodeListOf<HTMLButtonElement>;
          buttons.forEach(btn => btn.disabled = true);
          
          const badge = document.createElement("div");
          badge.className = "av-threat-status-badge";
          let actStr = "RÉSOLU";
          if (data.action === "delete") actStr = "SUPPRIMÉ";
          else if (data.action === "clean") actStr = "NETTOYÉ";
          else if (data.action === "quarantine") actStr = "MIS EN QUARANTAINE";
          else if (data.action === "allow") actStr = "AUTORISÉ";
          badge.textContent = `◈ STATUT: ${actStr}`;
          itemEl.appendChild(badge);
          
          avResolvedThreatsCount++;
          if (avThreatsCount) avThreatsCount.textContent = `MENACES DÉTECTÉES: ${avThreatsList.length - avResolvedThreatsCount}`;
          
          if (avResolvedThreatsCount === avThreatsList.length) {
            if (avPanelEl) avPanelEl.classList.remove("threat-detected");
            if (avStatusLabel) avStatusLabel.textContent = "SYS_STATUS: SAIN";
            const sLine = document.createElement("div");
            sLine.className = "av-console-line success";
            sLine.textContent = "[SYSTEME] Résolution complète. Toutes les menaces ont été traitées.";
            avConsole.appendChild(sLine);
            
            // Verbal feedback
            if (ws && ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({
                type: "av_speak",
                text: "Toutes les menaces détectées ont été résolues, Mickael. Votre système est entièrement sécurisé."
              }));
            }
          }
        }
      }
    } else {
      line.className = "av-console-line threat";
      line.textContent = `[ÉCHEC] Action '${data.action.toUpperCase()}' sur la cible ${data.threat_target} : ${data.message}`;
      
      // Re-enable buttons
      if (idx !== -1) {
        const itemEl = document.getElementById(`av-threat-${idx}`);
        if (itemEl) {
          const buttons = itemEl.querySelectorAll(".av-action-btn") as NodeListOf<HTMLButtonElement>;
          buttons.forEach(btn => btn.disabled = false);
        }
      }
    }
    avConsole.appendChild(line);
    avConsole.scrollTop = avConsole.scrollHeight;
  }
}

function renderThreatsList() {
  const listContainer = document.getElementById("av-threats-list");
  if (!listContainer) return;
  
  listContainer.innerHTML = "";
  listContainer.classList.remove("hidden");
  
  // Hide scanning visuals
  const radarCont = avPanelEl?.querySelector(".av-radar-container") as HTMLElement;
  const progressCont = avPanelEl?.querySelector(".av-progress-bar-container") as HTMLElement;
  const currentFileCont = document.getElementById("av-current-file") as HTMLElement;
  if (radarCont) radarCont.style.display = "none";
  if (progressCont) progressCont.style.display = "none";
  if (currentFileCont) currentFileCont.style.display = "none";
  
  if (avThreatsList.length === 0) {
    listContainer.innerHTML = '<div style="text-align:center;font-size:10px;color:#22c55e;padding:10px;">AUCUNE MENACE ACTIVE</div>';
    return;
  }
  
  avThreatsList.forEach((threat, idx) => {
    const item = document.createElement("div");
    item.className = "av-threat-item";
    item.id = `av-threat-${idx}`;
    
    item.innerHTML = `
      <div class="av-threat-meta">
        <span class="av-threat-class">${threat.class}</span>
        <span class="av-threat-type">${threat.type.toUpperCase()}</span>
      </div>
      <div class="av-threat-details">
        <span class="av-threat-name">${threat.name}</span>
        <span class="av-threat-target">${threat.target}</span>
        <span class="av-threat-desc">${threat.desc || ''}</span>
      </div>
      <div class="av-threat-actions">
        <button class="av-action-btn delete" data-index="${idx}" data-action="delete">SUPPRIMER</button>
        <button class="av-action-btn clean" data-index="${idx}" data-action="clean">NETTOYER</button>
        <button class="av-action-btn quarantine" data-index="${idx}" data-action="quarantine">QUARANTAINE</button>
        <button class="av-action-btn allow" data-index="${idx}" data-action="allow">AUTORISER</button>
      </div>
    `;
    listContainer.appendChild(item);
  });
  
  // Attach event listeners to buttons
  listContainer.querySelectorAll(".av-action-btn").forEach(button => {
    button.addEventListener("click", (e) => {
      const targetBtn = e.target as HTMLButtonElement;
      const idxStr = targetBtn.getAttribute("data-index");
      const action = targetBtn.getAttribute("data-action");
      if (idxStr !== null && action !== null) {
        const idx = parseInt(idxStr);
        triggerAvThreatAction(action, idx);
      }
    });
  });
}

function triggerAvThreatAction(action: string, idx: number) {
  const threat = avThreatsList[idx];
  if (!threat) return;
  
  // Disable all buttons in this threat item
  const itemEl = document.getElementById(`av-threat-${idx}`);
  if (itemEl) {
    const buttons = itemEl.querySelectorAll(".av-action-btn") as NodeListOf<HTMLButtonElement>;
    buttons.forEach(btn => btn.disabled = true);
  }
  
  // Send action to backend
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: "av_threat_action",
      action: action,
      threat: threat
    }));
  }
}

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

// Plus d'info sur l'antivirus
const settingsAvInfoBtn = document.getElementById("settings-av-info-btn") as HTMLAnchorElement;
const avInfoModal = document.getElementById("av-info-modal") as HTMLDivElement;
const avInfoModalClose = document.getElementById("av-info-modal-close") as HTMLSpanElement;
const avInfoModalOk = document.getElementById("av-info-modal-ok") as HTMLButtonElement;

if (settingsAvInfoBtn && avInfoModal) {
  settingsAvInfoBtn.addEventListener("click", (e) => {
    e.preventDefault();
    avInfoModal.style.display = "flex";
  });
}

if (avInfoModalClose && avInfoModal) {
  avInfoModalClose.addEventListener("click", () => {
    avInfoModal.style.display = "none";
  });
}

if (avInfoModalOk && avInfoModal) {
  avInfoModalOk.addEventListener("click", () => {
    avInfoModal.style.display = "none";
  });
}


// ── LOGIQUE DU DÉSINSTALLATEUR (UNINSTALLER PANEL) ──────────────────────────
if (uninstallerPanel && uninstallerHeader) {
  makePanelDraggable(uninstallerPanel, uninstallerHeader);
}

uninstallerCloseBtn?.addEventListener("click", () => {
  closeUninstallerPanel();
});

uninstallerToggleBtn?.addEventListener("click", () => {
  const isHidden = uninstallerPanel.classList.contains("hidden");
  if (isHidden) {
    openUninstallerPanel();
  } else {
    closeUninstallerPanel();
  }
});

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

// ── LOGIQUE DU PANNEAU DE COURSES (SHOPPING PANEL) ───────────────────────────
if (shoppingPanel && shoppingHeader) {
  makePanelDraggable(shoppingPanel, shoppingHeader);
}

shoppingCloseBtn?.addEventListener("click", () => {
  shoppingPanel.classList.add("hidden");
  shoppingPanel.classList.remove("visible");
});

shoppingClearBtn?.addEventListener("click", () => {
  currentShoppingList = [];
  sendShoppingListToBackend();
});

function renderShoppingList() {
  if (!shoppingListContainer) return;
  shoppingListContainer.innerHTML = "";
  if (currentShoppingList.length === 0) {
    const empty = document.createElement("div");
    empty.style.cssText = "padding:20px;font-size:11px;color:rgba(0,229,255,0.3);text-align:center;";
    empty.textContent = "Aucun article dans la liste";
    shoppingListContainer.appendChild(empty);
    return;
  }
  currentShoppingList.forEach((itemText) => {
    const isChecked = itemText.startsWith("[x] ");
    const cleanText = isChecked ? itemText.substring(4) : itemText;

    const div = document.createElement("div");
    div.className = `shopping-item${isChecked ? " checked" : ""}`;

    const cb = document.createElement("div");
    cb.className = "shopping-checkbox";
    cb.onclick = () => {
      const idx = currentShoppingList.indexOf(itemText);
      if (idx !== -1) {
        if (isChecked) {
          currentShoppingList[idx] = cleanText;
        } else {
          currentShoppingList[idx] = `[x] ${cleanText}`;
        }
        sendShoppingListToBackend();
      }
    };

    const textSpan = document.createElement("span");
    textSpan.className = "shopping-item-text";
    textSpan.textContent = cleanText;

    const del = document.createElement("button");
    del.className = "shopping-item-delete";
    del.innerHTML = "&times;";
    del.onclick = () => {
      currentShoppingList = currentShoppingList.filter(i => i !== itemText);
      sendShoppingListToBackend();
    };

    div.appendChild(cb);
    div.appendChild(textSpan);
    div.appendChild(del);
    shoppingListContainer.appendChild(div);
  });
}

function sendShoppingListToBackend() {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: "update_shopping_list",
      items: currentShoppingList
    }));
  }
}

function addShoppingItem() {
  if (!shoppingAddInput) return;
  const val = shoppingAddInput.value.trim();
  if (val) {
    currentShoppingList.push(val);
    shoppingAddInput.value = "";
    sendShoppingListToBackend();
  }
}

shoppingAddBtn?.addEventListener("click", addShoppingItem);
shoppingAddInput?.addEventListener("keydown", (e) => {
  if (e.key === "Enter") addShoppingItem();
});

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


// ── Image Panels Logic (Iron Man style floating panels) ──────────────────────
let imgPanelCount = 0;
let maxZIndex = 600;

function showImagePanel(query: string, images: string[]) {
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

// ── Uninstaller core functions and listeners ──
function openUninstallerPanel() {
  if (uninstallerPanel) {
    uninstallerPanel.classList.remove("hidden");
    uninstallerPanel.classList.add("visible");
    uninstallerToggleBtn?.setAttribute("aria-pressed", "true");
    
    // Synchroniser avec le bouton du menu dropdown unifié
    const menuBtn = document.getElementById("menu-uninstaller-toggle-btn");
    if (menuBtn) {
      menuBtn.setAttribute("aria-pressed", "true");
      menuBtn.classList.add("active");
    }
    
    if (wingetPanel) closeWingetPanel();
    
    // Switch to list view initially
    uninstallerListView?.classList.remove("hidden");
    uninstallerActionView?.classList.add("hidden");
    
    // Set loading status
    if (uninstallerAppsList) {
      uninstallerAppsList.innerHTML = '<div class="uninstaller-loading">CHARGEMENT DE LA LISTE DES LOGICIELS...</div>';
    }
    
    // Request installed programs
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "get_installed_programs" }));
    }
  }
}

function closeUninstallerPanel() {
  if (uninstallerPanel) {
    uninstallerPanel.classList.add("hidden");
    uninstallerPanel.classList.remove("visible");
    uninstallerToggleBtn?.setAttribute("aria-pressed", "false");
    
    // Synchroniser avec le bouton du menu dropdown unifié
    const menuBtn = document.getElementById("menu-uninstaller-toggle-btn");
    if (menuBtn) {
      menuBtn.setAttribute("aria-pressed", "false");
      menuBtn.classList.remove("active");
    }
  }
}

function renderInstalledPrograms(programs: typeof allInstalledPrograms) {
  if (!uninstallerAppsList) return;
  uninstallerAppsList.innerHTML = "";
  
  if (programs.length === 0) {
    const empty = document.createElement("div");
    empty.className = "uninstaller-loading";
    empty.textContent = "AUCUN LOGICIEL TROUVÉ";
    uninstallerAppsList.appendChild(empty);
    return;
  }
  
  programs.forEach(prog => {
    const item = document.createElement("div");
    item.className = "uninstaller-app-item";
    
    item.innerHTML = `
      <div class="uninstaller-app-info">
        <div class="uninstaller-app-name">${prog.name}</div>
        <div class="uninstaller-app-publisher">${prog.publisher || 'Éditeur inconnu'} - v${prog.version || 'Inconnue'} (${prog.hive})</div>
      </div>
      <button class="uninstaller-app-btn">DÉSINSTALLER</button>
    `;
    
    const btn = item.querySelector(".uninstaller-app-btn") as HTMLButtonElement;
    btn.addEventListener("click", () => {
      triggerUninstall(prog);
    });
    
    uninstallerAppsList.appendChild(item);
  });
}

function triggerUninstall(prog: typeof allInstalledPrograms[0]) {
  uninstallerListView?.classList.add("hidden");
  uninstallerActionView?.classList.remove("hidden");
  
  uninstallerRadarContainer?.classList.remove("hidden");
  uninstallerLeftoversContainer?.classList.add("hidden");
  if (uninstallerStatusMsg) {
    uninstallerStatusMsg.textContent = `Lancement de la désinstallation de ${prog.name}...`;
  }
  
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: "uninstall_program",
      name: prog.name,
      publisher: prog.publisher,
      install_location: prog.install_location,
      uninstall_string: prog.uninstall_string
    }));
  }
}

function updateUninstallProgress(data: any) {
  if (uninstallerStatusMsg) {
    uninstallerStatusMsg.textContent = data.message || "En cours...";
  }
}

function showUninstallComplete(data: any) {
  uninstallerRadarContainer?.classList.add("hidden");
  uninstallerLeftoversContainer?.classList.remove("hidden");
  
  currentLeftovers = data.leftovers || [];
  
  // Reset Select All checkbox
  if (uninstallerSelectAll) {
    uninstallerSelectAll.checked = true;
  }
  
  renderLeftovers();
}

function renderLeftovers() {
  if (!uninstallerLeftoversList) return;
  uninstallerLeftoversList.innerHTML = "";
  
  if (currentLeftovers.length === 0) {
    const empty = document.createElement("div");
    empty.className = "uninstaller-leftover-empty";
    empty.textContent = "Aucune trace résiduelle détectée sur le système.";
    uninstallerLeftoversList.appendChild(empty);
    if (uninstallerCleanBtn) uninstallerCleanBtn.disabled = true;
    return;
  }
  
  if (uninstallerCleanBtn) uninstallerCleanBtn.disabled = false;
  
  currentLeftovers.forEach((leftover, idx) => {
    const item = document.createElement("div");
    item.className = "uninstaller-leftover-item";
    
    const icon = leftover.type === 'folder' ? '📁' : '🔑';
    const typeLabel = leftover.type === 'folder' ? 'Dossier' : 'Registre';
    
    item.innerHTML = `
      <label class="uninstaller-leftover-label">
        <input type="checkbox" class="uninstaller-leftover-checkbox" data-idx="${idx}" checked>
        <span class="uninstaller-leftover-icon">${icon}</span>
        <div class="uninstaller-leftover-details">
          <div class="uninstaller-leftover-path" title="${leftover.path}">${leftover.path}</div>
          <div class="uninstaller-leftover-desc">${typeLabel} - ${leftover.desc}</div>
        </div>
      </label>
    `;
    
    uninstallerLeftoversList.appendChild(item);
  });
}

function showCleanComplete(data: any) {
  const cleaned = data.cleaned_count || 0;
  const total = data.total_count || 0;
  alert(`Nettoyage terminé : ${cleaned}/${total} traces supprimées.`);
  
  // Go back to program list
  openUninstallerPanel();
}

// Event Listeners for Uninstaller Controls
uninstallerSearchInput?.addEventListener("input", () => {
  const query = uninstallerSearchInput.value.trim().toLowerCase();
  if (!query) {
    renderInstalledPrograms(allInstalledPrograms);
  } else {
    const filtered = allInstalledPrograms.filter(p => 
      p.name.toLowerCase().includes(query) || 
      (p.publisher && p.publisher.toLowerCase().includes(query))
    );
    renderInstalledPrograms(filtered);
  }
});

uninstallerSelectAll?.addEventListener("change", () => {
  const checked = uninstallerSelectAll.checked;
  const checkboxes = document.querySelectorAll(".uninstaller-leftover-checkbox") as NodeListOf<HTMLInputElement>;
  checkboxes.forEach(cb => {
    cb.checked = checked;
  });
});

uninstallerCleanBtn?.addEventListener("click", () => {
  const selectedItems: any[] = [];
  const checkboxes = document.querySelectorAll(".uninstaller-leftover-checkbox") as NodeListOf<HTMLInputElement>;
  checkboxes.forEach(cb => {
    if (cb.checked) {
      const idx = parseInt(cb.getAttribute("data-idx") || "0");
      selectedItems.push(currentLeftovers[idx]);
    }
  });
  
  if (selectedItems.length === 0) {
    alert("Veuillez sélectionner au moins une trace à nettoyer.");
    return;
  }
  
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: "clean_leftovers",
      items: selectedItems
    }));
  }
});

uninstallerSkipBtn?.addEventListener("click", () => {
  openUninstallerPanel();
});

// ── Winget Upgrade Panel Toggle and Draggable ──
if (wingetPanel && wingetHeader) {
  makePanelDraggable(wingetPanel, wingetHeader);
}

wingetCloseBtn?.addEventListener("click", () => {
  closeWingetPanel();
});

wingetToggleBtn?.addEventListener("click", () => {
  const isHidden = wingetPanel.classList.contains("hidden");
  if (isHidden) {
    openWingetPanel();
  } else {
    closeWingetPanel();
  }
});

// ── Winget Upgrade Panel Core Functions ──
function openWingetPanel() {
  if (wingetPanel) {
    wingetPanel.classList.remove("hidden");
    wingetPanel.classList.add("visible");
    wingetToggleBtn?.setAttribute("aria-pressed", "true");
    
    // Synchroniser avec le bouton du menu dropdown unifié
    const menuBtn = document.getElementById("winget-toggle-btn");
    if (menuBtn) {
      menuBtn.setAttribute("aria-pressed", "true");
      menuBtn.classList.add("active");
    }
    
    // Close other panels if needed
    if (uninstallerPanel) closeUninstallerPanel();
    
    wingetLogsContainer?.classList.add("hidden");
    
    if (wingetList) {
      wingetList.innerHTML = '<div class="uninstaller-loading" style="color: #00e5ff;">RECHERCHE DES MISES À JOUR...</div>';
    }
    
    // Request winget upgrades
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "get_winget_upgrades" }));
    }
  }
}

function closeWingetPanel() {
  if (wingetPanel) {
    wingetPanel.classList.add("hidden");
    wingetPanel.classList.remove("visible");
    wingetToggleBtn?.setAttribute("aria-pressed", "false");
    
    // Synchroniser avec le bouton du menu dropdown unifié
    const menuBtn = document.getElementById("winget-toggle-btn");
    if (menuBtn) {
      menuBtn.setAttribute("aria-pressed", "false");
      menuBtn.classList.remove("active");
    }
  }
}

function renderWingetUpgrades(upgrades: WingetUpgradeItem[]) {
  if (!wingetList) return;
  wingetList.innerHTML = "";
  
  if (upgrades.length === 0) {
    const empty = document.createElement("div");
    empty.className = "uninstaller-loading";
    empty.style.color = "#00e5ff";
    empty.textContent = "VOTRE SYSTÈME EST À JOUR";
    wingetList.appendChild(empty);
    
    if (wingetCountBadge) {
      wingetCountBadge.textContent = "0";
      wingetCountBadge.classList.add("hidden");
    }
    return;
  }
  
  if (wingetCountBadge) {
    wingetCountBadge.textContent = upgrades.length.toString();
    wingetCountBadge.classList.remove("hidden");
  }
  
  upgrades.forEach((item, idx) => {
    const el = document.createElement("div");
    el.className = "uninstaller-app-item";
    el.innerHTML = `
      <div class="uninstaller-app-info" style="display:flex; align-items:center; gap:10px; width:65%;">
        <input type="checkbox" class="winget-select-checkbox" data-idx="${idx}" checked style="accent-color: #00e5ff;">
        <div style="flex:1;">
          <div class="uninstaller-app-name" style="color:#00e5ff;">${item.name}</div>
          <div class="uninstaller-app-publisher" style="font-size:9px; opacity:0.7;">
            ID: ${item.id} | v${item.version} → <span style="color:#00ff88;">v${item.available}</span>
          </div>
        </div>
      </div>
      <button class="uninstaller-app-btn winget-upgrade-item-btn" data-id="${item.id}" style="border-color:#00e5ff; color:#00e5ff; background:rgba(0,229,255,0.05);">METTRE À JOUR</button>
    `;
    
    const btn = el.querySelector(".winget-upgrade-item-btn") as HTMLButtonElement;
    btn.addEventListener("click", () => {
      runWingetUpgrade([item.id]);
    });
    
    wingetList.appendChild(el);
  });
}

function runWingetUpgrade(ids: string[]) {
  if (ids.length === 0) return;
  if (wingetLogsContainer && wingetConsole) {
    wingetLogsContainer.classList.remove("hidden");
    wingetConsole.textContent = `[JARVIS] Lancement de la mise à jour pour:\n- ${ids.join("\n- ")}\n\n`;
    wingetConsole.scrollTop = wingetConsole.scrollHeight;
  }
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: "run_winget_upgrade",
      ids: ids
    }));
  }
}

// Event Listeners for Winget controls
wingetSearchInput?.addEventListener("input", () => {
  const query = wingetSearchInput.value.trim().toLowerCase();
  const items = document.querySelectorAll("#winget-upgrades-list .uninstaller-app-item");
  items.forEach(item => {
    const text = item.textContent?.toLowerCase() || "";
    if (text.includes(query)) {
      (item as HTMLElement).style.display = "";
    } else {
      (item as HTMLElement).style.display = "none";
    }
  });
});

wingetSelectAll?.addEventListener("change", () => {
  const checked = wingetSelectAll.checked;
  const checkboxes = document.querySelectorAll(".winget-select-checkbox") as NodeListOf<HTMLInputElement>;
  checkboxes.forEach(cb => {
    cb.checked = checked;
  });
});

wingetRefreshBtn?.addEventListener("click", () => {
  if (wingetList) {
    wingetList.innerHTML = '<div class="uninstaller-loading" style="color: #00e5ff;">RECHERCHE DES MISES À JOUR...</div>';
  }
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "get_winget_upgrades" }));
  }
});

wingetUpgradeSelectedBtn?.addEventListener("click", () => {
  const ids: string[] = [];
  const checkboxes = document.querySelectorAll(".winget-select-checkbox") as NodeListOf<HTMLInputElement>;
  checkboxes.forEach(cb => {
    if (cb.checked) {
      const idx = parseInt(cb.getAttribute("data-idx") || "0");
      ids.push(allWingetUpgrades[idx].id);
    }
  });
  if (ids.length === 0) {
    alert("Veuillez sélectionner au moins un logiciel à mettre à jour.");
    return;
  }
  runWingetUpgrade(ids);
});

wingetUpgradeAllBtn?.addEventListener("click", () => {
  if (allWingetUpgrades.length === 0) {
    alert("Aucune mise à jour disponible à installer.");
    return;
  }
  if (wingetLogsContainer && wingetConsole) {
    wingetLogsContainer.classList.remove("hidden");
    wingetConsole.textContent = "[JARVIS] Lancement de la mise à jour globale du système...\n\n";
    wingetConsole.scrollTop = wingetConsole.scrollHeight;
  }
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: "run_winget_upgrade",
      all: true
    }));
  }
});

wingetCloseLogsBtn?.addEventListener("click", () => {
  wingetLogsContainer?.classList.add("hidden");
  // Refresh the list after upgrade closes
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "get_winget_upgrades" }));
  }
});

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

// ── Dynamic Ambient Glow Management ──────────────────────────────────────────
function initDynamicAmbientGlow() {
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
function initMagneticButtons() {
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
