import * as THREE from 'three';

// ── Continuous Polyline Paths for Digits 0-9 (centered at 0,0) ────────────────
const DIGIT_PATHS: THREE.Vector2[][] = [
  // 0: Smooth Oval
  [
    new THREE.Vector2(0, 9),
    new THREE.Vector2(3.5, 7.5),
    new THREE.Vector2(4.5, 4),
    new THREE.Vector2(4.5, -4),
    new THREE.Vector2(3.5, -7.5),
    new THREE.Vector2(0, -9),
    new THREE.Vector2(-3.5, -7.5),
    new THREE.Vector2(-4.5, -4),
    new THREE.Vector2(-4.5, 4),
    new THREE.Vector2(-3.5, 7.5),
    new THREE.Vector2(0, 9)
  ],
  // 1: Serif, vertical stem, and flat base
  [
    new THREE.Vector2(-2.5, 6),
    new THREE.Vector2(0, 8.5),
    new THREE.Vector2(0, -8.5),
    new THREE.Vector2(-3, -8.5),
    new THREE.Vector2(3, -8.5)
  ],
  // 2: Upper arch, diagonal slide, and base
  [
    new THREE.Vector2(-4, 5.5),
    new THREE.Vector2(-2.5, 8),
    new THREE.Vector2(0, 8.5),
    new THREE.Vector2(2.5, 8),
    new THREE.Vector2(4, 5.5),
    new THREE.Vector2(4, 3.5),
    new THREE.Vector2(1.5, 0.5),
    new THREE.Vector2(-4, -8.5),
    new THREE.Vector2(4, -8.5)
  ],
  // 3: Symmetrical double loop
  [
    new THREE.Vector2(-4, 6),
    new THREE.Vector2(-2, 8.5),
    new THREE.Vector2(1, 8.7),
    new THREE.Vector2(4, 6.5),
    new THREE.Vector2(3, 3.5),
    new THREE.Vector2(0, 2),
    new THREE.Vector2(3, 0.5),
    new THREE.Vector2(4, -2.5),
    new THREE.Vector2(3.5, -6),
    new THREE.Vector2(1, -8.5),
    new THREE.Vector2(-2, -8.5),
    new THREE.Vector2(-4, -6)
  ],
  // 4: Triangle top and stem
  [
    new THREE.Vector2(-4, 1.5),
    new THREE.Vector2(2, 8.5),
    new THREE.Vector2(2, -8.5),
    new THREE.Vector2(2, 1.5),
    new THREE.Vector2(-4, 1.5),
    new THREE.Vector2(4.5, 1.5)
  ],
  // 5: Top bar, vertical stem, and bottom loop
  [
    new THREE.Vector2(4, 8.5),
    new THREE.Vector2(-3, 8.5),
    new THREE.Vector2(-3, 2.5),
    new THREE.Vector2(1, 2.5),
    new THREE.Vector2(4, 1),
    new THREE.Vector2(4, -4.5),
    new THREE.Vector2(1.5, -8.5),
    new THREE.Vector2(-2, -8.5),
    new THREE.Vector2(-4, -6)
  ],
  // 6: Arching hook into a bottom loop
  [
    new THREE.Vector2(3, 8.5),
    new THREE.Vector2(0, 8.7),
    new THREE.Vector2(-4, 5.5),
    new THREE.Vector2(-4.5, -4),
    new THREE.Vector2(-2, -8.5),
    new THREE.Vector2(2, -8.5),
    new THREE.Vector2(4, -5.5),
    new THREE.Vector2(4, -1.5),
    new THREE.Vector2(1.5, 1),
    new THREE.Vector2(-2, 1),
    new THREE.Vector2(-4, -1.5),
    new THREE.Vector2(-4.5, -4)
  ],
  // 7: Top bar, diagonal stem, and crossbar
  [
    new THREE.Vector2(-4, 8.5),
    new THREE.Vector2(4, 8.5),
    new THREE.Vector2(-1.5, -8.5),
    new THREE.Vector2(-1.5, 0.5),
    new THREE.Vector2(-3.5, 0.5),
    new THREE.Vector2(1.5, 0.5)
  ],
  // 8: Figure eight loops
  [
    new THREE.Vector2(0, 0),
    new THREE.Vector2(-3, 2),
    new THREE.Vector2(-3, 6.5),
    new THREE.Vector2(0, 8.5),
    new THREE.Vector2(3, 6.5),
    new THREE.Vector2(3, 2),
    new THREE.Vector2(0, 0),
    new THREE.Vector2(-3.3, -2),
    new THREE.Vector2(-3.3, -6.5),
    new THREE.Vector2(0, -8.5),
    new THREE.Vector2(3.3, -6.5),
    new THREE.Vector2(3.3, -2),
    new THREE.Vector2(0, 0)
  ],
  // 9: Top loop into a bottom hook
  [
    new THREE.Vector2(-3, -8.5),
    new THREE.Vector2(0, -8.7),
    new THREE.Vector2(4, -5.5),
    new THREE.Vector2(4.5, 4),
    new THREE.Vector2(2, 8.5),
    new THREE.Vector2(-2, 8.5),
    new THREE.Vector2(-4, 5.5),
    new THREE.Vector2(-4, 1.5),
    new THREE.Vector2(-1.5, -1),
    new THREE.Vector2(2, -1),
    new THREE.Vector2(4, 1.5),
    new THREE.Vector2(4.5, 4)
  ]
];

