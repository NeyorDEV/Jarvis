/**
 * J.A.R.V.I.S — Widgets Logic (Calendar & Weather)
 */

export function initWidgets(ws: WebSocket | null) {
  // 1. Calendar is self-sufficient
  updateCalendar();
  setInterval(updateCalendar, 1000 * 60 * 60);

  // 2. Initial state for Music
  updateMusicUI({ status: 'Stopped', title: 'DEEZER_OFFLINE', artist: 'ATTENTE_BACKEND' });

  // 3. Weather-hud header (close button), data filled by backend via weather_update
  initWeatherHudHeader();

  // Start logic
  initWeather(ws);
  initMusic(ws);
}

// ── Widget show/hide helpers ─────────────────────────────────────────────────
export function showCalendarWidget() {
  const el = document.getElementById("calendar-hud");
  if (el) el.classList.add("hud-revealed");
}

export function hideCalendarWidget() {
  const el = document.getElementById("calendar-hud");
  if (el) el.classList.remove("hud-revealed");
}

export function showWeatherHudWidget() {
  const el = document.getElementById("weather-hud");
  if (el) el.classList.add("hud-revealed");
}

export function hideWeatherHudWidget() {
  const el = document.getElementById("weather-hud");
  if (el) el.classList.remove("hud-revealed");
}

export function showMusicWidget() {
  const el = document.getElementById("music-hud");
  if (el) el.classList.add("hud-revealed");
}

export function hideMusicWidget() {
  const el = document.getElementById("music-hud");
  if (el) el.classList.remove("hud-revealed");
}

