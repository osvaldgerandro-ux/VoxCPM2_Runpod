from pydantic import BaseModel, Field
from typing import Literal


class TTSRequest(BaseModel):
    text: str
    voice: str = "female_en"
    instructions: str | None = None
    response_format: Literal["base64", "wav"] = "base64"


class TTSResponse(BaseModel):
    audio: str
    format: str
    duration_secs: float | None = None
    voice: str
    model: str