// Layout parameters
const SLOT_X = [-41.5, -28.5, -17.5, -6.5, 6.5, 17.5, 28.5, 41.5];
const IS_COLON = [false, false, true, false, false, true, false, false];
const DEPTH_Z = 1.2;

interface Node3D {
  frontSprite: THREE.Sprite;
  backSprite: THREE.Sprite;
  currentX: number;
  currentY: number;
  targetX: number;
  targetY: number;
  phaseX: number;
  phaseY: number;
  ampX: number;
  ampY: number;
  speed: number;
}

interface SlotData {
  nodes: Node3D[];
  frontLines: THREE.LineSegments;
  backLines: THREE.LineSegments;
  depthLines: THREE.LineSegments;
  currentValue: number; // -1 for colon, 0-9 for digits
}

// ── Uniform sampling along path ──────────────────────────────────────────────
function samplePolyline(vertices: THREE.Vector2[], count: number): THREE.Vector2[] {
  const points: THREE.Vector2[] = [];
  if (vertices.length === 0) {
    for (let i = 0; i < count; i++) points.push(new THREE.Vector2(0, 0));
    return points;
  }
  if (vertices.length === 1) {
    for (let i = 0; i < count; i++) points.push(vertices[0].clone());
    return points;
  }

  const segLengths: number[] = [];
  const cumLengths: number[] = [0];
  let totalLen = 0;
  for (let i = 0; i < vertices.length - 1; i++) {
    const d = vertices[i].distanceTo(vertices[i + 1]);
    segLengths.push(d);
    totalLen += d;
    cumLengths.push(totalLen);
  }

  for (let i = 0; i < count; i++) {
    const target = (i / (count - 1)) * totalLen;
    let segIdx = 0;
    while (segIdx < segLengths.length - 1 && cumLengths[segIdx + 1] < target) {
      segIdx++;
    }
    const segStartLen = cumLengths[segIdx];
    const segLen = segLengths[segIdx];
    const t = segLen > 0 ? (target - segStartLen) / segLen : 0;

    const pStart = vertices[segIdx];
    const pEnd = vertices[segIdx + 1];
    const p = new THREE.Vector2().lerpVectors(pStart, pEnd, t);
    points.push(p);
  }
  return points;
}

// Cache sampled coordinates for speed
const DIGIT_POINTS_CACHE: Record<number, THREE.Vector2[]> = {};

function getDigitPoints(val: number): THREE.Vector2[] {
  if (DIGIT_POINTS_CACHE[val]) {
    return DIGIT_POINTS_CACHE[val].map(p => p.clone());
  }

  let pts: THREE.Vector2[] = [];
  if (val === -1) {
    // Colon: Two circles of 16 points each
    for (let i = 0; i < 16; i++) {
      const theta = (i / 16) * Math.PI * 2;
      pts.push(new THREE.Vector2(Math.cos(theta) * 0.6, 3.5 + Math.sin(theta) * 0.6));
    }
    for (let i = 0; i < 16; i++) {
      const theta = (i / 16) * Math.PI * 2;
      pts.push(new THREE.Vector2(Math.cos(theta) * 0.6, -3.5 + Math.sin(theta) * 0.6));
    }
  } else {
    pts = samplePolyline(DIGIT_PATHS[val], 32);
  }

  DIGIT_POINTS_CACHE[val] = pts;
  return pts.map(p => p.clone());
}

