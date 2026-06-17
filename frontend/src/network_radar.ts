import * as THREE from 'three';
import { feature } from 'topojson-client';

interface RadarConnection {
  ip: string;
  port: number;
  process: string;
  country: string;
  cc: string;
  lat: number;
  lon: number;
  isp: string;
  risk: 'normal' | 'medium' | 'high';
}

interface ArcData {
  curve: THREE.QuadraticBezierCurve3;
  lineMesh: THREE.Line;
  headMesh: THREE.Mesh;
  headProgress: number;
  headSpeed: number;
}

const RISK_COLOR: Record<string, number> = {
  normal: 0x00e5ff,
  medium: 0xff8a1a,
  high:   0xff2e4d,
};

const FLAG: Record<string, string> = {
  FR:'🇫🇷', US:'🇺🇸', DE:'🇩🇪', GB:'🇬🇧', NL:'🇳🇱', JP:'🇯🇵',
  SG:'🇸🇬', IE:'🇮🇪', SE:'🇸🇪', CH:'🇨🇭', CA:'🇨🇦', AU:'🇦🇺',
  IN:'🇮🇳', BR:'🇧🇷', PL:'🇵🇱', FI:'🇫🇮', NO:'🇳🇴', DK:'🇩🇰',
  CN:'🇨🇳', RU:'🇷🇺', KP:'🇰🇵', IR:'🇮🇷', BY:'🇧🇾', SY:'🇸🇾',
  VN:'🇻🇳', PK:'🇵🇰', NG:'🇳🇬', UA:'🇺🇦', RO:'🇷🇴',
};

// Préchargement des frontières pays en arrière-plan dès l'import du module
let _countryBorderPoints: THREE.Vector3[][] | null = null;
let _bordersReady = false;

(async () => {
  try {
    const topo = await import('world-atlas/countries-110m.json');
    const geojson = feature(topo as any, (topo as any).objects.countries) as any;
    _countryBorderPoints = [];
    for (const f of geojson.features) {
      const geom = f.geometry;
      const polys: number[][][][] =
        geom.type === 'Polygon'      ? [geom.coordinates] :
        geom.type === 'MultiPolygon' ? geom.coordinates   : [];
      for (const poly of polys) {
        for (const ring of poly) {
          // Éviter les lignes qui "coupent" à travers le globe entre 179° et -179°
          const pts: THREE.Vector3[] = [];
          let prevLon: number | null = null;
          for (const [lon, lat] of ring as [number, number][]) {
            if (prevLon !== null && Math.abs(lon - prevLon) > 170) {
              if (pts.length > 1) _countryBorderPoints!.push([...pts]);
              pts.length = 0;
            }
            pts.push(_ll2v(lat, lon, 2.205));
            prevLon = lon;
          }
          if (pts.length > 1) _countryBorderPoints!.push(pts);
        }
      }
    }
    _bordersReady = true;
  } catch (e) {
    console.warn('[RADAR] Frontières pays non disponibles :', e);
  }
})();

function _ll2v(lat: number, lon: number, r: number): THREE.Vector3 {
  const phi   = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  return new THREE.Vector3(
    -r * Math.sin(phi) * Math.cos(theta),
     r * Math.cos(phi),
     r * Math.sin(phi) * Math.sin(theta)
  );
}

export class NetworkRadar {
  public active = false;
  private scene: THREE.Scene;
  private camera: THREE.Camera;
  private group: THREE.Group;

  private globeGroup: THREE.Group | null = null;
  private arcsGroup: THREE.Group | null = null;
  private dotsGroup: THREE.Group | null = null;

  private arcs: Map<string, ArcData> = new Map();
  private destDots: Map<string, THREE.Mesh> = new Map();

  private readonly R = 2.2;
  private readonly LOCAL_LAT = 46.0;
  private readonly LOCAL_LON = 2.0;

  private savedCameraPos = new THREE.Vector3();
  private globeRotY = 0;
  private time = 0;

  // Mouse drag pour rotation globe
  private _mouseRightDown = false;
  private _mouseLastX = 0;
  private _mouseLastY = 0;
  private _globeRotX = 0;
  private _onMouseDown: ((e: MouseEvent) => void) | null = null;
  private _onMouseMove: ((e: MouseEvent) => void) | null = null;
  private _onMouseUp: ((e: MouseEvent) => void) | null = null;
  private _onContextMenu: ((e: MouseEvent) => void) | null = null;

  constructor(scene: THREE.Scene, camera: THREE.Camera) {
    this.scene = scene;
    this.camera = camera;
    this.group = new THREE.Group();
    this.group.name = 'network_radar_group';
  }

