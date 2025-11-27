from typing import List, Dict, Any


def print_report(findings: List[Dict[str, Any]]) -> None:
    """Pretty-print normalized OSV findings."""
    if not findings:
        print("✅ No known vulnerable dependencies found.")
        return

    print("❗ Vulnerable dependencies detected:\n")

    for f in findings:
        print(f"- Package: {f['package']}")
        print(f"  Installed: {f['installed']}")
        print(f"  Vulnerable range: {f['vulnerable_range']}")
        if f.get("fixed"):
            print(f"  Fixed in: {f['fixed']}")
        if f.get("cve"):
            print(f"  CVE: {f['cve']}")
        if f.get("summary"):
            print(f"  Summary: {f['summary']}")
        print()
