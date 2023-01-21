import lightning as L
from lightning.app.storage import Drive
from lightning.app.utilities.app_helpers import Logger

from src.telegram_bot import TelegramBot
from src.whisper_endpoint import WhisperServer
from pathlib import Path
logger = Logger(__name__)


class Flow(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.drive = Drive(id="lit://bot", allow_duplicates=False, component_name="telegram_bot")
        self.telegram_bot = TelegramBot(drive=self.drive, cloud_compute=L.CloudCompute("default"))
        self.whisper_endpoint = WhisperServer(drive=self.drive, cloud_compute=L.CloudCompute("cpu-medium", idle_timeout=10))

    def run(self):
        self.whisper_endpoint.run()
        if self.whisper_endpoint.is_alive:
            self.telegram_bot.run(endpoint_url=self.whisper_endpoint.endpoint_url)


    # def configure_layout(self):
    #     return {"name": "endpoint", "content": self.whisper_endpoint}


app = L.LightningApp(Flow(), log_level="info", flow_cloud_compute=L.CloudCompute("cpu-small"))
