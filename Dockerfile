FROM runpod/base:1.0.5-dev-fix-image-vulnerabilities-cuda1281-ubuntu2404

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124

RUN pip install --no-cache-dir vllm==0.22.0 vllm-omni==0.22.0

RUN pip install --no-cache-dir runpod-flash soundfile pydantic huggingface_hub numpy
