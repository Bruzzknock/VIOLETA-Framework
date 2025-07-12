import pathlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data"
FILE_PATH  = DATA_PATH / "info.txt"

def save(info: str):
    with open(FILE_PATH, "a") as f:
        f.write(info)

def load(file_path: str) -> str:
    with open(file_path) as f:
        return f.read()