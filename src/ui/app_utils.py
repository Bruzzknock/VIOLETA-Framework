import pathlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "ui" / "data"
FILE_PATH  = DATA_PATH / "info.txt"

def save(info: str):
    with open(FILE_PATH, "w") as f:
        f.write(info)

def load(file_path: str) -> str:
    with open(FILE_PATH) as f:
        return f.read()