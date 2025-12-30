from __future__ import annotations
from .common import ParsedConfig, read_text_file, guess_device_name

def parse_cisco_config(path: str) -> ParsedConfig:
    text = read_text_file(path)
    return ParsedConfig(device_name=guess_device_name(path), vendor="Cisco", text=text)
