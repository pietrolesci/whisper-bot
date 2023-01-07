import lightning as L
import os
from pyrogram import Client, filters
from pyrogram.types import Message
import uvloop
from run import AnotherSpeechRecognizer


class TelegramBot(L.LightningWork):

    def __init__(self, cloud_compute: L.CloudCompute):
        super().__init__(cloud_compute=cloud_compute, raise_exception=False, parallel=True)
        self.api_id = os.environ.get("API_ID")
        self.api_hash = os.environ.get("API_HASH")
        self.bot_token = os.environ.get("BOT_TOKEN")
        self._transcriber = AnotherSpeechRecognizer("small")

    def run(self):

        uvloop.install()
        
        app = Client("my_bot", api_id=self.api_id, api_hash=self.api_hash, bot_token=self.bot_token)

        @app.on_message(filters.text & filters.private)
        async def echo(client: Client, message: Message):
            await message.reply(message.text)

        @app.on_message(filters.voice & filters.private)
        async def echo(client: Client, message: Message):
            audio_file_path = await message.download(f"audio_{message.voice.file_id}.ogg")
            
            transcription, runtime = self._transcriber(audio_file_path)
            if transcription is not None and len(transcription) > 0:
                result = f"Processato in {round(runtime, 2)} secondi.\nTrascrizione:\n\n{transcription.strip()}"
            else:
                result = "Il file audio è vuoto o troppo breve. Nessun risultato"

            os.remove(audio_file_path)

            await message.reply(result)

        app.run()


class LitApp(L.LightningFlow):
    def __init__(self) -> None:
        super().__init__()
        self.telegram_bot = TelegramBot(L.CloudCompute("cpu-medium"))

    def run(self):
        self.telegram_bot.run()


app = L.LightningApp(TelegramBot(L.CloudCompute("cpu-medium")), flow_cloud_compute=L.CloudCompute("default"))
