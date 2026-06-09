import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    model_name: str = "osvald/voxcpm2-tts"
    hf_token: str | None = None
    max_input_length: int = 512
    max_output_length: int = 4096
    gpu_mem_util: float = 0.90
    max_num_seqs: int = 256

    def __post_init__(self):
        self.hf_token = os.environ.get("HF_TOKEN") or None
