from __future__ import annotations
import re
from typing import Any, Dict, List
import yaml

from .models import Finding, STATUS_PASS, STATUS_FAIL, STATUS_MANUAL, STATUS_UNKNOWN

def load_rules(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    rules = data.get("rules", [])
    if not isinstance(rules, list):
        raise ValueError("rules file must contain a top-level 'rules' list")
    return rules

def _snippet(lines: List[str], idxs: List[int], max_lines: int = 3) -> str:
    out = []
    for i in idxs[:max_lines]:
        if 0 <= i < len(lines):
            out.append(lines[i].rstrip())
    return "\n".join(out)

def _find_matches(lines: List[str], pattern: str, flags=re.IGNORECASE) -> List[int]:
    rx = re.compile(pattern, flags)
    return [i for i, ln in enumerate(lines) if rx.search(ln)]

def evaluate_rules(text: str, rules: List[Dict[str, Any]], device: str, vendor: str) -> List[Finding]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    findings: List[Finding] = []

    for r in rules:
        rid = str(r.get("id", "")).strip()
        name = str(r.get("name", "")).strip()
        fix_type = str(r.get("fix_type", "Quick")).strip()
        remediation = str(r.get("remediation", "")).strip()
        check = str(r.get("check", "")).strip().lower()

        patterns = r.get("patterns", [])
        if isinstance(patterns, str):
            patterns = [patterns]
        patterns = [p for p in patterns if isinstance(p, str) and p.strip()]

        manual_hint = str(r.get("manual_hint", "")).strip()
        min_count = int(r.get("min_count", 1) or 1)

        status = STATUS_UNKNOWN
        evidence = ""

        try:
            if check == "manual":
                status = STATUS_MANUAL
                evidence = manual_hint or "Manual verification required."
            elif check == "regex_present":
                found = []
                for p in patterns:
                    found += _find_matches(lines, p)
                if found:
                    status = STATUS_PASS
                    evidence = _snippet(lines, found)
                else:
                    status = STATUS_FAIL
                    evidence = manual_hint or f"Expected pattern(s) not found: {', '.join(patterns[:3])}"
            elif check == "regex_absent":
                found = []
                for p in patterns:
                    found += _find_matches(lines, p)
                if found:
                    status = STATUS_FAIL
                    evidence = _snippet(lines, found)
                else:
                    status = STATUS_PASS
                    evidence = "No prohibited patterns found."
            elif check == "min_occurrences":
                found = []
                for p in patterns:
                    found += _find_matches(lines, p)
                if len(found) >= min_count:
                    status = STATUS_PASS
                    evidence = _snippet(lines, found)
                else:
                    status = STATUS_FAIL
                    evidence = manual_hint or f"Expected at least {min_count} match(es), found {len(found)}."
            elif check == "either_or":
                found = []
                for p in patterns:
                    found += _find_matches(lines, p)
                if found:
                    status = STATUS_PASS
                    evidence = _snippet(lines, found)
                else:
                    status = STATUS_FAIL
                    evidence = manual_hint or "None of the acceptable patterns were found."
            else:
                status = STATUS_MANUAL
                evidence = manual_hint or f"Unrecognized check type '{check}'. Review manually."
        except Exception as e:
            status = STATUS_UNKNOWN
            evidence = f"Rule evaluation error: {e!r}"

        findings.append(Finding(
            issue_id=rid,
            issue_name=name,
            status=status,
            fix_type=fix_type,
            remediation=remediation,
            evidence=evidence,
            device=device,
            vendor=vendor,
            notes=str(r.get("notes", "") or "").strip(),
        ))

    return findings
