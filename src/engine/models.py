from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_MANUAL = "MANUAL"
STATUS_UNKNOWN = "UNKNOWN"

@dataclass
class Finding:
    issue_id: str
    issue_name: str
    status: str
    fix_type: str
    remediation: str
    evidence: str = ""
    device: str = ""
    vendor: str = ""
    notes: str = ""

@dataclass
class RunMeta:
    generated_at: str
    tool_version: str = "1.1"
    vendor_profile: str = ""
    source_files: List[str] = field(default_factory=list)
