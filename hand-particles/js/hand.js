// 手势检测参数
const HAND_SMOOTHING = 0.35;
const OPENNESS_SMOOTHING = 0.25;
const GESTURE_STABLE_THRESHOLD = 3;
const SWORD_FINGER_THRESHOLD = 0.4;
const OPEN_THRESHOLD = 0.55;
const FIST_THRESHOLD = 0.4;
const POINT_INDEX_THRESHOLD = 0.5;
const POINT_OTHER_THRESHOLD = 0.35;
const PEACE_SPREAD_THRESHOLD = 0.06; // min distance between index and middle tips for peace vs sword

export class HandDetector {
  constructor(videoEl, onResult) {
    this.video = videoEl;
    this.onResult = onResult;
    this.state = { gesture: 'none', palmX: 0.5, palmY: 0.5, confidence: 0 };
    this._palmXSmooth = 0.5;
    this._palmYSmooth = 0.5;
    this._opennessSmooth = 0.5;
    this._prevGesture = 'none';
    this._pendingGesture = null;
    this._stableCount = 0;
    this._init();
  }

  _init() {
    try {
      this._hands = new Hands({
        locateFile: (file) => `vendor/${file}`,
      });

      this._hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 1,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.6,
      });

      this._hands.onResults((results) => this._process(results));

      this._cam = new Camera(this.video, {
        onFrame: async () => {
          await this._hands.send({ image: this.video });
        },
        width: 640,
        height: 480,
      });

      // 监听摄像头权限错误
      this._cam.start().catch(err => {
        console.error('Camera access error:', err);
        const statusEl = document.getElementById('status');
        if (statusEl) {
          if (err.name === 'NotAllowedError') {
            statusEl.textContent = '摄像头权限被拒绝，请允许访问摄像头';
            statusEl.style.color = '#ff4444';
          } else if (err.name === 'NotFoundError') {
            statusEl.textContent = '未找到摄像头设备';
            statusEl.style.color = '#ff4444';
          } else {
            statusEl.textContent = '摄像头启动失败: ' + err.message;
            statusEl.style.color = '#ff4444';
          }
        }
      });
    } catch (e) {
      console.error('HandDetector init error:', e);
      const statusEl = document.getElementById('status');
      if (statusEl) {
        statusEl.textContent = '手势识别初始化失败';
        statusEl.style.color = '#ff4444';
      }
    }
  }

  destroy() {
    if (this._hands) {
      this._hands.close();
      this._hands = null;
    }
    if (this._cam) {
      this._cam.stop();
      this._cam = null;
    }
  }

  _process(results) {
    if (!results.multiHandLandmarks || results.multiHandLandmarks.length === 0) {
      this._stableCount = 0;
      this.state.gesture = 'none';
      this.state.confidence = 0;
      this.onResult(this.state);
      return;
    }

    const lm = results.multiHandLandmarks[0];

    const cx = (lm[0].x + lm[9].x) / 2;
    const cy = (lm[0].y + lm[9].y) / 2;
    this._palmXSmooth += (cx - this._palmXSmooth) * HAND_SMOOTHING;
    this._palmYSmooth += (cy - this._palmYSmooth) * HAND_SMOOTHING;
    this.state.palmX = this._palmXSmooth;
    this.state.palmY = this._palmYSmooth;

    const index = this._fingerRatio(lm, 5, 6, 8);
    const middle = this._fingerRatio(lm, 9, 10, 12);
    const ring = this._fingerRatio(lm, 13, 14, 16);
    const pinky = this._fingerRatio(lm, 17, 18, 20);
    const thumbDist = this._dist(lm[4], lm[9]);
    const thumbBase = this._dist(lm[2], lm[9]);
    const thumb = Math.min(Math.max((thumbDist / thumbBase - 0.8) / 0.6, 0), 1);

    const extended = [thumb, index, middle, ring, pinky];
    const extendedCount = extended.filter(r => r > 0.5).length;
    const avgRatio = extended.reduce((a, b) => a + b, 0) / 5;

    this._opennessSmooth += (avgRatio - this._opennessSmooth) * OPENNESS_SMOOTHING;

    // Pointing: only index finger extended, others curled
    const isPoint = index > POINT_INDEX_THRESHOLD &&
                    middle < POINT_OTHER_THRESHOLD &&
                    ring < POINT_OTHER_THRESHOLD &&
                    pinky < POINT_OTHER_THRESHOLD;

    // Two-finger gesture: index + middle extended, ring + pinky down
    const isTwoFinger = index > SWORD_FINGER_THRESHOLD && middle > SWORD_FINGER_THRESHOLD &&
                        ring < 0.45 && pinky < 0.45 && extendedCount === 2;

    // Distinguish peace (spread fingers) from sword (together)
    const fingerSpread = isTwoFinger ? this._dist(lm[8], lm[12]) : 0;
    const isPeace = isTwoFinger && fingerSpread > PEACE_SPREAD_THRESHOLD;
    const isSword = isTwoFinger && fingerSpread <= PEACE_SPREAD_THRESHOLD;

    let rawGesture;
    if (isPoint) {
      rawGesture = 'point';
    } else if (isPeace) {
      rawGesture = 'peace';
    } else if (isSword) {
      rawGesture = 'sword';
    } else if (this._opennessSmooth > OPEN_THRESHOLD) {
      rawGesture = 'open';
    } else if (this._opennessSmooth < FIST_THRESHOLD) {
      rawGesture = 'fist';
    } else {
      rawGesture = this._prevGesture;
    }

    if (this._prevGesture === 'none') {
      this._prevGesture = rawGesture;
      this._stableCount = 0;
    } else if (rawGesture !== this._prevGesture) {
      if (rawGesture !== this._pendingGesture) {
        this._pendingGesture = rawGesture;
        this._stableCount = 0;
      } else {
        this._stableCount++;
        if (this._stableCount >= GESTURE_STABLE_THRESHOLD) {
          this._prevGesture = rawGesture;
          this._stableCount = 0;
        }
      }
    } else {
      this._stableCount = 0;
      this._pendingGesture = null;
    }

    this.state.gesture = this._prevGesture;
    this.state.confidence = this._opennessSmooth;

    // Compute pointing direction (index finger MCP → tip)
    if (this._prevGesture === 'point' || this._prevGesture === 'peace') {
      const dx = lm[8].x - lm[5].x;
      const dy = lm[8].y - lm[5].y;
      this.state.pointAngle = Math.atan2(dy, dx) + Math.PI; // +PI to flip (camera is mirrored)
    }

    this.onResult(this.state);
  }

  _fingerRatio(lm, mcp, pip, tip) {
    const wrist = lm[0];
    const tipDist = this._dist(lm[tip], wrist);
    const pipDist = this._dist(lm[pip], wrist);
    const mcpDist = this._dist(lm[mcp], wrist);
    return Math.min(Math.max((tipDist - pipDist) / (mcpDist * 0.3 + 0.01), 0), 1);
  }

  _dist(a, b) {
    return Math.hypot(a.x - b.x, a.y - b.y);
  }
}
