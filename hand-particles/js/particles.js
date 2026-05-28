const PARTICLE_COUNT = 1200;
const MIN_PARTICLES = 400;
const MAX_PARTICLES = 2000;
const SPHERE_RADIUS = 130;
const RING_INNER = 80;
const RING_OUTER = 280;
const FPS_SAMPLE_INTERVAL = 2000;
const FPS_LOW_THRESHOLD = 30;
const FPS_HIGH_THRESHOLD = 55;
const STAR_COUNT = 150;
const PI2 = Math.PI * 2;

// 粒子物理参数
const PARTICLE_FRICTION = 0.9;
const SCATTER_SPEED_MIN = 300;
const SCATTER_SPEED_MAX = 600;
const SCATTER_DURATION = 1.8;
const SCATTER_DECAY_RATE = 2.5;
const SCATTER_FORM_DELAY = 0.3;
const SCATTER_FORM_DURATION = 1.2;

// Stream gesture physics
const STREAM_SPEED = 400;
const DUAL_STREAM_SPREAD = 0.4; // radians between two peace streams

// Object pool limits
const POOL_MAX = 2500;

// ── Pre-computed shape paths ────────────────────────────────────────────────
function _starPath(spikes, outerR, innerR) {
  const p = new Path2D();
  for (let i = 0; i < spikes * 2; i++) {
    const r = i % 2 === 0 ? outerR : innerR;
    const a = (i / (spikes * 2)) * PI2 - Math.PI / 2;
    if (i === 0) p.moveTo(Math.cos(a) * r, Math.sin(a) * r);
    else p.lineTo(Math.cos(a) * r, Math.sin(a) * r);
  }
  p.closePath();
  return p;
}

function _heartPath() {
  const p = new Path2D();
  p.moveTo(0, -0.35);
  p.bezierCurveTo(-0.55, -1.05, -1.1, -0.35, -0.55, 0.2);
  p.lineTo(0, 0.95);
  p.lineTo(0.55, 0.2);
  p.bezierCurveTo(1.1, -0.35, 0.55, -1.05, 0, -0.35);
  p.closePath();
  return p;
}

function _diamondPath() {
  const p = new Path2D();
  p.moveTo(0, -1);
  p.lineTo(0.6, 0);
  p.lineTo(0, 1);
  p.lineTo(-0.6, 0);
  p.closePath();
  return p;
}

function _customPath() {
  // 8-point star with alternating spike lengths for a cosmic shape
  const p = new Path2D();
  const pts = 8;
  const lens = [1, 0.35, 0.85, 0.35, 1, 0.35, 0.85, 0.35];
  for (let i = 0; i < pts; i++) {
    const a = (i / pts) * PI2 - Math.PI / 2;
    const r = lens[i];
    if (i === 0) p.moveTo(Math.cos(a) * r, Math.sin(a) * r);
    else p.lineTo(Math.cos(a) * r, Math.sin(a) * r);
  }
  p.closePath();
  return p;
}

const SHAPE_PATHS = {
  line: null,
  star: _starPath(5, 1, 0.4),
  heart: _heartPath(),
  diamond: _diamondPath(),
  custom: _customPath(),
};

// ── Object Pool ─────────────────────────────────────────────────────────────
const _pool = [];

function _poolGet() {
  return _pool.length > 0 ? _pool.pop() : null;
}

function _poolReturn(obj) {
  if (_pool.length < POOL_MAX) _pool.push(obj);
}

// ── ParticleSystem ──────────────────────────────────────────────────────────
export class ParticleSystem {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.particles = [];
    this.stars = [];
    this.time = 0;
    this.targetX = 0;
    this.targetY = 0;
    this._prevTargetX = 0;
    this._prevTargetY = 0;
    this._handVx = 0;
    this._handVy = 0;
    this.openness = 0;
    this._targetOpenness = 0.5;
    this._hueOffset = 0;
    this.colorMode = 'multi';
    this.gesture = 'none';
    this._scatterTime = 0;
    this._scatterActive = false;
    this._frameCount = 0;
    this._lastFPSSample = performance.now();
    this._currentFPS = 60;
    this._targetCount = PARTICLE_COUNT;
    this._shapeType = 'line';
    this._qualityScale = 1;        // 0.5..1 adaptive quality
    this._renderPasses = 6;         // number of glow passes (adaptive)
    this._pointAngle = -Math.PI / 2; // direction of pointing gesture
    this._setupDPI();
    this._initStars();
    this._initParticles();
    this._vignette = null;

