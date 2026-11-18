// Thai TTS Benchmark & Testing Studio - Frontend App
let modelsData = null;
let currentEngine = "vachanatts";
let activeAudios = [];

const PRESETS = [
  "โรงเรียนของเราน่าอยู่ คุณครูใจดีทุกคน รถไฟสายตะวันออกแล่นเร็วมาก",
  "วันที่ 15 พฤศจิกายน 2569 เวลา 14:30 น. ราคา 1,250.50 บาท",
  "วันนี้เรามี meeting สำคัญตอนเช้า และอย่าลืม update status ใน presentation ด้วยนะ",
  "สวัสดีครับ ยินดีต้อนรับสู่รายการพอดแคสต์เพื่อการเรียนรู้เทคโนโลยี AI ยุคใหม่",
  "เด็กๆ วิ่งเล่นกันสนุกสนานมากๆ ในวันหยุดสุดสัปดาห์นี้",
  "สวัสดีค่ะ มีบริการอะไรให้ช่วยเหลือเพิ่มเติมไหมคะ ยินดีให้บริการค่ะ",
  "ยินดีต้อนรับเจ้า วันนี้อากาศดีขนาด กิ๋นข้าวแลงแล้วกา ลำแต้ๆ เน้อ",
  "ยินดีต้อนรับเด้อจ้า สบายดีบ่ มื้อนี้เป็นจังใด๋แหน่ แซ่บอีหลีเด้อ",
  "สวัสดีพี่น้องชาวใต้ หรอยจังฮู้ วันนี้ไปทำไหรมามั่ง แหลงใต้ชัดเจน",
  "สวัสดีจ้ะพ่อแม่พี่น้อง วันนี้มาเจอกันอีกแล้วนะจ๊ะ สนุกสนานกันใหญ่เลยจ้ะ"
];

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", async () => {
  if (window.lucide) lucide.createIcons();

  // Setup text counter
  const textarea = document.getElementById("input-text");
  textarea.addEventListener("input", updateCharCount);
  applyPreset(0);

  // Setup sliders
  setupSliders();

  // Load models from API
  await loadModels();

  // Load history
  await loadHistory();
});

function switchTab(tabId) {
  const tabs = ['single', 'compare', 'guide'];
  tabs.forEach(t => {
    const view = document.getElementById(`view-${t}`);
    const btn = document.getElementById(`tab-btn-${t}`);
    if (t === tabId) {
      view.classList.remove('hidden');
      btn.classList.add('bg-indigo-600', 'text-white', 'shadow-lg', 'shadow-indigo-500/20');
      btn.classList.remove('bg-slate-800/80', 'text-slate-300');
    } else {
      view.classList.add('hidden');
      btn.classList.remove('bg-indigo-600', 'text-white', 'shadow-lg', 'shadow-indigo-500/20');
      btn.classList.add('bg-slate-800/80', 'text-slate-300');
    }
  });

  // Hide or show presets card based on tab
  const presetsCard = document.getElementById("presets-card");
  if (tabId === 'guide') {
    presetsCard.classList.add('hidden');
  } else {
    presetsCard.classList.remove('hidden');
  }

  if (window.lucide) lucide.createIcons();
}

function applyPreset(index, btnElem = null) {
  let text = "";
  if (btnElem && btnElem.getAttribute("data-text")) {
    text = btnElem.getAttribute("data-text");
  } else if (PRESETS && PRESETS[index]) {
    text = PRESETS[index];
  } else if (btnElem) {
    const p = btnElem.querySelector("p");
    if (p) text = p.textContent.trim();
  }

  if (!text) {
    const btns = document.querySelectorAll(".preset-btn");
    if (btns[index]) {
      text = btns[index].getAttribute("data-text") || btns[index].querySelector("p")?.textContent.trim() || "";
    }
  }

  const singleInput = document.getElementById("input-text");
  const compareInput = document.getElementById("compare-text");
  
  if (singleInput && text) {
    singleInput.value = text;
    updateCharCount();
    // Visual flash feedback
    singleInput.classList.add("ring-2", "ring-indigo-500");
    setTimeout(() => singleInput.classList.remove("ring-2", "ring-indigo-500"), 400);
  }
  if (compareInput && text) {
    compareInput.value = text;
  }

  // Highlight active preset button
  document.querySelectorAll(".preset-btn").forEach((b, i) => {
    if (i === index || b === btnElem) {
      b.classList.add("active-preset");
    } else {
      b.classList.remove("active-preset");
    }
  });

  // Auto select dialect engine when regional presets are clicked
  if (index === 6 && modelsData) { // Northern Thai
    selectEngine('meta_mms');
    const vs = document.getElementById("select-voice");
    if (vs) vs.value = "mms_nod_female";
  } else if (index === 7 && modelsData) { // Isan
    selectEngine('isan_trained');
    const vs = document.getElementById("select-voice");
    if (vs) vs.value = "isan_female_trained";
  } else if (index === 10 && modelsData) { // Dang Studio Clone
    selectEngine('voice_clone');
    const vs = document.getElementById("select-voice");
    if (vs) vs.value = "clone_male_dang";
  }
}

