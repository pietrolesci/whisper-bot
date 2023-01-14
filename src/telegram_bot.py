import os
from typing import Optional

import lightning as L
import uvloop
from lightning.app.utilities.app_helpers import Logger
from pyrogram import Client, filters
from pyrogram.types import Message
from lightning.app.storage import Drive
import requests
from pathlib import Path


logger = Logger(__name__)


class TelegramBot(L.LightningWork):
    def __init__(self, drive: Drive, cloud_compute: Optional[L.CloudCompute] = None):
        super().__init__(
            cloud_compute=cloud_compute,
            raise_exception=True,
            cache_calls=True,
            parallel=True,
            cloud_build_config=L.BuildConfig(requirements=["pyrogram", "tgcrypto", "uvloop"]),
        )

        self.api_id = os.environ.get("API_ID")
        self.api_hash = os.environ.get("API_HASH")
        self.bot_token = os.environ.get("BOT_TOKEN")
        self.drive = drive

    def run(self, host: str, port):

        uvloop.install()

        app = Client("my_bot", api_id=self.api_id, api_hash=self.api_hash, bot_token=self.bot_token)

        # @app.on_message(filters.text & filters.private)
        # async def echo(client: Client, message: Message):

        #     # save audio to shared drive
        #     audio_path = f"message_{message.id}.txt"
        #     with open(audio_path, "w") as fl:
        #         fl.write(message.text)

        #     self.drive.put(audio_path)
        #     os.remove(audio_path)

        #     logger.info(f"BOT: {'; '.join(self.drive.list())}")
            
        #     # send request to process audio
        #     response = requests.post("http://127.0.0.1:1994/predict", json={
        #         "audio_path": audio_path
        #     }).json()["text"]

        #     self.drive.delete(audio_path)
        #     logger.info(f"BOT: {'; '.join(self.drive.list())}")

        #     # send reply
        #     await message.reply(response)

        @app.on_message(filters.voice & filters.private)
        async def transcribe(client: Client, message: Message):
            full_audio_path = await message.download(f"{self.drive.root}/audio_{message.voice.file_id}.ogg",)
            # audio_path = str(Path(full_audio_path).relative_to(os.getcwd()))
            audio_path = Path(full_audio_path).name
            # self.drive.put(audio_path)
            
            # send request to process audio
            response = requests.post(f"https://{host}:{port}/predict", json={
                "audio_path": audio_path
            }).json()
            
            # send response
            text = f"Processato in {round(response['runtime'], 2)} secondi.\nTrascrizione:\n\n{response['text']}"
            await message.reply(text)

            # os.remove(full_audio_path)
            self.drive.delete(audio_path)

        app.run()