/**
 * Voice Assistant — Classical Multi-mode particle visualization.
 * Saved as a fallback backup.
 */

import * as THREE from "three";

export type OrbState = "idle" | "listening" | "thinking" | "speaking";

export interface Orb {
  setState(s: OrbState): void;
  setVolume(v: number): void;
  setAnalyser(a: AnalyserNode | null): void;
  triggerDemo(): void;
  setQuality(q: "low" | "high"): void;
  setTheme(t: string): void;
  destroy(): void;
}

export function createOrb(canvas: HTMLCanvasElement): Orb {
  let destroyed = false;
  const N = 2000;

  const mouse = new THREE.Vector2(-9999, -9999);
  const raycaster = new THREE.Raycaster();

  function onPointerMove(e: PointerEvent) {
    mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
  }
  function onPointerLeave() {
    mouse.x = -9999;
    mouse.y = -9999;
  }
  window.addEventListener("pointermove", onPointerMove);
  window.addEventListener("pointerleave", onPointerLeave);

  const w = window.innerWidth;
  const h = window.innerHeight;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(w, h);
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(
    45,
    w / h,
    1,
    1000
  );
  camera.position.z = 75;

  // ── Particles ──────────────────────────────────────────────────────────────
  const N_PINK = Math.floor(N * 0.03); // 60 particles
  const N_CYAN = N - N_PINK; // 1940 particles

  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(N * 3);
  const vel = new Float32Array(N * 3);
  const phase = new Float32Array(N);

  for (let i = 0; i < N; i++) {
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    const r = Math.pow(Math.random(), 0.5) * 25;
    pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
    pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    pos[i * 3 + 2] = r * Math.cos(phi);
    phase[i] = Math.random() * 1000;
  }

  // Split positions using TypedArray views sharing the same underlying ArrayBuffer
  const cyanPosView = new Float32Array(pos.buffer, N_PINK * 3 * 4, N_CYAN * 3);
  const pinkPosView = new Float32Array(pos.buffer, 0, N_PINK * 3);

  geo.setAttribute("position", new THREE.BufferAttribute(cyanPosView, 3));

  const pinkGeo = new THREE.BufferGeometry();
  pinkGeo.setAttribute("position", new THREE.BufferAttribute(pinkPosView, 3));

  const mat = new THREE.PointsMaterial({
    color: 0x4ca8e8,
    size: 0.4,
    transparent: true,
    opacity: 0.6,
    sizeAttenuation: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });

  const pinkMat = new THREE.PointsMaterial({
    color: 0xff007f, // flashy neon pink
    size: 0.45, // slightly larger for visibility
    transparent: true,
    opacity: 0.85,
    sizeAttenuation: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });

  const points = new THREE.Points(geo, mat);
  scene.add(points);

  const pinkPoints = new THREE.Points(pinkGeo, pinkMat);
  scene.add(pinkPoints);

  // ── Connection lines ────────────────────────────────────────────────────────
  const MAX_LINES = 8000;
  const linePos = new Float32Array(MAX_LINES * 6);
  const lineGeo = new THREE.BufferGeometry();
  lineGeo.setAttribute("position", new THREE.BufferAttribute(linePos, 3));
  lineGeo.setDrawRange(0, 0);

  const lineMat = new THREE.LineBasicMaterial({
    color: 0x4ca8e8,
    transparent: true,
    opacity: 0.0,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });

  const lines = new THREE.LineSegments(lineGeo, lineMat);
  scene.add(lines);

  // ── Electrons ──────────────────────────────────────────────────────────────
  const MAX_ELECTRONS = 200;
  const electronGeo = new THREE.BufferGeometry();
  const electronPos = new Float32Array(MAX_ELECTRONS * 3);
  electronGeo.setAttribute(
    "position",
    new THREE.BufferAttribute(electronPos, 3)
  );
  electronGeo.setDrawRange(0, 0);

  const electronMat = new THREE.PointsMaterial({
    color: 0xffffff,
    size: 0.8,
    transparent: true,
    opacity: 1.0,
    sizeAttenuation: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });

  const electronPoints = new THREE.Points(electronGeo, electronMat);
  scene.add(electronPoints);

  interface Electron {
    sx: number; sy: number; sz: number;
    ex: number; ey: number; ez: number;
    t: number;
    speed: number;
  }
  const activeElectrons: Electron[] = [];
  let electronSpawnRate = 0;
  let targetElectronRate = 0;
  let lastElectronSpawn = 0;

  let activeConnections: {
    x1: number; y1: number; z1: number;
    x2: number; y2: number; z2: number;
  }[] = [];

  // ── Base state vars ────────────────────────────────────────────────────────
  let state: OrbState = "idle";
  let targetRadius = 25, currentRadius = 25;
  let targetSpeed = 0.3, currentSpeed = 0.3;
  let targetBright = 0.6, currentBright = 0.6;
  let targetSize = 0.4, currentSize = 0.4;
  let lineAmount = 0, targetLineAmount = 0;
  const lineDistance = 8;

  let spinX = 0, spinY = 0, spinZ = 0;
  let transitionEnergy = 0;
  let lastState: OrbState = "idle";
  let cloudZ = 0, cloudZVel = 0;

  // ── Speaking-specific vars ─────────────────────────────────────────────────
  let vortexStrength = 0, targetVortex = 0;
  let breathAmp = 0, targetBreathAmp = 0;
  let shockwave = 0;
  let prevBass = 0;
  let burstCooldown = 1.5;

  // Delta time tracking
  let prevT = 0;

  // ── Audio ──────────────────────────────────────────────────────────────────
  let analyser: AnalyserNode | null = null;
  let externalVolume = 0;
  let freqData = new Uint8Array(64);
  let bass = 0, mid = 0, treble = 0;

  const clock = new THREE.Clock();

  // ── Colour helpers ─────────────────────────────────────────────────────────
  const THEME_COLORS: Record<string, {
    primary: number;
    secondary: number;
    think: number;
    speak: number;
    bright: number;
  }> = {
    cyan: {
      primary: 0x4ca8e8,
      secondary: 0xff007f, // flashy neon pink
      think: 0x6ec4ff,
      speak: 0x5ab8f0,
      bright: 0xb8eeff,
    },
    emerald: {
      primary: 0x00e575, // emerald green
      secondary: 0xff5500, // flashy hot orange
      think: 0x55ffb0,
      speak: 0x22f28b,
      bright: 0xbeffd8,
    },
    amber: {
      primary: 0xffaa00, // amber orange
      secondary: 0x7f00ff, // flashy purple/indigo
      think: 0xffcc44,
      speak: 0xffb833,
      bright: 0xffeed5,
    },
    red: {
      primary: 0xff2a2a, // tactical red
      secondary: 0x00e5ff, // flashy neon cyan
      think: 0xff6666,
      speak: 0xff4444,
      bright: 0xffcccc,
    },
    gold: {
      primary: 0xffd700, // gold yellow
      secondary: 0xd000ff, // flashy fuchsia/purple
      think: 0xffe875,
      speak: 0xffde33,
      bright: 0xfff9be,
    }
  };

  let currentSecondaryHex = 0xff007f;
  let currentThemeName = "cyan";

  const COL_BASE = new THREE.Color(0x4ca8e8);
  const COL_THINK = new THREE.Color(0x6ec4ff);
  const COL_SPEAK = new THREE.Color(0x5ab8f0);
  const COL_BRIGHT = new THREE.Color(0xb8eeff);
  const COL_FLASH = new THREE.Color(0xffffff);
  const _tmpColor = new THREE.Color();
  const _rainbowCol = new THREE.Color();

  // ── Demo state ─────────────────────────────────────────────────────────────
  let demoActive = false;
  let demoStartTime = 0;
  let demoBurstNextAt = 0;
  const DEMO_DURATION = 10.0;

  // ── Animate ────────────────────────────────────────────────────────────────
  function animate() {
    if (destroyed) return;
    requestAnimationFrame(animate);

    const t = clock.getElapsedTime();
    const dt = Math.min(t - prevT, 0.05);
    prevT = t;

    if (demoActive && t - demoStartTime >= DEMO_DURATION) {
      demoActive = false;
    }

    const demoElapsed = demoActive ? (t - demoStartTime) : -1;
    const demoBigBang = demoActive && demoElapsed < 2.0;
    const demoVortex = demoActive && demoElapsed >= 2.0 && demoElapsed < 5.0;
    const demoPulse = demoActive && demoElapsed >= 5.0 && demoElapsed < 7.5;
    const demoCollapse = demoActive && demoElapsed >= 7.5;

    // ── Per-state targets ───────────────────────────────────────────────────
    if (demoActive) {
      if (demoBigBang) {
        targetRadius = 25; targetSpeed = 1.0; targetBright = 1.0; targetSize = 0.75;
        targetLineAmount = 1.0; targetElectronRate = 0.04;
        targetVortex = 0.5; targetBreathAmp = 1.2;
      } else if (demoVortex) {
        targetRadius = 24; targetSpeed = 0.9; targetBright = 1.0; targetSize = 0.65;
        targetLineAmount = 1.0; targetElectronRate = 0.04;
        targetVortex = 4.5; targetBreathAmp = 1.0;
      } else if (demoPulse) {
        targetRadius = 22; targetSpeed = 0.7; targetBright = 0.95; targetSize = 0.55;
        targetLineAmount = 0.9; targetElectronRate = 0.03;
        targetVortex = 2.0; targetBreathAmp = 1.2;
      } else {
        targetRadius = 8; targetSpeed = 0.5; targetBright = 0.85; targetSize = 0.5;
        targetLineAmount = 0.7; targetElectronRate = 0.015;
        targetVortex = 1.0; targetBreathAmp = 0.5;
      }
    } else {
      switch (state) {
        case "idle":
          targetRadius = 15; targetSpeed = 0.2; targetBright = 0.55; targetSize = 0.35;
          targetLineAmount = 0.15; targetElectronRate = 0;
          targetVortex = 0; targetBreathAmp = 0;
          break;

        case "listening":
          targetRadius = 13; targetSpeed = 0.3; targetBright = 0.7; targetSize = 0.42;
          targetLineAmount = 0.4; targetElectronRate = 0;
          targetVortex = 0; targetBreathAmp = 0;
          break;

        case "thinking":
          targetRadius = 9; targetSpeed = 0.5; targetBright = 0.8; targetSize = 0.32;
          targetLineAmount = 1.0; targetElectronRate = 0.015;
          targetVortex = 0; targetBreathAmp = 0;
          break;

        case "speaking":
          targetRadius = 12; targetSpeed = 0.45; targetBright = 0.85; targetSize = 0.48;
          targetLineAmount = 0.8; targetElectronRate = 0.02;
          targetVortex = 0.3; targetBreathAmp = 1.2;
          break;
      }
    }

    const L = demoActive ? 0.06 : 0.035;
    currentRadius += (targetRadius - currentRadius) * L;
    currentSpeed += (targetSpeed - currentSpeed) * L;
    currentBright += (targetBright - currentBright) * L;
    currentSize += (targetSize - currentSize) * L;
    lineAmount += (targetLineAmount - lineAmount) * L;
    electronSpawnRate += (targetElectronRate - electronSpawnRate) * L;
    vortexStrength += (targetVortex - vortexStrength) * (demoActive ? 0.08 : 0.025);
    breathAmp += (targetBreathAmp - breathAmp) * (demoActive ? 0.08 : 0.025);

    if (state !== lastState) { transitionEnergy = 1.0; lastState = state; }
    transitionEnergy *= 0.985;
    if (transitionEnergy > 0.05) {
      spinX += transitionEnergy * 0.012 * Math.sin(t * 1.7);
      spinY += transitionEnergy * 0.015;
      spinZ += transitionEnergy * 0.008 * Math.cos(t * 1.3);
    }
    if (demoActive) {
      spinY += 0.008 * (demoVortex ? 3.0 : 1.0);
      spinX += Math.sin(t * 0.7) * 0.003;
    }

    bass = 0; mid = 0; treble = 0;
    if (analyser) {
      analyser.getByteFrequencyData(freqData);
      let bS = 0, mS = 0, tS = 0;
      for (let i = 0; i < 8;  i++) bS += freqData[i];
      for (let i = 8; i < 24; i++) mS += freqData[i];
      for (let i = 24;i < 48; i++) tS += freqData[i];
      bass   = bS / (8  * 255);
      mid    = mS / (16 * 255);
      treble = tS / (24 * 255);
    } else {
      bass = externalVolume * 0.8;
      mid = externalVolume * 0.4;
      treble = externalVolume * 0.2;
    }

    const bassJump = Math.max(0, bass - prevBass - 0.04) * 5.0;
    shockwave = Math.max(shockwave * 0.82, bassJump);
    prevBass = bass;

    if (demoActive) {
      if (t >= demoBurstNextAt) {
        const intensity = demoBigBang ? 0.45 : demoVortex ? 0.35 : demoPulse ? 0.4 : 0.25;
        shockwave = Math.max(shockwave, intensity);
        if (demoBigBang && demoElapsed < 0.05) {
          shockwave = 1.0;
        }
        const interval = demoBigBang ? 0.5 : demoVortex ? 0.7 : demoPulse ? 0.9 : 1.5;
        demoBurstNextAt = t + interval + Math.random() * 0.3;
      }
    } else {
      if (state === "speaking") {
        burstCooldown -= dt;
        if (burstCooldown <= 0) {
          shockwave = Math.max(shockwave, 0.28);
          burstCooldown = 1.3 + Math.random() * 0.5;
        }
      } else {
        burstCooldown = 1.5;
      }
    }

    let zTarget = Math.sin(t * 0.12) * 8;
    if (state === "thinking") zTarget = Math.sin(t * 0.3) * 15 + Math.sin(t * 0.9) * 6;
    else if (state === "speaking") zTarget = Math.sin(t * 0.18) * 7 - bass * 8;
    else if (demoActive) zTarget = Math.sin(t * 0.4) * 12;
    cloudZVel += (zTarget - cloudZ) * 0.008;
    cloudZVel *= 0.94;
    cloudZ += cloudZVel;

    points.rotation.x = spinX; points.rotation.y = spinY; points.rotation.z = spinZ;
    points.position.z = cloudZ;
    pinkPoints.rotation.x = spinX; pinkPoints.rotation.y = spinY; pinkPoints.rotation.z = spinZ;
    pinkPoints.position.z = cloudZ;
    lines.rotation.x = spinX; lines.rotation.y = spinY; lines.rotation.z = spinZ;
    lines.position.z = cloudZ;

    const p = geo.getAttribute("position") as THREE.BufferAttribute;
    const pinkP = pinkGeo.getAttribute("position") as THREE.BufferAttribute;
    const a = pos; // Use full parent-scoped Float32Array containing all N particles
    const speaking = state === "speaking" && !demoActive;

    let localRayDir: THREE.Vector3 | null = null;
    let localRayOrig: THREE.Vector3 | null = null;
    if (mouse.x > -9000) {
      raycaster.setFromCamera(mouse, camera);
      const tempRay = raycaster.ray.clone();
      points.updateMatrixWorld();
      const invMat = points.matrixWorld.clone().invert();
      tempRay.applyMatrix4(invMat);
      localRayDir = tempRay.direction;
      localRayOrig = tempRay.origin;
    }

    for (let i = 0; i < N; i++) {
      const i3 = i * 3;
      const x = a[i3], y = a[i3 + 1], z = a[i3 + 2];
      const px = phase[i];

      // ── Cursor repulsion (Piste 2) ──
      if (localRayDir && localRayOrig) {
        const ox = x - localRayOrig.x;
        const oy = y - localRayOrig.y;
        const oz = z - localRayOrig.z;
        const projT = ox * localRayDir.x + oy * localRayDir.y + oz * localRayDir.z;
        const cx = localRayOrig.x + projT * localRayDir.x;
        const cy = localRayOrig.y + projT * localRayDir.y;
        const cz = localRayOrig.z + projT * localRayDir.z;
        const rx = x - cx;
        const ry = y - cy;
        const rz = z - cz;
        const rDistSq = rx * rx + ry * ry + rz * rz;
        const repRange = 4.0;
        if (rDistSq < repRange * repRange) {
          const rDist = Math.sqrt(rDistSq) || 0.01;
          const push = (1.0 - rDist / repRange) * 0.06 * (demoActive ? 2.5 : 1.0);
          vel[i3] += (rx / rDist) * push;
          vel[i3 + 1] += (ry / rDist) * push;
          vel[i3 + 2] += (rz / rDist) * push;
        }
      }

      vel[i3] += Math.sin(t * 0.05 + px) * 0.001 * currentSpeed;
      vel[i3 + 1] += Math.cos(t * 0.06 + px * 1.3) * 0.001 * currentSpeed;
      vel[i3 + 2] += Math.sin(t * 0.055 + px * 0.7) * 0.001 * currentSpeed;
      vel[i3] += Math.sin(t * 0.02 + px * 2.1 + y * 0.1) * 0.0008 * currentSpeed;
      vel[i3 + 1] += Math.cos(t * 0.025 + px * 1.7 + z * 0.1) * 0.0008 * currentSpeed;
      vel[i3 + 2] += Math.sin(t * 0.022 + px * 0.9 + x * 0.1) * 0.0008 * currentSpeed;

      const dist = Math.sqrt(x * x + y * y + z * z) || 0.01;

      const radiusTarget = (speaking || demoActive)
        ? currentRadius * (1.0 + Math.sin(t * 3.5 + px * 0.2) * 0.15 * breathAmp)
        : currentRadius;

      const pullBase = demoCollapse
        ? Math.max(0, dist - radiusTarget) * 0.015 + 0.002
        : Math.max(0, dist - radiusTarget) * 0.002 + 0.0003;
      vel[i3] -= (x / dist) * pullBase;
      vel[i3 + 1] -= (y / dist) * pullBase;
      vel[i3 + 2] -= (z / dist) * pullBase;

      if (bass > 0.05) {
        const bf = (speaking || demoActive) ? bass * 0.025 : bass * 0.015;
        vel[i3] += (x / dist) * bf;
        vel[i3 + 1] += (y / dist) * bf;
        vel[i3 + 2] += (z / dist) * bf;
      }

      if (mid > 0.1) {
        const pulse = Math.sin(t * 8 + px);
        const mf = (speaking || demoActive) ? mid * 0.018 : mid * 0.01;
        vel[i3] += (x / dist) * mf * pulse;
        vel[i3 + 1] += (y / dist) * mf * pulse;
      }

      if (speaking) {
        if (vortexStrength > 0.01) {
          const wave = Math.sin(dist * 0.8 - t * 12.0) * vortexStrength * 0.0035;
          vel[i3] += (x / dist) * wave;
          vel[i3 + 1] += (y / dist) * wave;
          vel[i3 + 2] += (z / dist) * wave;
        }

        if (shockwave > 0.005) {
          vel[i3] += (x / dist) * shockwave * 0.08;
          vel[i3 + 1] += (y / dist) * shockwave * 0.04;
          vel[i3 + 2] += (z / dist) * shockwave * 0.08;
        }

        if (breathAmp > 0.005) {
          const bp = Math.sin(t * 7.5 + px * 0.4) * breathAmp * 0.0015;
          vel[i3] += (x / dist) * bp;
          vel[i3 + 1] += (y / dist) * bp;
          vel[i3 + 2] += (z / dist) * bp;
        }

        if (treble > 0.08) {
          const jitter = (Math.random() - 0.5) * treble * 0.03;
          vel[i3] += jitter;
          vel[i3 + 1] += jitter * 0.5;
          vel[i3 + 2] += jitter;
        }
      }

      if (demoActive) {
        if (vortexStrength > 0.01) {
          const xzLen = Math.sqrt(x * x + z * z) || 0.01;
          vel[i3] += (-z / xzLen) * vortexStrength * 0.004;
          vel[i3 + 2] += (x / xzLen) * vortexStrength * 0.004;
          if (demoVortex) {
            const xyLen = Math.sqrt(x * x + y * y) || 0.01;
            vel[i3] += (-y / xyLen) * vortexStrength * 0.0015;
            vel[i3 + 1] += (x / xyLen) * vortexStrength * 0.0015;
          }
          vel[i3 + 1] += Math.sin(px * 2.3 + t) * vortexStrength * 0.001;
        }

        if (shockwave > 0.005) {
          vel[i3] += (x / dist) * shockwave * 0.18;
          vel[i3 + 1] += (y / dist) * shockwave * 0.18;
          vel[i3 + 2] += (z / dist) * shockwave * 0.18;
        }

        if (breathAmp > 0.005) {
          const bp = Math.sin(t * 9.0 + px * 0.5) * breathAmp * 0.0035;
          vel[i3] += (x / dist) * bp;
          vel[i3 + 1] += (y / dist) * bp;
          vel[i3 + 2] += (z / dist) * bp;
        }

        if (demoPulse) {
          const ringFreq = 5.0;
          const ring = Math.sin(dist * ringFreq - t * 12.0 + px) * 0.003;
          vel[i3] += (x / dist) * ring;
          vel[i3 + 1] += (y / dist) * ring;
          vel[i3 + 2] += (z / dist) * ring;
        }

        if (demoBigBang) {
          const chaos = (Math.random() - 0.5) * 0.04;
          vel[i3] += chaos;
          vel[i3 + 1] += chaos * 0.7;
          vel[i3 + 2] += chaos;
        }
      }

      const damp = demoActive ? 0.988 : 0.992;
      vel[i3] *= damp;
      vel[i3 + 1] *= damp;
      vel[i3 + 2] *= damp;
      a[i3] += vel[i3];
      a[i3 + 1] += vel[i3 + 1];
      a[i3 + 2] += vel[i3 + 2];
    }
    p.needsUpdate = true;
    pinkP.needsUpdate = true;

    if (lineAmount > 0.01) {
      const lp = lineGeo.getAttribute("position") as THREE.BufferAttribute;
      const la = lp.array as Float32Array;
      let lineCount = 0;

      // Idle (0.15) => clamped to 250 lines, Listening (0.4) => ~1280 lines, Speaking (0.8) => ~5120 lines, Thinking (1.0) => 8000 lines.
      const dynamicMaxLines = Math.max(250, Math.floor(MAX_LINES * lineAmount * lineAmount));

      // Piste 3: Ephemeral synaptic connections peaking with volume
      const maxDist = (lineDistance - 1) * (1 + bass * ((speaking || demoActive) ? 1.15 : 0.4));
      const maxDistSq = maxDist * maxDist;
      const step = Math.max(1, Math.floor(N / 600));

      for (let i = 0; i < N && lineCount < dynamicMaxLines; i += step) {
        const i3 = i * 3;
        const x1 = a[i3], y1 = a[i3 + 1], z1 = a[i3 + 2];
        for (let j = i + step; j < N && lineCount < dynamicMaxLines; j += step) {
          const j3 = j * 3;
          const dx = a[j3] - x1, dy = a[j3 + 1] - y1, dz = a[j3 + 2] - z1;
          if (dx * dx + dy * dy + dz * dz < maxDistSq) {
            const idx = lineCount * 6;
            la[idx] = x1; la[idx + 1] = y1; la[idx + 2] = z1;
            la[idx + 3] = a[j3]; la[idx + 4] = a[j3 + 1]; la[idx + 5] = a[j3 + 2];
            lineCount++;
          }
        }
      }
      lineGeo.setDrawRange(0, lineCount * 2);
      lp.needsUpdate = true;
      const peakBass = Math.max(0, bass - 0.1) * 2.2;
      lineMat.opacity = Math.max(0.06, lineAmount * 0.22) + peakBass * 0.35 + shockwave * 0.20;

      activeConnections = [];
      for (let c = 0; c < Math.min(lineCount, 500); c++) {
        const ci = c * 6;
        activeConnections.push({
          x1: la[ci], y1: la[ci + 1], z1: la[ci + 2],
          x2: la[ci + 3], y2: la[ci + 4], z2: la[ci + 5],
        });
      }
    } else {
      lineGeo.setDrawRange(0, 0);
      activeConnections = [];
    }

    const maxElec = demoActive ? 25 : speaking ? 10 : 3;
    const spawnGap = demoActive ? 0.06 : speaking ? 0.18 : 1.0;
    const eSpeed = demoActive
      ? 0.014 + Math.random() * 0.012
      : speaking
        ? 0.009 + Math.random() * 0.009
        : 0.003 + Math.random() * 0.003;

    if (activeConnections.length > 0 && electronSpawnRate > 0.005) {
      if (activeElectrons.length < maxElec && (t - lastElectronSpawn) > spawnGap) {
        const conn = activeConnections[Math.floor(Math.random() * activeConnections.length)];
        activeElectrons.push({
          sx: conn.x1, sy: conn.y1, sz: conn.z1,
          ex: conn.x2, ey: conn.y2, ez: conn.z2,
          t: 0,
          speed: eSpeed,
        });
        lastElectronSpawn = t;
      }
    }

    const ep = electronGeo.getAttribute("position") as THREE.BufferAttribute;
    const ea = ep.array as Float32Array;
    let aliveCount = 0;

    for (let e = activeElectrons.length - 1; e >= 0; e--) {
      const el = activeElectrons[e];
      el.t += el.speed;
      if (el.t >= 1) { activeElectrons.splice(e, 1); continue; }
      const ei = aliveCount * 3;
      ea[ei] = el.sx + (el.ex - el.sx) * el.t;
      ea[ei + 1] = el.sy + (el.ey - el.sy) * el.t;
      ea[ei + 2] = el.sz + (el.ez - el.sz) * el.t;
      aliveCount++;
    }

    electronGeo.setDrawRange(0, aliveCount);
    ep.needsUpdate = true;

    electronPoints.rotation.x = spinX; electronPoints.rotation.y = spinY; electronPoints.rotation.z = spinZ;
    electronPoints.position.z = cloudZ;
    electronMat.size = demoActive ? 1.4 + shockwave * 1.2 : speaking ? 1.0 + shockwave * 0.8 : 0.8;
    electronMat.opacity = demoActive ? 1.0 : speaking ? 1.0 + shockwave * 0.5 : 1.0;

    if (demoActive) {
      const hue = ((t - demoStartTime) * 0.2) % 1.0;
      _rainbowCol.setHSL(hue, 1.0, 0.6);

      if (shockwave > 0.4) {
        _rainbowCol.lerp(COL_FLASH, Math.min(1, (shockwave - 0.4) * 2.0));
      }

      mat.opacity = Math.min(1.4, currentBright + shockwave * 0.3);
      mat.size = currentSize + shockwave * 0.5;
      mat.color.lerp(_rainbowCol, 0.12);
      lineMat.color.lerp(_rainbowCol, 0.12);
      lineMat.opacity = lineAmount * 0.18 + shockwave * 0.25;
      electronMat.color.lerp(_rainbowCol, 0.15);

      pinkMat.opacity = Math.min(1.4, currentBright + shockwave * 0.3) * 1.25;
      pinkMat.size = (currentSize + shockwave * 0.5) * 1.12;
      pinkMat.color.setHex(currentSecondaryHex);

    } else if (speaking) {
      mat.opacity = Math.min(1.2, currentBright + bass * 0.18 + shockwave * 0.25);
      mat.size = currentSize + bass * 0.12 + shockwave * 0.20;

      const pulseIntensity = (bass * 0.7 + mid * 0.2 + shockwave * 0.5);
      const wave = 0.5 + 0.5 * Math.sin(t * 12.0 + bass * 8.0);
      _tmpColor.lerpColors(COL_SPEAK, COL_BRIGHT, Math.min(1, pulseIntensity * wave));

      if (shockwave > 0.18) {
        _tmpColor.lerp(COL_FLASH, (shockwave - 0.18) * 3.0);
      }
      mat.color.lerp(_tmpColor, 0.14);
      lineMat.color.lerp(_tmpColor, 0.14);
      electronMat.color.set(0xffffff);

      pinkMat.opacity = Math.min(1.2, currentBright + bass * 0.18 + shockwave * 0.25) * 1.25;
      pinkMat.size = (currentSize + bass * 0.12 + shockwave * 0.20) * 1.12;
      pinkMat.color.setHex(currentSecondaryHex);

    } else {
      mat.opacity = currentBright + bass * 0.08;
      mat.size = currentSize + bass * 0.05;

      if (state === "thinking") {
        mat.color.lerp(COL_THINK, 0.015);
        lineMat.color.lerp(COL_THINK, 0.015);
      } else {
        mat.color.lerp(COL_BASE, 0.015);
        lineMat.color.lerp(COL_BASE, 0.015);
      }
      electronMat.color.set(0xffffff);

      pinkMat.opacity = (currentBright + bass * 0.08) * 1.25;
      pinkMat.size = (currentSize + bass * 0.05) * 1.12;
      pinkMat.color.setHex(currentSecondaryHex);
    }

    if (demoActive) {
      const demoT = demoElapsed;
      camera.position.x = Math.sin(demoT * 0.5) * 8;
      camera.position.y = Math.cos(demoT * 0.35) * 5;
      camera.position.z = 150 + Math.sin(demoT * 0.6) * 20;
    } else {
      camera.position.x = Math.sin(t * 0.02) * 3;
      camera.position.y = Math.cos(t * 0.03) * 2;
      camera.position.z = 75;
    }
    camera.lookAt(0, 0, cloudZ * 0.2);

    renderer.render(scene, camera);
  }

  function onResize() {
    const isMinimized = canvas.classList.contains("minimized");
    const width = isMinimized ? (canvas.clientWidth || 180) : window.innerWidth;
    const height = isMinimized ? (canvas.clientHeight || 180) : window.innerHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  }

  window.addEventListener("resize", onResize);
  onResize();
  animate();

  return {
    setState(s: OrbState) {
      state = s;
    },
    setVolume(v: number) {
      externalVolume = v;
      if (v > 0.4) shockwave = Math.max(shockwave, v * 0.5);
    },
    setAnalyser(a: AnalyserNode | null) {
      analyser = a;
      if (a) freqData = new Uint8Array(a.frequencyBinCount);
    },
    triggerDemo() {
      demoActive = true;
      demoStartTime = clock.getElapsedTime();
      demoBurstNextAt = demoStartTime;
      shockwave = 1.0;
      transitionEnergy = 1.0;
    },
    setQuality(q: "low" | "high") {
      if (q === "high") {
        renderer.setPixelRatio(window.devicePixelRatio);
        mat.opacity = 0.6;
        pinkMat.opacity = 0.85;
        lineMat.opacity = 0.15;
      } else {
        renderer.setPixelRatio(1);
        mat.opacity = 0.3;
        pinkMat.opacity = 0.4;
        lineMat.opacity = 0.05;
      }
    },
    setTheme(tName: string) {
      const theme = THEME_COLORS[tName] || THEME_COLORS.cyan;
      COL_BASE.setHex(theme.primary);
      COL_THINK.setHex(theme.think);
      COL_SPEAK.setHex(theme.speak);
      COL_BRIGHT.setHex(theme.bright);
      
      // Update materials colors directly
      mat.color.setHex(theme.primary);
      pinkMat.color.setHex(theme.secondary);
      lineMat.color.setHex(theme.primary);
      
      // Save theme variables
      currentSecondaryHex = theme.secondary;
      currentThemeName = tName;
    },
    destroy() {
      destroyed = true;
      window.removeEventListener("resize", onResize);
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerleave", onPointerLeave);
      renderer.dispose();
    },
  };
}
