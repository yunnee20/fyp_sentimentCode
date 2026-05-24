/**
 * Real-time Sentiment Analysis Dashboard
 * 
 * Displays multi-modal emotion analysis data (facial, vocal, textual) on a live dashboard.
 * Receives streaming data from Python backend via WebSocket and renders:
 * - Facial landmark tracking with emotion overlays
 * - Voice pitch and energy visualization
 * - Text sentiment classification
 * - Aggregated emotion metrics (radar chart, energy circles, waveform)
 */

const DESIGN_WIDTH = 1920;
const DESIGN_HEIGHT = 1080;

/**
 * Global application state
 * 
 * Maintains current values for all emotion metrics and facial landmarks.
 * Updated in real-time by WebSocket messages from the Python backend.
 */
let state = {
    face: {
        valence: 30,
        thinking: 20,
        arousal: 50,
        anxious: 10,
        score: 90
    },
    pos: {
        brow_left_inner: { x: 0.45, y: 0.35 },
        brow_left_mid: { x: 0.40, y: 0.35 },
        brow_left_outer: { x: 0.35, y: 0.36 },

        brow_right_inner: { x: 0.55, y: 0.35 },
        brow_right_mid: { x: 0.60, y: 0.35 },
        brow_right_outer: { x: 0.65, y: 0.36 },

        eye_left_top: { x: 0.42, y: 0.43 },
        eye_left_bottom: { x: 0.42, y: 0.46 },
        eye_left_outer: { x: 0.36, y: 0.44 },
        eye_left_inner: { x: 0.47, y: 0.44 },

        eye_right_top: { x: 0.58, y: 0.43 },
        eye_right_bottom: { x: 0.58, y: 0.46 },
        eye_right_inner: { x: 0.53, y: 0.44 },
        eye_right_outer: { x: 0.64, y: 0.44 },

        mouth_top: { x: 0.50, y: 0.62 },
        mouth_bottom: { x: 0.50, y: 0.67 },
        mouth_left: { x: 0.43, y: 0.65 },
        mouth_right: { x: 0.57, y: 0.65 },

        chin: { x: 0.50, y: 0.78 },
        jaw_left: { x: 0.35, y: 0.65 },
        jaw_right: { x: 0.65, y: 0.65 },
        nose: { x: 0.50, y: 0.52 }
    },

    voice: {
        pitch: 0,
        pitch_average: 0,
        pitch_diff: 0,
        energy: 0,
        energy_average: 0,
        energy_stability: 0,
        score: 0
    },
    text: {
        transcript: "waiting for transcript...",
        label: "neutral",
        joy: 0,
        neutral: 0,
        sadness: 0,
        anger: 0,
        fear: 0,
        disgust: 0,
        surprise: 0,
        score: 0
    },
    question: 5,
    log: "system waiting..."
};

// ============================================================================
// RESPONSIVE DISPLAY
// ============================================================================

/**
 * Responsive stage scaling
 * 
 * Maintains 16:9 aspect ratio regardless of window size.
 * Scales all elements proportionally using CSS transform.
 */
function scaleStage() {
    const stage = document.getElementById("stage");

    const scaleX = window.innerWidth / DESIGN_WIDTH;
    const scaleY = window.innerHeight / DESIGN_HEIGHT;
    const scale = Math.min(scaleX, scaleY);

    stage.style.transform = `scale(${scale})`;
}

window.addEventListener("resize", scaleStage);
scaleStage();

// ============================================================================
// TEXT RENDERING FUNCTIONS
// ============================================================================

/**
 * Set progress bar width based on percentage value.
 * 
 * @param {string} id - Element ID of the progress bar
 * @param {number} value - Value 0-100
 */
function setBar(id, value) {
    const el = document.getElementById(id);
    const maxWidth = 120;
    el.style.width = `${(Math.max(0, Math.min(100, value)) / 100) * maxWidth}px`;
}

/**
 * Update all text display elements with current state values.
 * 
 * Renders facial metrics, facial landmarks, voice parameters, and text sentiment.
 */
