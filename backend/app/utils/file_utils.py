from __future__ import annotations
import uuid
from pathlib import Path

def unique_filename(extension: str = ".jpg") -> str:
    return f"{uuid.uuid4().hex}{extension}"

def ensure_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def url_path(storage_path: str) -> str:
    return "/" + storage_path.replace("\\", "/").lstrip("/")
