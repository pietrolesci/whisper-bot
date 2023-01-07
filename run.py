import os

import uvloop
import subprocess
import tempfile
import time
from pyrogram import Client, filters
from pyrogram.types import Message
import whisper
import torch
uvloop.install()


class SimpleSpeechRecognizer:
    def __init__(self, whisper_home: str, model_size: str, n_threads: int = 4, n_proc: int = 1) -> None:
        self.whisper_home = whisper_home
        self.model_size = model_size
        self.n_threads = n_threads
        self.n_proc = n_proc

    def convert_to_audio(self, source_file_path: str) -> str:
        """Converts `.ogg` file to `.wav` (16kHz) using `ffmpeg`."""

        wav_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)

        # TODO: Handle exceptions from `ffmpeg`
        subprocess.call(
            f"ffmpeg -i {source_file_path} -y -ar 16000 -ac 1 -c:a pcm_s16le {wav_file.name}",
            shell=True,
        )

        return wav_file.name

    def recognize(self, audio_file_path: str) -> str:
        """Runs Whisper C++ implementation."""

        assert os.path.exists(
            audio_file_path
        ), f"File does not exist: {audio_file_path}"

        output_txt = f"{audio_file_path}.txt"

        commands = [
            f"{self.whisper_home}/main",
            f"-m {self.whisper_home}/models/ggml-{self.model_size}.bin",
            audio_file_path,
            "--language",
            "it",
            "--no-timestamps",
            f"--threads {self.n_threads}",
            f"--processors {self.n_proc}",
            "--output-txt",
        ]

        # TODO: Use Python bindings to `whisper.cpp` when they are officially released
        print(f"Running: {' '.join(commands)}")
        subprocess.call(" ".join(commands), shell=True)

        with open(output_txt) as f:
            transcription = f.read()

        return transcription

    def __call__(self, source_file_path: str) -> str:
        # convert to wav
        audio_file_path = self.convert_to_audio(source_file_path)

        # transcribe
        start_time = time.perf_counter()
        transcription = self.recognize(audio_file_path)
        end_time = time.perf_counter()

        os.remove(audio_file_path)

        return transcription, end_time - start_time


class AnotherSpeechRecognizer:

    def __init__(self, model_size: str, device: str = "cpu") -> None:
        self.model_size = model_size
        self.device = device
        self.model = whisper.load_model(model_size, in_memory=True, device=torch.device(device), download_root="./whisper")
        # self.decode_options = whisper.DecodingOptions(language="it")

    def __call__(self, source_file_path: str) -> str:
        start_time = time.perf_counter()
        transcription =  whisper.transcribe(self.model, audio=source_file_path, language="it")["text"]
        end_time = time.perf_counter()

        return transcription, end_time - start_time


if __name__ == "__main__":

    # transcriber = SimpleSpeechRecognizer(
    #     whisper_home="./whisper.cpp", 
    #     model_size="small",
    #     n_threads=4,
    #     n_proc=1,
    # )

    transcriber = AnotherSpeechRecognizer("small")
    
    api_id = os.environ.get("API_ID")
    api_hash = os.environ.get("API_HASH")
    bot_token = os.environ.get("BOT_TOKEN")

    app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

    @app.on_message(filters.text & filters.private)
    async def echo(client: Client, message: Message):
        await message.reply(message.text)

    @app.on_message(filters.voice & filters.private)
    async def echo(client: Client, message: Message):
        audio_file_path = await message.download(f"audio_{message.voice.file_id}.ogg")
        
        transcription, runtime = transcriber(audio_file_path)
        if transcription is not None and len(transcription) > 0:
            result = f"Processato in {round(runtime, 2)} secondi.\nTrascrizione:\n\n{transcription}"
        else:
            result = "Il file audio è vuoto o troppo breve. Nessun risultato"

        os.remove(audio_file_path)

        await message.reply(result)

    app.run()
