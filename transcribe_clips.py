"""Transcribe Dang Studio clips with Whisper small via transformers"""
import os
ffmpeg_dir = os.path.join('.venv', 'Lib', 'site-packages', 'imageio_ffmpeg', 'binaries')
os.environ['PATH'] = os.path.abspath(ffmpeg_dir) + os.pathsep + os.environ.get('PATH', '')

from transformers import pipeline
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'
dtype = torch.float16 if device == 'cuda' else torch.float32
print(f"Device: {device}")

print("Loading Whisper small...")
pipe = pipeline('automatic-speech-recognition', model='openai/whisper-small', 
                device=device, torch_dtype=dtype)

for i in range(1, 5):
    path = f'output/real_human_isan/male/clip_dang_{i}.wav'
    result = pipe(path, generate_kwargs={'language': 'thai', 'task': 'transcribe'})
    text = result["text"].strip()
    print(f"clip_dang_{i}: {text}")