// Get structural default connections
function getDefaultConnections(val: number): [number, number][] {
  const connections: [number, number][] = [];
  if (val === -1) {
    // Colon loops
    for (let i = 0; i < 16; i++) {
      connections.push([i, (i + 1) % 16]);
      connections.push([16 + i, 16 + (i + 1) % 16]);
    }
  } else {
    // Sequential digit path
    for (let i = 0; i < 31; i++) {
      connections.push([i, i + 1]);
    }
    if (val === 0) {
      connections.push([31, 0]);
    }
  }
  return connections;
}

// ── Canvas gradient particle textures ─────────────────────────────────────────
function createGlowTexture(colorStr: string): THREE.Texture {
  const canvas = document.createElement('canvas');
  canvas.width = 32;
  canvas.height = 32;
  const ctx = canvas.getContext('2d');
  if (ctx) {
    const grad = ctx.createRadialGradient(16, 16, 0, 16, 16, 16);
    grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
    grad.addColorStop(0.2, 'rgba(255, 255, 255, 0.85)');
    grad.addColorStop(0.5, colorStr);
    grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 32, 32);
  }
  return new THREE.CanvasTexture(canvas);
}

export function initHoloClock(): void {
  const container = document.getElementById('holo-clock-canvas-wrap');
  if (!container) return;

  const existingCanvas = document.getElementById('holo-clock-canvas');
  if (existingCanvas) {
    existingCanvas.remove();
  }

  const canvas = document.createElement('canvas');
  canvas.id = 'holo-clock-canvas';
  container.appendChild(canvas);

  const W = container.clientWidth || 380;
  const H = container.clientHeight || 95;
  canvas.width = W;
  canvas.height = H;

  // WebGL Setup
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(W, H);
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, W / H, 0.1, 1000);

  const clockGroup = new THREE.Group();
  scene.add(clockGroup);
  clockGroup.position.set(0, 0, 0);
  clockGroup.rotation.set(0, 0, 0);

  // Parallax pointer handler
  const mouse = new THREE.Vector2(0, 0);
  function onPointerMove(e: PointerEvent) {
    mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
  }
  function onPointerLeave() {
    mouse.set(0, 0);
  }
  window.addEventListener('pointermove', onPointerMove);
  window.addEventListener('pointerleave', onPointerLeave);

  // Textures and Materials
  const cyanGlow = createGlowTexture('rgba(0, 229, 255, 0.75)');
  const purpleGlow = createGlowTexture('rgba(148, 60, 255, 0.65)');

  const frontLineMat = new THREE.LineBasicMaterial({
    color: 0x00e5ff,
    transparent: true,
    opacity: 0.28,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });
  const backLineMat = new THREE.LineBasicMaterial({
    color: 0x943cff,
    transparent: true,
    opacity: 0.15,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });
  const depthLineMat = new THREE.LineBasicMaterial({
    color: 0x0088ff,
    transparent: true,
    opacity: 0.12,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });

  const slots: SlotData[] = [];

  // Build plexus and outline line structures
  function updateSlotLines(slot: SlotData) {
    const frontPos: number[] = [];
    const backPos: number[] = [];
    const depthPos: number[] = [];

    const nodes = slot.nodes;
    const connections = getDefaultConnections(slot.currentValue);

    // 1. Outline connections
    for (const [i, j] of connections) {
      const ni = nodes[i];
      const nj = nodes[j];

      frontPos.push(ni.frontSprite.position.x, ni.frontSprite.position.y, ni.frontSprite.position.z);
      frontPos.push(nj.frontSprite.position.x, nj.frontSprite.position.y, nj.frontSprite.position.z);

      backPos.push(ni.backSprite.position.x, ni.backSprite.position.y, ni.backSprite.position.z);
      backPos.push(nj.backSprite.position.x, nj.backSprite.position.y, nj.backSprite.position.z);
    }

    // 2. Extra dynamic Plexus connections based on 2D proximity
    for (let i = 0; i < 32; i++) {
      const ni = nodes[i];
      for (let j = i + 1; j < 32; j++) {
        const isDefault = connections.some(([a, b]) => (a === i && b === j) || (a === j && b === i));
        if (isDefault) continue;

        const nj = nodes[j];
        const dx = ni.currentX - nj.currentX;
        const dy = ni.currentY - nj.currentY;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 3.8) {
          frontPos.push(ni.frontSprite.position.x, ni.frontSprite.position.y, ni.frontSprite.position.z);
          frontPos.push(nj.frontSprite.position.x, nj.frontSprite.position.y, nj.frontSprite.position.z);

          backPos.push(ni.backSprite.position.x, ni.backSprite.position.y, ni.backSprite.position.z);
          backPos.push(nj.backSprite.position.x, nj.backSprite.position.y, nj.backSprite.position.z);
        }
      }
    }

    // 3. Dual-layer Depth connections
    for (let i = 0; i < 32; i++) {
      const ni = nodes[i];
      depthPos.push(ni.frontSprite.position.x, ni.frontSprite.position.y, ni.frontSprite.position.z);
      depthPos.push(ni.backSprite.position.x, ni.backSprite.position.y, ni.backSprite.position.z);

      for (let j = 0; j < 32; j++) {
        if (i === j) continue;
        const nj = nodes[j];
        const dx = ni.currentX - nj.currentX;
        const dy = ni.currentY - nj.currentY;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 2.8) {
          depthPos.push(ni.frontSprite.position.x, ni.frontSprite.position.y, ni.frontSprite.position.z);
          depthPos.push(nj.backSprite.position.x, nj.backSprite.position.y, nj.backSprite.position.z);
        }
      }
    }

    slot.frontLines.geometry.setAttribute('position', new THREE.Float32BufferAttribute(frontPos, 3));
    slot.frontLines.geometry.attributes.position.needsUpdate = true;

    slot.backLines.geometry.setAttribute('position', new THREE.Float32BufferAttribute(backPos, 3));
    slot.backLines.geometry.attributes.position.needsUpdate = true;

    slot.depthLines.geometry.setAttribute('position', new THREE.Float32BufferAttribute(depthPos, 3));
    slot.depthLines.geometry.attributes.position.needsUpdate = true;
  }

  function createSlot(slotIdx: number, val: number): SlotData {
    const nodes: Node3D[] = [];
    const pts = getDigitPoints(val);

    for (let i = 0; i < 32; i++) {
      const bx = SLOT_X[slotIdx] + pts[i].x;
      const by = pts[i].y;

      const frontMat = new THREE.SpriteMaterial({
        map: cyanGlow,
        transparent: true,
        opacity: 0.85,
        blending: THREE.AdditiveBlending,
        depthWrite: false
      });
      const frontSprite = new THREE.Sprite(frontMat);
      frontSprite.position.set(bx, by, DEPTH_Z);
      frontSprite.scale.set(0.9, 0.9, 1.0);
      clockGroup.add(frontSprite);

      const backMat = new THREE.SpriteMaterial({
        map: purpleGlow,
        transparent: true,
        opacity: 0.55,
        blending: THREE.AdditiveBlending,
        depthWrite: false
      });
      const backSprite = new THREE.Sprite(backMat);
      backSprite.position.set(bx, by, -DEPTH_Z);
      backSprite.scale.set(0.6, 0.6, 1.0);
      clockGroup.add(backSprite);

      nodes.push({
        frontSprite,
        backSprite,
        currentX: bx,
        currentY: by,
        targetX: bx,
        targetY: by,
        phaseX: Math.random() * Math.PI * 2,
        phaseY: Math.random() * Math.PI * 2,
        ampX: 0.12 + Math.random() * 0.12,
        ampY: 0.12 + Math.random() * 0.12,
        speed: 0.8 + Math.random() * 0.8,
      });
    }

    const frontLines = new THREE.LineSegments(new THREE.BufferGeometry(), frontLineMat);
    const backLines = new THREE.LineSegments(new THREE.BufferGeometry(), backLineMat);
    const depthLines = new THREE.LineSegments(new THREE.BufferGeometry(), depthLineMat);

    clockGroup.add(frontLines);
    clockGroup.add(backLines);
    clockGroup.add(depthLines);

    const slot: SlotData = {
      nodes,
      frontLines,
      backLines,
      depthLines,
      currentValue: val
    };

    updateSlotLines(slot);
    return slot;
  }

  // Time utilities
  function getTimeParts() {
    const now = new Date();
    const h = now.getHours();
    const m = now.getMinutes();
    const s = now.getSeconds();
    return [
      Math.floor(h / 10),
      h % 10,
      -1,
      Math.floor(m / 10),
      m % 10,
      -1,
      Math.floor(s / 10),
      s % 10,
    ];
  }

  // Initialize Slots
  const timeParts = getTimeParts();
  for (let i = 0; i < 8; i++) {
    slots.push(createSlot(i, timeParts[i]));
  }

  let prevParts = [...timeParts];
  let lastSecond = -1;

  function frameCamera() {
    const aspect = W / H;
    const fovRad = (camera.fov * Math.PI) / 180;
    const halfTan = Math.tan(fovRad / 2);

    const dWidth = (93 * 1.06) / (2 * halfTan * aspect);
    const dHeight = (18 * 1.22) / (2 * halfTan);
    const cameraZ = Math.max(dWidth, dHeight, 80);

    camera.position.set(0, 0, cameraZ);
    camera.lookAt(0, 0, 0);
  }

  frameCamera();

  // Animation Frame Loop
  let animId: number;
  function animate(t: number) {
    animId = requestAnimationFrame(animate);

    const tSec = t / 1000;
    const now = new Date();
    const currentSecond = now.getSeconds();

    // 1. Check time changes
    if (currentSecond !== lastSecond) {
      lastSecond = currentSecond;
      const newParts = getTimeParts();

      for (let i = 0; i < 8; i++) {
        if (IS_COLON[i]) continue;
        if (newParts[i] !== prevParts[i]) {
          const val = newParts[i] as number;
          slots[i].currentValue = val;
          const pts = getDigitPoints(val);
          for (let k = 0; k < 32; k++) {
            slots[i].nodes[k].targetX = SLOT_X[i] + pts[k].x;
            slots[i].nodes[k].targetY = pts[k].y;
          }
        }
      }
      prevParts = [...newParts];
    }

    // 2. Parallax rotation lerp
    const targetRotX = -mouse.y * 0.12;
    const targetRotY = mouse.x * 0.12;
    clockGroup.rotation.x += (targetRotX - clockGroup.rotation.x) * 0.08;
    clockGroup.rotation.y += (targetRotY - clockGroup.rotation.y) * 0.08;

    // 3. Node morph and shivering animation
    for (let si = 0; si < slots.length; si++) {
      const slot = slots[si];
      for (let ni = 0; ni < 32; ni++) {
        const nd = slot.nodes[ni];

        // Linear interpolation towards targets
        nd.currentX += (nd.targetX - nd.currentX) * 0.12;
        nd.currentY += (nd.targetY - nd.currentY) * 0.12;

        // Micro shivering noise
        const dx = Math.sin(tSec * nd.speed + nd.phaseX) * nd.ampX * 0.25;
        const dy = Math.cos(tSec * nd.speed * 0.85 + nd.phaseY) * nd.ampY * 0.25;

        nd.frontSprite.position.set(nd.currentX + dx, nd.currentY + dy, DEPTH_Z);
        nd.backSprite.position.set(nd.currentX + dx * 0.7, nd.currentY + dy * 0.7, -DEPTH_Z);
      }

      // 4. Update slot plexus lines
      updateSlotLines(slot);
    }

    renderer.render(scene, camera);
  }

  animate(0);

  // Resize listener
  window.addEventListener('resize', () => {
    const newW = container.clientWidth || 380;
    const newH = container.clientHeight || 95;
    canvas.width = newW;
    canvas.height = newH;
    renderer.setSize(newW, newH);
    camera.aspect = newW / newH;
    camera.updateProjectionMatrix();
    frameCamera();
  });
}
