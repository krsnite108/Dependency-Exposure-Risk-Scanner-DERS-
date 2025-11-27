import subprocess
import sys
import tempfile
from pathlib import Path
from importlib.metadata import version, requires, PackageNotFoundError


def create_temp_env(requirements_file: Path) -> Path:
    """
    Create a temporary venv and install each dependency individually.
    If a dependency fails to install (e.g., incompatible with Python 3.13),
    it is skipped gracefully. This ensures maximum graph completeness.
    """
    temp_dir = Path(tempfile.mkdtemp())
    venv_dir = temp_dir / "venv"

    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

    pip_conf = venv_dir / "pip.conf"
    pip_conf.write_text("""
[global]
index-url = https://pypi.org/simple
""")

    pip_path = venv_dir / "bin" / "pip"

    print("Installing dependencies individually…")

    # Read requirements.txt manually
    reqs = []
    for line in requirements_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        reqs.append(line)

    skipped = []

    # Install each dependency one-by-one
    for req in reqs:
        print(f"    ↳ Installing {req}…")
        result = subprocess.run(
            [str(pip_path), "install", "--no-cache-dir", req],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"[!] Failed to install {req}, skipping…")
            skipped.append(req)
            continue

    if skipped:
        print("[!] The following dependencies were skipped due to installation failure:")
        for s in skipped:
            print(f"    - {s}")
        print("[!] Continuing with remaining dependencies…")

    return venv_dir


def extract_dependencies(pkg: str) -> list[str]:
    try:
        deps = requires(pkg) or []
    except PackageNotFoundError:
        return []

    cleaned = []
    for dep in deps:
        dep_name = dep.split(";")[0].strip().split()[0]
        cleaned.append(dep_name)
    return cleaned


def build_graph_for_package(pkg: str, graph: dict):
    if pkg in graph:
        return graph

    deps = extract_dependencies(pkg)
    graph[pkg] = deps

    for dep in deps:
        build_graph_for_package(dep, graph)

    return graph


def build_dependency_graph(requirements_file: Path) -> tuple[dict, Path]:
    venv_dir = create_temp_env(requirements_file)
    graph = {}

    python_bin = venv_dir / "bin" / "python"

    result = subprocess.run(
        [str(python_bin), "-m", "pip", "freeze"],
        capture_output=True,
        text=True,
        check=True
    )

    for line in result.stdout.splitlines():
        if "==" in line:
            pkg, ver = line.split("==")
            build_graph_for_package(pkg, graph)

    return graph, venv_dir


def flatten_graph(graph: dict, venv_dir: Path) -> list[tuple[str, str]]:
    """
    Extract a full SBOM directly from pip freeze inside the temp venv.
    This ensures ALL installed packages (direct + transitive) are scanned.
    """
    python_bin = venv_dir / "bin" / "python"

    # Get full list of installed packages
    result = subprocess.run(
        [str(python_bin), "-m", "pip", "freeze"],
        capture_output=True,
        text=True,
        check=True
    )

    flattened = []

    for line in result.stdout.splitlines():
        if "==" not in line:
            continue
        pkg, ver = line.split("==")
        flattened.append((pkg, ver))

    return flattened
