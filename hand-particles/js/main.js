import { HandDetector } from './hand.js';
import { ParticleSystem } from './particles.js';

const canvas = document.getElementById('canvas');
const video = document.getElementById('video');
const statusEl = document.getElementById('status');

let particles;
let handDetector;
let currentOpenness = 0;
let lastTime = performance.now();
let frameId = null;

function initColorPicker() {
  const picker = document.getElementById('colorPicker');
  picker.querySelectorAll('.swatch').forEach(btn => {
    btn.addEventListener('click', () => {
      picker.querySelectorAll('.swatch').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      particles.colorMode = btn.dataset.color;
    });
  });
}

function initSettingsPanel() {
  const panel = document.getElementById('settingsPanel');
  const toggle = document.getElementById('settingsToggle');

  if (toggle && panel) {
    toggle.addEventListener('click', () => {
      panel.classList.toggle('open');
    });
    // Close on click outside
    document.addEventListener('click', (e) => {
      if (!panel.contains(e.target) && e.target !== toggle) {
        panel.classList.remove('open');
      }
    });
  }

  // Particle count slider
  const countSlider = document.getElementById('particleCount');
  const countLabel = document.getElementById('particleCountLabel');
  if (countSlider) {
    countSlider.addEventListener('input', () => {
      const val = parseInt(countSlider.value);
      particles.setParticleCount(val);
      if (countLabel) countLabel.textContent = val;
    });
  }

  // Shape selector
  const shapeSelect = document.getElementById('shapeSelect');
  if (shapeSelect) {
    shapeSelect.addEventListener('change', () => {
      particles.setShape(shapeSelect.value);
    });
  }

  // Effect toggles
  const toggleTrails = document.getElementById('toggleTrails');
  const toggleGlow = document.getElementById('toggleGlow');
  const toggleFlash = document.getElementById('toggleFlash');

  if (toggleTrails) {
    toggleTrails.addEventListener('change', () => {
      particles.effects.trails = toggleTrails.checked;
    });
  }
  if (toggleGlow) {
    toggleGlow.addEventListener('change', () => {
      particles.effects.glow = toggleGlow.checked;
    });
  }
  if (toggleFlash) {
    toggleFlash.addEventListener('change', () => {
      particles.effects.scatterFlash = toggleFlash.checked;
    });
  }

  // FPS display (updated in tick)
  return document.getElementById('fpsDisplay');
}

let fpsDisplayEl = null;
let fpsUpdateTimer = 0;

function cleanup() {
  if (frameId !== null) {
    cancelAnimationFrame(frameId);
    frameId = null;
  }
  if (handDetector) {
    handDetector.destroy();
    handDetector = null;
  }
  if (particles) {
    particles.destroy();
    particles = null;
  }
}

function tick(now) {
  const dt = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;

  const target = particles.getTargetOpenness();
  currentOpenness += (target - currentOpenness) * 0.06;
  particles.setOpenness(currentOpenness);

  particles.update(dt);
  particles.draw();

  // Update FPS display periodically
  fpsUpdateTimer += dt;
  if (fpsUpdateTimer > 0.5 && fpsDisplayEl) {
    fpsDisplayEl.textContent = particles.getFPS() + ' FPS';
    fpsUpdateTimer = 0;
  }

  frameId = requestAnimationFrame(tick);
}

const GESTURE_STATUS = {
  none: '未检测到手',
  sword: '剑指 - 万剑散开',
  open: '张开手掌 - 黑洞吸引',
  fist: '握拳 - 万剑归宗',
  point: '食指指向 - 粒子射流',
  peace: '双指 V 形 - 双流分射',
};

async function main() {
  particles = new ParticleSystem(canvas);
  initColorPicker();
  fpsDisplayEl = initSettingsPanel();

  window.addEventListener('resize', () => particles.resize());

  statusEl.textContent = '正在启动摄像头和手势模型...';

  handDetector = new HandDetector(video, (result) => {
    particles.setGesture(result.gesture);

    // Update status text
    statusEl.textContent = GESTURE_STATUS[result.gesture] || '未知手势';

    // Mirror X coordinate
    const px = (1 - result.palmX) * particles.w;
    const py = result.palmY * particles.h;
    particles.setTarget(px, py);

    // Pass pointing angle to particle system
    if (result.pointAngle !== undefined) {
      particles.setPointAngle(result.pointAngle);
    }

    // Compute target openness per gesture
    let targetOpen;
    switch (result.gesture) {
      case 'sword':
        targetOpen = 0.7;
        break;
      case 'point':
        targetOpen = 0.3;
        break;
      case 'peace':
        targetOpen = 0.4;
        break;
      case 'none':
        targetOpen = 0.5;
        break;
      default:
        targetOpen = result.confidence;
    }
    particles.setTargetOpenness(targetOpen);
  });

  lastTime = performance.now();
  frameId = requestAnimationFrame(tick);
}

main().catch(err => {
  console.error('Initialization failed:', err);
  statusEl.textContent = '初始化失败: ' + err.message;
  statusEl.style.color = '#ff4444';
});

window.addEventListener('beforeunload', cleanup);
