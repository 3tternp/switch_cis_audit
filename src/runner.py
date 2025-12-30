from __future__ import annotations
import os
from datetime import datetime
from typing import List

from .engine.models import RunMeta, Finding
from .engine.rules import load_rules, evaluate_rules
from .parsers.cisco import parse_cisco_config
from .parsers.juniper import parse_juniper_config
from .report.pdf_report import build_pdf

def run_review(vendor_profile: str, config_paths: List[str], out_pdf: str, rules_path: str) -> List[Finding]:
    rules = load_rules(rules_path)
    findings: List[Finding] = []

    for p in config_paths:
        if vendor_profile.lower().startswith("cisco"):
            parsed = parse_cisco_config(p)
        else:
            parsed = parse_juniper_config(p)
        findings.extend(evaluate_rules(parsed.text, rules, parsed.device_name, parsed.vendor))

    meta = RunMeta(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        vendor_profile=vendor_profile,
        source_files=[os.path.basename(p) for p in config_paths],
    )
    build_pdf(out_pdf, findings, meta)
    return findings