    // Effect toggles
    this.effects = {
      trails: true,
      glow: true,
      scatterFlash: true,
    };
  }

  // ── public API ──────────────────────────────────────────────────────────
  setTargetOpenness(val) { this._targetOpenness = val; }
  getTargetOpenness() { return this._targetOpenness; }
  setShape(type) { if (SHAPE_PATHS.hasOwnProperty(type)) this._shapeType = type; }
  getShape() { return this._shapeType; }

  setParticleCount(count) {
    this._targetCount = Math.max(MIN_PARTICLES, Math.min(MAX_PARTICLES, Math.round(count)));
    if (this._targetCount > this.particles.length) this._addParticles();
    else if (this._targetCount < this.particles.length) this._trimParticles();
  }

  getParticleCount() { return this._targetCount; }
  getFPS() { return Math.round(this._currentFPS); }

  // ── internal setup ──────────────────────────────────────────────────────
  _setupDPI() {
    const dpr = window.devicePixelRatio || 1;
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.canvas.width = w * dpr;
    this.canvas.height = h * dpr;
    this.canvas.style.width = w + 'px';
    this.canvas.style.height = h + 'px';
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.w = w;
    this.h = h;
    this.targetX = w / 2;
    this.targetY = h / 2;
  }

  _initStars() {
    this.stars = [];
    for (let i = 0; i < STAR_COUNT; i++) {
      this.stars.push({
        x: Math.random() * this.w,
        y: Math.random() * this.h,
        size: 0.3 + Math.random() * 1.2,
        alpha: 0.2 + Math.random() * 0.5,
        twinkleSpeed: 0.5 + Math.random() * 2,
        twinklePhase: Math.random() * PI2,
        driftX: (Math.random() - 0.5) * 0.1,
        driftY: (Math.random() - 0.5) * 0.1,
      });
    }
  }

  _getVignette() {
    if (this._vignette && this._vignette.w === this.w && this._vignette.h === this.h) {
      return this._vignette.grad;
    }
    const cx = this.w / 2;
    const cy = this.h / 2;
    const r = Math.hypot(cx, cy);
    const grad = this.ctx.createRadialGradient(cx, cy, r * 0.3, cx, cy, r);
    grad.addColorStop(0, 'transparent');
    grad.addColorStop(0.7, 'rgba(0,0,0,0.2)');
    grad.addColorStop(1, 'rgba(0,0,0,0.6)');
    this._vignette = { grad, w: this.w, h: this.h };
    return grad;
  }

  _initParticles() {
    const cx = this.w / 2;
    const cy = this.h / 2;
    // Return existing particles to pool
    for (const p of this.particles) _poolReturn(p);
    this.particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const goldenAngle = i * 2.399963;
      const r = Math.sqrt(i / PARTICLE_COUNT) * Math.max(this.w, this.h) * 0.4;
      this.particles.push(this._createParticle(i, cx + Math.cos(goldenAngle) * r, cy + Math.sin(goldenAngle) * r, goldenAngle));
    }
  }

  _createParticle(i, x, y, angle) {
    // Try to reuse from pool
    const p = _poolGet() || {};
    p.x = x; p.y = y; p.vx = 0; p.vy = 0; p.angle = angle;
    p.baseHue = (i / PARTICLE_COUNT) * 360;
    p.size = 1.4 + Math.random() * 1.6;
    p.baseAlpha = 0.8 + Math.random() * 0.2;
    p.ringAngle = Math.random() * PI2;
    p.ringRadius = RING_INNER + Math.random() * (RING_OUTER - RING_INNER);
    p.ringSpeed = (0.4 + Math.random() * 0.6) * (Math.random() > 0.5 ? 1 : -1);
    p.ringPhase = Math.random() * PI2;
    p.spherePhase = Math.random() * PI2;
    p.sphereTheta = Math.acos(2 * Math.random() - 1);
    p.sphereSpeed = 0.3 + Math.random() * 0.6;
    p.sphereRadius = 20 + Math.random() * (SPHERE_RADIUS - 20);
    p.scatterAngle = 0; p.scatterSpeed = 0;
    p._cos = 0; p._sin = 0; p._speed = 0; p._depthScale = 1; p._renderIdx = 0;
    return p;
  }

  setTarget(x, y) {
    this._prevTargetX = this.targetX;
    this._prevTargetY = this.targetY;
    this.targetX = x;
    this.targetY = y;
  }
  setOpenness(val) { this.openness = val; }

  setGesture(g) {
    if (g === 'sword' && this.gesture !== 'sword') this._triggerScatter();
    this.gesture = g;
  }

  setPointAngle(a) { this._pointAngle = a; }

  _triggerScatter() {
    this._scatterActive = true;
    this._scatterTime = 0;
    for (const p of this.particles) {
      p.scatterAngle = Math.random() * PI2;
      p.scatterSpeed = SCATTER_SPEED_MIN + Math.random() * (SCATTER_SPEED_MAX - SCATTER_SPEED_MIN);
    }
  }

  // ── update loop ─────────────────────────────────────────────────────────
  update(dt) {
    this.time += dt;
    this._hueOffset = (this._hueOffset + dt * 10) % 360;
    const cx = this.targetX;
    const cy = this.targetY;

    // Hand velocity for stream direction
    this._handVx = (this.targetX - this._prevTargetX) / Math.max(dt, 0.001);
    this._handVy = (this.targetY - this._prevTargetY) / Math.max(dt, 0.001);

    if (this._scatterActive) {
      this._scatterTime += dt;
      if (this._scatterTime > SCATTER_DURATION) this._scatterActive = false;
    }

    // Drift background stars
    for (const s of this.stars) {
      s.x += s.driftX;
      s.y += s.driftY;
      if (s.x < 0) s.x = this.w;
      else if (s.x > this.w) s.x = 0;
      if (s.y < 0) s.y = this.h;
      else if (s.y > this.h) s.y = 0;
    }

    const scatterActive = this._scatterActive;
    const scatterSword = scatterActive && this.gesture === 'sword';
    const scatterTime = this._scatterTime;
    const openness = this.openness;
    const time = this.time;
    const gesture = this.gesture;

    // Compute stream direction from hand velocity or default
    const handSpeed = Math.hypot(this._handVx, this._handVy);
    let streamDir = this._pointAngle;
    if (handSpeed > 50) {
      streamDir = Math.atan2(this._handVy, this._handVx);
    }

    for (const p of this.particles) {
      let tx, ty;

      if (scatterSword) {
        // Sword scatter effect (existing)
        const decay = Math.exp(-scatterTime * SCATTER_DECAY_RATE);
        const outward = p.scatterSpeed * decay;
        tx = p.x + Math.cos(p.scatterAngle) * outward * dt;
        ty = p.y + Math.sin(p.scatterAngle) * outward * dt;
        if (scatterTime > SCATTER_FORM_DELAY) {
          const formStr = Math.min((scatterTime - SCATTER_FORM_DELAY) / SCATTER_FORM_DURATION, 1);
          const bladeLen = 250 + p.sphereRadius * 0.6;
          const spread = (1 - formStr) * 60 + p.size * 2;
          const along = (p.baseHue / 360 - 0.5) * bladeLen;
          const perp = Math.sin(p.ringAngle) * spread;
          const ba = -Math.PI / 2;
          const bx = cx + Math.cos(ba) * along - Math.sin(ba) * perp;
          const by = cy + Math.sin(ba) * along + Math.cos(ba) * perp;
          tx += (bx - p.x) * 0.06 * formStr;
          ty += (by - p.y) * 0.06 * formStr;
        }
        p.vx += (tx - p.x) * 0.1;
        p.vy += (ty - p.y) * 0.1;

      } else if (gesture === 'point') {
        // Pointing: direct particle stream in pointing direction
        const idx = p._renderIdx || 0;
        const offset = ((idx % 30) - 15) * 3; // spread perpendicular to stream
        const perpAngle = streamDir + Math.PI / 2;
        const baseX = cx + Math.cos(perpAngle) * offset;
        const baseY = cy + Math.sin(perpAngle) * offset;
        // Particles flow along stream direction
        const flowPhase = (time * STREAM_SPEED + p.ringPhase * 50) % 400;
        tx = baseX + Math.cos(streamDir) * (flowPhase - 200);
        ty = baseY + Math.sin(streamDir) * (flowPhase - 200);
        p.vx += (tx - p.x) * 0.06;
        p.vy += (ty - p.y) * 0.06;

      } else if (gesture === 'peace') {
        // Peace sign: dual particle streams (V-shape)
        const idx = p._renderIdx || 0;
        const streamId = idx % 2; // 0 or 1
        const angle1 = streamDir - DUAL_STREAM_SPREAD;
        const angle2 = streamDir + DUAL_STREAM_SPREAD;
        const sAngle = streamId === 0 ? angle1 : angle2;
        const offset = ((idx % 20) - 10) * 3;
        const perpAngle = sAngle + Math.PI / 2;
        const baseX = cx + Math.cos(perpAngle) * offset;
        const baseY = cy + Math.sin(perpAngle) * offset;
        const flowPhase = (time * STREAM_SPEED + p.ringPhase * 50) % 400;
        tx = baseX + Math.cos(sAngle) * (flowPhase - 200);
        ty = baseY + Math.sin(sAngle) * (flowPhase - 200);
        p.vx += (tx - p.x) * 0.06;
        p.vy += (ty - p.y) * 0.06;

      } else if (openness > 0.5) {
        // Ring / open palm attraction
        const strength = (openness - 0.5) * 2;
        p.ringAngle += p.ringSpeed * dt * 1.5;
        const wobble = Math.sin(time * 0.8 + p.ringPhase) * 20 * strength;
        tx = cx + Math.cos(p.ringAngle) * p.ringRadius;
        ty = cy + Math.sin(p.ringAngle) * p.ringRadius * 0.4 + wobble;
        p.vx += (tx - p.x) * 0.025 * strength;
        p.vy += (ty - p.y) * 0.025 * strength;

      } else {
        // Sphere / fist compact
        const strength = (0.5 - openness) * 2;
        p.spherePhase += p.sphereSpeed * dt;
        const r = p.sphereRadius * (1 - strength * 0.6);
        const sp = Math.sin(p.spherePhase);
        const cp = Math.cos(p.spherePhase);
        const st = Math.sin(p.sphereTheta);
        const ct = Math.cos(p.sphereTheta);
        tx = cx + st * cp * r;
        ty = cy + st * sp * r * 0.6;
        const tz = ct * r;
        p._depthScale = 0.5 + (tz + p.sphereRadius) / (p.sphereRadius * 2) * 0.5;
        p.vx += (tx - p.x) * 0.035 * strength;
        p.vy += (ty - p.y) * 0.035 * strength;
      }

      p.vx *= PARTICLE_FRICTION;
      p.vy *= PARTICLE_FRICTION;
      p.x += p.vx;
      p.y += p.vy;

      const speed = Math.hypot(p.vx, p.vy);
      p._speed = speed;
      if (speed > 0.5) {
        const targetAngle = Math.atan2(p.vy, p.vx);
        let diff = targetAngle - p.angle;
        if (diff > Math.PI) diff -= PI2;
        else if (diff < -Math.PI) diff += PI2;
        p.angle += diff * 0.15;
      }
      p._cos = Math.cos(p.angle);
      p._sin = Math.sin(p.angle);
    }

    // ── Adaptive quality (FPS) ──────────────────────────────────────────
    this._frameCount++;
    const now = performance.now();
    if (now - this._lastFPSSample > FPS_SAMPLE_INTERVAL) {
      this._currentFPS = this._frameCount / ((now - this._lastFPSSample) / 1000);
      this._frameCount = 0;
      this._lastFPSSample = now;

      // Adjust particle count
      if (this._currentFPS < FPS_LOW_THRESHOLD && this._targetCount > MIN_PARTICLES) {
        this._targetCount = Math.max(MIN_PARTICLES, this._targetCount - 200);
        this._trimParticles();
      } else if (this._currentFPS > FPS_HIGH_THRESHOLD && this._targetCount < PARTICLE_COUNT) {
        this._targetCount = Math.min(PARTICLE_COUNT, this._targetCount + 100);
        this._addParticles();
      }

      // Adjust render quality
      if (this._currentFPS < 25) {
        this._qualityScale = 0.5;
        this._renderPasses = 3;
      } else if (this._currentFPS < 40) {
        this._qualityScale = 0.75;
        this._renderPasses = 4;
      } else {
        this._qualityScale = 1;
        this._renderPasses = 6;
      }
    }
  }

  _trimParticles() {
    while (this.particles.length > this._targetCount) {
      _poolReturn(this.particles.pop());
    }
  }

  _addParticles() {
    const cx = this.w / 2, cy = this.h / 2;
    while (this.particles.length < this._targetCount) {
      const i = this.particles.length;
      const goldenAngle = i * 2.399963;
      const r = Math.sqrt(i / PARTICLE_COUNT) * Math.max(this.w, this.h) * 0.4;
      this.particles.push(this._createParticle(i, cx + Math.cos(goldenAngle) * r, cy + Math.sin(goldenAngle) * r, goldenAngle));
    }
  }

  // ── draw ────────────────────────────────────────────────────────────────
  draw() {
    const ctx = this.ctx;
    const w = this.w;
    const h = this.h;
    const shape = this._shapeType;
    const isLineShape = shape === 'line';

    ctx.fillStyle = '#050508';
    ctx.fillRect(0, 0, w, h);

    // Background stars
    for (const s of this.stars) {
      const twinkle = 0.5 + 0.5 * Math.sin(this.time * s.twinkleSpeed + s.twinklePhase);
      ctx.beginPath();
      ctx.fillStyle = `rgba(200,210,255,${(s.alpha * twinkle).toFixed(2)})`;
      ctx.arc(s.x, s.y, s.size, 0, PI2);
      ctx.fill();
    }

    // Fade trail (skip if trails disabled)
    if (this.effects.trails) {
      ctx.fillStyle = 'rgba(5,5,8,0.18)';
      ctx.fillRect(0, 0, w, h);
    }

    // Batch draw particles — group by hue bucket
    const particles = this.particles;
    const hueOffset = this._hueOffset;
    const colorMode = this.colorMode;
    const time = this.time;
    const qualityScale = this._qualityScale;
    const renderPasses = this._renderPasses;

    const buckets = this._hueBuckets || (this._hueBuckets = Array.from({ length: 36 }, () => []));
    for (let i = 0; i < 36; i++) buckets[i].length = 0;

    for (const p of particles) {
      const hue = this._computeHue(p, colorMode, hueOffset, time);
      const bucket = Math.floor(((hue % 360 + 360) % 360) / 10);
      if (bucket >= 0 && bucket < 36) buckets[bucket].push(p);
    }

    ctx.lineCap = 'round';

    // Pre-compute per-particle render data
    const renderData = this._renderData || (this._renderData = new Array(MAX_PARTICLES));
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p._renderIdx = i;
      const depth = p._depthScale;
      const speedFactor = Math.min(p._speed * 0.25, 1);
      const alpha = p.baseAlpha * depth * (0.4 + speedFactor * 0.6);
      const sz = p.size * depth;
      const bladeLen = (5 + speedFactor * 16) * qualityScale;
      const cos = p._cos;
      const sin = p._sin;
      renderData[i] = {
        x1: p.x - cos * bladeLen * 0.4,
        y1: p.y - sin * bladeLen * 0.4,
        x2: p.x + cos * bladeLen,
        y2: p.y + sin * bladeLen,
        mx: p.x + cos * bladeLen * 0.2,
        my: p.y + sin * bladeLen * 0.2,
        alpha, sz,
      };
    }

    // ── Draw each hue bucket ─────────────────────────────────────────────
    if (isLineShape) {
      this._drawLineParticles(ctx, buckets, renderData, renderPasses, hueOffset, time, qualityScale);
    } else {
      this._drawShapeParticles(ctx, buckets, renderData, shape, hueOffset, time, qualityScale);
    }

    // Vignette
    ctx.fillStyle = this._getVignette();
    ctx.fillRect(0, 0, w, h);

    // Dark void center for black hole
    if (this.openness > 0.3 && this.gesture !== 'sword' && this.gesture !== 'point' && this.gesture !== 'peace') {
      const vs = (this.openness - 0.3) / 0.7;
      const vr = 60 * vs;
      const grad = ctx.createRadialGradient(this.targetX, this.targetY, vr * 0.3, this.targetX, this.targetY, vr);
      grad.addColorStop(0, `rgba(0,0,0,${(0.85 * vs).toFixed(3)})`);
      grad.addColorStop(0.6, `rgba(0,0,0,${(0.3 * vs).toFixed(3)})`);
      grad.addColorStop(1, 'transparent');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(this.targetX, this.targetY, vr, 0, PI2);
      ctx.fill();
    }

    // Scatter flash
    if (this.effects.scatterFlash && this._scatterActive && this._scatterTime < 0.15) {
      const flash = 1 - this._scatterTime / 0.15;
      const grad = ctx.createRadialGradient(this.targetX, this.targetY, 0, this.targetX, this.targetY, 300);
      grad.addColorStop(0, `rgba(255,255,255,${(0.2 * flash).toFixed(3)})`);
      grad.addColorStop(1, 'transparent');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, w, h);
    }

    // Point indicator (small directional arrow)
    if (this.gesture === 'point') {
      this._drawStreamIndicator(ctx, this.targetX, this.targetY, this._pointAngle, '#ffffff');
    }
    // Peace indicator (two directional arrows)
    if (this.gesture === 'peace') {
      this._drawStreamIndicator(ctx, this.targetX, this.targetY, this._pointAngle - DUAL_STREAM_SPREAD, '#ffffff');
      this._drawStreamIndicator(ctx, this.targetX, this.targetY, this._pointAngle + DUAL_STREAM_SPREAD, '#ffffff');
    }
  }

  // ── line rendering (original style) ───────────────────────────────────────
  _drawLineParticles(ctx, buckets, renderData, renderPasses, hueOffset, time, qualityScale) {
    for (let b = 0; b < 36; b++) {
      const bucket = buckets[b];
      if (!bucket.length) continue;
      const hue = b * 10 + 5;

      const outerGlow = `hsla(${hue},70%,40%,`;
      const midGlow = `hsla(${hue},85%,55%,`;
      const innerBright = `hsla(${hue},90%,75%,`;
      const whiteHot = `hsla(${hue},100%,92%,`;
      const tipFlare = `hsla(${hue},100%,96%,`;
      const baseGlow = `hsla(${hue},80%,60%,`;

      // Outer glow
      if (renderPasses >= 4 && this.effects.glow) {
        for (const p of bucket) {
          const rd = renderData[p._renderIdx];
          ctx.beginPath();
          ctx.strokeStyle = outerGlow + (rd.alpha * 0.12).toFixed(3) + ')';
          ctx.lineWidth = rd.sz * 5;
          ctx.moveTo(rd.x1, rd.y1);
          ctx.lineTo(rd.x2, rd.y2);
          ctx.stroke();
        }
      }

      // Mid glow
      if (renderPasses >= 3 && this.effects.glow) {
        for (const p of bucket) {
          const rd = renderData[p._renderIdx];
          ctx.beginPath();
          ctx.strokeStyle = midGlow + (rd.alpha * 0.3).toFixed(3) + ')';
          ctx.lineWidth = rd.sz * 2.2;
          ctx.moveTo(rd.x1, rd.y1);
          ctx.lineTo(rd.x2, rd.y2);
          ctx.stroke();
        }
      }

      // Inner bright + white core + tip
      ctx.globalCompositeOperation = 'lighter';
      for (const p of bucket) {
        const rd = renderData[p._renderIdx];
        ctx.beginPath();
        ctx.strokeStyle = innerBright + (rd.alpha * 0.7).toFixed(3) + ')';
        ctx.lineWidth = rd.sz;
        ctx.moveTo(rd.mx, rd.my);
        ctx.lineTo(rd.x2, rd.y2);
        ctx.stroke();

        if (renderPasses >= 5) {
          ctx.beginPath();
          ctx.strokeStyle = whiteHot + (rd.alpha * 0.5).toFixed(3) + ')';
          ctx.lineWidth = rd.sz * 0.4;
          ctx.moveTo(rd.mx, rd.my);
          ctx.lineTo(rd.x2, rd.y2);
          ctx.stroke();
        }

        ctx.beginPath();
        ctx.fillStyle = tipFlare + (rd.alpha * 0.8).toFixed(3) + ')';
        ctx.arc(rd.x2, rd.y2, rd.sz * 0.6, 0, PI2);
        ctx.fill();
      }

      // Base glow
      ctx.globalCompositeOperation = 'source-over';
      if (renderPasses >= 6) {
        for (const p of bucket) {
          const rd = renderData[p._renderIdx];
          ctx.beginPath();
          ctx.fillStyle = baseGlow + (rd.alpha * 0.15).toFixed(3) + ')';
          ctx.arc(rd.x1, rd.y1, rd.sz * 1.5, 0, PI2);
          ctx.fill();
        }
      }
    }
  }

  // ── shape rendering (star, heart, diamond, custom) ────────────────────────
  _drawShapeParticles(ctx, buckets, renderData, shape, hueOffset, time, qualityScale) {
    const path = SHAPE_PATHS[shape];

    for (let b = 0; b < 36; b++) {
      const bucket = buckets[b];
      if (!bucket.length) continue;
      const hue = b * 10 + 5;

      ctx.globalCompositeOperation = 'source-over';

      // Outer glow pass
      if (this.effects.glow) {
        ctx.shadowColor = `hsla(${hue},70%,50%,0.4)`;
        ctx.shadowBlur = 12 * qualityScale;
        for (const p of bucket) {
          const rd = renderData[p._renderIdx];
          const sz = rd.sz * 2.5;
          ctx.save();
          ctx.translate(rd.x2, rd.y2);
          ctx.rotate(p.angle + time * 0.3);
          ctx.scale(sz, sz);
          ctx.fillStyle = `hsla(${hue},80%,60%,${(rd.alpha * 0.2).toFixed(3)})`;
          ctx.fill(path);
          ctx.restore();
        }
      }

      // Main shape fill
      ctx.shadowBlur = 4 * qualityScale;
      for (const p of bucket) {
        const rd = renderData[p._renderIdx];
        const sz = rd.sz * 2;
        ctx.save();
        ctx.translate(rd.x2, rd.y2);
        ctx.rotate(p.angle + time * 0.3);
        ctx.scale(sz, sz);
        ctx.fillStyle = `hsla(${hue},85%,55%,${(rd.alpha * 0.6).toFixed(3)})`;
        ctx.fill(path);
        ctx.restore();
      }

      // Bright center (smaller)
      ctx.globalCompositeOperation = 'lighter';
      ctx.shadowBlur = 0;
      for (const p of bucket) {
        const rd = renderData[p._renderIdx];
        const sz = rd.sz;
        ctx.save();
        ctx.translate(rd.x2, rd.y2);
        ctx.rotate(p.angle + time * 0.3);
        ctx.scale(sz, sz);
        ctx.fillStyle = `hsla(${hue},100%,85%,${(rd.alpha * 0.5).toFixed(3)})`;
        ctx.fill(path);
        ctx.restore();
      }

      ctx.globalCompositeOperation = 'source-over';
    }
  }

  // ── stream direction indicator ────────────────────────────────────────────
  _drawStreamIndicator(ctx, x, y, angle, color) {
    const len = 60;
    const tipX = x + Math.cos(angle) * len;
    const tipY = y + Math.sin(angle) * len;
    ctx.save();
    ctx.strokeStyle = color;
    ctx.globalAlpha = 0.15;
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(tipX, tipY);
    ctx.stroke();
    // Arrow head
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.moveTo(tipX, tipY);
    ctx.lineTo(tipX - Math.cos(angle - 0.4) * 12, tipY - Math.sin(angle - 0.4) * 12);
    ctx.moveTo(tipX, tipY);
    ctx.lineTo(tipX - Math.cos(angle + 0.4) * 12, tipY - Math.sin(angle + 0.4) * 12);
    ctx.stroke();
    ctx.restore();
  }

  // ── color ────────────────────────────────────────────────────────────────
  _computeHue(p, colorMode, hueOffset, time) {
    const t = Math.sin(time * 0.5 + p.baseHue * 0.01);
    switch (colorMode) {
      case 'yellow': return 45 + t * 10;
      case 'blue': return 210 + t * 15;
      case 'cyan': return 180 + t * 12;
      case 'green': return 120 + t * 15;
      case 'red': return 0 + t * 8;
      default: return (p.baseHue + hueOffset) % 360;
    }
  }

  resize() {
    this._setupDPI();
    this._initStars();
    this._initParticles();
    this._vignette = null;
    this._targetCount = PARTICLE_COUNT;
  }

  destroy() {
    for (const p of this.particles) _poolReturn(p);
    this.particles = [];
    this.stars = [];
    this._hueBuckets = null;
    this._renderData = null;
    this._vignette = null;
  }
}
