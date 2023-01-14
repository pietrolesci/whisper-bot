import time
from dataclasses import dataclass
from typing import List
from lightning.app.storage import Drive

import lightning as L
from lightning.app.components.serve import PythonServer
from lightning.app.utilities.app_helpers import Logger
import whisper
from pydantic import BaseModel
from torch.cuda import is_available

logger = Logger(__name__)


@dataclass
class CustomBuildConfig(L.BuildConfig):
    def build_commands(self) -> List[str]:
        return [
            "sudo apt-get update",
            "sudo apt-get install -y ffmpeg libmagic1",
        ]


class AudioFile(BaseModel):
    audio_path: str

class Response(BaseModel):
    text: str
    runtime: float


class WhisperServer(PythonServer):
    def __init__(self, drive: Drive, **kwargs):
        super().__init__(
            input_type=AudioFile,
            output_type=Response,
            port=1994,
            cloud_build_config=CustomBuildConfig(requirements=["git+https://github.com/openai/whisper.git"]),
            **kwargs,
        )
        self.drive = drive

    def setup(self):
        self._device = "cuda:0" if is_available() else "cpu"
        self._model = whisper.load_model("small", in_memory=True, device=self._device, download_root="whisper_model")
    
    def predict(self, request: AudioFile) -> Response:
        
        # get file from shared drive
        self.drive.get(request.audio_path, timeout=1.)
        logger.info(f"MODEL: {'; '.join(self.drive.list())}")
        
        start_time = time.perf_counter()
        # with open(request.audio_path, "r") as fl:
        #     text = fl.read()
        text = whisper.transcribe(self._model, audio=request.audio_path, language="it", fp16=False)["text"]        
        end_time = time.perf_counter()

        if text is None or len(text) < 1:
            text = "Il file audio è vuoto o troppo breve. Nessun risultato"

        return {
            "text": text.strip(),
            "runtime": end_time - start_time,
        }


