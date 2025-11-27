from __future__ import annotations

from typing import Tuple


def parse_version(v: str) -> Tuple[int, ...]:
    """
    Parse version string like '1.2.3' into a tuple of ints (1, 2, 3).
    Non-numeric parts will be ignored in v0 (we can improve later).
    """
    parts = v.split(".")
    nums = []
    for p in parts:
        try:
            nums.append(int(p))
        except ValueError:
            # ignore for now, or truncate at first non-int
            break
    return tuple(nums)


def compare_versions(a: str, b: str) -> int:
    """
    Compare two version strings.

    Returns:
        -1 if a < b
         0 if a == b
         1 if a > b
    """
    va = parse_version(a)
    vb = parse_version(b)

    # normalize length by padding with zeros
    max_len = max(len(va), len(vb))
    va += (0,) * (max_len - len(va))
    vb += (0,) * (max_len - len(vb))

    if va < vb:
        return -1
    elif va > vb:
        return 1
    return 0


def matches_range(version: str, range_expr: str) -> bool:
    """
    Very small v1 range matcher.

    Supports:
      '<X.Y.Z'
      '<=X.Y.Z'
      '==X.Y.Z'

    Example: '<=2.19.0'
    """
    range_expr = range_expr.strip()
    if range_expr.startswith("<="):
        bound = range_expr[2:].strip()
        return compare_versions(version, bound) <= 0
    elif range_expr.startswith("<"):
        bound = range_expr[1:].strip()
        return compare_versions(version, bound) < 0
    elif range_expr.startswith("=="):
        bound = range_expr[2:].strip()
        return compare_versions(version, bound) == 0
    else:
        # unsupported in v1
        return False
