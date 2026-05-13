const DESIGN_WIDTH = 1920;
const DESIGN_HEIGHT = 1080;


let state = {
  face: {
    valence: 0,
    thinking: 0,
    arousal: 0,
    anxious: 0,
    score: 0
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
    energy: 0,
    pitch: 0,
    pitch_norm: 0,
    score: 0
  },
  text: {
    transcript: "waiting for transcript...",
    label: "neutral",
    sentiment: 0,
    score: 0
  },
  question: 1,
  log: "system waiting..."
};

function scaleStage() {
  const stage = document.getElementById("stage");

  const scaleX = window.innerWidth / DESIGN_WIDTH;
  const scaleY = window.innerHeight / DESIGN_HEIGHT;
  const scale = Math.min(scaleX, scaleY);

  stage.style.transform = `scale(${scale})`;
}

window.addEventListener("resize", scaleStage);
scaleStage();

function setBar(id, value) {
  const el = document.getElementById(id);
  const maxWidth = 120;
  el.style.width = `${(Math.max(0, Math.min(100, value)) / 100) * maxWidth}px`;
}

function updateText() {
  document.getElementById("valenceText").textContent = `${Math.round(state.face.valence)}%`;
  document.getElementById("thinkingText").textContent = `${Math.round(state.face.thinking)}%`;
  document.getElementById("arousalText").textContent = `${Math.round(state.face.arousal)}%`;
  document.getElementById("anxiousText").textContent = `${Math.round(state.face.anxious)}%`;
  document.getElementById("faceScoreText").textContent = `${Math.round(state.face.score)}%`;

  document.getElementById("pitchText").textContent = `${state.voice.pitch.toFixed(1)}hz`;
  document.getElementById("energyText").textContent = `${Math.round(state.voice.energy * 100)}%`;
  document.getElementById("voiceScoreText").textContent = `${Math.round(state.voice.score)}%`;

  document.getElementById("transcriptText").textContent = state.text.transcript;
  document.getElementById("sentimentLabel").textContent = state.text.label;
  document.getElementById("sentimentScore").textContent = `${Math.round(state.text.sentiment)}%`;
  document.getElementById("textScore").textContent = `${Math.round(state.text.score)}%`;

  document.getElementById("questionNum").textContent = String(state.question).padStart(2, "0");
  document.getElementById("logText").textContent = state.log;
}

function updateBars() {
  setBar("barValence", state.face.valence);
  setBar("barThinking", state.face.thinking);
  setBar("barArousal", state.face.arousal);
  setBar("barAnxious", state.face.anxious);
  setBar("barScore", state.face.score);
}

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

  for (let r = 35; r <= 105; r += 25) {
    ctx.beginPath();

    for (let i = 0; i < 5; i++) {
      const angle = -Math.PI / 2 + i * Math.PI * 2 / 5;
      const x = cx + Math.cos(angle) * r;
      const y = cy + Math.sin(angle) * r;

      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }

    ctx.closePath();
    ctx.stroke();
  }

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

const wave = [];

function drawWave() {
  const canvas = document.getElementById("waveCanvas");
  const ctx = canvas.getContext("2d");

  wave.push(state.voice.energy);

  if (wave.length > 80) {
    wave.shift();
  }

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.strokeStyle = "#00ffd0";
  ctx.lineWidth = 2;
  ctx.beginPath();

  wave.forEach((value, i) => {
    const x = (i / 79) * canvas.width;
    const y = canvas.height - value * canvas.height;

    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });

  ctx.stroke();
}

function drawFace() {
  const canvas = document.getElementById("faceCanvas");
  const ctx = canvas.getContext("2d");

  const w = canvas.width;
  const h = canvas.height;

  ctx.clearRect(0, 0, w, h);

  function hasPoint(name) {
    return state.pos[name] !== undefined;
  }

  function p(name) {
    return {
      x: state.pos[name].x * w,
      y: state.pos[name].y * h
    };
  }

  function line(a, b) {
    if (!hasPoint(a) || !hasPoint(b)) return;

    const pa = p(a);
    const pb = p(b);

    ctx.beginPath();
    ctx.moveTo(pa.x, pa.y);
    ctx.lineTo(pb.x, pb.y);
    ctx.stroke();
  }

  function rectBlob(name, value, label) {
    if (!hasPoint(name)) return;

    const point = p(name);

    const size = 30 + value * 0.8;

    ctx.strokeStyle = "#00ffd0";
    ctx.lineWidth = 2;
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

function updateUI() {
  updateText();
  updateBars();
  drawRadar();
  drawWave();
  drawFace();

  requestAnimationFrame(updateUI);
}

updateUI();

/* temporary mock data */
setInterval(() => {
  state.face.valence = Math.random() * 100;
  state.face.thinking = Math.random() * 100;
  state.face.arousal = Math.random() * 100;
  state.face.anxious = Math.random() * 100;
  state.face.score =
    (state.face.valence +
      state.face.thinking +
      state.face.arousal +
      state.face.anxious) / 4;

  state.voice.energy = Math.random();
  state.voice.pitch = 80 + Math.random() * 220;
  state.voice.score = Math.random() * 100;

  state.log = "receiving simulated data...";
}, 300);