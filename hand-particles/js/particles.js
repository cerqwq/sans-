const PARTICLE_COUNT = 1200;
const MIN_PARTICLES = 400;
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

// 手势检测参数
const HAND_SMOOTHING = 0.35;
const OPENNESS_SMOOTHING = 0.25;
const GESTURE_STABLE_THRESHOLD = 3;
const SWORD_FINGER_THRESHOLD = 0.4;
const OPEN_THRESHOLD = 0.55;
const FIST_THRESHOLD = 0.4;

// 视觉效果参数
const STAR_DRIFT_SPEED = 0.1;
const HUE_ROTATION_SPEED = 10;
const TRAIL_FADE_ALPHA = 0.18;

export class ParticleSystem {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.particles = [];
    this.stars = [];
    this.time = 0;
    this.targetX = 0;
    this.targetY = 0;
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
    this._setupDPI();
    this._initStars();
    this._initParticles();
    this._vignette = null;
  }

  setTargetOpenness(val) { this._targetOpenness = val; }
  getTargetOpenness() { return this._targetOpenness; }

  _setupDPI() {
    const dpr = window.devicePixelRatio || 1;
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.canvas.width = w * dpr;
    this.canvas.height = h * dpr;
    this.canvas.style.width = w + 'px';
    this.canvas.style.height = h + 'px';
    this.ctx.scale(dpr, dpr);
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
    this.particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const goldenAngle = i * 2.399963;
      const r = Math.sqrt(i / PARTICLE_COUNT) * Math.max(this.w, this.h) * 0.4;
      this.particles.push(this._createParticle(i, cx + Math.cos(goldenAngle) * r, cy + Math.sin(goldenAngle) * r, goldenAngle));
    }
  }

  _createParticle(i, x, y, angle) {
    return {
      x, y, vx: 0, vy: 0, angle,
      baseHue: (i / PARTICLE_COUNT) * 360,
      size: 1.4 + Math.random() * 1.6,
      baseAlpha: 0.8 + Math.random() * 0.2,
      ringAngle: Math.random() * PI2,
      ringRadius: RING_INNER + Math.random() * (RING_OUTER - RING_INNER),
      ringSpeed: (0.4 + Math.random() * 0.6) * (Math.random() > 0.5 ? 1 : -1),
      ringPhase: Math.random() * PI2,
      spherePhase: Math.random() * PI2,
      sphereTheta: Math.acos(2 * Math.random() - 1),
      sphereSpeed: 0.3 + Math.random() * 0.6,
      sphereRadius: 20 + Math.random() * (SPHERE_RADIUS - 20),
      scatterAngle: 0, scatterSpeed: 0,
      _cos: 0, _sin: 0, _speed: 0, _depthScale: 1,
    };
  }

  setTarget(x, y) { this.targetX = x; this.targetY = y; }
  setOpenness(val) { this.openness = val; }

  setGesture(g) {
    if (g === 'sword' && this.gesture !== 'sword') this._triggerScatter();
    this.gesture = g;
  }

  _triggerScatter() {
    this._scatterActive = true;
    this._scatterTime = 0;
    for (const p of this.particles) {
      p.scatterAngle = Math.random() * PI2;
      p.scatterSpeed = SCATTER_SPEED_MIN + Math.random() * (SCATTER_SPEED_MAX - SCATTER_SPEED_MIN);
    }
  }

  update(dt) {
    this.time += dt;
    this._hueOffset = (this._hueOffset + dt * 10) % 360;
    const cx = this.targetX;
    const cy = this.targetY;

    if (this._scatterActive) {
      this._scatterTime += dt;
      if (this._scatterTime > SCATTER_DURATION) this._scatterActive = false;
    }

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

    for (const p of this.particles) {
      let tx, ty;

      if (scatterSword) {
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
      } else if (openness > 0.5) {
        const strength = (openness - 0.5) * 2;
        p.ringAngle += p.ringSpeed * dt * 1.5;
        const wobble = Math.sin(time * 0.8 + p.ringPhase) * 20 * strength;
        tx = cx + Math.cos(p.ringAngle) * p.ringRadius;
        ty = cy + Math.sin(p.ringAngle) * p.ringRadius * 0.4 + wobble;
        p.vx += (tx - p.x) * 0.025 * strength;
        p.vy += (ty - p.y) * 0.025 * strength;
      } else {
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

    this._frameCount++;
    const now = performance.now();
    if (now - this._lastFPSSample > FPS_SAMPLE_INTERVAL) {
      this._currentFPS = this._frameCount / ((now - this._lastFPSSample) / 1000);
      this._frameCount = 0;
      this._lastFPSSample = now;
      if (this._currentFPS < FPS_LOW_THRESHOLD && this._targetCount > MIN_PARTICLES) {
        this._targetCount = Math.max(MIN_PARTICLES, this._targetCount - 200);
        this._trimParticles();
      } else if (this._currentFPS > FPS_HIGH_THRESHOLD && this._targetCount < PARTICLE_COUNT) {
        this._targetCount = Math.min(PARTICLE_COUNT, this._targetCount + 100);
        this._addParticles();
      }
    }
  }

  _trimParticles() { if (this.particles.length > this._targetCount) this.particles.length = this._targetCount; }

  _addParticles() {
    const cx = this.w / 2, cy = this.h / 2;
    while (this.particles.length < this._targetCount) {
      const i = this.particles.length;
      const goldenAngle = i * 2.399963;
      const r = Math.sqrt(i / PARTICLE_COUNT) * Math.max(this.w, this.h) * 0.4;
      this.particles.push(this._createParticle(i, cx + Math.cos(goldenAngle) * r, cy + Math.sin(goldenAngle) * r, goldenAngle));
    }
  }

  draw() {
    const ctx = this.ctx;
    const w = this.w;
    const h = this.h;

    ctx.fillStyle = '#050508';
    ctx.fillRect(0, 0, w, h);

    // Stars
    for (const s of this.stars) {
      const twinkle = 0.5 + 0.5 * Math.sin(this.time * s.twinkleSpeed + s.twinklePhase);
      ctx.beginPath();
      ctx.fillStyle = `rgba(200,210,255,${(s.alpha * twinkle).toFixed(2)})`;
      ctx.arc(s.x, s.y, s.size, 0, PI2);
      ctx.fill();
    }

    // Fade trail
    ctx.fillStyle = 'rgba(5,5,8,0.18)';
    ctx.fillRect(0, 0, w, h);

    // Batch draw particles - group by approximate hue for fewer state changes
    const particles = this.particles;
    const hueOffset = this._hueOffset;
    const colorMode = this.colorMode;
    const time = this.time;

    // Sort by hue bucket (10-degree buckets) for batching
    const buckets = this._hueBuckets || (this._hueBuckets = new Array(36).fill(null).map(() => []));
    for (let i = 0; i < 36; i++) buckets[i].length = 0;

    for (const p of particles) {
      const hue = this._computeHue(p, colorMode, hueOffset, time);
      const bucket = Math.floor(Math.floor(((hue % 360) + 360) % 360) / 10);
      if (bucket >= 0 && bucket < 36) buckets[bucket].push(p);
    }

    ctx.lineCap = 'round';

    // Draw each bucket with shared stroke style
    for (let b = 0; b < 36; b++) {
      const bucket = buckets[b];
      if (!bucket.length) continue;

      const hue = b * 10 + 5; // bucket center hue

      // Pre-compute shared color strings for this hue bucket
      const outerGlow = `hsla(${hue},70%,40%,`;
      const midGlow = `hsla(${hue},85%,55%,`;
      const innerBright = `hsla(${hue},90%,75%,`;
      const whiteHot = `hsla(${hue},100%,92%,`;
      const tipFlare = `hsla(${hue},100%,96%,`;
      const baseGlow = `hsla(${hue},80%,60%,`;

      // Batch 1: outer glow (all particles in bucket)
      for (const p of bucket) {
        const depth = p._depthScale;
        const speedFactor = Math.min(p._speed * 0.25, 1);
        const alpha = p.baseAlpha * depth * (0.4 + speedFactor * 0.6);
        const sz = p.size * depth;
        const bladeLen = 5 + speedFactor * 16;
        const cos = p._cos;
        const sin = p._sin;
        const x1 = p.x - cos * bladeLen * 0.4;
        const y1 = p.y - sin * bladeLen * 0.4;
        const x2 = p.x + cos * bladeLen;

        ctx.beginPath();
        ctx.strokeStyle = outerGlow + (alpha * 0.12).toFixed(3) + ')';
        ctx.lineWidth = sz * 5;
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, p.y + sin * bladeLen);
        ctx.stroke();
      }

      // Batch 2: mid glow
      for (const p of bucket) {
        const depth = p._depthScale;
        const speedFactor = Math.min(p._speed * 0.25, 1);
        const alpha = p.baseAlpha * depth * (0.4 + speedFactor * 0.6);
        const sz = p.size * depth;
        const bladeLen = 5 + speedFactor * 16;
        const cos = p._cos;
        const sin = p._sin;
        const x1 = p.x - cos * bladeLen * 0.4;
        const y1 = p.y - sin * bladeLen * 0.4;
        const x2 = p.x + cos * bladeLen;

        ctx.beginPath();
        ctx.strokeStyle = midGlow + (alpha * 0.3).toFixed(3) + ')';
        ctx.lineWidth = sz * 2.2;
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, p.y + sin * bladeLen);
        ctx.stroke();
      }

      // Batch 3: inner bright + white core + tip
      ctx.globalCompositeOperation = 'lighter';
      for (const p of bucket) {
        const depth = p._depthScale;
        const speedFactor = Math.min(p._speed * 0.25, 1);
        const alpha = p.baseAlpha * depth * (0.4 + speedFactor * 0.6);
        const sz = p.size * depth;
        const bladeLen = 5 + speedFactor * 16;
        const cos = p._cos;
        const sin = p._sin;
        const mx = p.x + cos * bladeLen * 0.2;
        const my = p.y + sin * bladeLen * 0.2;
        const x2 = p.x + cos * bladeLen;
        const y2 = p.y + sin * bladeLen;

        // Inner bright
        ctx.beginPath();
        ctx.strokeStyle = innerBright + (alpha * 0.7).toFixed(3) + ')';
        ctx.lineWidth = sz;
        ctx.moveTo(mx, my);
        ctx.lineTo(x2, y2);
        ctx.stroke();

        // White-hot core
        ctx.beginPath();
        ctx.strokeStyle = whiteHot + (alpha * 0.5).toFixed(3) + ')';
        ctx.lineWidth = sz * 0.4;
        ctx.moveTo(mx, my);
        ctx.lineTo(x2, y2);
        ctx.stroke();

        // Tip flare
        ctx.beginPath();
        ctx.fillStyle = tipFlare + (alpha * 0.8).toFixed(3) + ')';
        ctx.arc(x2, y2, sz * 0.6, 0, PI2);
        ctx.fill();
      }

      // Batch 4: base glow (back to source-over for dark outlines)
      ctx.globalCompositeOperation = 'source-over';
      for (const p of bucket) {
        const depth = p._depthScale;
        const speedFactor = Math.min(p._speed * 0.25, 1);
        const alpha = p.baseAlpha * depth * (0.4 + speedFactor * 0.6);
        const sz = p.size * depth;
        const bladeLen = 5 + speedFactor * 16;
        const cos = p._cos;
        const sin = p._sin;
        const x1 = p.x - cos * bladeLen * 0.4;
        const y1 = p.y - sin * bladeLen * 0.4;

        ctx.beginPath();
        ctx.fillStyle = baseGlow + (alpha * 0.15).toFixed(3) + ')';
        ctx.arc(x1, y1, sz * 1.5, 0, PI2);
        ctx.fill();
      }
    }

    // Vignette
    ctx.fillStyle = this._getVignette();
    ctx.fillRect(0, 0, w, h);

    // Dark void center for black hole
    if (this.openness > 0.3 && this.gesture !== 'sword') {
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
    if (this._scatterActive && this._scatterTime < 0.15) {
      const flash = 1 - this._scatterTime / 0.15;
      const grad = ctx.createRadialGradient(this.targetX, this.targetY, 0, this.targetX, this.targetY, 300);
      grad.addColorStop(0, `rgba(255,255,255,${(0.2 * flash).toFixed(3)})`);
      grad.addColorStop(1, 'transparent');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, w, h);
    }
  }

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
    this._vignette = null;
  }
}
