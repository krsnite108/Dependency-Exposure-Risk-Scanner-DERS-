# Dependency Exposure & Risk Scanner (DERS)

A lightweight, developer-friendly tool for scanning Python project dependencies for known vulnerabilities using the OSV.dev API. DERS builds a complete dependency graph including **transitive dependencies** and detects security issues in your entire software bill of materials (SBOM).

---

##  Overview

Modern Python projects often depend on dozens (sometimes hundreds) of libraries. Many of these dependencies may contain known vulnerabilities, and your application may be affected **even if the vulnerable package is not a direct dependency**.

**DERS automatically:**

* Creates a *clean temporary virtual environment*
* Installs each dependency individually
* Extracts *all direct + transitive dependencies*
* Builds a dependency graph
* Queries **OSV.dev** for known vulnerabilities
* Produces a structured, readable security report

This makes it ideal for:

* Security analysis
* Audit reports
* Demonstrating vulnerability detection in interviews
* Learning how real-world dependency scanners work

---

##  Features

*  Full transitive dependency graph resolution
*  Clean isolated temporary environment
*  Online OSV.dev vulnerability scanning
*  Human-friendly security report
*  Works with standard `requirements.txt`
*  Gracefully skips incompatible dependencies (e.g., Python 3.13 issues)

---

##  Project Structure

```
project/
│
├── data/
│   └── vulndb.json         # (placeholder for future offline DB)
│
├── examples/
│   └── requirements.txt    # Sample requirements file
│
├── src_ders/
│   ├── cli.py              # Command-line interface
│   ├── dependency_graph.py # Graph builder & venv logic
│   ├── osv_client.py       # OSV API integration
│   ├── report.py           # Output formatter
│   └── __init__.py
│
├── README.md
├── pyproject.toml
└── requirements.txt
```

---

##  How DERS Works (Architecture)

### **1️⃣ Build a clean temporary environment**

DERS creates a temp virtualenv and installs each dependency **one-by-one**:

* If a package is incompatible with the host Python (e.g., NumPy on 3.13), it is skipped
* This allows maximum transitive resolution

### **2️⃣ Dependency Graph Construction**

Using Python’s built-in `importlib.metadata`:

* Extracts the dependencies of every installed package
* Recursively builds the full graph
* Avoids using pip internals

### **3️⃣ SBOM Flattening**

The full list of installed packages via `pip freeze` becomes the effective SBOM.

### **4️⃣ OSV Scanning**

Each (package, version) pair is queried against:

```
https://api.osv.dev/v1/query
```

OSV returns:

* Vulnerable version ranges
* CVEs
* Fix versions
* Summaries

### **5️⃣ Reporting**

DERS prints a clean, readable report listing:

* Package
* Installed version
* Vulnerable range
* Fix version
* CVE ID
* Summary

---

##  Installation

From project root:

```
pip install -e .
```

Ensure that `pip.conf` inside the temp venv uses PyPI instead of custom enterprise indexes.

---

##  Usage

Run the scanner on any `requirements.txt`:

```
ders path/to/requirements.txt --online
```

Example:

```
ders examples/requirements.txt --online
```

---

##  Example Output

Example results from scanning Flask, Requests, Django:

```
❗ Vulnerable dependencies detected:

- Package: Django
  Installed: 3.2.5
  Vulnerable range: >= 3.2, < 3.2.21
  Fixed in: 4.2.5
  CVE: CVE-2023-41164
  Summary: Django DoS vulnerability in uri_to_iri

- Package: requests
  Installed: 2.31.0
  Vulnerable range: >= 0, < 2.32.4
  Fixed in: 2.32.4
  CVE: CVE-2024-47081
  Summary: `.netrc` credential leak via malicious URLs
```

---

##  How This Differs From Real Tools

This project intentionally simplifies many aspects:

* No dependency resolver
* No environment markers
* No wheel metadata parsing
* No multi-ecosystem scanning

But:

* It demonstrates **all the core ideas** behind professional scanners like `pip-audit`, `npm audit`, SCA platforms, etc.

This makes DERS an excellent educational + portfolio project.

---

##  Roadmap

Future improvements may include:

* Offline vulnerability DB support
* Rich HTML/JSON output
* Visual dependency graphs
* Parallel OSV queries
* Poetry / Pipenv support
* SBOM export (CycloneDX)

---
