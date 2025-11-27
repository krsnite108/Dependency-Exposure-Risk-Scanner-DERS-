import requests
from typing import List, Dict, Any

OSV_URL = "https://api.osv.dev/v1/query"


def query_osv(package: str, version: str) -> dict:
    """Query OSV.dev for vulnerabilities for a given PyPI package + version."""
    payload = {
        "package": {"name": package, "ecosystem": "PyPI"},
        "version": version,
    }
    resp = requests.post(OSV_URL, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def scan_all_dependencies(dep_list: List[tuple[str, str]]) -> Dict[str, List[dict]]:
    """
    Given a list of (package, version) pairs, query OSV for each.
    Returns {package: [vulns]} only for vulnerable packages.
    """
    results: Dict[str, List[dict]] = {}

    for name, ver in dep_list:
        try:
            data = query_osv(name, ver)
        except Exception:
            continue

        vulns = data.get("vulns", [])
        if vulns:
            results[name] = vulns

    return results


def format_osv_results(osv_results: Dict[str, List[dict]], dep_list: List[tuple[str, str]]):
    """
    Convert OSV raw results + installed versions into a unified report structure.
    """
    formatted = []

    version_map = {pkg.lower(): ver for pkg, ver in dep_list}

    for pkg, vulns in osv_results.items():
        installed_version = version_map.get(pkg.lower(), "unknown")

        for vuln in vulns:
            affected = vuln.get("affected", [])
            ranges = []
            fixed = None

            for aff in affected:
                for r in aff.get("ranges", []):
                    if r.get("type") == "ECOSYSTEM":
                        for event in r.get("events", []):
                            if "introduced" in event:
                                ranges.append(f">= {event['introduced']}")
                            if "fixed" in event:
                                fixed = event["fixed"]
                                ranges.append(f"< {event['fixed']}")

            vulnerable_range = ", ".join(ranges) if ranges else "unknown"
            cve = None
            for alias in vuln.get("aliases", []):
                if alias.startswith("CVE-"):
                    cve = alias

            formatted.append(
                {
                    "package": pkg,
                    "installed": installed_version,
                    "vulnerable_range": vulnerable_range,
                    "fixed": fixed,
                    "cve": cve,
                    "summary": vuln.get("summary", ""),
                }
            )

    return formatted
