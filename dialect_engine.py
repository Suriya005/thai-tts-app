"""
dialect_engine.py - Regional Thai Dialects Engine using Meta MMS & VITS with Studio DSP
Supports:
- Northern Thai / คำเมือง (facebook/mms-tts-nod) - Male & Female (Studio Pitch & Formant Shift)
- Isan / Northeastern Thai (facebook/mms-tts-lao with Thai-to-Lao phonetic bridge) - Male & Female
- Central Thai / ไทยกลาง (facebook/mms-tts-tha) - Male & Female
"""

import os
import re
import time
from pathlib import Path
from typing import Dict, Any, Optional
import torch
import soundfile as sf
from transformers import VitsModel, AutoTokenizer

# Thai to Lao Unicode script transliteration mapping
THAI_TO_LAO_MAP = {
    # Consonants
    'ก': 'ກ', 'ข': 'ຂ', 'ฃ': 'ຂ', 'ค': 'ຄ', 'ฅ': 'ຄ', 'ฆ': 'ຄ',
    'ง': 'ງ', 'จ': 'ຈ', 'ฉ': 'ສ', 'ช': 'ຊ', 'ซ': 'ຊ', 'ฌ': 'ຊ',
    'ญ': 'ຍ', 'ฎ': 'ດ', 'ฏ': 'ຕ', 'ฐ': 'ຖ', 'ฑ': 'ທ', 'ฒ': 'ທ',
    'ณ': 'ນ', 'ด': 'ດ', 'ต': 'ຕ', 'ถ': 'ຖ', 'ท': 'ທ', 'ธ': 'ท',
    'น': 'ນ', 'บ': 'ບ', 'ป': 'ປ', 'ผ': 'ຜ', 'ฝ': 'ຝ', 'พ': 'ພ',
    'ฟ': 'ຟ', 'ภ': 'ພ', 'ม': 'ມ', 'ย': 'ຍ', 'ร': 'ຣ', 'ฤ': 'ຣິ',
    'ล': 'ລ', 'ว': 'ວ', 'ศ': 'ສ', 'ษ': 'ສ', 'ส': 'ສ', 'ห': 'ຫ',
    'ฬ': 'ລ', 'อ': 'ອ', 'ฮ': 'ຮ',
    # Vowels
    'ะ': 'ະ', 'ั': 'ັ', 'า': 'າ', 'ำ': 'ໍາ', 'ิ': 'ິ', 'ี': 'ີ',
    'ึ': 'ຶ', 'ื': 'ື', 'ุ': 'ຸ', 'ู': 'ູ',
    'เ': 'ເ', 'แ': 'ແ', 'โ': 'ໂ', 'ใ': 'ໃ', 'ไ': 'ໄ',
    # Tone marks & signs
    '่': '່', '้': '້', '๊': '້', '๋': '້',
    '์': '', '็': 'ັ', ' ': ' '
}

def thai_to_lao(text: str) -> str:
    """Converts Thai script text to Lao script for the Lao MMS-TTS model."""
    chars = []
    for c in text:
        chars.append(THAI_TO_LAO_MAP.get(c, c))
    return "".join(chars)

