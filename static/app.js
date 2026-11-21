// Thai Voice Studio - Frontend App
let modelsData = null;
let currentEngine = "voice_clone";
let currentVoice = "clone_male_dang";
let activeAudios = [];

const SCRIPTS = {
  dang_long: "สวัสดีครับพี่น้อง มื้อนี้พบกับด่างสตูดิโอ มาเว้าพื้นหนังให้ฟัง หนังเรื่องนี้บอกได้คำเดียวว่าแซ่บคักแท้ มื้อนี้สิพาไปเบิ่งเรื่อง กรีนบุ๊ค หนังที่หมอผิวดำนั่งรถไปกับคนขับรถอิตาลี นั่งนำกันไปทั่วบ้านทั่วเมือง ตอนแรกกะบ่มักขี้หน้ากันดอก แต่พอดนไปดนมา กะฮักแพงกันคือพี่น้อง ลุงโทนี่เรากะหมัดหนักคัก ไผมากวนโอ๊ยนี่ลากไปกระทืบนอกร้านโลด บักตัวต้นเหตุนี่แลนหนีเกือบตาย นั่งเบิ่งแล้วม่วนหลายอีหลีสู ไผยังบ่ได้เบิ่ง ฟ้าวไปหาเบิ่งเด้อ แซ่บอีหลีตั๊วนี่",
  isan_eating: "สบายดีบ่พี่น้อง มื้อนี้เมื่อยนำงานหลาย มาเด้อมากินข้าวแลงนำกัน มื้อนี้มีตำบักหุ่งใส่ต่อนปลาร้าต้มสุก กลิ่นหอมหิ่นๆ กินกับผักบุ้งกะเพราลวก แล้วกะมีต้มไก่บ้านใส่ใบมะขามอ่อน ซดน้ำฮ้อนๆ แซ่บจนน้ำตาไหล ข้าวเหนียวฮ้อนๆ ปั้นตุ้ยคุ้ยใส่ถ้วยลาบหมูคักๆ กินอิ่มแล้วกะมานั่งล้อมวงเว้าพื้นความหลังกัน ลมหนาวพัดมาวี่ๆ นั่งผิงไฟใต้ถุนเรือน ฟังเสียงกบเสียงเขียดฮ้อง มีความสุขหลายตั๊วชีวิตบ้านเฮา",
  isan_joke: "มื้อหนึ่งบักเซียงกับบักจ่อย ชวนกันไปหากินปลาอยู่ทุ่งนา ยามแลงแดดร่มลมตก บักเซียงกะว่า มึงเบิ่งพุ้น ปลามันเต้นด่องๆ อยู่ในหนองน้ำ พอพากันหย่างไปฮอด แทนที่สิเป็นปลา ดันเป็นบักกบโตใหญ่ตาโปโล บักจ่อยฟ้าวตะครุบปั๊บ ปรากฏว่ามื่นขี้ตม ล้มคะมำลงก้นจ้ำเบ้า บักเซียงกะหัวขวัญจนท้องคัดท้องแข็ง บักจ่อยลุกขึ้นมาหน้าเปื้อนขี้ตมเบิด บอกว่า อย่าหัวขวัญหลายสู กูจับบักกบได้แล้วนี่เด้ คักหลายพี่น้องเอ๊ย",
  female_invite: "สวัสดีจ้าพ่อแม่พี่น้อง มื้อนี้สิพามาเที่ยวบ้านเฮาเด้อ อากาศยามเช้าดีหลาย หมอกลงจางๆ ทุ่งนาเขียวขจี ลมพัดเย็นสบาย มื้อนี้มีงานบุญบั้งไฟประจำปี เพิ่นจัดยิ่งใหญ่คัก มีขบวนแห่เซิ้งบั้งไฟ สาวงามฟ้อนรำนำหน้า หนุ่มๆ ตีกลองตุ้มม่วนซื่นโฮแซว ผู้เฒ่าผู้แก่กะพากันมาร่วมบุญฮอดวัด ขอเชิญชวนสุคนมาเที่ยวบ้านเฮาเด้อจ้า ยินดีต้อนรับสู่คนเด้อ",
  short_greeting: "สวัสดีครับพี่น้อง มื้อนี้มาเว้าพื้นหนังให้ฟังเด้อสู แซ่บอีหลีตั๊วนี่",
  southern_food: "สวัสดีสู วันนี้อากาศดีจังฮู้ นุ้ยจะพาไปกินข้าวแกงไตปลาที่หาดใหญ่ แหลงใต้ให้ฟังชาดหรอยแรง ลอกอกะมี ยานัดกะหวาน ได้แรงอกชาดสูเอ้ย วันนี้อย่ามัวแต่ขี้หก หลบบ้านไปกินข้าวกันตะ"
};

