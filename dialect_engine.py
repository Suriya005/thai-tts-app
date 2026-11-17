"""
dialect_engine.py - Regional Thai Dialects Engine using Meta MMS & VITS
Supports:
- Northern Thai / คำเมือง (facebook/mms-tts-nod)
- Isan / Northeastern Thai (facebook/mms-tts-lao with Thai-to-Lao phonetic bridge)
- Central Thai / ไทยกลาง (facebook/mms-tts-tha)
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
    'ณ': 'ນ', 'ด': 'ດ', 'ต': 'ຕ', 'ถ': 'ຖ', 'ท': 'ທ', 'ธ': 'ທ',
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
    "mms_nod": {
        "id": "mms_nod",
        "name": "ภาษาเหนือ (คำเมือง / Lanna)",
        "region": "Northern",
        "badge": "Meta MMS Native",
        "repo": "facebook/mms-tts-nod",
        "script": "thai",
        "sample": "ยินดีต้อนรับเจ้า วันนี้อากาศดีขนาด กิ๋นข้าวแลงแล้วกา"
    },
    "mms_isan": {
        "id": "mms_isan",
        "name": "ภาษาอีสาน (Isan / Lao Phonology)",
        "region": "Northeastern",
        "badge": "Meta MMS + Script Bridge",
        "repo": "facebook/mms-tts-lao",
        "script": "lao",
        "sample": "ยินดีต้อนรับเด้อครับ สบายดีบ่ มื้อนี้เป็นจังใด๋แหน่"
    },
    "mms_tha": {
        "id": "mms_tha",
        "name": "ภาษาไทยกลาง (Central Thai - MMS)",
        "region": "Central",
        "badge": "Meta MMS Native",
        "repo": "facebook/mms-tts-tha",
        "script": "thai",
        "sample": "สวัสดีครับ ยินดีต้อนรับสู่ระบบสังเคราะห์เสียงภาษาไทย"
    }
}

_models_cache: Dict[str, VitsModel] = {}
_tokenizers_cache: Dict[str, AutoTokenizer] = {}

def load_dialect_model(dialect_id: str):
    if dialect_id not in DIALECT_CATALOG:
        raise ValueError(f"Unknown dialect id: {dialect_id}")
    
    repo = DIALECT_CATALOG[dialect_id]["repo"]
    if dialect_id not in _models_cache:
        tokenizer = AutoTokenizer.from_pretrained(repo)
        model = VitsModel.from_pretrained(repo)
        _models_cache[dialect_id] = model
        _tokenizers_cache[dialect_id] = tokenizer
    return _models_cache[dialect_id], _tokenizers_cache[dialect_id]

def synthesize_dialect(dialect_id: str, text: str, out_path: str, speed: float = 1.0) -> Dict[str, Any]:
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

    # Convert tensor to numpy and write to WAV
    audio_data = waveform[0].cpu().numpy()
    sample_rate = model.config.sampling_rate

    # If speed is adjusted (simple linear resample if different from 1.0)
    if speed != 1.0 and 0.5 <= speed <= 2.0:
        import scipy.signal
        new_len = int(len(audio_data) / speed)
        audio_data = scipy.signal.resample(audio_data, new_len)

    sf.write(out_path, audio_data, samplerate=sample_rate)

    duration = round(len(audio_data) / float(sample_rate), 2)
    file_size_kb = round(os.path.getsize(out_path) / 1024, 1)

    return {
        "dialect_id": dialect_id,
        "name": dialect_info["name"],
        "region": dialect_info["region"],
        "duration_sec": duration,
        "file_size_kb": file_size_kb,
        "sample_rate": sample_rate,
        "latency_ms": elapsed_ms
    }
