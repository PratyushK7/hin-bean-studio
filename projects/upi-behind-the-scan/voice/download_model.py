from pathlib import Path
from huggingface_hub import hf_hub_download

HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

path = hf_hub_download(
    repo_id="litert-community/Kokoro-82M",
    filename="kokoro_int8_fp16.litertlm",
    local_dir=str(MODEL_DIR),
)
print("Kokoro model ready: " + str(path))
