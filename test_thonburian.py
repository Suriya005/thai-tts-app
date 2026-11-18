"""
Test ThonburianTTS - Thai-fine-tuned F5-TTS for voice cloning with Dang Studio voice
"""

import os
import sys
import time
from huggingface_hub import hf_hub_download

# Fix ffmpeg path for Windows
ffmpeg_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Lib", "site-packages", "imageio_ffmpeg", "binaries")
if os.path.exists(ffmpeg_dir):
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

import soundfile as sf
import torch
import torchaudio

# Monkeypatch torchaudio.load with soundfile on Windows (fix torchcodec issue)
def _custom_torchaudio_load(filepath, *args, **kwargs):
    data, sr = sf.read(filepath)
    tensor = torch.from_numpy(data).float()
    if tensor.ndim == 1:
        tensor = tensor.unsqueeze(0)
    else:
        tensor = tensor.t()
    return tensor, sr
torchaudio.load = _custom_torchaudio_load

from f5_tts.api import F5TTS

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    
    # Download / resolve local paths for ThonburianTTS
    print("Resolving ThonburianTTS files...")
    vocab_path = hf_hub_download(repo_id="biodatlab/ThonburianTTS", filename="megaF5/mega_vocab.txt")
    ckpt_path = hf_hub_download(repo_id="biodatlab/ThonburianTTS", filename="megaF5/mega_f5_last.safetensors")
    print(f"Vocab: {vocab_path}")
    print(f"Checkpoint: {ckpt_path}")
    
    print("Loading ThonburianTTS (Thai F5-TTS)...")
    t0 = time.time()
    
    model = F5TTS(
        model="F5TTS_v1_Base",
        ckpt_file=ckpt_path,
        vocab_file=vocab_path,
        device=device
    )
    
    print(f"Model loaded in {time.time()-t0:.1f}s")
    
    # Reference audio - Dang Studio clip 4 (longest, 3.7s)
    ref_audio = "output/real_human_isan/male/clip_dang_4.wav"
    # From Whisper small: "ลุงโทษนี้มีนาทีลากบักตัวต้นเหตุไปกระเทือบนอกลัน"
    ref_text = "ลุงโทนี่มีหน้าที่ลากบักตัวต้นเหตุไปกระทืบนอกร้าน"
    
    test_texts = [
        ("สวัสดีครับพี่น้อง มื้อนี้มาเว้าพื้นหนังให้ฟังเด้อ", "greeting"),
        ("หนังเรื่องนี้มันแซ่บคักแท้ ดูแล้วม่วนหลาย", "review"),
    ]
    
    os.makedirs("output", exist_ok=True)
    
    for text, label in test_texts:
        print(f"\n--- Test '{label}': {text}")
        t1 = time.time()
        
        out_path = f"output/test_thonburian_{label}.wav"
        
        wav, sr, spec = model.infer(
            ref_file=ref_audio,
            ref_text=ref_text,
            gen_text=text,
            nfe_step=32,
            speed=1.0,
            file_wave=out_path
        )
        
        audio_data, out_sr = sf.read(out_path)
        dur = len(audio_data) / out_sr
        elapsed = time.time() - t1
        size_kb = os.path.getsize(out_path) / 1024
        
        print(f"  Output: {dur:.2f}s, {out_sr}Hz, {size_kb:.1f}KB, took {elapsed:.1f}s")
    
    print("\n✅ Done testing ThonburianTTS!")

if __name__ == "__main__":
    main()
