import base64
import io
import os

import soundfile as sf
from runpod_flash import Endpoint

from app.config import AppConfig
from app.engine import generate, init_engine
from app.schemas import TTSRequest, TTSResponse
from app.voices import get_voice, load_voices

VOICES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "voices")
config = AppConfig()


@Endpoint(
    name="voxcpm2-tts",
    flashboot=True,
)
def tts_generate(job):
    try:
        request = TTSRequest(**job["input"])

        voices = load_voices(VOICES_DIR)
        voice_ref = get_voice(request.voice, voices)

        init_engine()
        audio = generate(request.text, voice_ref, request.instructions)

        buffer = io.BytesIO()
        sf.write(buffer, audio, voice_ref.sample_rate, format="WAV")
        wav_bytes = buffer.getvalue()

        audio_b64 = base64.b64encode(wav_bytes).decode("utf-8")
        duration_secs = float(len(audio)) / voice_ref.sample_rate

        response = TTSResponse(
            audio=audio_b64,
            format=request.response_format,
            duration_secs=duration_secs,
            voice=request.voice,
            model=config.model_name,
        )

        return response.model_dump()

    except Exception as exc:
        return {"error": str(exc)}
