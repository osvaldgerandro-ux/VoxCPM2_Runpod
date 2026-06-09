import os
from dataclasses import dataclass

import numpy as np
import soundfile as sf


@dataclass
class VoiceRef:
    name: str
    audio: np.ndarray
    sample_rate: int
    transcript: str | None = None


_voices_cache: dict[str, VoiceRef] | None = None


def load_voices(voices_dir: str) -> dict[str, VoiceRef]:
    global _voices_cache
    if _voices_cache is not None:
        return _voices_cache

    voices: dict[str, VoiceRef] = {}
    if not os.path.isdir(voices_dir):
        _voices_cache = voices
        return voices

    for entry in sorted(os.listdir(voices_dir)):
        subdir = os.path.join(voices_dir, entry)
        if not os.path.isdir(subdir):
            continue

        ref_wav = os.path.join(subdir, "ref.wav")
        transcript_txt = os.path.join(subdir, "transcript.txt")

        if not os.path.isfile(ref_wav):
            continue

        audio, sr = sf.read(ref_wav, dtype="float32")
        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        transcript: str | None = None
        if os.path.isfile(transcript_txt):
            with open(transcript_txt, encoding="utf-8") as f:
                transcript = f.read().strip()

        voices[entry] = VoiceRef(
            name=entry,
            audio=audio,
            sample_rate=sr,
            transcript=transcript,
        )

    _voices_cache = voices
    return voices


def get_voice(name: str, voices: dict[str, VoiceRef]) -> VoiceRef:
    if name in voices:
        return voices[name]
    if voices:
        first_key = next(iter(voices))
        return voices[first_key]
    raise ValueError(f"No voices loaded and requested voice '{name}' not found")
