"""Load the modular application as a single merged AST for regression checks.

The monolithic ``main_X.py`` regression tools parse one file and extract
top-level classes/functions by name. The modular build splits that file into
one module per component, so this helper merges every top-level node from the
package's ``*.py`` files into one synthetic ``ast.Module``. Extracted nodes can
then be compiled and exec'd exactly as before.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_app_tree() -> ast.Module:
    """Return a merged AST of every top-level node in the package's modules."""
    body: list[ast.stmt] = []
    for path in sorted(ROOT.glob("*.py")):
        if path.name == "__init__.py":
            continue
        body.extend(ast.parse(path.read_text(encoding="utf-8")).body)
    return ast.Module(body=body, type_ignores=[])


def load_app_source() -> str:
    """Return the concatenated source of every package module."""
    parts = []
    for path in sorted(ROOT.glob("*.py")):
        if path.name == "__init__.py":
            continue
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)
