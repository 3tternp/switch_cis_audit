from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class ParsedConfig:
    device_name: str
    vendor: str
    text: str

def read_text_file(path: str) -> str:
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("latin-1", errors="replace")

def guess_device_name(path: str) -> str:
    base = os.path.basename(path)
    stem, _ = os.path.splitext(base)
    return stem or base