function updateText() {
    // first section
    document.getElementById("valenceText").textContent = `${Math.round(state.face.valence)}%`;
    document.getElementById("thinkingText").textContent = `${Math.round(state.face.thinking)}%`;
    document.getElementById("arousalText").textContent = `${Math.round(state.face.arousal)}%`;
    document.getElementById("anxiousText").textContent = `${Math.round(state.face.anxious)}%`;
    document.getElementById("faceScoreText").textContent = `${Math.round(state.face.score)}%`;

    // face section
    document.getElementById("eyeL").textContent = `[${state.pos.eye_left_top.x.toFixed(2)}, ${state.pos.eye_left_top.y.toFixed(2)}]`;
    document.getElementById("eyeR").textContent = `[${state.pos.eye_right_top.x.toFixed(2)}, ${state.pos.eye_right_top.y.toFixed(2)}]`;
    document.getElementById("browL").textContent = `[${state.pos.brow_left_mid.x.toFixed(2)}, ${state.pos.brow_left_mid.y.toFixed(2)}]`;
    document.getElementById("browR").textContent = `[${state.pos.brow_right_mid.x.toFixed(2)}, ${state.pos.brow_right_mid.y.toFixed(2)}]`;
    document.getElementById("mouth").textContent = `[${state.pos.mouth_top.x.toFixed(2)}, ${state.pos.mouth_top.y.toFixed(2)}]`;
    document.getElementById("jaw").textContent = `[${state.pos.chin.x.toFixed(2)}, ${state.pos.chin.y.toFixed(2)}]`;

    // voice section
    document.getElementById("pitchText").textContent = `${state.voice.pitch.toFixed(1)}hz`;
    document.getElementById("averagePitch").textContent = `${Math.round(state.voice.pitch_average).toFixed(1)}hz`;
    document.getElementById("diffPitch").textContent = `${Math.round(state.voice.pitch_diff * 100)}%`;

    document.getElementById("energyText").textContent = `${Math.round(state.voice.energy * 100)}%`;
    document.getElementById("averageEnergy").textContent = `${Math.round(state.voice.energy_average * 100)}%`;
    document.getElementById("stability").textContent = `${Math.round(state.voice.energy_stability * 100)}%`;
    
    // text section
    document.getElementById("transcriptText").textContent = state.text.transcript;
    document.getElementById("sentimentLabel").textContent = state.text.label;
    document.getElementById("joy").textContent = `${Math.round(state.text.joy)}%`;
    document.getElementById("neutral").textContent = `${Math.round(state.text.neutral)}%`;
    document.getElementById("sadness").textContent = `${Math.round(state.text.sadness)}%`;
    document.getElementById("anger").textContent = `${Math.round(state.text.anger)}%`;
    document.getElementById("fear").textContent = `${Math.round(state.text.fear)}%`;
    document.getElementById("disgust").textContent = `${Math.round(state.text.disgust)}%`;
    document.getElementById("surprise").textContent = `${Math.round(state.text.surprise)}%`;
    document.getElementById("score").textContent = `${Math.round(state.text.score)}%`;
    
    document.getElementById("questionNum").textContent = String(state.question).padStart(2, "0");
    // document.getElementById("logText").textContent = state.log;
}

/**
 * Update all progress bars for facial emotion dimensions.
 */
function updateBars() {
    setBar("barValence", state.face.valence);
    setBar("barThinking", state.face.thinking);
    setBar("barArousal", state.face.arousal);
    setBar("barAnxious", state.face.anxious);
    setBar("barScore", state.face.score);
}

// ============================================================================
// CANVAS VISUALIZATION FUNCTIONS
// ============================================================================

/**
 * Draw 5-axis radar chart of emotion dimensions.
 * 
 * Axes: score, thinking, arousal, anxious, valence
 * Renders filled polygon based on current values (0-100 scale).
 */
