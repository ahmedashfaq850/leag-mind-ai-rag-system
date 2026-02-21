import json
from pathlib import Path

def load_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def save_json(path: str, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")