DIALECT_CATALOG = {
    "mms_nod_female": {
        "id": "mms_nod_female",
        "name": "ภาษาเหนือ (คำเมือง - เสียงหญิง)",
        "region": "Northern",
        "gender": "female",
        "badge": "Meta MMS + Female DSP",
        "repo": "facebook/mms-tts-nod",
        "script": "thai",
        "pitch_semitones": 4.0,
        "sample": "ยินดีต้อนรับเจ้า วันนี้อากาศดีขนาด กิ๋นข้าวแลงแล้วกา ลำแต้ๆ เน้อ"
    },
    "mms_nod_male": {
        "id": "mms_nod_male",
        "name": "ภาษาเหนือ (คำเมือง - เสียงชาย)",
        "region": "Northern",
        "gender": "male",
        "badge": "Meta MMS Native",
        "repo": "facebook/mms-tts-nod",
        "script": "thai",
        "pitch_semitones": 0.0,
        "sample": "ยินดีต้อนรับครับ วันนี้อากาศดีขนาด กิ๋นข้าวแลงแล้วกา ลำแต้ๆ ครับ"
    },
    "mms_nod": {
        "id": "mms_nod",
        "name": "ภาษาเหนือ (คำเมือง / ค่าเริ่มต้น)",
        "region": "Northern",
        "gender": "female",
        "badge": "Meta MMS",
        "repo": "facebook/mms-tts-nod",
        "script": "thai",
        "pitch_semitones": 4.0,
        "sample": "ยินดีต้อนรับเจ้า วันนี้อากาศดีขนาด กิ๋นข้าวแลงแล้วกา ลำแต้ๆ เน้อ"
    },
    "mms_isan_female": {
        "id": "mms_isan_female",
        "name": "ภาษาอีสาน (สำเนียงลาว - เสียงหญิง)",
        "region": "Northeastern",
        "gender": "female",
        "badge": "Meta MMS + Female DSP",
        "repo": "facebook/mms-tts-lao",
        "script": "lao",
        "pitch_semitones": 4.0,
        "sample": "ยินดีต้อนรับเด้อจ้า สบายดีบ่ มื้อนี้เป็นจังใด๋แหน่ แซ่บอีหลีเด้อค่ะ"
    },
    "mms_isan_male": {
        "id": "mms_isan_male",
        "name": "ภาษาอีสาน (สำเนียงลาว - เสียงชาย)",
        "region": "Northeastern",
        "gender": "male",
        "badge": "Meta MMS + Script Bridge",
        "repo": "facebook/mms-tts-lao",
        "script": "lao",
        "pitch_semitones": 0.0,
        "sample": "ยินดีต้อนรับเด้อครับ สบายดีบ่ มื้อนี้เป็นจังใด๋แหน่ แซ่บอีหลีเด้อครับ"
    },
    "mms_isan": {
        "id": "mms_isan",
        "name": "ภาษาอีสาน (สำเนียงลาว / ค่าเริ่มต้น)",
        "region": "Northeastern",
        "gender": "female",
        "badge": "Meta MMS",
        "repo": "facebook/mms-tts-lao",
        "script": "lao",
        "pitch_semitones": 4.0,
        "sample": "ยินดีต้อนรับเด้อจ้า สบายดีบ่ มื้อนี้เป็นจังใด๋แหน่ แซ่บอีหลีเด้อค่ะ"
    },
    "mms_tha_female": {
        "id": "mms_tha_female",
        "name": "ภาษาไทยกลาง (MMS - เสียงหญิง)",
        "region": "Central",
        "gender": "female",
        "badge": "Meta MMS + Female DSP",
        "repo": "facebook/mms-tts-tha",
        "script": "thai",
        "pitch_semitones": 4.0,
        "sample": "สวัสดีค่ะ ยินดีต้อนรับสู่ระบบสังเคราะห์เสียงภาษาไทย"
    },
    "mms_tha_male": {
        "id": "mms_tha_male",
        "name": "ภาษาไทยกลาง (MMS - เสียงชาย)",
        "region": "Central",
        "gender": "male",
        "badge": "Meta MMS Native",
        "repo": "facebook/mms-tts-tha",
        "script": "thai",
        "pitch_semitones": 0.0,
        "sample": "สวัสดีครับ ยินดีต้อนรับสู่ระบบสังเคราะห์เสียงภาษาไทย"
    },
    "mms_tha": {
        "id": "mms_tha",
        "name": "ภาษาไทยกลาง (MMS / ค่าเริ่มต้น)",
        "region": "Central",
        "gender": "female",
        "badge": "Meta MMS",
        "repo": "facebook/mms-tts-tha",
        "script": "thai",
        "pitch_semitones": 4.0,
        "sample": "สวัสดีค่ะ ยินดีต้อนรับสู่ระบบสังเคราะห์เสียงภาษาไทย"
    }
}