function drawRadar() {
    const canvas = document.getElementById("radarCanvas");
    const ctx = canvas.getContext("2d");

    const cx = canvas.width / 2;
    const cy = canvas.height / 2;

    const values = [
        state.face.score,
        state.face.thinking,
        state.face.arousal,
        state.face.anxious,
        state.face.valence
    ];

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = "rgba(0,255,208,0.45)";
    ctx.lineWidth = 1;

    // for (let r = 10; r <= 105; r += 25) {
    //     ctx.beginPath();

    //     for (let i = 0; i < 5; i++) {
    //     const angle = -Math.PI / 2 + i * Math.PI * 2 / 5;
    //     const x = cx + Math.cos(angle) * r;
    //     const y = cy + Math.sin(angle) * r;

    //     if (i === 0) ctx.moveTo(x, y);
    //     else ctx.lineTo(x, y);
    //     }

    //     ctx.closePath();
    //     ctx.stroke();
    // }

    ctx.beginPath();

    values.forEach((value, i) => {
        const r = (value / 100) * 105;
        const angle = -Math.PI / 2 + i * Math.PI * 2 / 5;
        const x = cx + Math.cos(angle) * r;
        const y = cy + Math.sin(angle) * r;

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });

    ctx.closePath();
    ctx.fillStyle = "rgba(0,255,208,0.25)";
    ctx.strokeStyle = "#00ffd0";
    ctx.lineWidth = 3;
    ctx.fill();
    ctx.stroke();
}

const wave = [];  // Circular buffer for pitch visualization

/**
 * Draw animated waveform of voice pitch over time.
 * 
 * Maintains rolling window of last 80 pitch samples.
 * Normalized to 0-400 Hz range.
 */
function drawWave() {
    const canvas = document.getElementById("waveCanvas");
    const ctx = canvas.getContext("2d");

    if (state.voice.pitch > 0) {
        wave.push(state.voice.pitch);
    }

    if (wave.length > 80) {
        wave.shift();
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = "#00ffd0";
    ctx.lineWidth = 2;
    ctx.beginPath();

    wave.forEach((value, i) => {
        const x = (i / Math.max(1, wave.length - 1)) * canvas.width;
        const normalized = Math.min(value / 400, 1);
        const y = canvas.height * (1 - normalized);

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });

    ctx.stroke();
}

/**
 * Draw dynamic circle with variable line thickness.
 * 
 * Thickness varies with the input value, providing visual feedback for energy levels.
 * 
 * @param {string} canvasId - Canvas element ID
 * @param {number} value - Value 0-1 (normalized)
 */
function drawCircle(canvasId, value) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext("2d");

    const w = canvas.width;
    const h = canvas.height;

    const cx = w / 2;
    const cy = h / 2;

    const radius = 30;

    ctx.clearRect(0, 0, w, h);

    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);

    ctx.strokeStyle = "#00ffd0";

    // dynamic thickness
    ctx.lineWidth = 2 + value * 4;

    ctx.stroke();
}

const video = document.getElementById("cameraVideo");
const canvas = document.getElementById("faceCanvas");
const ctx = canvas.getContext("2d");

canvas.width = 990;
canvas.height = 610;

/**
 * Start webcam feed for live facial visualization.
 * 
 * Requests browser camera access and streams video
 * into the hidden HTML video element.
 */
async function startCamera() {
  const stream = await navigator.mediaDevices.getUserMedia({
    video: true,
    audio: false
  });
  video.srcObject = stream;
}

/**
 * Generate edge-detection camera effect.
 * 
 * Converts webcam feed into high-contrast outline visualization
 * using Sobel edge detection to create surveillance-style aesthetics.
 */
