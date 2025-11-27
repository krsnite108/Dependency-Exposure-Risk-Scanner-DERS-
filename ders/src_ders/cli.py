import argparse
import sys
from pathlib import Path

from .dependency_graph import build_dependency_graph, flatten_graph
from .osv_client import scan_all_dependencies, format_osv_results
from .report import print_report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="DERS - Dependency Exposure & Risk Scanner"
    )

    parser.add_argument(
        "requirements",
        type=Path,
        help="Path to requirements.txt (or similar) file containing dependencies.",
    )

    parser.add_argument(
        "--vuln-db",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "vulndb.json",
        help="Path to vulnerability database JSON (optional, reserved for offline mode).",
    )

    parser.add_argument(
        "--online",
        action="store_true",
        help="Enable online OSV scanning.",
    )

    args = parser.parse_args()

    if not args.requirements.exists():
        print(f"Error: Requirements file not found: {args.requirements}")
        sys.exit(1)

    # Step 1: Build dependency graph (creates temp venv, installs deps)
    print("[+] Resolving full dependency graph…")
    graph, venv_dir = build_dependency_graph(args.requirements)

    # Step 2: Flatten graph into (package, version) pairs via pip freeze
    print("[+] Flattening dependency graph…")
    flat_deps = flatten_graph(graph, venv_dir)

    # Step 3: Scan vulnerabilities
    if args.online:
        print("[+] Querying OSV.dev for vulnerabilities…")
        osv_results = scan_all_dependencies(flat_deps)
        findings = format_osv_results(osv_results, flat_deps)
    else:
        print("[+] Local/offline vulnerability DB scanning not implemented yet. Use --online.")
        sys.exit(1)

    # Step 4: Print report
    print_report(findings)


if __name__ == "__main__":
    main()
