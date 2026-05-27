import { HandDetector } from './hand.js';
import { ParticleSystem } from './particles.js';

const canvas = document.getElementById('canvas');
const video = document.getElementById('video');
const statusEl = document.getElementById('status');

let particles;
let currentOpenness = 0;
let lastTime = performance.now();

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

async function main() {
  particles = new ParticleSystem(canvas);
  initColorPicker();

  window.addEventListener('resize', () => particles.resize());

  statusEl.textContent = '正在启动摄像头和手势模型...';

  new HandDetector(video, (result) => {
    particles.setGesture(result.gesture);

    if (result.gesture === 'none') {
      statusEl.textContent = '未检测到手';
    } else if (result.gesture === 'sword') {
      statusEl.textContent = '🗡 剑指 — 万剑散开';
    } else if (result.gesture === 'open') {
      statusEl.textContent = '✋ 张开手掌 — 黑洞吸引';
    } else {
      statusEl.textContent = '✊ 握拳 — 万剑归宗';
    }

    const px = (1 - result.palmX) * particles.w;
    const py = result.palmY * particles.h;
    particles.setTarget(px, py);

    let targetOpen;
    if (result.gesture === 'sword') {
      targetOpen = 0.7;
    } else if (result.gesture === 'none') {
      targetOpen = 0.5;
    } else {
      targetOpen = result.confidence;
    }
    particles.setTargetOpenness(targetOpen);
  });

  requestAnimationFrame(tick);
}

function tick(now) {
  const dt = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;

  const target = particles.getTargetOpenness();
  currentOpenness += (target - currentOpenness) * 0.06;
  particles.setOpenness(currentOpenness);

  particles.update(dt);
  particles.draw();

  requestAnimationFrame(tick);
}

main();