// Quick Speaker Mapping to Engine & Voice
const SPEAKER_MAP = {
  clone_male_dang: { engine: "voice_clone", voice: "clone_male_dang" },
  clone_female_wiri: { engine: "voice_clone", voice: "clone_female_wiri" },
  clone_male_kasin: { engine: "voice_clone", voice: "clone_male_kasin" },
  mms_nod_female: { engine: "meta_mms", voice: "mms_nod_female" },
  mms_sou_female: { engine: "meta_mms", voice: "mms_sou_female" },
  th_f_2: { engine: "vachanatts", voice: "th_f_2" }
};

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", async () => {
  if (window.lucide) lucide.createIcons();

  // Setup text counter
  const textarea = document.getElementById("input-text");
  if (textarea) {
    textarea.addEventListener("input", updateCharCount);
    // Default text
    fillScript("dang_long");
  }

  // Setup sliders
  setupSliders();

  // Load models from API
  await loadModels();

  // Select default quick speaker (Dang Studio)
  selectQuickSpeaker("clone_male_dang");

  // Load history
  await loadHistory();

  // Initialize Studio Waveform Visualizer & Hotkeys (Claude UI/UX)
  initWaveformVisualizer();
  setupKeyboardShortcuts();
});

function selectQuickSpeaker(speakerKey) {
  const mapping = SPEAKER_MAP[speakerKey];
  if (!mapping) return;

  currentEngine = mapping.engine;
  currentVoice = mapping.voice;

  // Highlight active quick speaker button
  document.querySelectorAll(".quick-spk-btn").forEach(btn => {
    btn.classList.remove(
      "border-amber-500", "border-pink-500", "border-sky-500", "border-rose-500", "border-emerald-500", "border-indigo-500",
      "shadow-md", "shadow-amber-500/20", "bg-gradient-to-b", "from-amber-950/40"
    );
    btn.classList.add("border-slate-800", "bg-slate-950/70");
  });

  const activeBtn = document.getElementById(`spk-${speakerKey}`);
  if (activeBtn) {
    activeBtn.classList.remove("border-slate-800", "bg-slate-950/70");
    if (speakerKey === 'clone_male_dang') {
      activeBtn.classList.add("border-amber-500", "bg-gradient-to-b", "from-amber-950/40", "shadow-md", "shadow-amber-500/10");
    } else if (speakerKey === 'clone_female_wiri') {
      activeBtn.classList.add("border-pink-500", "bg-slate-900", "shadow-md", "shadow-pink-500/10");
    } else if (speakerKey === 'clone_male_kasin') {
      activeBtn.classList.add("border-sky-500", "bg-slate-900", "shadow-md", "shadow-sky-500/10");
    } else if (speakerKey === 'mms_nod_female') {
      activeBtn.classList.add("border-rose-500", "bg-slate-900", "shadow-md", "shadow-rose-500/10");
    } else if (speakerKey === 'mms_sou_female') {
      activeBtn.classList.add("border-emerald-500", "bg-slate-900", "shadow-md", "shadow-emerald-500/10");
    } else {
      activeBtn.classList.add("border-indigo-500", "bg-slate-900", "shadow-md", "shadow-indigo-500/10");
    }
  }

  // Sync advanced dropdowns if available
  const engSelect = document.getElementById("select-engine-advanced");
  if (engSelect) engSelect.value = currentEngine;
  updateVoiceDropdown(currentEngine, currentVoice);
}

