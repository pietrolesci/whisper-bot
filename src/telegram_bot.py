import os
from pathlib import Path
from typing import Optional

import lightning as L
import requests
import uvloop
from lightning.app.frontend import StaticWebFrontend
from lightning.app.storage import Drive
from lightning.app.utilities.app_helpers import Logger
from pyrogram import Client, filters
from pyrogram.types import Message

logger = Logger(__name__)


class TelegramBot(L.LightningWork):
    def __init__(self, drive: Drive, cloud_compute: Optional[L.CloudCompute] = None):
        super().__init__(
            cloud_compute=cloud_compute,
            raise_exception=True,
            cache_calls=True,
            parallel=True,
            cloud_build_config=L.BuildConfig(
                requirements=["pyrogram", "tgcrypto", "uvloop"]
            ),
        )

        self._api_id = os.environ.get("API_ID")
        self._api_hash = os.environ.get("API_HASH")
        self._bot_token = os.environ.get("BOT_TOKEN")
        self._drive = drive

    def run(self, endpoint_url: str):

        uvloop.install()

        app = Client(
            "my_bot",
            api_id=self._api_id,
            api_hash=self._api_hash,
            bot_token=self._bot_token,
        )

        @app.on_message(filters.voice & filters.private)
        async def transcribe(client: Client, message: Message):

            # save audio to shared drive
            absolute_audio_path = await message.download(f"{os.getcwd()}/audio_{message.voice.file_id}.ogg")
            audio_path = str(Path(absolute_audio_path).relative_to(os.getcwd()))
            self._drive.put(audio_path)

            # send request to process audio
            response = requests.post(
                f"{endpoint_url}/predict", json={"audio_path": audio_path}
            ).json()

            # send response
            text = f"Processato in {round(response['runtime'], 2)} secondi.\nTrascrizione:\n\n{response['text']}"
            await message.reply(text)

            # clean up
            self._drive.delete(audio_path)
            os.remove(absolute_audio_path)

        app.run()
