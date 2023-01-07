from lightning.app.components import TracerPythonScript
import lightning as L
from dataclasses import dataclass


@dataclass
class CustomBuildConfig(L.BuildConfig):

    def build_commands(self):
        return [
            "sudo apt-get update",
            "sudo apt-get install -y ffmpeg libmagic1",
            "git clone https://github.com/ggerganov/whisper.cpp.git",
            "cd ./whisper.cpp && make small",
            "cd ..",
        ]

class SpeechRecognizerWork(TracerPythonScript):

    def __init__(self, script_path, cloud_compute):
        super().__init__(
            script_path=script_path,
            parallel=True,
            cloud_compute=L.CloudCompute(cloud_compute),
            cloud_build_config=CustomBuildConfig(requirements=[]),
            raise_exception=False,
        )



component = SpeechRecognizerWork(script_path="run.py", cloud_compute="cpu-medium")    
app = L.LightningApp(component, flow_cloud_compute=L.CloudCompute("default"))