function updateCharCount() {
  const val = document.getElementById("input-text").value || "";
  document.getElementById("char-counter").textContent = `${val.length} ตัวอักษร`;
}

async function autoTranslateToKhamMueang() {
  const textarea = document.getElementById("input-text");
  const text = (textarea.value || "").trim();
  if (!text) {
    alert("กรุณาพิมพ์หรือเลือกข้อความภาษาไทยก่อน แล้วกดแปลงเป็นคำเมืองครับ");
    return;
  }
  try {
    const res = await fetch("/api/convert_khammueang", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, gender: "female" })
    });
    if (!res.ok) throw new Error("ไม่สามารถแปลงข้อความเป็นคำเมืองได้");
    const data = await res.json();
    if (data.khammueang) {
      textarea.value = data.khammueang;
      updateCharCount();
      // Auto select Northern Thai engine & female voice
      selectEngine("meta_mms");
      const vs = document.getElementById("select-voice");
      if (vs) vs.value = "mms_nod_female";
      // Visual flash feedback
      textarea.classList.add("ring-2", "ring-pink-500");
      setTimeout(() => textarea.classList.remove("ring-2", "ring-pink-500"), 500);
    }
  } catch (err) {
    alert("เกิดข้อผิดพลาดในการแปลงข้อความ: " + err.message);
  }
}

async function autoTranslateToIsan() {
  const textarea = document.getElementById("input-text");
  const text = (textarea.value || "").trim();
  if (!text) {
    alert("กรุณาพิมพ์หรือเลือกข้อความภาษาไทยก่อน แล้วกดแปลงเป็นภาษาอีสานครับ");
    return;
  }
  const vs = document.getElementById("select-voice");
  const currentVoice = vs ? vs.value : "";
  const currentGender = (currentVoice && currentVoice.includes("male")) ? "male" : "female";

  try {
    const res = await fetch("/api/convert_isan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, gender: currentGender })
    });
    if (!res.ok) throw new Error("ไม่สามารถแปลงข้อความเป็นภาษาอีสานได้");
    const data = await res.json();
    if (data.isan) {
      textarea.value = data.isan;
      updateCharCount();
      // Auto select YouTube-trained Isan engine & keep gender voice
      selectEngine("isan_trained");
      if (vs) {
        vs.value = currentGender === "male" ? "isan_male_trained" : "isan_female_trained";
      }
      // Visual flash feedback
      textarea.classList.add("ring-2", "ring-amber-500");
      setTimeout(() => textarea.classList.remove("ring-2", "ring-amber-500"), 500);
    }
  } catch (err) {
    alert("เกิดข้อผิดพลาดในการแปลงข้อความ: " + err.message);
  }
}

function setupSliders() {
  const speed = document.getElementById("param-speed");
  const speedVal = document.getElementById("speed-val");
  speed.addEventListener("input", (e) => {
    speedVal.textContent = `${parseFloat(e.target.value).toFixed(1)}x`;
  });

  const volume = document.getElementById("param-volume");
  const volumeVal = document.getElementById("volume-val");
  volume.addEventListener("input", (e) => {
    volumeVal.textContent = `${parseFloat(e.target.value).toFixed(1)}x`;
  });

  const noise = document.getElementById("param-noise");
  const noiseVal = document.getElementById("noise-val");
  noise.addEventListener("input", (e) => {
    noiseVal.textContent = `${parseFloat(e.target.value).toFixed(3)}`;
  });
}

