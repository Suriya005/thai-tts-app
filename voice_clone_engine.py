"""
voice_clone_engine.py - Zero-Shot Neural Voice Cloning Engine using F5-TTS
Performs authentic timbre, pitch contour, and accent cloning from native reference audio clips.
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
import soundfile as sf
import torch
import torchaudio

# Monkeypatch torchaudio.load with soundfile on Windows
def _custom_torchaudio_load(filepath, *args, **kwargs):
    data, sr = sf.read(filepath)
    tensor = torch.from_numpy(data).float()
    if tensor.ndim == 1:
        tensor = tensor.unsqueeze(0)
    else:
        tensor = tensor.t()
    return tensor, sr

torchaudio.load = _custom_torchaudio_load

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Reference Speakers Catalog
CLONE_SPEAKERS = {
    "clone_male_dang": {
        "id": "clone_male_dang",
        "name": "🤠 ด่าง สตูดิโอ (โคลนเสียงและสำเนียงแท้ 100% - เว้าพื้นหนัง)",
        "gender": "male",
        "ref_audio": str(OUTPUT_DIR / "real_human_isan" / "male" / "clip_dang_1.wav"),
        "ref_text": "ข้อนนึงสองสิกเป็นคนมีอีกที่คนเธอนั้น",
        "description": "โคลนเสียงพูดและสำเนียงพากย์อีสานของ ด่าง สตูดิโอ จากคลิปเว้าพื้นหนัง Green Book แบบ 100%"
    },
    "clone_female_wiri": {
        "id": "clone_female_wiri",
        "name": "🌸 สาวอีสาน WiriWiri (โคลนเสียงแท้ 100%)",
        "gender": "female",
        "ref_audio": str(OUTPUT_DIR / "real_human_isan" / "female" / "clip_1.wav"),
        "ref_text": "สวัสดีค่ะ ยินดีต้อนรับสู่ช่องวิริวิรินะคะ",
        "description": "โคลนเสียงสาวอีสานขอนแก่นแท้ จากคลิป WiriWiri"
    },
    "clone_male_kasin": {
        "id": "clone_male_kasin",
        "name": "🌾 บ่าวอีสาน Kasin TV (โคลนเสียงแท้ 100%)",
        "gender": "male",
        "ref_audio": str(OUTPUT_DIR / "real_human_isan" / "male" / "clip_1.wav"),
        "ref_text": "สวัสดีครับพี่น้อง มื้อนี้มาเว้าสู่กันฟังเด้อครับ",
        "description": "โคลนเสียงบ่าวอีสาน Kasin TV สำเนียงอีสานแท้"
    }
}

_f5_model = None

def get_device():
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"

def load_f5_model():
    global _f5_model
    if _f5_model is None:
        from f5_tts.api import F5TTS
        device = get_device()
        print(f"[VoiceClone] Loading F5-TTS Neural Voice Cloner on device: {device.upper()}...", flush=True)
        _f5_model = F5TTS(device=device)
        print("[VoiceClone] F5-TTS Loaded successfully!", flush=True)
    return _f5_model

def synthesize_cloned_voice(
    voice_id: str,
    text: str,
    out_path: str,
    speed: float = 1.0,
    nfe_step: int = 16,
    auto_isan: bool = True
) -> Dict[str, Any]:
    """
    Performs True Zero-Shot Voice Cloning of target speaker using F5-TTS Flow Matching Diffusion.
    """
    t0 = time.time()
    
    if voice_id not in CLONE_SPEAKERS:
        voice_id = "clone_male_dang"
    
    spk = CLONE_SPEAKERS[voice_id]
    
    # 1. Translate to authentic colloquial Isan if enabled
    if auto_isan:
        import isan_converter
        clean_text = isan_converter.to_isan(text, gender=spk["gender"])
    else:
        clean_text = text.strip()

    # 2. Check reference audio
    ref_audio = spk["ref_audio"]
    if not os.path.exists(ref_audio):
        fallback_ref = str(BASE_DIR / "training_data" / "male" / "raw_dang_studio.wav")
        if os.path.exists(fallback_ref):
            ref_audio = fallback_ref
        else:
            raise FileNotFoundError(f"Reference audio not found: {ref_audio}")

    # 3. Load Model and Infer
    model = load_f5_model()
    
    # If on CPU, limit nfe_step for responsiveness
    device = get_device()
    actual_steps = min(nfe_step, 12) if device == "cpu" else nfe_step
    
    print(f"[VoiceClone] Cloning voice for: {spk['name']} | Steps: {actual_steps} | Device: {device}...", flush=True)
    
    wav, sr, spec = model.infer(
        ref_file=ref_audio,
        ref_text=spk["ref_text"],
        gen_text=clean_text,
        nfe_step=actual_steps,
        speed=speed,
        file_wave=out_path
    )
    
    elapsed_ms = int((time.time() - t0) * 1000)
    audio_info, out_sr = sf.read(out_path)
    duration = round(len(audio_info) / float(out_sr), 2)
    file_size_kb = round(os.path.getsize(out_path) / 1024, 1)

    return {
        "engine": "voice_clone",
        "voice": voice_id,
        "name": spk["name"],
        "gender": spk["gender"],
        "text": clean_text,
        "duration_sec": duration,
        "file_size_kb": file_size_kb,
        "sample_rate": out_sr,
        "latency_ms": elapsed_ms,
        "device": device
    }

if __name__ == "__main__":
    test_text = "สวัสดีครับพี่น้อง มื้อนี้มาเว้าพื้นหนังให้ฟัง สบายดีบ่สู เป็นจั่งใด๋แหน่ แซ่บอีหลีตั๊วนี่"
    out = "output/test_cli_clone_dang.wav"
    res = synthesize_cloned_voice("clone_male_dang", test_text, out, nfe_step=8)
    print("Result:", res)
