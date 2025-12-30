from __future__ import annotations
import re
from .common import ParsedConfig, read_text_file, guess_device_name

def parse_juniper_config(path: str) -> ParsedConfig:
    text = read_text_file(path)
    lines = []
    for ln in text.splitlines():
        ln = ln.rstrip()
        if not ln:
            continue
        lines.append(re.sub(r"\s+", " ", ln))
    return ParsedConfig(device_name=guess_device_name(path), vendor="Juniper", text="\n".join(lines))
