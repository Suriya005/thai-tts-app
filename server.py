import os
import sys
import time
import uuid
import asyncio
import traceback
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import soundfile as sf
import edge_tts
from gtts import gTTS

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
STATIC_DIR = BASE_DIR / "static"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

_pythaitts_models: Dict[str, Any] = {}
_history: List[Dict[str, Any]] = []

app = FastAPI(title="Thai TTS Benchmark & Testing Studio", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SynthesizeRequest(BaseModel):
    text: str
    engine: str = "vachanatts" # vachanatts, pythaitts, edge, gtts, meta_mms
    voice: Optional[str] = "th_f_2"
    speed: float = 1.0
    volume: float = 1.0
    noise_scale: float = 0.667
    auto_khammueang: Optional[bool] = False
    auto_isan: Optional[bool] = False

class ConvertRequest(BaseModel):
    text: str
    gender: Optional[str] = "female"

class CompareRequest(BaseModel):
    text: str
    targets: Optional[List[Dict[str, str]]] = None

def get_pythaitts_model(model_name: str):
    if model_name not in _pythaitts_models:
        from pythaitts import TTS as PyThaiTTS
        _pythaitts_models[model_name] = PyThaiTTS(pretrained=model_name)
    return _pythaitts_models[model_name]

@app.get("/api/system_info")
def get_system_info():
    gpu_name = "NVIDIA GeForce RTX 3050 Laptop GPU (4GB VRAM)"
    return {
        "python_version": sys.version.split()[0],
        "gpu": gpu_name,
        "supported_engines": ["Meta MMS (สำเนียงถิ่นไทย)", "VachanaTTS (ONNX/VITS)", "PyThaiTTS (Kokoro / MakHam / Lunarlist)", "Edge Neural TTS", "Google TTS"],
        "cached_dialects": ["คำเมือง เหนือ (mms_nod)", "อีสาน (mms_lao)", "ไทยกลาง (mms_tha)"],
        "cached_vachana_voices": ["th_f_1", "th_f_2", "th_m_1", "th_m_2"],
        "cached_pythai_models": ["fastthaig2p (Kokoro)", "makham_paradee", "lunarlist_onnx"]
    }

@app.get("/api/models")
def get_models():
    return {
        "engines": [
            {
                "id": "isan_trained",
                "name": "🔥 โมเดลเสียงอีสานแท้ (เทรนจาก YouTube)",
                "type": "local",
                "badge": "YouTube Trained",
                "description": "โมเดลเสียงภาษาอีสานแท้เทรนจากคลิปยูทูปคนอีสานจริง (สาวอีสาน: น้องครีม & WiriWiri, หนุ่มอีสาน: เสียงเป็นธรรมชาติสมจริง ไม่เป็นหุ่นยนต์ / บ่าวไทบ้าน) ชัดถ้อยชัดคำ ม่วนซื่นเป็นธรรมชาติ",
                "voices": [
                    {"id": "isan_female_trained", "name": "🌸 สาวอีสานแท้ (น้องครีม & WiriWiri) [👩 หญิง]", "gender": "female"},
                    {"id": "isan_male_trained", "name": "🤠 หนุ่มอีสานแท้ - เสียงเป็นธรรมชาติ สมจริง [👨 ชาย - แนะนำ]", "gender": "male"},
                    {"id": "isan_male_acoustic", "name": "🌾 บ่าวไทบ้าน (Acoustic DSP Morphed) [👨 ชาย]", "gender": "male"}
                ],
                "controls": {"speed": True, "volume": True, "noise_scale": False}
            },
            {
                "id": "meta_mms",
                "name": "Meta MMS (สำเนียงถิ่นไทย / Regional Dialects)",
                "type": "local",
                "badge": "Regional Dialects",
                "description": "โมเดล VITS สำเนียงท้องถิ่นจาก Meta Massively Multilingual Speech พร้อมโทนเสียงหญิงหวานธรรมชาติ (DSP) และเสียงชาย",
                "voices": [
                    {"id": "mms_nod_female", "name": "🌸 ภาษาเหนือ (คำเมือง - เสียงหญิง)", "gender": "female"},
                    {"id": "mms_nod_male", "name": "🌸 ภาษาเหนือ (คำเมือง - เสียงชาย)", "gender": "male"},
                    {"id": "mms_isan_female", "name": "🌾 ภาษาอีสาน (สำเนียงลาว - เสียงหญิง)", "gender": "female"},
                    {"id": "mms_isan_male", "name": "🌾 ภาษาอีสาน (สำเนียงลาว - เสียงชาย)", "gender": "male"},
                    {"id": "mms_tha_female", "name": "🏛️ ภาษาไทยกลาง (MMS - เสียงหญิง)", "gender": "female"},
                    {"id": "mms_tha_male", "name": "🏛️ ภาษาไทยกลาง (MMS - เสียงชาย)", "gender": "male"}
                ],
                "controls": {"speed": True, "volume": False, "noise_scale": False}
            },
            {
                "id": "vachanatts",
                "name": "VachanaTTS (VITS / Piper Architecture)",
                "type": "local",
                "badge": "Recommended / Natural",
                "description": "โมเดล VITS สำเนียงไทยแท้ พัฒนาจาก PiperTTS/Meta MMS ทำงานด้วย ONNX รวดเร็ว ไม่กินแรม",
                "voices": [
                    {"id": "th_f_2", "name": "th_f_2 - หญิง 2 (สมดุล ชัดเจน CER ต่ำ แนะนำ)", "gender": "female"},
                    {"id": "th_f_1", "name": "th_f_1 - หญิง 1 (เสียงหวาน เป็นธรรมชาติ)", "gender": "female"},
                    {"id": "th_m_1", "name": "th_m_1 - ชาย 1 (เสียงทุ้ม เหมาะกับพอดแคสต์/ข่าว CER ต่ำ)", "gender": "male"},
                    {"id": "th_m_2", "name": "th_m_2 - ชาย 2 (เสียงชายทางการ)", "gender": "male"}
                ],
                "controls": {"speed": True, "volume": True, "noise_scale": True}
            },
            {
                "id": "pythaitts",
                "name": "PyThaiTTS (NLP Engine Suite)",
                "type": "local",
                "badge": "Multi-Engine / Preprocessing",
                "description": "ชุดโมเดลจากคอมมูนิตี้ PyThaiNLP มีระบบแปลงตัวเลข ไม้ยมก และ IPA อังกฤษเป็นไทยในตัว",
                "voices": [
                    {"id": "fastthaig2p", "name": "FastThaiG2P (Kokoro-82M Thai - thai_som)", "gender": "female"},
                    {"id": "makham_paradee", "name": "MakHam Paradee (ขนาดเล็กพิเศษ ~8MB ออฟไลน์)", "gender": "female"},
                    {"id": "lunarlist_onnx", "name": "Lunarlist Thai ONNX (โมเดลน้ำหนักเบา)", "gender": "female"}
                ],
                "controls": {"speed": False, "volume": False, "noise_scale": False}
            },
            {
                "id": "edge",
                "name": "Microsoft Edge Neural TTS",
                "type": "cloud",
                "badge": "Cloud Baseline",
                "description": "ระบบเสียงสังเคราะห์ระดับพรีเมียมจาก Microsoft Neural สำหรับใช้วัดเปรียบเทียบมาตรฐาน (Baseline)",
                "voices": [
                    {"id": "th-TH-NiwatNeural", "name": "Niwat (ชาย - Neural HD เสถียร)", "gender": "male"},
                    {"id": "th-TH-PremwadeeNeural", "name": "Premwadee (หญิง - Neural HD)", "gender": "female"}
                ],
                "controls": {"speed": True, "volume": False, "noise_scale": False}
            },
            {
                "id": "gtts",
                "name": "Google Translate TTS",
                "type": "cloud",
                "badge": "Standard Baseline",
                "description": "เสียง Google Thai มาตรฐานดั้งเดิม สำหรับทดสอบเปรียบเทียบความก้าวหน้าของ Deep Learning",
                "voices": [
                    {"id": "th", "name": "Google Thai (Default)", "gender": "female"}
                ],
                "controls": {"speed": False, "volume": False, "noise_scale": False}
            }
        ]
    }

async def generate_speech(engine: str, voice: str, text: str, speed: float = 1.0, volume: float = 1.0, noise_scale: float = 0.667, auto_khammueang: bool = False, auto_isan: bool = False) -> Dict[str, Any]:
    file_id = str(uuid.uuid4())[:12]
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("ข้อความว่างเปล่า กรุณากรอกข้อความภาษาไทย")
    
    t0 = time.time()
    out_ext = "wav"
    out_filename = f"{engine}_{voice}_{file_id}.{out_ext}"
    out_path = OUTPUT_DIR / out_filename

    if engine == "isan_trained":
        import isan_voice_engine
        import isan_converter
        target_gender = "female" if "female" in voice else "male"
        clean_text = isan_converter.to_isan(clean_text, gender=target_gender)
        await asyncio.to_thread(
            isan_voice_engine.synthesize_trained_isan,
            text=clean_text,
            voice_id=voice,
            out_path=str(out_path),
            speed=speed,
            volume=volume,
            auto_translate=False
        )
    elif engine == "meta_mms":
        import dialect_engine
        if voice.startswith("mms_nod") and auto_khammueang:
            import khammueang_converter
            target_gender = "female" if "female" in voice else "male"
            clean_text = khammueang_converter.to_khammueang(clean_text, gender=target_gender)
        elif voice.startswith("mms_isan") and auto_isan:
            import isan_converter
            target_gender = "female" if "female" in voice else "male"
            clean_text = isan_converter.to_isan(clean_text, gender=target_gender)
        await asyncio.to_thread(
            dialect_engine.synthesize_dialect,
            dialect_id=voice,
            text=clean_text,
            out_path=str(out_path),
            speed=speed
        )
    elif engine == "vachanatts":
        from vachanatts import TTS as VachanaTTS
        await asyncio.to_thread(
            VachanaTTS,
            clean_text,
            voice=voice,
            output=str(out_path),
            volume=volume,
            speed=speed,
            noise_scale=noise_scale
        )
    elif engine == "pythaitts":
        model = await asyncio.to_thread(get_pythaitts_model, voice)
        await asyncio.to_thread(model.tts, clean_text, filename=str(out_path))
    elif engine == "edge":
        out_filename = f"{engine}_{voice}_{file_id}.mp3"
        out_path = OUTPUT_DIR / out_filename
        rate_str = f"{int((speed - 1.0) * 100):+d}%"
        try:
            communicate = edge_tts.Communicate(clean_text, voice, rate=rate_str)
            await communicate.save(str(out_path))
        except Exception:
            # Fallback to Niwat or gTTS if Premwadee fails
            fallback_voice = "th-TH-NiwatNeural" if voice != "th-TH-NiwatNeural" else voice
            try:
                communicate = edge_tts.Communicate(clean_text, fallback_voice)
                await communicate.save(str(out_path))
            except Exception:
                def _run_gtts():
                    tts = gTTS(text=clean_text, lang='th')
                    tts.save(str(out_path))
                await asyncio.to_thread(_run_gtts)
    elif engine == "gtts":
        out_filename = f"{engine}_{voice}_{file_id}.mp3"
        out_path = OUTPUT_DIR / out_filename
        def _run_gtts():
            tts = gTTS(text=clean_text, lang='th')
            tts.save(str(out_path))
        await asyncio.to_thread(_run_gtts)
    else:
        raise ValueError(f"Engine ไม่ถูกต้อง: {engine}")

    elapsed_ms = int((time.time() - t0) * 1000)
    
    # Calculate duration and size
    duration = 0.0
    try:
        if str(out_path).endswith(".wav"):
            data, samplerate = sf.read(str(out_path))
            duration = round(len(data) / float(samplerate), 2)
        else:
            file_bytes = os.path.getsize(out_path)
            duration = round(file_bytes / 4000.0, 2)
    except Exception:
        pass

    file_size_kb = round(os.path.getsize(out_path) / 1024, 1)

    result = {
        "id": file_id,
        "engine": engine,
        "voice": voice,
        "text": clean_text,
        "audio_url": f"/api/audio/{out_filename}",
        "filename": out_filename,
        "latency_ms": elapsed_ms,
        "duration": duration,
        "size_kb": file_size_kb,
        "timestamp": time.strftime("%H:%M:%S")
    }

    _history.insert(0, result)
    if len(_history) > 30:
        _history.pop()

    return result

@app.post("/api/convert_khammueang")
def api_convert_khammueang(req: ConvertRequest):
    import khammueang_converter
    converted = khammueang_converter.to_khammueang(req.text, gender=req.gender or "female")
    return {"original": req.text, "khammueang": converted}

@app.post("/api/convert_isan")
def api_convert_isan(req: ConvertRequest):
    import isan_converter
    converted = isan_converter.to_isan(req.text, gender=req.gender or "female")
    return {"original": req.text, "isan": converted}

@app.post("/api/synthesize")
async def api_synthesize(req: SynthesizeRequest):
    try:
        res = await generate_speech(
            engine=req.engine,
            voice=req.voice or "th_f_2",
            text=req.text,
            speed=req.speed,
            volume=req.volume,
            noise_scale=req.noise_scale,
            auto_khammueang=req.auto_khammueang or False,
            auto_isan=req.auto_isan or False
        )
        return res
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compare")
async def api_compare(req: CompareRequest):
    targets = req.targets or [
        {"engine": "isan_trained", "voice": "isan_female_trained", "label": "🔥 สาวอีสานแท้ (เทรนจาก YouTube - หญิง)"},
        {"engine": "isan_trained", "voice": "isan_male_trained", "label": "🔥 หนุ่มอีสานแท้ (เทรนจาก YouTube - ชาย)"},
        {"engine": "meta_mms", "voice": "mms_nod_female", "label": "🌸 Meta MMS (คำเมือง เหนือ - หญิง)"},
        {"engine": "vachanatts", "voice": "th_f_2", "label": "VachanaTTS (หญิง 2 - สมดุล/CER ต่ำ)"},
        {"engine": "edge", "voice": "th-TH-PremwadeeNeural", "label": "Edge Neural (คุณเปรมวดี - หญิง)"},
        {"engine": "edge", "voice": "th-TH-NiwatNeural", "label": "Edge Neural (คุณนิวัฒน์ - ชาย)"}
    ]

    async def _safe_gen(target):
        try:
            res = await generate_speech(
                engine=target["engine"],
                voice=target["voice"],
                text=req.text,
                speed=1.0,
                volume=1.0
            )
            res["label"] = target["label"]
            res["status"] = "success"
            return res
        except Exception as e:
            return {
                "engine": target["engine"],
                "voice": target["voice"],
                "label": target["label"],
                "status": "error",
                "error": str(e)
            }

    tasks = [_safe_gen(t) for t in targets]
    results = await asyncio.gather(*tasks)
    return {"results": results, "text": req.text}

@app.get("/api/audio/{filename}")
def get_audio(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์เสียง")
    media_type = "audio/wav" if filename.endswith(".wav") else "audio/mpeg"
    return FileResponse(file_path, media_type=media_type)

@app.get("/api/history")
def get_history():
    return {"history": _history}

app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("Starting Thai TTS Benchmark Studio on http://127.0.0.1:8765")
    uvicorn.run(app, host="127.0.0.1", port=8765)
