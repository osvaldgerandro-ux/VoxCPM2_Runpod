import threading

from app.config import AppConfig

config = AppConfig()

_engine = None
_lock = threading.Lock()
_initialized = False


def _bootstrap():
    global _engine, _initialized

    if _initialized:
        return

    with _lock:
        if _initialized:
            return

        try:
            import torch
            from vllm import LLM

            _engine = LLM(
                model=config.model_name,
                trust_remote_code=True,
                max_model_len=config.max_output_length,
                gpu_memory_utilization=config.gpu_mem_util,
                max_num_seqs=config.max_num_seqs,
                dtype="auto",
            )
            _initialized = True
        except Exception as exc:
            raise RuntimeError(f"Failed to bootstrap vLLM engine: {exc}") from exc


def init_engine():
    if not _initialized:
        _bootstrap()
    return _engine


def generate(text: str, voice_ref, instructions: str | None = None) -> "np.ndarray":
    import numpy as np

    engine = init_engine()

    try:
        from vllm import SamplingParams

        sampling_params = SamplingParams(
            max_tokens=config.max_output_length,
            temperature=0.7,
            top_p=0.9,
        )

        prompt = {"text": text}
        if voice_ref is not None:
            prompt["audio"] = voice_ref.audio
            prompt["sample_rate"] = voice_ref.sample_rate
        if instructions:
            prompt["instructions"] = instructions

        outputs = engine.generate(prompt, sampling_params=sampling_params)
        audio = outputs[0].outputs["audio"]

        if isinstance(audio, list):
            audio = np.array(audio, dtype=np.float32)

        return audio

    except Exception as exc:
        raise RuntimeError(f"Generation failed: {exc}") from exc