function fillScript(scriptKey) {
  const text = SCRIPTS[scriptKey];
  if (!text) return;

  const input = document.getElementById("input-text");
  if (input) {
    input.value = text;
    updateCharCount();
    // Visual flash
    input.classList.add("ring-2", "ring-amber-500");
    setTimeout(() => input.classList.remove("ring-2", "ring-amber-500"), 400);
  }

  // Auto-switch speaker according to script
  if (scriptKey === "dang_long" || scriptKey === "short_greeting" || scriptKey === "isan_joke") {
    selectQuickSpeaker("clone_male_dang");
  } else if (scriptKey === "female_invite") {
    selectQuickSpeaker("clone_female_wiri");
  } else if (scriptKey === "isan_eating") {
    selectQuickSpeaker("clone_male_kasin");
  } else if (scriptKey === "southern_food") {
    currentEngine = "meta_mms";
    currentVoice = "mms_sou_female";
    const engSelect = document.getElementById("select-engine-advanced");
    if (engSelect) engSelect.value = "meta_mms";
    updateVoiceDropdown("meta_mms", "mms_sou_female");
  }
}

function clearInputText() {
  const input = document.getElementById("input-text");
  if (input) {
    input.value = "";
    updateCharCount();
    input.focus();
  }
}

function updateCharCount() {
  const val = document.getElementById("input-text")?.value || "";
  const el = document.getElementById("char-counter");
  if (el) el.textContent = `${val.length} ตัวอักษร`;
}

function toggleAdvancedSettings() {
  const panel = document.getElementById("advanced-settings-panel");
  const txt = document.getElementById("advanced-toggle-text");
  if (!panel) return;

  if (panel.classList.contains("hidden")) {
    panel.classList.remove("hidden");
    if (txt) txt.textContent = "ซ่อนการตั้งค่า";
  } else {
    panel.classList.add("hidden");
    if (txt) txt.textContent = "ตั้งค่าเสียงขั้นสูง";
  }
  if (window.lucide) lucide.createIcons();
}

function toggleCompareMode() {
  const viewSingle = document.getElementById("view-single");
  const viewCompare = document.getElementById("view-compare");
  const label = document.getElementById("compare-toggle-label");

  if (viewCompare.classList.contains("hidden")) {
    viewCompare.classList.remove("hidden");
    viewSingle.classList.add("hidden");
    if (label) label.textContent = "กลับโหมดหลัก";
  } else {
    viewCompare.classList.add("hidden");
    viewSingle.classList.remove("hidden");
    if (label) label.textContent = "โหมดเทียบเสียง";
  }
  if (window.lucide) lucide.createIcons();
}

function onAdvancedEngineChange(engineId) {
  currentEngine = engineId;
  updateVoiceDropdown(engineId);
}

function updateVoiceDropdown(engineId, defaultVoiceId = null) {
  if (!modelsData) return;
  const engine = modelsData.engines.find(e => e.id === engineId);
  const voiceSelect = document.getElementById("select-voice");
  if (!engine || !voiceSelect) return;

  voiceSelect.innerHTML = "";
  engine.voices.forEach(v => {
    const opt = document.createElement("option");
    opt.value = v.id;
    const genderBadge = v.gender === 'female' ? '👩 หญิง' : (v.gender === 'male' ? '👨 ชาย' : '🗣️ กลาง');
    opt.textContent = `${v.name} [${genderBadge}]`;
    if (defaultVoiceId && v.id === defaultVoiceId) {
      opt.selected = true;
    }
    voiceSelect.appendChild(opt);
  });

  currentVoice = voiceSelect.value;
  voiceSelect.onchange = () => {
    currentVoice = voiceSelect.value;
  };
}

function setupSliders() {
  const speed = document.getElementById("param-speed");
  const speedVal = document.getElementById("speed-val");
  if (speed && speedVal) {
    speed.addEventListener("input", (e) => {
      speedVal.textContent = `${parseFloat(e.target.value).toFixed(1)}x`;
    });
  }

  const volume = document.getElementById("param-volume");
  const volumeVal = document.getElementById("volume-val");
  if (volume && volumeVal) {
    volume.addEventListener("input", (e) => {
      volumeVal.textContent = `${parseFloat(e.target.value).toFixed(1)}x`;
    });
  }

  const noise = document.getElementById("param-noise");
  const noiseVal = document.getElementById("noise-val");
  if (noise && noiseVal) {
    noise.addEventListener("input", (e) => {
      noiseVal.textContent = `${parseFloat(e.target.value).toFixed(3)}`;
    });
  }
}

async function loadModels() {
  try {
    const res = await fetch("/api/models");
    modelsData = await res.json();
    updateVoiceDropdown(currentEngine, currentVoice);
  } catch (err) {
    console.error("Failed to load models:", err);
  }
}

