/* ══════════════════════════════════════════════════════════════════════════
   MISSION ANNIVERSAIRE SECRET — 8 KEYS MAGICAL FAIRY TALE GAME ENGINE
   ══════════════════════════════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {
  
  // Game State (8 Keys)
  const state = {
    unlockedKeys: [false, false, false, false, false, false, false, false],
    currentLevel: 1,
    targetLettersSequence: ["P", "R", "I", "N", "C", "E", "S", "S", "E"],
    currentSequenceIndex: 0,
    userCollectedLetters: [],
    targetLat: 48,
    targetLong: 70,
    signalLocked: false
  };

  // Helper string normalization
  function cleanStr(str) {
    return (str || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]/g, "");
  }

  // DOM Elements
  const globalProgress = document.getElementById("global-progress");

  // ── KEY UNLOCK UTILITY (8 KEYS) ──────────────────────────────────────────
  function unlockKey(index) {
    if (state.unlockedKeys[index - 1]) return;
    state.unlockedKeys[index - 1] = true;

    const slotEl = document.getElementById(`slot-key-${index}`);
    if (slotEl) {
      slotEl.classList.add("unlocked");
      slotEl.querySelector(".key-icon").textContent = "🔑";
    }

    const vkEl = document.getElementById(`vk${index}`);
    if (vkEl) {
      vkEl.classList.add("active");
    }

    const activeKeysCount = state.unlockedKeys.filter(Boolean).length;
    const progressPct = 4 + (activeKeysCount * 12);
    globalProgress.style.width = `${progressPct}%`;
  }

  function switchToLevel(nextLevelNum) {
    document.querySelectorAll(".card-level").forEach(card => card.classList.remove("active"));
    const nextCard = document.getElementById(`level-${nextLevelNum}`);
    if (nextCard) {
      nextCard.classList.add("active");
      state.currentLevel = nextLevelNum;
    }
  }
  function requestFullScreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    }
  }
  // ── WELCOME SCREEN & DIGICODE LEVEL 0 LISTENER ──────────────────────────
  const btnStartQuest = document.getElementById("btn-start-quest");
  btnStartQuest?.addEventListener("click", () => {
    requestFullScreen();
    switchToLevel(0);
  });

  // ════════════════════════════════════════════════════════════════════════
  // LEVEL 0: DIGICODE IRL VERIFICATION (130 / 1604 / 143)
  // ════════════════════════════════════════════════════════════════════════
  const code1Input = document.getElementById("code1-input");
  const code2Input = document.getElementById("code2-input");
  const code3Input = document.getElementById("code3-input");
  const btnValidateDigicode = document.getElementById("btn-validate-digicode");
  const l0Error = document.getElementById("l0-error");

  [code1Input, code2Input, code3Input].forEach(inp => {
    inp?.addEventListener("input", () => {
      inp.classList.remove("input-error", "input-success");
      if (l0Error) l0Error.textContent = "";
    });
  });

  btnValidateDigicode?.addEventListener("click", () => {
    const c1 = (code1Input?.value || "").trim();
    const c2 = (code2Input?.value || "").trim();
    const c3 = (code3Input?.value || "").trim();

    let valid = true;

    if (c1 !== "130") {
      code1Input?.classList.add("input-error");
      valid = false;
    } else {
      code1Input?.classList.add("input-success");
    }

    if (c2 !== "1604") {
      code2Input?.classList.add("input-error");
      valid = false;
    } else {
      code2Input?.classList.add("input-success");
    }

    if (c3 !== "143") {
      code3Input?.classList.add("input-error");
      valid = false;
    } else {
      code3Input?.classList.add("input-success");
    }

    if (!valid) {
      if (l0Error) {
        l0Error.style.color = "#ff477e";
        l0Error.textContent = "❌ Accès refusé ! Vérifie les codes obtenus durant ta recherche dans la maison.";
      }
      return;
    }

    if (l0Error) {
      l0Error.style.color = "#2ed573";
      l0Error.textContent = "✨ SÉCURITÉ VERROUILLÉE DÉVERROUILLÉE ! Lancement de l'aventure...";
    }

    setTimeout(() => {
      switchToLevel(1);
    }, 900);
  });

  // ════════════════════════════════════════════════════════════════════════
  // LEVEL 1: SOUVENIRS (5 EXACT QUESTIONS)
  // ════════════════════════════════════════════════════════════════════════
  const q1Input = document.getElementById("q1-input");
  const q2Input = document.getElementById("q2-input");
  const q3Input = document.getElementById("q3-input");
  const q4Input = document.getElementById("q4-input");
  const q5Input = document.getElementById("q5-input");

  const btnValidateL1 = document.getElementById("btn-validate-l1");
  const l1Error = document.getElementById("l1-error");

  const answersQ1 = ["billsburger", "billburger", "bills", "bill", "billssburger"];
  const answersQ2 = ["hyeres", "hyere"];
  const answersQ3 = ["hogwartslegacy", "hogwarts", "harrypotter", "hogwart"];
  const answersQ4 = ["nuggets", "nugget", "lesnuggets"];
  const answersQ5 = ["disney", "disneyland", "disneylandparis"];

  [q1Input, q2Input, q3Input, q4Input, q5Input].forEach(inputEl => {
    inputEl?.addEventListener("input", () => {
      inputEl.classList.remove("input-error", "input-success");
    });
  });

  btnValidateL1?.addEventListener("click", () => {
    const val1 = cleanStr(q1Input.value);
    const val2 = cleanStr(q2Input.value);
    const val3 = cleanStr(q3Input.value);
    const val4 = cleanStr(q4Input.value);
    const val5 = cleanStr(q5Input.value);

    const raw1 = (q1Input?.value || "").trim();
    const raw2 = (q2Input?.value || "").trim();
    const raw3 = (q3Input?.value || "").trim();
    const raw4 = (q4Input?.value || "").trim();
    const raw5 = (q5Input?.value || "").trim();

    // STRICT Easter Egg: ONLY if Q3 === "3" AND Q1, Q2, Q4, Q5 are ALL EMPTY!
    const isEasterEgg = (raw3 === "3" || val3 === "3") && !raw1 && !raw2 && !raw4 && !raw5;

    if (isEasterEgg) {
      q1Input.value = "Bill's Burger";
      q2Input.value = "Hyères";
      q3Input.value = "Hogwarts Legacy";
      q4Input.value = "Nuggets";
      q5Input.value = "Disneyland Paris";

      [q1Input, q2Input, q3Input, q4Input, q5Input].forEach(el => {
        if (el) {
          el.classList.remove("input-error");
          el.classList.add("input-success");
        }
      });
      l1Error.style.color = "#2ed573";
      l1Error.textContent = "✨ 5/5 BONNES RÉPONSES ! CLÉ 1 DÉBLOQUÉE ! ✨";
      unlockKey(1);
      btnValidateL1.textContent = "VALIDÉ ! 🗝️";
      btnValidateL1.disabled = true;

      setTimeout(() => {
        switchToLevel(2);
        initLevel2Laser();
      }, 800);
      return;
    }

    const ok1 = val1.length >= 3 && answersQ1.some(ans => val1 === ans || val1.includes(ans));
    const ok2 = val2.length >= 3 && answersQ2.some(ans => val2 === ans || val2.includes(ans));
    const ok3 = val3.length >= 4 && answersQ3.some(ans => val3 === ans || val3.includes(ans));
    const ok4 = val4.length >= 4 && answersQ4.some(ans => val4 === ans || val4.includes(ans));
    const ok5 = val5.length >= 4 && answersQ5.some(ans => val5.includes(ans));

    function markField(inputEl, isOk) {
      if (!inputEl) return;
      inputEl.classList.remove("input-error", "input-success");
      void inputEl.offsetWidth;
      if (isOk) {
        inputEl.classList.add("input-success");
      } else {
        inputEl.classList.add("input-error");
      }
    }

    markField(q1Input, ok1);
    markField(q2Input, ok2);
    markField(q3Input, ok3);
    markField(q4Input, ok4);
    markField(q5Input, ok5);

    if (!val1 || !val2 || !val3 || !val4 || !val5) {
      l1Error.style.color = "#ff477e";
      l1Error.textContent = "Merci de répondre aux 5 questions pour continuer !";
      return;
    }

    if (!ok1 || !ok2 || !ok3 || !ok4 || !ok5) {
      l1Error.style.color = "#ff477e";
      l1Error.textContent = "Les réponses incorrectes sont entourées en rouge ! Corrige-les.";
      return;
    }

    l1Error.style.color = "#2ed573";
    l1Error.textContent = "✨ 5/5 BONNES RÉPONSES ! CLÉ 1 DÉBLOQUÉE ! ✨";
    unlockKey(1);
    btnValidateL1.textContent = "VALIDÉ ! 🗝️";
    btnValidateL1.disabled = true;

    setTimeout(() => {
      switchToLevel(2);
      initLevel2Laser();
    }, 1200);
  });

  // ════════════════════════════════════════════════════════════════════════
  // LEVEL 2: LE GRAND LABYRINTHE OPTIQUE SUR GRILLE 15x15
  // ════════════════════════════════════════════════════════════════════════
  const laserCanvas = document.getElementById("laser-canvas");
  const laserCtx = laserCanvas ? laserCanvas.getContext("2d") : null;
  const laserStatus = document.getElementById("laser-status");
  const btnValidateL2 = document.getElementById("btn-validate-l2");

  // 15 Glass Mirrors on 15x15 Grid (12 Schema + 3 Decoy Mirrors)
  const mirrorObjects = [
    { x: 161, y: 23,  angle: 135, length: 50, id: 1 },  // Col 3, Row 0
    { x: 437, y: 23,  angle: 90,  length: 50, id: 2 },  // Col 9, Row 0
    { x: 575, y: 23,  angle: 0,   length: 50, id: 3 },  // Col 12, Row 0
    { x: 23,  y: 115, angle: 90,  length: 50, id: 4 },  // Col 0, Row 2
    { x: 575, y: 115, angle: 0,   length: 50, id: 5 },  // Col 12, Row 2
    { x: 253, y: 299, angle: 90,  length: 50, id: 6 },  // Col 5, Row 6
    { x: 529, y: 299, angle: 0,   length: 50, id: 7 },  // Col 11, Row 6
    { x: 23,  y: 437, angle: 90,  length: 50, id: 8 },  // Col 0, Row 9
    { x: 161, y: 437, angle: 0,   length: 50, id: 9 },  // Col 3, Row 9
    { x: 253, y: 575, angle: 90,  length: 50, id: 10 }, // Col 5, Row 12
    { x: 437, y: 575, angle: 0,   length: 50, id: 11 }, // Col 9, Row 12
    { x: 529, y: 621, angle: 90,  length: 50, id: 12 }, // Col 11, Row 13
    // Decoy Mirrors (Miroirs leurres)
    { x: 345, y: 161, angle: 45,  length: 50, id: 13 }, // Col 7, Row 3 (Decoy 1)
    { x: 391, y: 483, angle: 135, length: 50, id: 14 }, // Col 8, Row 10 (Decoy 2)
    { x: 115, y: 345, angle: 90,  length: 50, id: 15 }  // Col 2, Row 7 (Decoy 3)
  ];

  // 5 Dark Alloy Obstacle Pillars (3 Schema + 2 Decoy Obstacles)
  const obstacleObjects = [
    { x: 253, y: 23,  radius: 20, label: "" }, // Col 5, Row 0
    { x: 621, y: 299, radius: 20, label: "" }, // Col 13, Row 6
    { x: 322, y: 437, radius: 20, label: "" }, // Col 7, Row 9
    // Decoy Obstacles (Piliers leurres)
    { x: 115, y: 207, radius: 20, label: "" }, // Col 2, Row 4 (Decoy 1)
    { x: 575, y: 483, radius: 20, label: "" }  // Col 12, Row 10 (Decoy 2)
  ];

  const emitterPos = { x: 23, y: 23, dirX: 1, dirY: 0 };  // Col 0, Row 0 (>)
  const targetPos = { x: 621, y: 621, radius: 22 };      // Col 13, Row 13 (<)

  let laserPulseTime = 0;

  function initLevel2Laser() {
    if (!laserCanvas || !laserCtx) return;

    if (btnValidateL2) btnValidateL2.disabled = true;

    laserCanvas.onclick = (e) => {
      const rect = laserCanvas.getBoundingClientRect();
      const clickX = (e.clientX - rect.left) * (laserCanvas.width / rect.width);
      const clickY = (e.clientY - rect.top) * (laserCanvas.height / rect.height);

      mirrorObjects.forEach(m => {
        const dist = Math.hypot(clickX - m.x, clickY - m.y);
        if (dist <= 36) {
          // 4-Way Rotation Mechanic: 0° -> 45° -> 90° -> 135° -> 0°
          m.angle = (m.angle + 45) % 180;
          renderLaserScene();
        }
      });
    };

    renderLaserScene();
  }

  function renderLaserScene() {
    if (!laserCtx) return;
    laserPulseTime += 0.08;
    const w = laserCanvas.width;
    const h = laserCanvas.height;

    laserCtx.clearRect(0, 0, w, h);

    // 1. 15x15 Sci-Fi Grid Floor
    laserCtx.fillStyle = "#090312";
    laserCtx.fillRect(0, 0, w, h);

    // Draw 15x15 Grid Lines
    laserCtx.strokeStyle = "rgba(255, 126, 179, 0.12)";
    laserCtx.lineWidth = 1;
    for (let x = 0; x <= w; x += 46) {
      laserCtx.beginPath(); laserCtx.moveTo(x, 0); laserCtx.lineTo(x, h); laserCtx.stroke();
    }
    for (let y = 0; y <= h; y += 46) {
      laserCtx.beginPath(); laserCtx.moveTo(0, y); laserCtx.lineTo(w, y); laserCtx.stroke();
    }

    // 2. Trace Laser Ray Path
    const rayPoints = [{ x: emitterPos.x, y: emitterPos.y }];
    let curX = emitterPos.x;
    let curY = emitterPos.y;
    let dirX = emitterPos.dirX;
    let dirY = emitterPos.dirY;
    let hitTarget = false;
    let hitObstaclePos = null;

    for (let bounce = 0; bounce < 14; bounce++) {
      let maxDist = 950;
      let nextX = curX + dirX * maxDist;
      let nextY = curY + dirY * maxDist;
      let closestT = maxDist;
      let hitMirror = null;
      let hitObstacle = null;

      // Check wall bounds
      if (dirX > 0) { const t = (w - curX) / dirX; if (t < closestT) { closestT = t; nextX = w; nextY = curY + dirY * t; hitMirror = null; } }
      if (dirX < 0) { const t = (0 - curX) / dirX; if (t < closestT) { closestT = t; nextX = 0; nextY = curY + dirY * t; hitMirror = null; } }
      if (dirY > 0) { const t = (h - curY) / dirY; if (t < closestT) { closestT = t; nextY = h; nextX = curX + dirX * t; hitMirror = null; } }
      if (dirY < 0) { const t = (0 - curY) / dirY; if (t < closestT) { closestT = t; nextY = 0; nextX = curX + dirX * t; hitMirror = null; } }

      // Check Target Collision
      const projT = (targetPos.x - curX) * dirX + (targetPos.y - curY) * dirY;
      if (projT > 0 && projT < closestT) {
        const perpX = curX + dirX * projT;
        const perpY = curY + dirY * projT;
        const perpDist = Math.hypot(targetPos.x - perpX, targetPos.y - perpY);
        if (perpDist <= targetPos.radius) {
          closestT = projT;
          nextX = curX + dirX * projT;
          nextY = curY + dirY * projT;
          hitTarget = true;
          hitMirror = null;
          hitObstacle = null;
        }
      }

      // Check Obstacle Collisions
      obstacleObjects.forEach(obs => {
        const oT = (obs.x - curX) * dirX + (obs.y - curY) * dirY;
        if (oT > 0 && oT < closestT) {
          const perpX = curX + dirX * oT;
          const perpY = curY + dirY * oT;
          const perpDist = Math.hypot(obs.x - perpX, obs.y - perpY);
          if (perpDist <= obs.radius) {
            closestT = oT;
            nextX = curX + dirX * oT;
            nextY = curY + dirY * oT;
            hitTarget = false;
            hitMirror = null;
            hitObstacle = obs;
          }
        }
      });

      // Check Mirror Collisions
      mirrorObjects.forEach(m => {
        const rad = (m.angle * Math.PI) / 180;
        const mx1 = m.x - Math.cos(rad) * (m.length / 2);
        const my1 = m.y - Math.sin(rad) * (m.length / 2);
        const mx2 = m.x + Math.cos(rad) * (m.length / 2);
        const my2 = m.y + Math.sin(rad) * (m.length / 2);

        const den = (curX - (curX + dirX)) * (my1 - my2) - (curY - (curY + dirY)) * (mx1 - mx2);
        if (Math.abs(den) > 0.0001) {
          const t = ((curX - mx1) * (my1 - my2) - (curY - my1) * (mx1 - mx2)) / den;
          const u = -((curX - (curX + dirX)) * (curY - my1) - (curY - (curY + dirY)) * (curX - mx1)) / den;
          if (t > 1 && u >= 0 && u <= 1 && t < closestT) {
            closestT = t;
            nextX = curX + dirX * t;
            nextY = curY + dirY * t;
            hitMirror = m;
            hitTarget = false;
            hitObstacle = null;
          }
        }
      });

      rayPoints.push({ x: nextX, y: nextY });

      if (hitObstacle) {
        hitObstaclePos = { x: nextX, y: nextY };
        break;
      }

      if (hitTarget || !hitMirror) break;

      curX = nextX;
      curY = nextY;
      const mRad = (hitMirror.angle * Math.PI) / 180;
      let nx = -Math.sin(mRad);
      let ny = Math.cos(mRad);
      const dot = dirX * nx + dirY * ny;
      dirX = dirX - 2 * dot * nx;
      dirY = dirY - 2 * dot * ny;
    }

    // 3. Draw Magical Energy Laser Beam
    if (rayPoints.length > 1) {
      laserCtx.beginPath();
      laserCtx.moveTo(rayPoints[0].x, rayPoints[0].y);
      for (let i = 1; i < rayPoints.length; i++) laserCtx.lineTo(rayPoints[i].x, rayPoints[i].y);
      laserCtx.strokeStyle = "rgba(255, 71, 126, 0.75)";
      laserCtx.lineWidth = 10;
      laserCtx.shadowBlur = 20;
      laserCtx.shadowColor = "#ff477e";
      laserCtx.stroke();

      laserCtx.beginPath();
      laserCtx.moveTo(rayPoints[0].x, rayPoints[0].y);
      for (let i = 1; i < rayPoints.length; i++) laserCtx.lineTo(rayPoints[i].x, rayPoints[i].y);
      laserCtx.strokeStyle = "#ff7eb3";
      laserCtx.lineWidth = 4;
      laserCtx.stroke();

      laserCtx.beginPath();
      laserCtx.moveTo(rayPoints[0].x, rayPoints[0].y);
      for (let i = 1; i < rayPoints.length; i++) laserCtx.lineTo(rayPoints[i].x, rayPoints[i].y);
      laserCtx.strokeStyle = "#ffffff";
      laserCtx.lineWidth = 2;
      laserCtx.shadowBlur = 0;
      laserCtx.stroke();
    }

    // Draw Energy Impact Flare on Obstacle
    if (hitObstaclePos) {
      laserCtx.save();
      laserCtx.beginPath();
      laserCtx.arc(hitObstaclePos.x, hitObstaclePos.y, 14, 0, Math.PI * 2);
      laserCtx.fillStyle = "rgba(255, 71, 87, 0.9)";
      laserCtx.shadowBlur = 25;
      laserCtx.shadowColor = "#ff4757";
      laserCtx.fill();

      // Spark particles
      for (let p = 0; p < 8; p++) {
        const pAng = (p * Math.PI) / 4 + laserPulseTime * 2;
        const px = hitObstaclePos.x + Math.cos(pAng) * 18;
        const py = hitObstaclePos.y + Math.sin(pAng) * 18;
        laserCtx.fillStyle = "#ffa502";
        laserCtx.fillRect(px - 2, py - 2, 4, 4);
      }
      laserCtx.restore();
    }

    // 4. Draw Realistic Laser Cannon Nozzle
    laserCtx.save();
    laserCtx.translate(emitterPos.x, emitterPos.y);
    
    // Base housing
    laserCtx.fillStyle = "#1e293b";
    laserCtx.beginPath(); laserCtx.arc(0, 0, 22, 0, Math.PI * 2); laserCtx.fill();
    laserCtx.strokeStyle = "#cbd5e1"; laserCtx.lineWidth = 3; laserCtx.stroke();
    
    // Metallic Nozzle Barrel
    const barrelGrad = laserCtx.createLinearGradient(0, -8, 0, 8);
    barrelGrad.addColorStop(0, "#94a3b8");
    barrelGrad.addColorStop(0.5, "#f8fafc");
    barrelGrad.addColorStop(1, "#475569");
    laserCtx.fillStyle = barrelGrad;
    laserCtx.fillRect(10, -8, 16, 16);
    laserCtx.strokeStyle = "#0f172a";
    laserCtx.lineWidth = 1.5;
    laserCtx.strokeRect(10, -8, 16, 16);
    laserCtx.restore();

    // 5. Draw Realistic Dark Alloy Obstacle Obelisks (NO EMOJIS, NO CIRCLES)
    obstacleObjects.forEach(obs => {
      laserCtx.save();
      laserCtx.translate(obs.x, obs.y);

      // Floor Shadow
      laserCtx.beginPath();
      laserCtx.ellipse(0, 16, 26, 10, 0, 0, Math.PI * 2);
      laserCtx.fillStyle = "rgba(0, 0, 0, 0.7)";
      laserCtx.fill();

      // 3D Hexagonal Dark Alloy Pillar
      const r = obs.radius;
      laserCtx.fillStyle = "#0f172a";
      laserCtx.beginPath();
      for (let i = 0; i < 6; i++) {
        const a = (i * Math.PI) / 3 - Math.PI / 6;
        const px = Math.cos(a) * r;
        const py = Math.sin(a) * r;
        if (i === 0) laserCtx.moveTo(px, py);
        else laserCtx.lineTo(px, py);
      }
      laserCtx.closePath();

      const pillarGrad = laserCtx.createLinearGradient(-r, -r, r, r);
      pillarGrad.addColorStop(0, "#334155");
      pillarGrad.addColorStop(0.5, "#1e293b");
      pillarGrad.addColorStop(1, "#0f172a");
      laserCtx.fillStyle = pillarGrad;
      laserCtx.shadowBlur = 15;
      laserCtx.shadowColor = "rgba(0, 0, 0, 0.8)";
      laserCtx.fill();

      laserCtx.strokeStyle = "#64748b";
      laserCtx.lineWidth = 2;
      laserCtx.stroke();

      // Inner Glowing Energy Core Slot
      laserCtx.beginPath();
      laserCtx.arc(0, 0, 9, 0, Math.PI * 2);
      laserCtx.fillStyle = "rgba(239, 68, 68, 0.7)";
      laserCtx.shadowBlur = 15;
      laserCtx.shadowColor = "#ef4444";
      laserCtx.fill();

      laserCtx.restore();
    });

    // 6. Draw Realistic 3D Glass Mirrors (NO DOTTED YELLOW CIRCLE, NO EMOJIS)
    mirrorObjects.forEach(m => {
      laserCtx.save();
      laserCtx.translate(m.x, m.y);

      // 1. Realistic Floor Base Drop Shadow
      laserCtx.beginPath();
      laserCtx.ellipse(0, 20, 28, 9, 0, 0, Math.PI * 2);
      laserCtx.fillStyle = "rgba(0, 0, 0, 0.65)";
      laserCtx.fill();

      // 2. Swivel Base Mount Pin
      laserCtx.beginPath();
      laserCtx.arc(0, 0, 6, 0, Math.PI * 2);
      laserCtx.fillStyle = "#64748b";
      laserCtx.fill();

      laserCtx.rotate((m.angle * Math.PI) / 180);

      // 3. Heavy Metal Mirror Backing & Bevel Frame
      const frameGrad = laserCtx.createLinearGradient(0, -9, 0, 9);
      frameGrad.addColorStop(0, "#475569");
      frameGrad.addColorStop(0.5, "#cbd5e1");
      frameGrad.addColorStop(1, "#1e293b");
      laserCtx.fillStyle = frameGrad;
      laserCtx.fillRect(-m.length / 2 - 4, -8, m.length + 8, 16);
      laserCtx.strokeStyle = "#0f172a";
      laserCtx.lineWidth = 1.5;
      laserCtx.strokeRect(-m.length / 2 - 4, -8, m.length + 8, 16);

      // 4. Photorealistic Glass Mirror Face
      const glassGrad = laserCtx.createLinearGradient(-m.length / 2, -5, m.length / 2, 5);
      glassGrad.addColorStop(0, "#f8fafc");
      glassGrad.addColorStop(0.35, "#cbd5e1");
      glassGrad.addColorStop(0.7, "#64748b");
      glassGrad.addColorStop(1, "#334155");
      laserCtx.fillStyle = glassGrad;
      laserCtx.fillRect(-m.length / 2, -5, m.length, 10);

      // 5. Specular Sheen Ray Across Glass
      laserCtx.beginPath();
      laserCtx.moveTo(-m.length / 2 + 8, -3);
      laserCtx.lineTo(m.length / 2 - 8, -3);
      laserCtx.strokeStyle = "rgba(255, 255, 255, 0.95)";
      laserCtx.lineWidth = 2;
      laserCtx.stroke();

      laserCtx.restore();
    });

    // 7. Draw Realistic Solar Receiver Target Target
    laserCtx.save();
    laserCtx.translate(targetPos.x, targetPos.y);

    if (hitTarget) {
      laserCtx.beginPath();
      laserCtx.arc(0, 0, targetPos.radius + Math.sin(laserPulseTime * 2) * 5, 0, Math.PI * 2);
      laserCtx.fillStyle = "rgba(46, 213, 115, 0.45)";
      laserCtx.shadowBlur = 35;
      laserCtx.shadowColor = "#2ed573";
      laserCtx.fill();

      laserCtx.beginPath();
      laserCtx.arc(0, 0, targetPos.radius, 0, Math.PI * 2);
      laserCtx.fillStyle = "#2ed573";
      laserCtx.fill();
      laserCtx.strokeStyle = "#ffffff";
      laserCtx.lineWidth = 3.5;
      laserCtx.stroke();

      laserCtx.beginPath();
      laserCtx.arc(0, 0, 10, 0, Math.PI * 2);
      laserCtx.fillStyle = "#ffffff";
      laserCtx.fill();

      laserStatus.textContent = "✨ FAISCEAU ALIGNÉ ! CLÉ 2 DÉBLOQUÉE ! ✨";
      laserStatus.style.borderColor = "#2ed573";
      laserStatus.style.color = "#2ed573";
      unlockKey(2);
      if (btnValidateL2) btnValidateL2.disabled = false;

    } else {
      laserCtx.beginPath();
      laserCtx.arc(0, 0, targetPos.radius, 0, Math.PI * 2);
      laserCtx.fillStyle = "rgba(15, 23, 42, 0.8)";
      laserCtx.strokeStyle = "#64748b";
      laserCtx.lineWidth = 3;
      laserCtx.stroke();

      laserCtx.beginPath();
      laserCtx.arc(0, 0, 10, 0, Math.PI * 2);
      laserCtx.fillStyle = "rgba(255, 126, 179, 0.4)";
      laserCtx.fill();

      if (hitObstaclePos) {
        laserStatus.textContent = "💥 FAISCEAU ENTRAVÉ PAR UN PILIER OBSCUR — Oriente les miroirs pour le contourner !";
        laserStatus.style.borderColor = "#ef4444";
        laserStatus.style.color = "#ef4444";
      } else {
        laserStatus.textContent = "FAISCEAU DISPERSÉ — Ajuste l'orientation des 8 miroirs de verre...";
        laserStatus.style.borderColor = "rgba(255, 126, 179, 0.3)";
        laserStatus.style.color = "var(--pink-glow)";
      }
      if (btnValidateL2) btnValidateL2.disabled = true;
    }

    laserCtx.restore();
  }

  btnValidateL2?.addEventListener("click", () => {
    switchToLevel(3);
    initLevel3Letters();
  });

  // ════════════════════════════════════════════════════════════════════════
  // LEVEL 3: SCATTERED MOVING LETTERS (P R I N C E S S E)
  // ════════════════════════════════════════════════════════════════════════
  const cipherWordGrid = document.getElementById("cipher-word-grid");
  const lettersScatterField = document.getElementById("letters-scatter-field");
  const btnResetCipher = document.getElementById("btn-reset-cipher");
  const l3Error = document.getElementById("l3-error");

  let movingLettersInterval = null;

  function initLevel3Letters() {
    state.currentSequenceIndex = 0;
    state.userCollectedLetters = [];
    l3Error.textContent = "";

    cipherWordGrid.innerHTML = "";
    for (let i = 0; i < 9; i++) {
      const slot = document.createElement("div");
      slot.className = "cipher-letter-slot";
      slot.id = `c-slot-${i}`;
      slot.textContent = "_";
      cipherWordGrid.appendChild(slot);
    }

    lettersScatterField.innerHTML = "";
    const extraDecoys = [
      "A", "B", "D", "F", "G", "H", "J", "K", "L", "M", "O", "Q", "T", "U", "V", "W", "X", "Y", "Z",
      "A", "E", "I", "O", "U", "B", "C", "D", "F", "G", "H", "L", "M", "N", "P", "R", "S", "T",
      "✨", "⭐", "💖", "🔮", "👑", "🌟", "💎", "🎀"
    ];
    const allLetters = [
      ...state.targetLettersSequence,
      ...extraDecoys
    ];

    allLetters.sort(() => Math.random() - 0.5);

    const letterNodes = [];

    allLetters.forEach((char) => {
      const letterBtn = document.createElement("div");
      letterBtn.className = "scatter-letter-btn";
      letterBtn.textContent = char;

      let x = Math.random() * 85 + 5;
      let y = Math.random() * 80 + 5;
      let vx = (Math.random() - 0.5) * 1.2;
      let vy = (Math.random() - 0.5) * 1.2;

      letterBtn.style.left = `${x}%`;
      letterBtn.style.top = `${y}%`;

      letterNodes.push({ el: letterBtn, x, y, vx, vy });

      letterBtn.addEventListener("click", () => {
        const expectedChar = state.targetLettersSequence[state.currentSequenceIndex];

        if (char === expectedChar && !letterBtn.classList.contains("clicked")) {
          letterBtn.classList.add("clicked");
          
          const currentSlot = document.getElementById(`c-slot-${state.currentSequenceIndex}`);
          if (currentSlot) {
            currentSlot.textContent = char;
            currentSlot.classList.add("filled");
          }

          state.userCollectedLetters.push(char);
          state.currentSequenceIndex++;
          l3Error.style.color = "#2ed573";
          l3Error.textContent = `Lettre correcte ! Continuer...`;

          if (state.currentSequenceIndex === 9) {
            l3Error.textContent = "✨ MOT RECONSTITUÉ ! CLÉ 3 DÉBLOQUÉE ! ✨";
            unlockKey(3);
            if (movingLettersInterval) clearInterval(movingLettersInterval);

            setTimeout(() => {
              switchToLevel(4);
              initLevel4Caesar();
            }, 1200);
          }
        } else if (!letterBtn.classList.contains("clicked")) {
          l3Error.style.color = "#ff477e";
          l3Error.textContent = `Lettre incorrecte ! Réessaie !`;
        }
      });

      lettersScatterField.appendChild(letterBtn);
    });

    if (movingLettersInterval) clearInterval(movingLettersInterval);
    movingLettersInterval = setInterval(() => {
      letterNodes.forEach(item => {
        if (item.el.classList.contains("clicked")) return;

        item.x += item.vx;
        item.y += item.vy;

        if (item.x < 3 || item.x > 88) item.vx *= -1;
        if (item.y < 3 || item.y > 85) item.vy *= -1;

        item.el.style.left = `${item.x}%`;
        item.el.style.top = `${item.y}%`;
      });
    }, 50);
  }

  btnResetCipher?.addEventListener("click", () => {
    initLevel3Letters();
  });

  // ════════════════════════════════════════════════════════════════════════
  // LEVEL 4: CAESAR CIPHER WHEEL (MOT: ANNIVERSAIRE, CRAN 18)
  // ════════════════════════════════════════════════════════════════════════
  const caesarShiftSlider = document.getElementById("caesar-shift-slider");
  const caesarShiftVal = document.getElementById("caesar-shift-val");
  const caesarOutput = document.getElementById("caesar-output");
  const btnValidateL4 = document.getElementById("btn-validate-l4");
  const l4Error = document.getElementById("l4-error");

  const caesarEncrypted = "SFFANWJKSAJW";

  function initLevel4Caesar() {
    if (!caesarShiftSlider) return;

    // Real-time visual feedback while dragging
    caesarShiftSlider.addEventListener("input", () => {
      const shift = parseInt(caesarShiftSlider.value);
      caesarShiftVal.textContent = shift;

      let decoded = "";
      for (let i = 0; i < caesarEncrypted.length; i++) {
        const code = caesarEncrypted.charCodeAt(i);
        let newCode = code - shift;
        if (newCode < 65) newCode += 26;
        decoded += String.fromCharCode(newCode);
      }

      caesarOutput.textContent = decoded;
      l4Error.textContent = "";
      btnValidateL4.disabled = true;
    });

    // Validation ONLY when slider handle is released (mouse/touch release)
    caesarShiftSlider.addEventListener("change", () => {
      const shift = parseInt(caesarShiftSlider.value);
      let decoded = "";
      for (let i = 0; i < caesarEncrypted.length; i++) {
        const code = caesarEncrypted.charCodeAt(i);
        let newCode = code - shift;
        if (newCode < 65) newCode += 26;
        decoded += String.fromCharCode(newCode);
      }

      if (shift === 18 && decoded === "ANNIVERSAIRE") {
        l4Error.style.color = "#2ed573";
        l4Error.textContent = "✨ CODE DÉCRYPTÉ : ANNIVERSAIRE ! CLÉ 4 DÉBLOQUÉE ! ✨";
        unlockKey(4);
        btnValidateL4.disabled = false;
      } else {
        l4Error.style.color = "#ff477e";
        l4Error.textContent = "Positions des rouages incorrectes. Continue à chercher !";
        btnValidateL4.disabled = true;
      }
    });
  }

  btnValidateL4?.addEventListener("click", () => {
    switchToLevel(5);
    initLevel5Canvas();
  });

  // ════════════════════════════════════════════════════════════════════════
  // LEVEL 5: DUAL WAVE FREQUENCY TUNER & GPS CITY TERMINAL (PARIS)
  // ════════════════════════════════════════════════════════════════════════
  const waveCanvas = document.getElementById("wave-canvas");
  const ctx = waveCanvas ? waveCanvas.getContext("2d") : null;
  const sliderLat = document.getElementById("slider-lat");
  const sliderLong = document.getElementById("slider-long");
  const signalStatus = document.getElementById("signal-status");
  const coordsVal = document.getElementById("coords-val");
  const gpsTerminalWrap = document.getElementById("gps-terminal-wrap");
  const cityTargetInput = document.getElementById("city-target-input");
  const btnValidateCity = document.getElementById("btn-validate-city");
  const l5Error = document.getElementById("l5-error");

  let waveAnimationId = null;
  let waveTime = 0;
  let isWaveSliderReleasedValid = false;

  function initLevel5Canvas() {
    if (!ctx || !waveCanvas) return;

    function checkWaveReleaseValidation() {
      const latVal = parseInt(sliderLat.value);
      const longVal = parseInt(sliderLong.value);
      const diffLat = Math.abs(latVal - state.targetLat);
      const diffLong = Math.abs(longVal - state.targetLong);

      if (diffLat <= 2 && diffLong <= 2) {
        state.signalLocked = true;
        signalStatus.textContent = "SIGNAL VERROUILLÉ";
        signalStatus.classList.add("locked");
        coordsVal.textContent = "48.8566° N , 2.3522° E";
        gpsTerminalWrap.classList.remove("hidden");
      } else {
        state.signalLocked = false;
        signalStatus.textContent = "RECHERCHE DU SIGNAL...";
        signalStatus.classList.remove("locked");
        coordsVal.textContent = "??.????° N , ?.????° E";
        gpsTerminalWrap.classList.add("hidden");
      }
    }

    sliderLat?.addEventListener("change", checkWaveReleaseValidation);
    sliderLong?.addEventListener("change", checkWaveReleaseValidation);

    function drawWaves() {
      waveTime += 0.05;
      const width = waveCanvas.width;
      const height = waveCanvas.height;

      ctx.clearRect(0, 0, width, height);

      ctx.strokeStyle = "rgba(255, 126, 179, 0.08)";
      ctx.lineWidth = 1;
      for (let x = 0; x < width; x += 30) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += 30) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      const targetFreq = 0.038;
      const targetAmp = 35;

      ctx.beginPath();
      ctx.strokeStyle = "rgba(255, 215, 0, 0.75)";
      ctx.lineWidth = 2.5;
      for (let x = 0; x < width; x++) {
        const y = (height / 2) + Math.sin(x * targetFreq + waveTime) * targetAmp;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      const latVal = parseInt(sliderLat.value);
      const longVal = parseInt(sliderLong.value);

      const userFreq = 0.01 + (latVal / 100) * 0.056;
      const userAmp = 10 + (longVal / 100) * 35;

      const diffLat = Math.abs(latVal - state.targetLat);
      const diffLong = Math.abs(longVal - state.targetLong);

      const isExactMatch = (diffLat <= 2 && diffLong <= 2);

      ctx.beginPath();
      ctx.strokeStyle = (state.signalLocked && isExactMatch) ? "#2ed573" : "rgba(255, 126, 179, 0.85)";
      ctx.lineWidth = (state.signalLocked && isExactMatch) ? 3.5 : 2.5;

      for (let x = 0; x < width; x++) {
        const y = (height / 2) + Math.sin(x * userFreq + waveTime) * userAmp;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      if (!state.signalLocked) {
        const signalPct = Math.max(0, Math.min(100, Math.round(100 - (diffLat * 2.5 + diffLong * 2.5))));
        signalStatus.textContent = `SIGNAL : ${signalPct}%`;
      }

      waveAnimationId = requestAnimationFrame(drawWaves);
    }

    if (waveAnimationId) cancelAnimationFrame(waveAnimationId);
    drawWaves();
  }

  btnValidateCity?.addEventListener("click", () => {
    const userCity = cleanStr(cityTargetInput.value);
    
    if (userCity === "paris" || userCity.includes("paris")) {
      l5Error.style.color = "#2ed573";
      l5Error.textContent = "✨ ZONE VERROUILLÉE ! CLÉ 5 DÉBLOQUÉE ! ✨";
      unlockKey(5);
      btnValidateCity.textContent = "ZONE CONFIRMÉE 📡";
      btnValidateCity.disabled = true;

      setTimeout(() => {
        switchToLevel(6);
        initLevel6Switches();
      }, 1200);
    } else {
      l5Error.style.color = "#ff477e";
      l5Error.textContent = "Nom de ville incorrect pour ces coordonnées GPS ! Réessaie.";
    }
  });

  // ════════════════════════════════════════════════════════════════════════
  // LEVEL 6: LIGHTS OUT CRYSTAL SWITCHES (7 CRISTAUX)
  // ════════════════════════════════════════════════════════════════════════
  const switchesContainer = document.getElementById("switches-container");
  const btnResetSwitches = document.getElementById("btn-reset-switches");
  const btnValidateL6 = document.getElementById("btn-validate-l6");
  const l6Error = document.getElementById("l6-error");

  const switchStates = [false, true, false, true, false, true, false];

  function initLevel6Switches() {
    if (!switchesContainer) return;
    renderSwitches();
  }

  function renderSwitches() {
    switchesContainer.innerHTML = "";
    switchStates.forEach((stateVal, idx) => {
      const swBtn = document.createElement("div");
      swBtn.className = `crystal-switch ${stateVal ? "active" : ""}`;
      swBtn.textContent = stateVal ? "💎" : "🔮";

      swBtn.addEventListener("click", () => {
        switchStates[idx] = !switchStates[idx];
        if (idx > 0) switchStates[idx - 1] = !switchStates[idx - 1];
        if (idx < 6) switchStates[idx + 1] = !switchStates[idx + 1];

        renderSwitches();
        checkSwitchesWin();
      });

      switchesContainer.appendChild(swBtn);
    });
  }

  function checkSwitchesWin() {
    const allOn = switchStates.every(Boolean);
    if (allOn) {
      l6Error.style.color = "#2ed573";
      l6Error.textContent = "✨ TOUS LES 7 CRISTAUX RECHARGÉS ! CLÉ 6 DÉBLOQUÉE ! ✨";
      unlockKey(6);
      btnValidateL6.disabled = false;
    } else {
      l6Error.textContent = "";
      btnValidateL6.disabled = true;
    }
  }

  btnResetSwitches?.addEventListener("click", () => {
    switchStates[0] = false;
    switchStates[1] = true;
    switchStates[2] = false;
    switchStates[3] = true;
    switchStates[4] = false;
    switchStates[5] = true;
    switchStates[6] = false;
    renderSwitches();
    checkSwitchesWin();
  });

  btnValidateL6?.addEventListener("click", () => {
    switchToLevel(7);
    initLevel7Chaos();
  });

  // ════════════════════════════════════════════════════════════════════════
  // LEVEL 7: ULTRA HIGH DENSITY CHAOS FIELD (180 FAST SHAPES)
  // ════════════════════════════════════════════════════════════════════════
  const chaosField = document.getElementById("chaos-field");
  const l7Error = document.getElementById("l7-error");
  let chaosAnimationId = null;

  function initLevel7Chaos() {
    if (!chaosField) return;
    chaosField.innerHTML = "";
    l7Error.textContent = "";

    const dummyIcons = ["❖", "✦", "⬡", "▲", "◆", "✴", "✖", "◈", "◇", "⬢", "★", "✨", "⭐", "🌟"];
    const nodes = [];

    const targetNode = document.createElement("div");
    targetNode.className = "floating-node target";
    targetNode.textContent = "⭐";
    chaosField.appendChild(targetNode);

    const targetObj = {
      el: targetNode,
      x: Math.random() * 80 + 10,
      y: Math.random() * 70 + 10,
      vx: (Math.random() > 0.5 ? 1 : -1) * (Math.random() * 0.315 + 0.21),
      vy: (Math.random() > 0.5 ? 1 : -1) * (Math.random() * 0.315 + 0.21),
      isTarget: true
    };
    nodes.push(targetObj);

    targetNode.addEventListener("click", (e) => {
      e.stopPropagation();
      unlockKey(7);
      l7Error.style.color = "#2ed573";
      l7Error.textContent = "✨ CLÉ 7 DÉBLOQUÉE ! ✨";
      
      if (chaosAnimationId) cancelAnimationFrame(chaosAnimationId);

      document.querySelectorAll("#chaos-field .floating-node").forEach(node => {
        node.style.transition = "all 0.5s ease";
        node.style.opacity = "0.1";
      });
      targetNode.style.opacity = "1";
      targetNode.style.transform = "scale(2.8)";

      setTimeout(() => {
        switchToLevel(8);
      }, 1200);
    });

    for (let i = 0; i < 175; i++) {
      const node = document.createElement("div");
      node.className = "floating-node";
      node.textContent = dummyIcons[i % dummyIcons.length];

      const zIdx = Math.floor(Math.random() * 35) + 5;
      node.style.zIndex = zIdx;

      if (i % 4 === 0) {
        node.style.color = "rgba(255, 215, 0, 0.85)";
      } else if (i % 3 === 0) {
        node.style.color = "rgba(255, 126, 179, 0.7)";
      } else {
        node.style.color = "rgba(255, 255, 255, 0.5)";
      }

      node.style.fontSize = `${Math.random() * 18 + 12}px`;
      chaosField.appendChild(node);

      const nodeObj = {
        el: node,
        x: Math.random() * 92 + 2,
        y: Math.random() * 90 + 2,
        vx: (Math.random() > 0.5 ? 1 : -1) * (Math.random() * 0.385 + 0.175),
        vy: (Math.random() > 0.5 ? 1 : -1) * (Math.random() * 0.385 + 0.175),
        isTarget: false
      };

      node.addEventListener("click", () => {
        l7Error.style.color = "#ff477e";
        l7Error.textContent = "Symbole incorrect !";
      });

      nodes.push(nodeObj);
    }

    function updateChaosFrame() {
      nodes.forEach(n => {
        n.x += n.vx;
        n.y += n.vy;

        if (n.x <= 2 || n.x >= 94) n.vx *= -1;
        if (n.y <= 2 || n.y >= 92) n.vy *= -1;

        n.el.style.left = `${n.x}%`;
        n.el.style.top = `${n.y}%`;
      });

      if (!state.unlockedKeys[6]) {
        chaosAnimationId = requestAnimationFrame(updateChaosFrame);
      }
    }

    if (chaosAnimationId) cancelAnimationFrame(chaosAnimationId);
    updateChaosFrame();
  }

  // ════════════════════════════════════════════════════════════════════════
  // LEVEL 8 & GRAND DISNEY REVEAL
  // ════════════════════════════════════════════════════════════════════════
  const btnGrandReveal = document.getElementById("btn-grand-reveal");
  const finalGuessInput = document.getElementById("final-guess-input");
  const disneyRevealScreen = document.getElementById("disney-reveal-screen");
  const gameContainer = document.getElementById("game-container");
  const btnReplay = document.getElementById("btn-replay");

  btnGrandReveal?.addEventListener("click", () => {
    const val = cleanStr(finalGuessInput?.value);
    
    if (!val.includes("disney")) {
      alert("❌ Réponse incorrecte ! Concentre-toi bien sur la destination...");
      return;
    }

    btnGrandReveal.disabled = true;
    btnGrandReveal.textContent = "INSERTION DES 8 CLÉS D'OR... 🗝️";

    const vaultRing = document.getElementById("vault-ring");
    const vaultCenterLock = document.getElementById("vault-center-lock");

    // Animate 8 keys inserting sequentially
    for (let i = 1; i <= 8; i++) {
      setTimeout(() => {
        unlockKey(i);
        const vkEl = document.getElementById(`vk${i}`);
        if (vkEl) {
          vkEl.classList.add("inserting");
        }
      }, i * 220);
    }

    // Spin ring and unlock central padlock
    setTimeout(() => {
      if (vaultRing) vaultRing.classList.add("unlocking");
      if (vaultCenterLock) {
        vaultCenterLock.textContent = "🔓";
        vaultCenterLock.style.transform = "scale(1.5)";
      }
    }, 2000);

    // Grand reveal transition
    setTimeout(() => {
      startFireworksAndConfetti();
      gameContainer.style.opacity = "0";
      setTimeout(() => {
        gameContainer.style.display = "none";
        disneyRevealScreen.classList.remove("hidden");
      }, 600);
    }, 3200);
  });

  btnReplay?.addEventListener("click", () => {
    location.reload();
  });

  // Global helper & Shift+F shortcut to preview the final reveal screen instantly
  window.showFinalReveal = function() {
    const gc = document.getElementById("game-container");
    const drs = document.getElementById("disney-reveal-screen");
    if (gc) gc.style.display = "none";
    if (drs) drs.classList.remove("hidden");
    startFireworksAndConfetti();
  };

  document.addEventListener("keydown", (e) => {
    if (e.shiftKey && (e.key === "F" || e.key === "f")) {
      window.showFinalReveal();
    }
  });

  if (window.location.search.includes("final=true")) {
    setTimeout(window.showFinalReveal, 200);
  }

  // ── FIREWORKS & CONFETTI CANVAS ANIMATION ────────────────────────────────
  function startFireworksAndConfetti() {
    const canvas = document.getElementById("fireworks-canvas");
    if (!canvas) return;
    const fCtx = canvas.getContext("2d");
    
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = [];
    const colors = ["#ffd700", "#ff4757", "#00e5ff", "#ffffff", "#a855f7", "#2ed573", "#ff7f50"];

    for (let i = 0; i < 150; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * -canvas.height,
        vx: (Math.random() - 0.5) * 3,
        vy: Math.random() * 4 + 2,
        size: Math.random() * 8 + 4,
        color: colors[Math.floor(Math.random() * colors.length)],
        rotation: Math.random() * 360,
        rSpeed: (Math.random() - 0.5) * 10,
        type: "confetti"
      });
    }

    function createExplosion(x, y) {
      for (let i = 0; i < 70; i++) {
        const angle = Math.random() * Math.PI * 2;
        const speed = Math.random() * 6 + 2;
        particles.push({
          x: x,
          y: y,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed,
          color: colors[Math.floor(Math.random() * colors.length)],
          alpha: 1,
          size: Math.random() * 4 + 2,
          type: "spark"
        });
      }
    }

    setInterval(() => {
      createExplosion(
        Math.random() * canvas.width,
        Math.random() * canvas.height * 0.5
      );
    }, 450);

    function render() {
      fCtx.fillStyle = "rgba(7, 10, 20, 0.25)";
      fCtx.fillRect(0, 0, canvas.width, canvas.height);

      particles.forEach((p, idx) => {
        if (p.type === "confetti") {
          p.x += p.vx;
          p.y += p.vy;
          p.rotation += p.rSpeed;

          if (p.y > canvas.height) {
            p.y = -10;
            p.x = Math.random() * canvas.width;
          }

          fCtx.save();
          fCtx.translate(p.x, p.y);
          fCtx.rotate((p.rotation * Math.PI) / 180);
          fCtx.fillStyle = p.color;
          fCtx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
          fCtx.restore();
        } else {
          p.x += p.vx;
          p.y += p.vy;
          p.vy += 0.05;
          p.alpha -= 0.015;

          fCtx.beginPath();
          fCtx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          fCtx.fillStyle = p.color;
          fCtx.globalAlpha = Math.max(0, p.alpha);
          fCtx.fill();

          if (p.alpha <= 0) {
            particles.splice(idx, 1);
          }
        }
      });

      requestAnimationFrame(render);
    }

    render();
  }

});