function drawCameraOutline() {
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const src = img.data;
  const output = ctx.createImageData(canvas.width, canvas.height);
  const dst = output.data;

  const w = canvas.width;
  const h = canvas.height;

  function grayAt(x, y) {
    const i = (y * w + x) * 4;
    return (src[i] + src[i + 1] + src[i + 2]) / 3;
  }

  for (let y = 1; y < h - 1; y++) {
    for (let x = 1; x < w - 1; x++) {
      const gx =
        -grayAt(x - 1, y - 1) + grayAt(x + 1, y - 1) +
        -2 * grayAt(x - 1, y) + 2 * grayAt(x + 1, y) +
        -grayAt(x - 1, y + 1) + grayAt(x + 1, y + 1);

      const gy =
        -grayAt(x - 1, y - 1) - 2 * grayAt(x, y - 1) - grayAt(x + 1, y - 1) +
         grayAt(x - 1, y + 1) + 2 * grayAt(x, y + 1) + grayAt(x + 1, y + 1);

      const edge = Math.sqrt(gx * gx + gy * gy);

      const i = (y * w + x) * 4;

      if (edge > 40) {
        dst[i] = 0;
        dst[i + 1] = 255;
        dst[i + 2] = 195;
        dst[i + 3] = 255;
      } else {
        dst[i] = 0;
        dst[i + 1] = 0;
        dst[i + 2] = 0;
        dst[i + 3] = 255;    
      }
    }
  }

  ctx.putImageData(output, 0, 0);
}


/**
 * Draw facial landmark mesh and reactive rectangle blobs.
 * 
 * Uses streamed landmark coordinates from Python backend
 * to render facial structure lines, tracked points,
 * and dynamic emotion-reactive overlays.
 */
function drawFace() {
  const canvas = document.getElementById("faceCanvas");
  const ctx = canvas.getContext("2d");

  const w = canvas.width;
  const h = canvas.height;

  // ctx.clearRect(0, 0, w, h);

  // Check whether a facial landmark exists before drawing
  function hasPoint(name) {
      return state.pos[name] !== undefined;
  }

  // Convert normalized landmark coordinates into canvas pixel positions
  function p(name) {
      return {
      x: state.pos[name].x * w,
      y: state.pos[name].y * h
      };
  }
  // Draw connection line between two facial landmarks
  function line(a, b) {
      if (!hasPoint(a) || !hasPoint(b)) return;

      const pa = p(a);
      const pb = p(b);

      ctx.beginPath();
      ctx.moveTo(pa.x, pa.y);
      ctx.lineTo(pb.x, pb.y);
      ctx.stroke();
  }

  // Draw dynamic rectangle blob that scales based on emotion intensity
  function rectBlob(name, value, label) {
      if (!hasPoint(name)) return;

      const point = p(name);

      const size = 30 + value * 0.8;

      ctx.strokeStyle = "#00ffd0";
      ctx.lineWidth = 1;
      ctx.strokeRect(
      point.x - size / 2,
      point.y - size / 2,
      size,
      size
      );

      ctx.font = "12px JetBrainsMono, monospace";
      ctx.fillStyle = "#00ffd0";
      ctx.fillText(label, point.x + size / 2 + 6, point.y);
  }

  // --------------------
  // FACE GRID
  // --------------------
  ctx.strokeStyle = "rgba(0,255,208,0.65)";
  ctx.lineWidth = 2;

  // brows
  line("brow_left_outer", "brow_left_mid");
  line("brow_left_mid", "brow_left_inner");
  line("brow_right_inner", "brow_right_mid");
  line("brow_right_mid", "brow_right_outer");

  // eyes
  line("eye_left_outer", "eye_left_top");
  line("eye_left_top", "eye_left_inner");
  line("eye_left_inner", "eye_left_bottom");
  line("eye_left_bottom", "eye_left_outer");

  line("eye_right_inner", "eye_right_top");
  line("eye_right_top", "eye_right_outer");
  line("eye_right_outer", "eye_right_bottom");
  line("eye_right_bottom", "eye_right_inner");

  // mouth
  line("mouth_left", "mouth_top");
  line("mouth_top", "mouth_right");
  line("mouth_right", "mouth_bottom");
  line("mouth_bottom", "mouth_left");

  // face structure
  line("jaw_left", "chin");
  line("chin", "jaw_right");
  line("nose", "mouth_top");
  line("nose", "eye_left_inner");
  line("nose", "eye_right_inner");
  line("brow_left_inner", "nose");
  line("brow_right_inner", "nose");

  // --------------------
  // POINTS
  // --------------------
  Object.keys(state.pos).forEach((name) => {
      const point = p(name);

      ctx.beginPath();
      ctx.arc(point.x, point.y, 3, 0, Math.PI * 2);
      ctx.fillStyle = "#00ffd0";
      ctx.fill();
  });

  // --------------------
  // RECTANGLE BLOBS
  // --------------------
  rectBlob("brow_left_mid", state.face.thinking, "brow");
  rectBlob("brow_right_mid", state.face.thinking, "brow");
  rectBlob("mouth_top", state.face.valence, "mouth");
  rectBlob("chin", state.face.arousal, "jaw");
  rectBlob("eye_left_top", state.face.anxious, "eye");
  rectBlob("eye_right_top", state.face.anxious, "eye");
}


