FROM runpod/base:1.0.5-dev-fix-image-vulnerabilities-cuda1281-ubuntu2404

# System dependencies for audio processing and source builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# PyTorch 2.6 with CUDA 12.4 support (compatible with cuda1281 runtime)
RUN pip install --no-cache-dir torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124

# vLLM 0.22 + Omni for TTS inference (all dependencies from real PyPI)
RUN pip install --no-cache-dir vllm==0.22.0 vllm-omni==0.22.0

# Application dependencies
RUN pip install --no-cache-dir runpod-flash soundfile pydantic huggingface_hub numpy