function resetSliders() {
  document.getElementById("param-speed").value = 1.0;
  document.getElementById("speed-val").textContent = "1.0x";
  document.getElementById("param-volume").value = 1.0;
  document.getElementById("volume-val").textContent = "1.0x";
  document.getElementById("param-noise").value = 0.667;
  document.getElementById("noise-val").textContent = "0.667";
}

async function loadModels() {
  try {
    const res = await fetch("/api/models");
    modelsData = await res.json();
    renderEngineCards();
    selectEngine(modelsData.engines[0].id);
  } catch (err) {
    console.error("Failed to load models:", err);
  }
}

function renderEngineCards() {
  const container = document.getElementById("engine-options");
  container.innerHTML = "";

  modelsData.engines.forEach(engine => {
    const card = document.createElement("div");
    card.id = `engine-card-${engine.id}`;
    card.className = "engine-card p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 cursor-pointer hover:border-slate-700 transition-all";
    card.onclick = () => selectEngine(engine.id);

    const badgeColor = engine.type === 'local' ? 'text-emerald-400 bg-emerald-950/60 border-emerald-800/40' : 'text-sky-400 bg-sky-950/60 border-sky-800/40';

    card.innerHTML = `
      <div class="flex items-start justify-between">
        <div class="font-semibold text-xs text-white">${engine.name}</div>
        <span class="text-[9px] px-2 py-0.5 rounded-full border ${badgeColor} uppercase tracking-wider">${engine.badge}</span>
      </div>
      <p class="text-[11px] text-slate-400 mt-1 line-clamp-2">${engine.description}</p>
    `;
    container.appendChild(card);
  });
}

function selectEngine(engineId) {
  currentEngine = engineId;
  const engine = modelsData.engines.find(e => e.id === engineId);
  if (!engine) return;

  // Highlight selected card
  document.querySelectorAll(".engine-card").forEach(el => el.classList.remove("active"));
  const activeCard = document.getElementById(`engine-card-${engineId}`);
  if (activeCard) activeCard.classList.add("active");

  // Populate voice dropdown
  const voiceSelect = document.getElementById("select-voice");
  voiceSelect.innerHTML = "";
  engine.voices.forEach(v => {
    const opt = document.createElement("option");
    opt.value = v.id;
    const genderBadge = v.gender === 'female' ? '👩 หญิง' : (v.gender === 'male' ? '👨 ชาย' : '🗣️ กลาง');
    opt.textContent = `${v.name} [${genderBadge}]`;
    voiceSelect.appendChild(opt);
  });

  document.getElementById("engine-desc").textContent = engine.description;

  // Toggle controls visibility
  const noiseContainer = document.getElementById("noise-scale-container");
  if (engine.controls.noise_scale) {
    noiseContainer.style.display = "block";
  } else {
    noiseContainer.style.display = "none";
  }
}

async function startSingleSynthesis() {
  const text = document.getElementById("input-text").value.trim();
  if (!text) {
    alert("กรุณากรอกข้อความภาษาไทยที่ต้องการสังเคราะห์");
    return;
  }

  const voice = document.getElementById("select-voice").value;
  const speed = parseFloat(document.getElementById("param-speed").value);
  const volume = parseFloat(document.getElementById("param-volume").value);
  const noiseScale = parseFloat(document.getElementById("param-noise").value);

  const btn = document.getElementById("btn-synthesize");
  const emptyView = document.getElementById("player-empty");
  const loadingView = document.getElementById("player-loading");
  const activeView = document.getElementById("player-active");
  const statusTag = document.getElementById("status-tag");

  btn.disabled = true;
  emptyView.classList.add("hidden");
  activeView.classList.add("hidden");
  loadingView.classList.remove("hidden");
  statusTag.textContent = "กำลังสร้างเสียง...";
  statusTag.className = "text-xs px-2.5 py-1 rounded-full bg-indigo-950 text-indigo-400 font-medium animate-pulse";

  try {
    const res = await fetch("/api/synthesize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        engine: currentEngine,
        voice,
        speed,
        volume,
        noise_scale: noiseScale,
        auto_khammueang: voice.startsWith("mms_nod"),
        auto_isan: voice.startsWith("mms_isan")
      })
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "เกิดข้อผิดพลาดในการสังเคราะห์เสียง");
    }

    const data = await res.json();
    displaySingleResult(data);
    await loadHistory();
  } catch (err) {
    alert(`ข้อผิดพลาด: ${err.message}`);
    emptyView.classList.remove("hidden");
    statusTag.textContent = "เกิดข้อผิดพลาด";
    statusTag.className = "text-xs px-2.5 py-1 rounded-full bg-rose-950 text-rose-400 font-medium";
  } finally {
    btn.disabled = false;
    loadingView.classList.add("hidden");
  }
}