  // ── Activation ──────────────────────────────────────────────────────────────

  public activate(): void {
    if (this.active) return;
    this.active = true;

    this.scene.traverse(child => {
      if (['domotic_group', 'cortex_group', 'explorer_group', 'chess_map_group']
          .includes(child.name)) child.visible = false;
    });

    this.savedCameraPos.copy(this.camera.position);
    this.scene.add(this.group);

    this.globeGroup = new THREE.Group();
    this.arcsGroup  = new THREE.Group();
    this.dotsGroup  = new THREE.Group();
    this.group.add(this.globeGroup, this.arcsGroup, this.dotsGroup);

    this.buildGlobe();

    this.camera.position.set(0, 1.5, 6.2);
    (this.camera as any).lookAt(new THREE.Vector3(0, 0, 0));

    const panel = document.getElementById('network-radar-panel');
    if (panel) panel.style.display = 'flex';

    this._setupMouseRotation();
  }

  public deactivate(): void {
    if (!this.active) return;
    this.active = false;

    this.scene.traverse(child => {
      if (['domotic_group', 'cortex_group'].includes(child.name)) child.visible = true;
    });

    this.clearAll();
    this.scene.remove(this.group);
    this.camera.position.copy(this.savedCameraPos);

    const panel = document.getElementById('network-radar-panel');
    if (panel) panel.style.display = 'none';

    this._teardownMouseRotation();
  }

  // ── Rotation souris ─────────────────────────────────────────────────────────

  private _setupMouseRotation(): void {
    const canvas = document.getElementById('holo-three-canvas');
    if (!canvas) return;

    this._onMouseDown = (e: MouseEvent) => {
      if (e.button === 2) {
        this._mouseRightDown = true;
        this._mouseLastX = e.clientX;
        this._mouseLastY = e.clientY;
      }
    };
    this._onMouseMove = (e: MouseEvent) => {
      if (!this._mouseRightDown) return;
      const dx = e.clientX - this._mouseLastX;
      const dy = e.clientY - this._mouseLastY;
      this._mouseLastX = e.clientX;
      this._mouseLastY = e.clientY;
      this.globeRotY  += dx * 0.006;
      this._globeRotX += dy * 0.006;
      this._globeRotX  = Math.max(-Math.PI / 2.2, Math.min(Math.PI / 2.2, this._globeRotX));
      [this.globeGroup, this.arcsGroup, this.dotsGroup].forEach(g => {
        if (g) { g.rotation.y = this.globeRotY; g.rotation.x = this._globeRotX; }
      });
    };
    this._onMouseUp = () => { this._mouseRightDown = false; };
    this._onContextMenu = (e: MouseEvent) => { e.preventDefault(); e.stopPropagation(); };

    canvas.addEventListener('mousedown',    this._onMouseDown);
    window.addEventListener('mousemove',    this._onMouseMove);
    window.addEventListener('mouseup',      this._onMouseUp);
    canvas.addEventListener('contextmenu',  this._onContextMenu);
  }

  private _teardownMouseRotation(): void {
    const canvas = document.getElementById('holo-three-canvas');
    if (this._onMouseDown) canvas?.removeEventListener('mousedown',   this._onMouseDown);
    if (this._onMouseMove) window.removeEventListener('mousemove',    this._onMouseMove);
    if (this._onMouseUp)   window.removeEventListener('mouseup',      this._onMouseUp);
    if (this._onContextMenu) canvas?.removeEventListener('contextmenu', this._onContextMenu);
    this._onMouseDown = this._onMouseMove = this._onMouseUp = this._onContextMenu = null;
  }

  // ── Globe ───────────────────────────────────────────────────────────────────

