# Switch CIS-style Configuration Review (Cisco + Juniper)

Offline CIS-aligned (CIS-style) configuration review for:
- Cisco IOS/NX-OS running-config exports
- Juniper Junos configurations (set/hierarchical)

Outputs: a PDF report with executive summary, pie chart, findings table, and evidence.

## Run
```bash
python -m venv .venv
# Windows without activation:
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe main.py
```

## Extend rules
Edit:
- rules/cisco_ios.yml
- rules/juniper_junos.yml

Check types:
- regex_present, regex_absent, either_or, min_occurrences, manual


## YAML note
If you edit regex patterns, prefer **single quotes** in YAML to avoid backslash escape issues (e.g., '\\s', '\\b').


## More checks
This version expands Cisco and Juniper CIS-style controls (management, AAA, logging, time, SNMP, and L2 protections). Many controls remain **MANUAL** when the setting cannot be reliably inferred from config alone.
