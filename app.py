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
        self.telegram_bot.run()
        self.whisper_endpoint.run()


app = L.LightningApp(Flow(), log_level="info", flow_cloud_compute=L.CloudCompute("cpu-small"))
