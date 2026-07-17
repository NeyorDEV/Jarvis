// ── Panneau antivirus JARVIS (scan, menaces, actions) — extrait de main.ts ──

import { wsRef } from "../ws_link";
import { makePanelDraggable } from "../ui/draggable";

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

export function openAntivirusPanel() {
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
  if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
    wsRef.current.send(JSON.stringify({ type: "av_scan_start" }));
  }
}

export function closeAntivirusPanel() {
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
  if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
    wsRef.current.send(JSON.stringify({ type: "av_scan_cancel" }));
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

export function handleAntivirusWSMessage(data: any) {
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
            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
              wsRef.current.send(JSON.stringify({
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
  if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
    wsRef.current.send(JSON.stringify({
      type: "av_threat_action",
      action: action,
      threat: threat
    }));
  }
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