/**
 * Main rendering loop.
 * 
 * Continuously updates all visual dashboard components
 * including face visualization, waveform, radar chart,
 * circles, bars, and text displays.
 */
function updateUI() {
  drawCameraOutline(); // background camera trace
  drawFace();  
  updateText();
  updateBars();
  drawRadar();
  drawWave();
  drawCircle("energyCircle", state.voice.energy);
  drawCircle("averageCircle", state.voice.energy_average); 

  requestAnimationFrame(updateUI);
}

startCamera().then(() => {
  video.onloadedmetadata = () => {
    updateUI();
  };
});

// WebSocket connection to Python backend for receiving live emotion data
const socket = new WebSocket("ws://localhost:8765");

socket.onopen = () => {
  console.log("Connected to Python WebSocket");
};

/**
 * Receive real-time streamed data from Python backend.
 * 
 * Updates dashboard state for:
 * - facial analysis
 * - voice analysis
 * - text sentiment
 * - interaction state
 * - terminal logs
 */
socket.onmessage = (event) => {
  const msg = JSON.parse(event.data);

  if (msg.type === "face") {
    state.face.valence = msg.values.valence;
    state.face.thinking = msg.values.thinking;
    state.face.arousal = msg.values.arousal;
    state.face.anxious = msg.values.anxious;
    state.face.score = msg.values.score;

    state.pos = msg.positions;
  }

  if (msg.type === "voice") {
    const prevPitch = state.voice.pitch;
    state.voice.pitch += (msg.pitch - state.voice.pitch) * 0.3;
    state.voice.pitch_diff = Math.abs(
        state.voice.pitch - prevPitch
    ) / 400;
    state.voice.pitch_average = msg.pitch_average;
    state.voice.energy = msg.energy;
    state.voice.energy_average = msg.energy_average;
    state.voice.energy_stability = 1 - Math.abs(msg.energy - msg.energy_average);
    state.voice.energy_stability = Math.max(0,Math.min(1, state.voice.energy_stability));
    state.voice.score = msg.score;
  }

  if (msg.type === "text") {
    state.text.transcript = msg.transcript;
    state.text.label = msg.label;
    state.text.joy = msg.joy || 0;
    state.text.neutral = msg.neutral || 0;
    state.text.sadness = msg.sadness || 0;
    state.text.anger = msg.anger || 0;
    state.text.fear = msg.fear || 0;
    state.text.disgust = msg.disgust || 0;
    state.text.surprise = msg.surprise || 0;
    state.text.score = msg.score || 0;
  }

  if (msg.type === "state") {
    if (msg.question !== undefined) {
      state.question = msg.question;
    }
  }
  if (msg.type === "log") {
    addTerminalLine(msg.message);
  }
}

/**
 * Add timestamped system log message to terminal panel.
 * 
 * Maintains rolling list of latest log entries.
 */
function addTerminalLine(text) {
    const terminal = document.getElementById("terminal");

    const line = document.createElement("div");
    line.className = "terminal-line";

    const timestamp = new Date().toLocaleTimeString();

    line.textContent = `[${timestamp}] ${text}`;

    terminal.prepend(line);

    // limit lines
    while (terminal.children.length > 8) {
        terminal.removeChild(terminal.lastChild);
    }
}