_models_cache: Dict[str, VitsModel] = {}
_tokenizers_cache: Dict[str, AutoTokenizer] = {}

def load_dialect_model(dialect_id: str):
    if dialect_id not in DIALECT_CATALOG:
        raise ValueError(f"Unknown dialect id: {dialect_id}")
    
    repo = DIALECT_CATALOG[dialect_id]["repo"]
    if repo not in _models_cache:
        tokenizer = AutoTokenizer.from_pretrained(repo)
        model = VitsModel.from_pretrained(repo)
        _models_cache[repo] = model
        _tokenizers_cache[repo] = tokenizer
    return _models_cache[repo], _tokenizers_cache[repo]

def apply_female_voice_dsp(audio_data, sample_rate: int, semitones: float = 4.0):
    """
    Applies high-grade vocal pitch and formant shaping via Spotify Pedalboard DSP.
    Shifts the fundamental vocal frequency (+4 semitones) into a sweet, natural female tone
    while clearing deep male chest resonance and enhancing vocal brilliance.
    """
    try:
        from pedalboard import Pedalboard, PitchShift, HighpassFilter, HighShelfFilter, Compressor, Gain
        board = Pedalboard([
            HighpassFilter(cutoff_frequency_hz=110.0),
            PitchShift(semitones=semitones),
            HighShelfFilter(cutoff_frequency_hz=2800.0, gain_db=2.5),
            Compressor(threshold_db=-14.0, ratio=2.0),
            Gain(gain_db=1.0)
        ])
        return board(audio_data, sample_rate)
    except Exception as e:
        print(f"[Warning] Failed to apply female DSP ({e}), returning original audio")
        return audio_data

def synthesize_dialect(
    dialect_id: str,
    text: str,
    out_path: str,
    speed: float = 1.0,
    pitch_semitones: Optional[float] = None
) -> Dict[str, Any]:
    if dialect_id not in DIALECT_CATALOG:
        raise ValueError(f"Unknown dialect id: {dialect_id}")

    dialect_info = DIALECT_CATALOG[dialect_id]
    model, tokenizer = load_dialect_model(dialect_id)

    # Preprocessing
    processed_text = text.strip()
    if dialect_info["script"] == "lao":
        processed_text = thai_to_lao(processed_text)

    # Tokenization
    inputs = tokenizer(processed_text, return_tensors="pt")
    
    t0 = time.time()
    with torch.no_grad():
        waveform = model(**inputs).waveform
    elapsed_ms = int((time.time() - t0) * 1000)

    # Convert tensor to numpy
    audio_data = waveform[0].cpu().numpy()
    sample_rate = model.config.sampling_rate

    # Speed adjustment (resample)
    if speed != 1.0 and 0.5 <= speed <= 2.0:
        import scipy.signal
        new_len = int(len(audio_data) / speed)
        audio_data = scipy.signal.resample(audio_data, new_len)

    # Pitch / Tone adjustment (Female voice transformation)
    semitones = pitch_semitones if pitch_semitones is not None else dialect_info.get("pitch_semitones", 0.0)
    if semitones != 0.0:
        audio_data = apply_female_voice_dsp(audio_data, sample_rate, semitones=semitones)

    # Write final audio to WAV
    sf.write(out_path, audio_data, samplerate=sample_rate)

    duration = round(len(audio_data) / float(sample_rate), 2)
    file_size_kb = round(os.path.getsize(out_path) / 1024, 1)

    return {
        "dialect_id": dialect_id,
        "name": dialect_info["name"],
        "region": dialect_info["region"],
        "gender": dialect_info.get("gender", "neutral"),
        "duration_sec": duration,
        "file_size_kb": file_size_kb,
        "sample_rate": sample_rate,
        "latency_ms": elapsed_ms
    }
