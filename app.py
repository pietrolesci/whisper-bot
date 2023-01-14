import lightning as L
from lightning.app.utilities.app_helpers import Logger
from lightning.app.storage import Drive

from src.telegram_bot import TelegramBot
from src.whisper_endpoint import WhisperServer

logger = Logger(__name__)


class Flow(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.drive = Drive(id="lit://whisper", allow_duplicates=False, component_name="telegram_bot")
        self.telegram_bot = TelegramBot(drive=self.drive, cloud_compute=L.CloudCompute("cpu-small"))
        self.whisper_endpoint = WhisperServer(drive=self.drive, cloud_compute=L.CloudCompute("cpu-small"))

    def run(self):
        self.whisper_endpoint.run()
        self.telegram_bot.run(host=self.whisper_endpoint.host, port=self.whisper_endpoint.port)

    # def configure_layout(self):
    #     return [
    #         dict(name="whisper_endpoint", content=self.whisper_endpoint)
    #     ]


app = L.LightningApp(Flow(), log_level="info", flow_cloud_compute=L.CloudCompute("cpu-small"))
