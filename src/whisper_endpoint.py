import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import lightning as L
import whisper
from lightning.app.components.serve import PythonServer
from lightning.app.storage import Drive
from pydantic import BaseModel
from torch.cuda import is_available


DRIVE_SOURCE_FILE_TIMEOUT_SECONDS = 10
DEFAULT_MODEL_SIZE = "small"


class AudioFile(BaseModel):
    audio_path: str


class Response(BaseModel):
    text: str
    runtime: float


@dataclass
class CustomBuildConfig(L.BuildConfig):
    def build_commands(self) -> List[str]:
        return [
            "sudo apt-get update",
            "sudo apt-get install -y ffmpeg libmagic1",
        ]


class WhisperServer(PythonServer):
    def __init__(self, drive: Drive, **kwargs):
        super().__init__(
            input_type=AudioFile,
            output_type=Response,
            port=1994,
            cloud_build_config=CustomBuildConfig(
                requirements=["git+https://github.com/openai/whisper.git"]
            ),
            **kwargs,
        )
        self._drive = drive

    def setup(self) -> None:
        self._device = "cuda:0" if is_available() else "cpu"
        self._model = whisper.load_model(
            DEFAULT_MODEL_SIZE,
            in_memory=True,
            device=self._device,
            download_root="whisper_model",
        )

    def predict(self, request: AudioFile) -> Response:

        # get file from shared drive
        self._drive.get(request.audio_path, timeout=DRIVE_SOURCE_FILE_TIMEOUT_SECONDS)

        # run inference with Whisper model
        start_time = time.perf_counter()
        text = whisper.transcribe(
            self._model, audio=request.audio_path, language="en", fp16=False
        )["text"]
        end_time = time.perf_counter()

        if text is None or len(text) < 1:
            text = "The audio file is too short or empty. No results."

        # remove audio from local drive
        if Path(request.audio_path).exists():
            os.remove(request.audio_path)

        return Response(
            text=text.strip(),
            runtime=end_time - start_time,
        )

    @property
    def endpoint_url(self) -> Optional[str]:
        use_localhost = "LIGHTNING_APP_STATE_URL" not in os.environ
        if use_localhost:
            return self.url
        if self.internal_ip != "":
            return f"http://{self.internal_ip}:{self.port}"
        return self.internal_ip

    @property
    def is_alive(self):
        """Hack: Returns whether the server is alive."""
        return self.endpoint_url != ""