async function autoTranslateToIsan() {
  const textarea = document.getElementById("input-text");
  const text = (textarea?.value || "").trim();
  if (!text) {
    alert("กรุณาพิมพ์ข้อความก่อน แล้วกดแปลงเป็นภาษาอีสานครับ");
    return;
  }
  try {
    const res = await fetch("/api/convert_isan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, gender: "male" })
    });
    if (!res.ok) throw new Error("ไม่สามารถแปลงข้อความเป็นภาษาอีสานได้");
    const data = await res.json();
    if (data.isan) {
      textarea.value = data.isan;
      updateCharCount();
      selectQuickSpeaker("clone_male_dang");
      textarea.classList.add("ring-2", "ring-amber-500");
      setTimeout(() => textarea.classList.remove("ring-2", "ring-amber-500"), 500);
    }
  } catch (err) {
    alert("เกิดข้อผิดพลาดในการแปลงข้อความ: " + err.message);
  }
}

async function autoTranslateToKhamMueang() {
  const textarea = document.getElementById("input-text");
  const text = (textarea?.value || "").trim();
  if (!text) {
    alert("กรุณาพิมพ์ข้อความก่อน แล้วกดแปลงเป็นคำเมืองครับ");
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
      selectQuickSpeaker("mms_nod_female");
      textarea.classList.add("ring-2", "ring-pink-500");
      setTimeout(() => textarea.classList.remove("ring-2", "ring-pink-500"), 500);
    }
  } catch (err) {
    alert("เกิดข้อผิดพลาดในการแปลงข้อความ: " + err.message);
  }
}

async function autoTranslateToSouthern() {
  const textarea = document.getElementById("input-text");
  const text = (textarea?.value || "").trim();
  if (!text) {
    alert("กรุณาพิมพ์ข้อความก่อน แล้วกดแปลงเป็นภาษาใต้ครับ");
    return;
  }
  try {
    const res = await fetch("/api/convert_southern", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, gender: "female" })
    });
    if (!res.ok) throw new Error("ไม่สามารถแปลงข้อความเป็นภาษาใต้ได้");
    const data = await res.json();
    if (data.southern) {
      textarea.value = data.southern;
      updateCharCount();
      currentEngine = "meta_mms";
      currentVoice = "mms_sou_female";
      const engSelect = document.getElementById("select-engine-advanced");
      if (engSelect) engSelect.value = "meta_mms";
      updateVoiceDropdown("meta_mms", "mms_sou_female");
      textarea.classList.add("ring-2", "ring-emerald-500");
      setTimeout(() => textarea.classList.remove("ring-2", "ring-emerald-500"), 500);
    }
  } catch (err) {
    alert("เกิดข้อผิดพลาดในการแปลงข้อความ: " + err.message);
  }
}

async function startSingleSynthesis() {
  const text = document.getElementById("input-text").value.trim();
  if (!text) {
    alert("กรุณากรอกข้อความภาษาไทยหรืออีสานที่ต้องการสังเคราะห์");
    return;
  }

  const voiceSelect = document.getElementById("select-voice");
  const voice = (voiceSelect && voiceSelect.value) ? voiceSelect.value : currentVoice;
  const speed = parseFloat(document.getElementById("param-speed")?.value || 1.0);
  const volume = parseFloat(document.getElementById("param-volume")?.value || 1.0);
  const noiseScale = parseFloat(document.getElementById("param-noise")?.value || 0.667);

  const btn = document.getElementById("btn-synthesize");
  const emptyView = document.getElementById("player-empty");
  const loadingView = document.getElementById("player-loading");
  const activeView = document.getElementById("player-active");

  btn.disabled = true;
  if (emptyView) emptyView.classList.add("hidden");
  if (activeView) activeView.classList.add("hidden");
  if (loadingView) loadingView.classList.remove("hidden");

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
        auto_isan: false
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
    if (emptyView) emptyView.classList.remove("hidden");
  } finally {
    btn.disabled = false;
    if (loadingView) loadingView.classList.add("hidden");
  }
}