// ── MUSIC ─────────────────────────────────────────────────────────────────────
export function updateMusicUI(data: any) {
  const container = document.getElementById("music-hud");
  if (!container || !data) return;

  const isPlaying = data.status === "Playing";
  
  container.innerHTML = `
    <div class="music-content">
      <div class="music-header">
        <div class="music-source">
          <div class="music-source-icon"></div>
          <span>DEEZER</span>
        </div>
        <button class="widget-close-btn" id="music-close-btn" title="Masquer">✕</button>
      </div>
      <div class="music-info">
        <div class="music-title">${data.title || 'DEEZER_IDLE'}</div>
        <div class="music-artist">${data.artist || 'EN_ATTENTE'}</div>
      </div>
      <div class="music-controls">
        <button class="music-btn" id="music-prev">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h2v12H6zm3.5 6L18 18V6z"/></svg>
        </button>
        <button class="music-btn play-pause" id="music-toggle">
          ${isPlaying 
            ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>`
            : `<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>`
          }
        </button>
        <button class="music-btn" id="music-next">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M6 18l8.5-6L6 6zm9-12v12h2V6z"/></svg>
        </button>
      </div>
    </div>
  `;

  // Re-attach listeners
  const btnPrev = document.getElementById("music-prev");
  const btnNext = document.getElementById("music-next");
  const btnToggle = document.getElementById("music-toggle");
  
  const sendCmd = (cmd: string) => {
    window.dispatchEvent(new CustomEvent('music-cmd', { detail: cmd }));
  };

  btnPrev?.addEventListener('click', () => sendCmd('prev'));
  btnNext?.addEventListener('click', () => sendCmd('next'));
  btnToggle?.addEventListener('click', () => sendCmd('toggle'));

  document.getElementById("music-close-btn")?.addEventListener('click', () => {
    hideMusicWidget();
  });
}

function initMusic(ws: WebSocket | null) {
  // Initial empty state
  updateMusicUI({ status: 'Paused', title: 'CHARGEMENT...', artist: 'DEEZER' });

  window.addEventListener('music-cmd', (e: any) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "music_control", action: e.detail }));
    }
  });
}

// ── CALENDAR ──────────────────────────────────────────────────────────────────
function updateCalendar() {
  const container = document.getElementById("calendar-hud");
  if (!container) return;

  const now = new Date();
  const month = now.toLocaleString('fr-FR', { month: 'long' });
  const year = now.getFullYear();

  let html = `<div class="cal-header"><span class="cal-header-title">${month} ${year}</span><button class="widget-close-btn" id="cal-close-btn" title="Masquer">✕</button></div>`;
  html += `<div class="cal-grid">`;

  // Days of week
  const days = ['L', 'M', 'M', 'J', 'V', 'S', 'D'];
  days.forEach(d => html += `<div class="cal-day-name">${d}</div>`);

  // Calculate days
  const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
  const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
  
  // Starting day (0=Sun, 1=Mon...) -> map to Mon-Sun
  let startDay = firstDay.getDay(); 
  if (startDay === 0) startDay = 7; // Sunday is 7
  startDay--; // Adjust to 0-indexed (Mon=0)

  // Empty slots for prev month
  for (let i = 0; i < startDay; i++) {
    html += `<div class="cal-day other-month"></div>`;
  }

  // Days of current month
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const isToday = d === now.getDate();
    html += `<div class="cal-day ${isToday ? 'today' : ''}">${d}</div>`;
  }

  html += `</div>`;
  container.innerHTML = html;

  document.getElementById("cal-close-btn")?.addEventListener('click', () => {
    hideCalendarWidget();
  });
}

// ── WEATHER ───────────────────────────────────────────────────────────────────
interface WeatherData {
  city: string;
  temp: number;
  desc: string;
  apparent: number;
  humidity: number;
  wind: number;
  max: number;
  min: number;
}

export function updateWeatherUI(data: WeatherData, type: 'local' | 'monistrol') {
  const container = document.getElementById("weather-hud");
  if (!container) return;

  let block = document.getElementById(`weather-${type}`);
  if (!block) {
    block = document.createElement("div");
    block.id = `weather-${type}`;
    block.className = "weather-block";
    container.appendChild(block);
  }

  block.innerHTML = `
    <div class="weather-city">${data.city}</div>
    <div class="weather-main">
      <div class="weather-desc">${data.desc}</div>
      <div class="weather-temp">${Math.round(data.temp)}°</div>
    </div>
    <div class="weather-details">
      <div class="weather-detail-item">
        <span class="weather-detail-label">Ressenti</span>
        <span class="weather-detail-val">${Math.round(data.apparent)}°</span>
      </div>
      <div class="weather-detail-item">
        <span class="weather-detail-label">Humidité</span>
        <span class="weather-detail-val">${data.humidity}%</span>
      </div>
      <div class="weather-detail-item">
        <span class="weather-detail-label">Vent</span>
        <span class="weather-detail-val">${data.wind} km/h</span>
      </div>
      <div class="weather-detail-item">
        <span class="weather-detail-label">Max / Min</span>
        <span class="weather-detail-val">${Math.round(data.max)}° / ${Math.round(data.min)}°</span>
      </div>
    </div>
  `;
}

function initWeatherHudHeader() {
  const container = document.getElementById("weather-hud");
  if (!container) return;

  // Insert a header row with close button if not already there
  if (!document.getElementById("weather-hud-header")) {
    const header = document.createElement("div");
    header.id = "weather-hud-header";
    header.className = "weather-hud-header";
    header.innerHTML = `<span>ATMOSPHERIC_DATA</span><button class="widget-close-btn" id="weather-hud-close-btn" title="Masquer">✕</button>`;
    container.insertBefore(header, container.firstChild);

    header.querySelector("#weather-hud-close-btn")?.addEventListener('click', () => {
      hideWeatherHudWidget();
    });
  }
}

function initWeather(ws: WebSocket | null) {
  // 1. Detection de localisation
  if ("geolocation" in navigator) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const coords = { lat: pos.coords.latitude, lon: pos.coords.longitude };
        console.log("[METEO] Localisation detectee :", coords);
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: "set_location", ...coords }));
        }
      },
      (err) => {
        console.warn("[METEO] Geolocation refusee ou erreur :", err.message);
        // Le backend utilisera l'IP par defaut
      }
    );
  }
}
