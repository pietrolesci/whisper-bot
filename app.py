import os
import time
from dataclasses import dataclass
from typing import List

import lightning as L
import uvloop
import whisper
from lightning.app.utilities.app_helpers import Logger
from pyrogram import Client, filters
from pyrogram.types import Message

logger = Logger(__name__)


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
            raise_exception=True,
            parallel=True,
            cloud_build_config=CustomBuildConfig(
                # requirements=[
                #     "pyrogram",
                #     "tgcrypto",
                #     "uvloop",
                #     "git+https://github.com/openai/whisper.git",
                # ]
            ),
        )

        self.api_id = os.environ.get("API_ID")
        self.api_hash = os.environ.get("API_HASH")
        self.bot_token = os.environ.get("BOT_TOKEN")
        self._model = None  # if initialized here it does not work with Redis error or Error Code -9

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

        if self._model is None:
            # TODO: why do I need to initialize here?
            self._model = whisper.load_model("small", in_memory=True, device="cpu")

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


telegram_bot = TelegramBot(L.CloudCompute("cpu-medium"))

app = L.LightningApp(telegram_bot, log_level="info")
