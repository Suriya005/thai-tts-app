"""
train_isan_voice.py - Fast Acoustic Feature Extraction & Voice Model Training
Trains authentic Isan Voice Models from native YouTube speech datasets.
Includes:
1. Kasin TV (Clear colloquial Isan educator & native speaker)
2. Tai Baan (Young rural native Isan conversational speech)
3. WiriWiri & Nong Cream (Authentic northeastern female creators)
"""

import os
import sys
import numpy as np
import librosa
import noisereduce as nr

MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

def train_speaker_model(audio_paths, output_model_path, gender="female"):
    print(f"\n==========================================", flush=True)
    print(f"Training Isan Voice Model [{gender.upper()}] from {len(audio_paths)} source files...", flush=True)
    print(f"==========================================", flush=True)

    all_voiced_chunks = []
    chunk_durations = []
    target_sr = 22050
    f0_list = []
    spectral_envelopes = []

    fmin = 80 if gender == "male" else 130
    fmax = 280 if gender == "male" else 450

    for path in audio_paths:
        if not os.path.exists(path):
            print(f"File not found, skipping: {path}", flush=True)
            continue

        print(f"Processing: {os.path.basename(path)}...", flush=True)
        # Load up to 180 seconds per file for high training richness and speed
        data, sr = librosa.load(path, sr=target_sr, mono=True, duration=180.0)
        
        # 1. Noise reduction
        try:
            cleaned = nr.reduce_noise(y=data, sr=target_sr, prop_decrease=0.6, n_fft=1024)
        except Exception:
            cleaned = data

        # 2. Extract voiced segments
        intervals = librosa.effects.split(cleaned, top_db=25, frame_length=1024, hop_length=256)
        print(f"Found {len(intervals)} speech intervals in {os.path.basename(path)}", flush=True)
        
        for start, end in intervals:
            duration = (end - start) / target_sr
            if 0.25 <= duration <= 8.0:
                chunk = cleaned[start:end]
                max_val = np.max(np.abs(chunk))
                if max_val > 0.04:
                    chunk = chunk / max_val * 0.95
                    all_voiced_chunks.append(chunk)
                    chunk_durations.append(duration)

                    # Compute 64-band Mel spectral envelope
                    S = np.abs(librosa.stft(chunk, n_fft=1024, hop_length=256))
                    mel = librosa.feature.melspectrogram(S=S**2, sr=target_sr, n_mels=64)
                    log_mel = librosa.power_to_db(mel, ref=np.max)
                    spectral_envelopes.append(np.mean(log_mel, axis=1))

        # Fast F0 estimation using librosa.yin on downsampled cleaned audio
        downsampled = librosa.resample(cleaned, orig_sr=target_sr, target_sr=11025)
        f0 = librosa.yin(downsampled, fmin=fmin, fmax=fmax, sr=11025, frame_length=1024, hop_length=256)
        valid_f0 = f0[(f0 >= fmin) & (f0 <= fmax) & ~np.isnan(f0)]
        if len(valid_f0) > 0:
            f0_list.extend(valid_f0)

    if not all_voiced_chunks:
        raise ValueError(f"No voiced audio extracted for {gender} model!")

    total_duration = sum(len(c) for c in all_voiced_chunks) / target_sr
    mean_chunk_dur = float(np.mean(chunk_durations))
    median_chunk_dur = float(np.median(chunk_durations))
    print(f"Extracted {len(all_voiced_chunks)} clean voiced chunks ({total_duration:.1f} seconds total)", flush=True)
    print(f"Speech interval cadence: Mean={mean_chunk_dur:.2f}s, Median={median_chunk_dur:.2f}s", flush=True)

    # 3. Model Parameters Calculation
    median_f0 = float(np.median(f0_list)) if len(f0_list) > 0 else (195.0 if gender == "female" else 135.0)
    std_f0 = float(np.std(f0_list)) if len(f0_list) > 0 else 25.0
    mean_spectral_env = np.mean(spectral_envelopes, axis=0)
    mel_freqs = librosa.mel_frequencies(n_mels=64, fmin=0, fmax=target_sr//2)

    # 4. Formant Resonances & EQ profile
    sample_limit = min(30, len(all_voiced_chunks))
    combined_audio = np.concatenate(all_voiced_chunks[:sample_limit])
    a = librosa.lpc(combined_audio, order=16)
    
    eq_curve = mean_spectral_env - np.mean(mean_spectral_env)
    eq_curve = np.clip(eq_curve, -12.0, 12.0)

    # Target speaking rate: Isan speech is punchy and fast (~1.15x to 1.25x compared to formal Bangkok Thai)
    optimal_rate_boost = 18 if gender == "male" else 12

    # Save Voice Model Artifact
    model_data = {
        "gender": gender,
        "sample_rate": target_sr,
        "median_f0": median_f0,
        "std_f0": std_f0,
        "mean_chunk_dur": mean_chunk_dur,
        "median_chunk_dur": median_chunk_dur,
        "optimal_rate_boost": optimal_rate_boost,
        "spectral_envelope": mean_spectral_env,
        "mel_freqs": mel_freqs,
        "eq_curve": eq_curve,
        "lpc_coeffs": a,
        "num_training_chunks": len(all_voiced_chunks),
        "training_duration_sec": total_duration
    }

    np.savez(output_model_path, **model_data)
    print(f"Saved trained {gender.upper()} Isan model to: {output_model_path}", flush=True)
    print(f" -> Target F0: {median_f0:.1f} Hz (Std: {std_f0:.1f} Hz)", flush=True)
    print(f" -> Optimal Rate Boost: +{optimal_rate_boost}% (Snappy, non-dragging)", flush=True)
    print(f" -> Spectral Bands: 64 Mel filters (0 - {target_sr//2} Hz)", flush=True)
    return model_data

if __name__ == "__main__":
    female_sources = [
        "training_data/female/raw_wiriwiri.wav",
        "training_data/female/raw_nongcream.wav",
        "output/ref_female_isan.wav"
    ]
    train_speaker_model(female_sources, "models/isan_female_voice.npz", gender="female")

    male_sources = [
        "training_data/male/raw_kasin.wav",
        "training_data/male/raw_taibaan.wav",
        "training_data/male/raw_pnui.wav",
        "output/ref_male_isan.wav"
    ]
    train_speaker_model(male_sources, "models/isan_male_voice.npz", gender="male")
