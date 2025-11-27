from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple


def load_requirements(path: Path) -> List[Tuple[str, str]]:
    """
    Parse a simple requirements.txt of the form:
        package==version

    Returns a list of (name, version) pairs.
    """
    deps: List[Tuple[str, str]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "==" not in line:
            # later you can handle other operators, but keep v1 simple
            continue
        name, version = line.split("==", 1)
        deps.append((name.strip().lower(), version.strip()))
    return deps


def load_vuln_db(path: Path) -> Dict[str, list]:
    """
    Load vulnerability database from JSON.

    Structure:
    {
      "package_name": [
        { "vulnerable": "<=2.0.0", "fixed": "2.0.1", "cve": "...", "summary": "..." }
      ]
    }
    """
    return json.loads(path.read_text())