function displaySingleResult(data) {
  const activeView = document.getElementById("player-active");
  const audioEl = document.getElementById("audio-element");

  if (!activeView || !audioEl) return;
  activeView.classList.remove("hidden");

  let voiceLabel = data.voice;
  if (data.voice === "clone_male_dang") voiceLabel = "🤠 ด่าง สตูดิโอ (อีสานแท้)";
  else if (data.voice === "clone_female_wiri") voiceLabel = "🌸 สาวอีสาน WiriWiri";
  else if (data.voice === "clone_male_kasin") voiceLabel = "🌾 บ่าวอีสาน Kasin TV";
  else if (data.voice.startsWith("mms_nod")) voiceLabel = "🌸 สาวเหนือ (คำเมือง)";
  else if (data.voice === "th_f_2") voiceLabel = "🏛️ ไทยกลาง (Vachana)";

  document.getElementById("res-model-badge").textContent = voiceLabel;
  document.getElementById("res-latency").innerHTML = `<i data-lucide="zap" class="w-3.5 h-3.5 text-emerald-400"></i> ${data.latency_ms} ms`;
  document.getElementById("res-text-preview").textContent = `"${data.text}"`;
  document.getElementById("res-duration").textContent = `${data.duration}s`;
  document.getElementById("res-size").textContent = `${data.size_kb} KB`;

  audioEl.src = data.audio_url;
  audioEl.play().catch(() => {});

  const dlBtn = document.getElementById("btn-download-audio");
  if (dlBtn) {
    dlBtn.href = data.audio_url;
    dlBtn.download = data.filename;
  }

  if (window.lucide) lucide.createIcons();
}

function playRealHumanAudio(audioUrl, title) {
  const activeView = document.getElementById("player-active");
  const emptyView = document.getElementById("player-empty");
  const audioEl = document.getElementById("audio-element");

  if (emptyView) emptyView.classList.add("hidden");
  if (activeView) activeView.classList.remove("hidden");

  document.getElementById("res-model-badge").textContent = "🎙️ ต้นฉบับคนพูดจริง YouTube";
  document.getElementById("res-latency").innerHTML = `<i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-400"></i> เสียงคนจริง 100%`;
  document.getElementById("res-text-preview").textContent = title;
  
  audioEl.src = audioUrl;
  audioEl.play().catch(() => {});

  const dlBtn = document.getElementById("btn-download-audio");
  if (dlBtn) {
    dlBtn.href = audioUrl;
    dlBtn.download = audioUrl.split("/").pop();
  }

  // Scroll smoothly to player
  document.getElementById("player-card")?.scrollIntoView({ behavior: "smooth", block: "center" });
  if (window.lucide) lucide.createIcons();
}

async function loadHistory() {
  try {
    const res = await fetch("/api/history");
    const data = await res.json();
    const container = document.getElementById("history-list");
    const countEl = document.getElementById("history-count");
    if (!container) return;

    if (!data.history || data.history.length === 0) {
      container.innerHTML = `<p class="text-xs text-slate-600 text-center py-3">ยังไม่มีประวัติการสังเคราะห์</p>`;
      if (countEl) countEl.textContent = "0 รายการ";
      return;
    }

    if (countEl) countEl.textContent = `${data.history.length} รายการ`;
    container.innerHTML = "";

    data.history.slice(0, 8).forEach(item => {
      const div = document.createElement("div");
      div.className = "flex items-center justify-between p-2 rounded-lg bg-slate-950/70 border border-slate-800 hover:border-slate-700 text-xs gap-2 transition-all";
      div.innerHTML = `
        <div class="flex-1 truncate">
          <span class="text-amber-400 font-semibold mr-1.5">[${item.voice}]</span>
          <span class="text-slate-300">${item.text}</span>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <span class="text-[10px] text-slate-500 font-mono">${item.timestamp}</span>
          <button onclick="playHistoryItem('${item.audio_url}', '${item.text.replace(/'/g, "\\'")}')" class="p-1 text-slate-400 hover:text-amber-400 transition-colors" title="เล่นเสียง">
            <i data-lucide="play" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      `;
      container.appendChild(div);
    });

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error("Failed to load history:", err);
  }
}

