from dataclasses import dataclass
from typing import List
import lightning as L
from lightning.app.components import TracerPythonScript, AutoScaler


@dataclass
class CustomBuildConfig(L.BuildConfig):
    def build_commands(self) -> List[str]:
        return [
            "sudo apt-get update",
            "sudo apt-get install -y ffmpeg libmagic1",
            "git clone https://github.com/ggerganov/whisper.cpp.git",
            "cd ./whisper.cpp && make small",
            "cd ..",
        ]


class SpeechRecognizerWork(TracerPythonScript):
    def __init__(self, script_path: str, cloud_compute: L.CloudCompute) -> None:
        super().__init__(
            script_path=script_path,
            parallel=True,
            cloud_compute=cloud_compute,
            cloud_build_config=CustomBuildConfig(requirements=[]),
            raise_exception=False,
        )


component = SpeechRecognizerWork(script_path="run.py", cloud_compute=L.CloudCompute("cpu-medium"))
# auto_scaled_component = AutoScaler(
#         SpeechRecognizerWork,
#         min_replicas=1,
#         max_replicas=4,
#         scale_out_interval=10,
#         scale_in_interval=10,
#         max_batch_size=16,  # for auto batching
#         timeout_batching=1,  # for auto batching
#         script_path="run.py", 
#         cloud_compute=L.CloudCompute("cpu-small"),
#     )


app = L.LightningApp(component, flow_cloud_compute=L.CloudCompute("default"))