  private buildGlobe(): void {
    if (!this.globeGroup) return;
    const R = this.R;

    // Sphère de base
    this.globeGroup.add(new THREE.Mesh(
      new THREE.SphereGeometry(R, 64, 64),
      new THREE.MeshBasicMaterial({ color: 0x000d1a, transparent: true, opacity: 0.92 })
    ));

    // Frontières pays (si déjà chargées) — sinon on les ajoute en différé
    this.addCountryBorders();

    // Graticule léger (lignes de lat/lon) par-dessus les frontières
    const graticule = new THREE.LineBasicMaterial({ color: 0x00e5ff, transparent: true, opacity: 0.04 });
    for (let lat = -80; lat <= 80; lat += 20) {
      const pts: THREE.Vector3[] = [];
      for (let lon = 0; lon <= 362; lon += 2) pts.push(this.ll2v(lat, lon, R + 0.015));
      this.globeGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), graticule));
    }
    for (let lon = 0; lon < 360; lon += 20) {
      const pts: THREE.Vector3[] = [];
      for (let lat = -90; lat <= 90; lat += 2) pts.push(this.ll2v(lat, lon, R + 0.015));
      this.globeGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), graticule));
    }

    // Halo atmosphérique
    this.globeGroup.add(new THREE.Mesh(
      new THREE.SphereGeometry(R + 0.18, 32, 32),
      new THREE.MeshBasicMaterial({
        color: 0x0055ff, transparent: true, opacity: 0.055,
        side: THREE.BackSide, blending: THREE.AdditiveBlending
      })
    ));

    // Point local France
    this.addLocalDot();
  }

  private addCountryBorders(): void {
    if (!this.globeGroup) return;

    const doAdd = (borders: THREE.Vector3[][]) => {
      if (!this.globeGroup) return;
      const mat = new THREE.LineBasicMaterial({ color: 0x00e5ff, transparent: true, opacity: 0.22 });
      for (const pts of borders) {
        this.globeGroup.add(new THREE.Line(
          new THREE.BufferGeometry().setFromPoints(pts),
          mat
        ));
      }
    };

    if (_bordersReady && _countryBorderPoints) {
      doAdd(_countryBorderPoints);
    } else {
      // Différé : attendre que le chargement TopoJSON se termine
      const check = setInterval(() => {
        if (_bordersReady) {
          clearInterval(check);
          if (_countryBorderPoints && this.active) doAdd(_countryBorderPoints);
        }
      }, 200);
    }
  }

  private addLocalDot(): void {
    if (!this.dotsGroup) return;
    const pos = this.ll2v(this.LOCAL_LAT, this.LOCAL_LON, this.R + 0.04);

    const dot = new THREE.Mesh(
      new THREE.SphereGeometry(0.07, 12, 12),
      new THREE.MeshBasicMaterial({ color: 0x00ff88, blending: THREE.AdditiveBlending })
    );
    dot.position.copy(pos);
    dot.userData.isLocal = true;
    this.dotsGroup.add(dot);

    const ring = new THREE.Mesh(
      new THREE.RingGeometry(0.10, 0.16, 32),
      new THREE.MeshBasicMaterial({
        color: 0x00ff88, transparent: true, opacity: 0.65,
        side: THREE.DoubleSide, blending: THREE.AdditiveBlending
      })
    );
    ring.position.copy(pos);
    ring.lookAt(new THREE.Vector3(0, 0, 0));
    ring.userData.isLocal = true;
    this.dotsGroup.add(ring);
  }

  // ── Connexions ──────────────────────────────────────────────────────────────

  public handleRadarUpdate(connections: RadarConnection[]): void {
    if (!this.active) return;

    const newIps = new Set(connections.map(c => c.ip));

    for (const [ip, arc] of this.arcs) {
      if (!newIps.has(ip)) {
        this.arcsGroup?.remove(arc.lineMesh, arc.headMesh);
        arc.lineMesh.geometry.dispose();
        (arc.lineMesh.material as THREE.Material).dispose();
        arc.headMesh.geometry.dispose();
        (arc.headMesh.material as THREE.Material).dispose();
        this.arcs.delete(ip);

        const d = this.destDots.get(ip);
        if (d) {
          this.dotsGroup?.remove(d);
          d.geometry.dispose();
          (d.material as THREE.Material).dispose();
          this.destDots.delete(ip);
        }
      }
    }

    for (const conn of connections) {
      if (!this.arcs.has(conn.ip)) this.addArc(conn);
    }

    this.updatePanel(connections);
  }

  private addArc(conn: RadarConnection): void {
    const R = this.R;
    const color = RISK_COLOR[conn.risk] ?? RISK_COLOR.normal;

    const from = this.ll2v(this.LOCAL_LAT, this.LOCAL_LON, R + 0.04);
    const to   = this.ll2v(conn.lat, conn.lon, R + 0.04);
    const mid  = from.clone().add(to).multiplyScalar(0.5).normalize().multiplyScalar(R * 1.85);

    const curve = new THREE.QuadraticBezierCurve3(from, mid, to);

    const lineMesh = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints(curve.getPoints(80)),
      new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.22 })
    );
    this.arcsGroup?.add(lineMesh);

    const headMesh = new THREE.Mesh(
      new THREE.SphereGeometry(0.048, 8, 8),
      new THREE.MeshBasicMaterial({ color, blending: THREE.AdditiveBlending })
    );
    headMesh.position.copy(from);
    this.arcsGroup?.add(headMesh);

    const destDot = new THREE.Mesh(
      new THREE.SphereGeometry(0.05, 8, 8),
      new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending })
    );
    destDot.position.copy(to);
    this.dotsGroup?.add(destDot);
    this.destDots.set(conn.ip, destDot);

    this.arcs.set(conn.ip, {
      curve, lineMesh, headMesh,
      headProgress: Math.random(),
      headSpeed: 0.28 + Math.random() * 0.18,
    });
  }

  // ── Panel HUD ───────────────────────────────────────────────────────────────

  private updatePanel(connections: RadarConnection[]): void {
    const countries = new Set(connections.map(c => c.country));
    const threats   = connections.filter(c => c.risk !== 'normal');

    const el = (id: string) => document.getElementById(id);
    const count    = el('radar-count');
    const ctryEl   = el('radar-countries');
    const threatEl = el('radar-threats');
    const listEl   = el('radar-connections-list');

    if (count)    count.textContent    = String(connections.length);
    if (ctryEl)   ctryEl.textContent   = String(countries.size);
    if (threatEl) {
      const n = threats.length;
      threatEl.textContent = `${n} menace${n !== 1 ? 's' : ''}`;
      threatEl.style.color = n > 0 ? '#ff2e4d' : '#00ff88';
    }
    if (!listEl) return;
    listEl.innerHTML = '';

    const sorted = [...connections].sort((a, b) => {
      const o: Record<string, number> = { high: 0, medium: 1, normal: 2 };
      return (o[a.risk] ?? 2) - (o[b.risk] ?? 2);
    });

    for (const c of sorted) {
      const flag = FLAG[c.cc] ?? '🌐';
      const colorHex = '#' + (RISK_COLOR[c.risk] ?? RISK_COLOR.normal).toString(16).padStart(6, '0');
      const dot  = `<span style="color:${colorHex};font-size:9px">●</span>`;
      const row  = document.createElement('div');
      row.className = 'radar-conn-row';
      row.innerHTML = `${dot}<span>${flag} <span style="color:rgba(200,240,255,0.6);font-size:9px">${c.cc}</span></span><span class="radar-proc">${c.process.replace(/\.exe$/i, '')}</span><span class="radar-ip">${c.ip}</span><span class="radar-port">:${c.port}</span>`;
      listEl.appendChild(row);
    }
  }

  // ── Update loop ─────────────────────────────────────────────────────────────

  public update(dt: number): void {
    if (!this.active) return;
    this.time += dt;

    if (!this._mouseRightDown) this.globeRotY += dt * 0.04;
    [this.globeGroup, this.arcsGroup, this.dotsGroup].forEach(g => {
      if (g) { g.rotation.y = this.globeRotY; g.rotation.x = this._globeRotX; }
    });

    for (const arc of this.arcs.values()) {
      arc.headProgress += dt * arc.headSpeed;
      if (arc.headProgress > 1.0) arc.headProgress -= 1.0;
      arc.headMesh.position.copy(arc.curve.getPoint(arc.headProgress));
    }

    const pulse = 0.5 + Math.sin(this.time * 3.5) * 0.35;
    for (const dot of this.destDots.values()) {
      (dot.material as THREE.MeshBasicMaterial).opacity = pulse;
    }

    if (this.dotsGroup) {
      const localPulse = 0.75 + Math.sin(this.time * 2.5) * 0.25;
      this.dotsGroup.traverse(child => {
        if (child instanceof THREE.Mesh && child.userData.isLocal) {
          (child.material as THREE.MeshBasicMaterial).opacity = localPulse;
        }
      });
    }
  }

  // ── Utilitaires ─────────────────────────────────────────────────────────────

  private ll2v(lat: number, lon: number, r: number = this.R): THREE.Vector3 {
    return _ll2v(lat, lon, r);
  }

  private clearAll(): void {
    for (const arc of this.arcs.values()) {
      arc.lineMesh.geometry.dispose();
      (arc.lineMesh.material as THREE.Material).dispose();
      arc.headMesh.geometry.dispose();
      (arc.headMesh.material as THREE.Material).dispose();
    }
    this.arcs.clear();

    for (const dot of this.destDots.values()) {
      dot.geometry.dispose();
      (dot.material as THREE.Material).dispose();
    }
    this.destDots.clear();

    [this.globeGroup, this.arcsGroup, this.dotsGroup].forEach(g => {
      g?.traverse(child => {
        if (child instanceof THREE.Mesh || child instanceof THREE.Line) {
          child.geometry?.dispose();
          if (Array.isArray(child.material)) child.material.forEach(m => m.dispose());
          else child.material?.dispose();
        }
      });
      if (g) this.group.remove(g);
    });
    this.globeGroup = null;
    this.arcsGroup  = null;
    this.dotsGroup  = null;
  }
}
