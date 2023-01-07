import lightning as L
import os
from pyrogram import Client, filters
from pyrogram.types import Message
import uvloop
from lightning.app.utilities.app_helpers import Logger
from lightning.app.components.serve import PythonServer, Text
from lightning.app.frontend import StaticWebFrontend
import torch
from pydantic import BaseModel
import time
import whisper
from dataclasses import dataclass
from typing import List

logger = Logger(__name__)

# class ModelPrediction(BaseModel):
#     text: str
#     runtime: float


@dataclass
class CustomBuildConfig(L.BuildConfig):
    def build_commands(self) -> List[str]:
        return [
            "sudo apt-get update",
            "sudo apt-get install -y ffmpeg libmagic1",
        ]


class TelegramBot(L.LightningWork):
    def __init__(self, cloud_compute: L.CloudCompute):
        super().__init__(
            cloud_compute=cloud_compute,
            raise_exception=False,
            parallel=True,
            cloud_build_config=CustomBuildConfig(
                requirements=[
                    "pyrogram",
                    "tgcrypto",
                    "uvloop",
                    "git+https://github.com/openai/whisper.git",
                ]
            ),
        )

        self.api_id = os.environ.get("API_ID")
        self.api_hash = os.environ.get("API_HASH")
        self.bot_token = os.environ.get("BOT_TOKEN")
        self._model = whisper.load_model("small", in_memory=True, download_root="./whisper_model", device="cpu")

    def predict(self, audio_file_path: str) -> str:
        start_time = time.perf_counter()
        transcription = whisper.transcribe(self._model, audio=audio_file_path, language="it", fp16=False)["text"]
        end_time = time.perf_counter()
        runtime = end_time - start_time

        if transcription is not None and len(transcription) > 0:
            transcription = f"Processato in {round(runtime, 2)} secondi.\nTrascrizione:\n\n{transcription.strip()}"
        else:
            transcription = "Il file audio è vuoto o troppo breve. Nessun risultato"

        return transcription

    def run(self):

        uvloop.install()

        app = Client("my_bot", api_id=self.api_id, api_hash=self.api_hash, bot_token=self.bot_token)

        @app.on_message(filters.text & filters.private)
        async def echo(client: Client, message: Message):
            await message.reply(message.text)

        @app.on_message(filters.voice & filters.private)
        async def transcribe(client: Client, message: Message):
            audio_file_path = await message.download(f"audio_{message.voice.file_id}.ogg")
            logger.info(f"File downloaded in {audio_file_path}")

            result = self.predict(audio_file_path)
            logger.info(f"Transcription: {result}")

            await message.reply(result)
            logger.info("Message sent")

            # clean
            os.remove(audio_file_path)
            logger.info(f"File {audio_file_path} removed")

        app.run()


# class PyTorchServer(PythonServer):
#     def setup(self):
#         self._device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#         self._model = whisper.load_model("small", in_memory=True, download_root="./whisper_model", device=self._device)

#     def predict(self, request) -> ModelPrediction:
#         start_time = time.perf_counter()
#         transcription =  whisper.transcribe(self._model, audio=request, language="it")["text"]
#         end_time = time.perf_counter()

#         return ModelPrediction(text=transcription, runtime=end_time - start_time)

#     def configure_layout(self) -> StaticWebFrontend:
#         return StaticWebFrontend("model_endpoint")


# class LitApp(L.LightningFlow):
#     def __init__(self) -> None:
#         super().__init__()
#         self.telegram_bot = TelegramBot(L.CloudCompute("cpu-medium", spot=True))
#         self.model_endpoint = PyTorchServer(input_type=Text, output_type=ModelPrediction)

#     def run(self):
#         self.telegram_bot.run()


telegram_bot = TelegramBot(L.CloudCompute("cpu-medium"))
# pytorch_server =  PyTorchServer(input_type=Text, output_type=ModelPrediction)

app = L.LightningApp(telegram_bot, log_level="info", )