function displaySingleResult(data) {
  const activeView = document.getElementById("player-active");
  const statusTag = document.getElementById("status-tag");
  const audioEl = document.getElementById("audio-element");

  activeView.classList.remove("hidden");
  statusTag.textContent = "สำเร็จ";
  statusTag.className = "text-xs px-2.5 py-1 rounded-full bg-emerald-950 text-emerald-400 font-medium";

  document.getElementById("res-model-badge").textContent = `${data.engine.toUpperCase()} • ${data.voice}`;
  document.getElementById("res-latency").innerHTML = `<i data-lucide="zap" class="w-3 h-3 text-emerald-400"></i> ${data.latency_ms} ms`;
  document.getElementById("res-text-preview").textContent = `"${data.text}"`;
  document.getElementById("res-duration").textContent = `${data.duration} วินาที`;
  document.getElementById("res-size").textContent = `${data.size_kb} KB`;
  document.getElementById("res-time").textContent = data.timestamp;

  audioEl.src = data.audio_url;
  audioEl.play().catch(() => {}); // Auto-play if allowed by browser

  const dlBtn = document.getElementById("btn-download-audio");
  dlBtn.href = data.audio_url;
  dlBtn.download = data.filename;

  if (window.lucide) lucide.createIcons();
}

async function startCompareAll() {
  const text = document.getElementById("compare-text").value.trim();
  if (!text) {
    alert("กรุณากรอกข้อความสำหรับเปรียบเทียบ");
    return;
  }

  const btn = document.getElementById("btn-run-compare");
  const container = document.getElementById("compare-results-container");

  btn.disabled = true;
  btn.innerHTML = `<div class="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div> <span>กำลังสังเคราะห์ทุกโมเดลพร้อมกัน...</span>`;

  container.innerHTML = `
    <div class="col-span-full py-16 text-center space-y-3">
      <div class="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mx-auto"></div>
      <p class="text-sm text-indigo-300 font-semibold animate-pulse">กำลังประมวลผลเสียงผ่าน 6 โมเดลชั้นนำ...</p>
      <p class="text-xs text-slate-500">เปรียบเทียบ VachanaTTS, PyThaiTTS, Kokoro และ Edge Neural แบบขนาน</p>
    </div>
  `;

  try {
    const res = await fetch("/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    if (!res.ok) throw new Error("เกิดข้อผิดพลาดในการประมวลผลเปรียบเทียบ");

    const data = await res.json();
    renderCompareResults(data.results);
    await loadHistory();
  } catch (err) {
    alert(err.message);
    container.innerHTML = `<div class="col-span-full text-center text-rose-400 py-8">${err.message}</div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="zap" class="w-4 h-4 fill-white"></i> <span>⚡ สังเคราะห์เทียบทุกโมเดล (Compare All)</span>`;
    if (window.lucide) lucide.createIcons();
  }
}

function renderCompareResults(results) {
  const container = document.getElementById("compare-results-container");
  container.innerHTML = "";
  activeAudios = [];

  results.forEach((item, idx) => {
    const card = document.createElement("div");
    card.className = "bg-slate-950 border border-slate-800 rounded-xl p-4 shadow-lg hover:border-slate-700 transition-all flex flex-col justify-between";

    if (item.status === "error") {
      card.innerHTML = `
        <div class="space-y-2">
          <div class="text-xs font-bold text-rose-400">${item.label}</div>
          <p class="text-xs text-slate-500">Error: ${item.error}</p>
        </div>
      `;
    } else {
      card.innerHTML = `
        <div class="space-y-3">
          <div class="flex items-start justify-between gap-2">
            <div>
              <div class="text-xs font-bold text-white">${item.label}</div>
              <div class="text-[10px] text-slate-400 font-mono">${item.engine.toUpperCase()} • ${item.voice}</div>
            </div>
            <span class="text-[11px] font-mono font-medium text-emerald-400 bg-emerald-950/80 border border-emerald-800/40 px-2 py-0.5 rounded-full flex items-center gap-1">
              <i data-lucide="zap" class="w-3 h-3"></i> ${item.latency_ms} ms
            </span>
          </div>

          <audio id="compare-audio-${idx}" controls class="w-full mt-2"></audio>

          <div class="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/80">
            <span>ความยาว: <strong class="text-slate-200">${item.duration}s</strong></span>
            <span>ขนาด: <strong class="text-slate-200">${item.size_kb} KB</strong></span>
            <a href="${item.audio_url}" download="${item.filename}" class="text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1">
              <i data-lucide="download" class="w-3 h-3"></i> ดาวน์โหลด
            </a>
          </div>
        </div>
      `;
    }

    container.appendChild(card);

    if (item.status !== "error") {
      const audioEl = document.getElementById(`compare-audio-${idx}`);
      audioEl.src = item.audio_url;
      activeAudios.push(audioEl);

      // Auto pause others when this audio plays
      audioEl.addEventListener("play", () => {
        activeAudios.forEach(other => {
          if (other !== audioEl && !other.paused) {
            other.pause();
          }
        });
      });
    }
  });

  if (window.lucide) lucide.createIcons();
}

async function loadHistory() {
  try {
    const res = await fetch("/api/history");
    const data = await res.json();
    const list = document.getElementById("history-list");
    const count = document.getElementById("history-count");

    if (!data.history || data.history.length === 0) {
      list.innerHTML = `<p class="text-xs text-slate-600 text-center py-4">ยังไม่มีประวัติการสังเคราะห์</p>`;
      count.textContent = "0 รายการ";
      return;
    }

    count.textContent = `${data.history.length} รายการ`;
    list.innerHTML = "";

    data.history.forEach(item => {
      const row = document.createElement("div");
      row.className = "p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/60 flex items-center justify-between gap-3 text-xs";
      row.innerHTML = `
        <div class="truncate flex-1">
          <div class="flex items-center gap-1.5 font-medium text-slate-300">
            <span class="text-indigo-400 font-mono text-[11px]">${item.engine}</span>
            <span class="text-slate-500">•</span>
            <span class="text-slate-400 text-[11px]">${item.voice}</span>
            <span class="text-slate-600 text-[10px]">${item.timestamp}</span>
          </div>
          <p class="text-slate-400 truncate text-[11px] mt-0.5">"${item.text}"</p>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <button onclick="playHistoryAudio('${item.audio_url}')" class="p-1.5 rounded-md bg-slate-800 hover:bg-indigo-600 text-slate-300 hover:text-white transition-colors" title="เล่นเสียง">
            <i data-lucide="play" class="w-3.5 h-3.5"></i>
          </button>
          <a href="${item.audio_url}" download="${item.filename}" class="p-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors" title="ดาวน์โหลด">
            <i data-lucide="download" class="w-3.5 h-3.5"></i>
          </a>
        </div>
      `;
      list.appendChild(row);
    });

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error("Failed to load history:", err);
  }
}

function playHistoryAudio(url) {
  const audio = new Audio(url);
  audio.play().catch(e => console.error(e));
}

let activeHumanAudio = null;
function playRealHumanAudio(url, title) {
  const player = document.getElementById("audio-element");
  const resultBox = document.getElementById("result-card");
  const meta = document.getElementById("meta-engine");

  if (activeHumanAudio) {
    activeHumanAudio.pause();
    activeHumanAudio = null;
  }

  if (player) {
    player.src = url;
    player.play().catch(e => console.error(e));
    if (resultBox) resultBox.classList.remove("hidden");
    const metaVoice = document.getElementById("meta-voice");
    if (metaVoice) {
      metaVoice.textContent = title;
    }
    if (meta) {
      meta.textContent = "🎙️ เสียงคนอีสานแท้ 100% (YouTube)";
    }
  } else {
    activeHumanAudio = new Audio(url);
    activeHumanAudio.play().catch(e => console.error(e));
  }
}
