from __future__ import annotations

from typing import Dict, List, Tuple, Any

from .semver import matches_range


Finding = Dict[str, Any]


def scan_dependencies(
    deps: List[Tuple[str, str]],
    vuln_db: Dict[str, list],
) -> List[Finding]:
    findings: List[Finding] = []

    for name, version in deps:
        if name not in vuln_db:
            continue

        for entry in vuln_db[name]:
            vuln_range = entry.get("vulnerable")
            fixed = entry.get("fixed")
            cve = entry.get("cve")
            summary = entry.get("summary")

            if vuln_range and matches_range(version, vuln_range):
                findings.append(
                    {
                        "package": name,
                        "installed": version,
                        "vulnerable_range": vuln_range,
                        "fixed": fixed,
                        "cve": cve,
                        "summary": summary,
                    }
                )

    return findings