function playHistoryItem(url, text) {
  const activeView = document.getElementById("player-active");
  const emptyView = document.getElementById("player-empty");
  const audioEl = document.getElementById("audio-element");

  if (emptyView) emptyView.classList.add("hidden");
  if (activeView) activeView.classList.remove("hidden");

  document.getElementById("res-text-preview").textContent = `"${text}"`;
  audioEl.src = url;
  audioEl.play().catch(() => {});
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
  btn.innerHTML = `<div class="w-4 h-4 border-2 border-slate-950/20 border-t-slate-950 rounded-full animate-spin"></div> <span>กำลังสังเคราะห์ทุกโมเดลพร้อมกัน...</span>`;

  container.innerHTML = `
    <div class="col-span-full py-12 text-center space-y-3">
      <div class="w-10 h-10 border-4 border-amber-500/20 border-t-amber-500 rounded-full animate-spin mx-auto"></div>
      <p class="text-sm text-amber-300 font-semibold animate-pulse">กำลังประมวลผลเสียงผ่านโมเดลชั้นนำ...</p>
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
    btn.innerHTML = `<i data-lucide="zap" class="w-4 h-4 fill-slate-950"></i> <span>⚡ สังเคราะห์เทียบทุกโมเดล (Compare All)</span>`;
    if (window.lucide) lucide.createIcons();
  }
}

function renderCompareResults(results) {
  const container = document.getElementById("compare-results-container");
  container.innerHTML = "";

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

          <audio id="compare-audio-${idx}" controls class="w-full mt-2 custom-audio-player"></audio>

          <div class="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/80">
            <span>ความยาว: <strong class="text-slate-200">${item.duration}s</strong></span>
            <span>ขนาด: <strong class="text-slate-200">${item.size_kb} KB</strong></span>
          </div>
        </div>
      `;
    }
    container.appendChild(card);

    if (item.status !== "error") {
      setTimeout(() => {
        const a = document.getElementById(`compare-audio-${idx}`);
        if (a) a.src = item.audio_url;
      }, 50);
    }
  });

  if (window.lucide) lucide.createIcons();
}


// 🎛️ Neon Web Audio API Waveform Visualizer & Hotkeys (Claude UI/UX Studio Suite)
let _audioCtx = null;
let _analyser = null;
let _sourceNode = null;
let _visRunning = false;

function initWaveformVisualizer() {
  const audioEl = document.getElementById("audio-element");
  const canvas = document.getElementById("waveform-canvas");
  if (!audioEl || !canvas) return;

  function ensureAudioContext() {
    if (!_audioCtx) {
      const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
      _audioCtx = new AudioCtxClass();
      _analyser = _audioCtx.createAnalyser();
      _analyser.fftSize = 64;
      try {
        _sourceNode = _audioCtx.createMediaElementSource(audioEl);
        _sourceNode.connect(_analyser);
        _analyser.connect(_audioCtx.destination);
      } catch (e) {}
    }
    if (_audioCtx.state === "suspended") {
      _audioCtx.resume();
    }
  }

  audioEl.addEventListener("play", () => {
    ensureAudioContext();
    if (!_visRunning) {
      _visRunning = true;
      drawWaveform();
    }
  });

  audioEl.addEventListener("pause", () => { _visRunning = false; });
  audioEl.addEventListener("ended", () => { _visRunning = false; });

  function drawWaveform() {
    if (!_visRunning) return;
    requestAnimationFrame(drawWaveform);
    const ctx = canvas.getContext("2d");
    const width = (canvas.width = canvas.clientWidth || 300);
    const height = (canvas.height = canvas.clientHeight || 56);
    if (!_analyser) return;

    const bufferLength = _analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    _analyser.getByteFrequencyData(dataArray);

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "rgba(2, 6, 23, 0.95)";
    ctx.fillRect(0, 0, width, height);

    const barWidth = Math.max(2, (width / bufferLength) * 1.8);
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const barHeight = (dataArray[i] / 255) * height * 0.85;
      const grad = ctx.createLinearGradient(0, height, 0, 0);
      grad.addColorStop(0, "rgba(245, 158, 11, 0.4)");
      grad.addColorStop(0.5, "rgba(16, 185, 129, 0.8)");
      grad.addColorStop(1, "rgba(56, 189, 248, 1)");

      ctx.fillStyle = grad;
      ctx.fillRect(x, height - barHeight, barWidth - 1.5, barHeight);
      x += barWidth;
    }
  }
}

function setupKeyboardShortcuts() {
  window.addEventListener("keydown", (e) => {
    if (e.code === "Space" && e.target.tagName !== "TEXTAREA" && e.target.tagName !== "INPUT") {
      const audioEl = document.getElementById("audio-element");
      if (audioEl && audioEl.src) {
        e.preventDefault();
        if (audioEl.paused) audioEl.play().catch(() => {});
        else audioEl.pause();
      }
    }
  });
}
