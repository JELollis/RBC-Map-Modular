"""Regression checks for startup state and responsive navigation."""

from __future__ import annotations

import ast
import contextlib
import io
import logging
import sqlite3
from pathlib import Path
from types import SimpleNamespace


from _app import load_app_tree, load_app_source
ROOT = Path(__file__).resolve().parent.parent
MAIN = Path("modular_app")


def _function(tree: ast.AST, name: str) -> ast.FunctionDef:
    matches = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name]
    assert len(matches) == 1, f"expected one {name} function"
    return matches[0]


def check_pending_destination_initialization(tree: ast.Module) -> None:
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RBCCommunityMap")
    init = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "__init__")
    assert any(
        isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Attribute)
            and target.attr == "pending_character_id_for_map"
            for target in node.targets
        )
        for node in ast.walk(init)
    ), "pending_character_id_for_map must be initialized in __init__"


def load_logging_helper(tree: ast.Module):
    helper = _function(tree, "get_logging_level_from_db")
    namespace = {
        "sqlite3": sqlite3,
        "sys": __import__("sys"),
        "logging": logging,
        "DB_PATH": ":memory:",
    }
    exec(compile(ast.Module(body=[helper], type_ignores=[]), str(MAIN), "exec"), namespace)
    return namespace["get_logging_level_from_db"]


def check_missing_settings_table_is_quiet(tree: ast.Module) -> None:
    helper = load_logging_helper(tree)
    # An in-memory database starts without the settings table and avoids
    # platform-specific cleanup/locking behavior in the regression check.
    helper.__globals__["DB_PATH"] = ":memory:"
    output = io.StringIO()
    with contextlib.redirect_stderr(output):
        level = helper(17)
    assert level == 17
    assert output.getvalue() == "", "missing settings table should not print a startup error"


def check_other_operational_errors_are_reported(tree: ast.Module) -> None:
    helper = load_logging_helper(tree)

    class LockedConnection:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def cursor(self):
            return self

        def execute(self, *_args):
            raise sqlite3.OperationalError("database is locked")

        def fetchone(self):
            return None

    class FakeSqlite:
        OperationalError = sqlite3.OperationalError

        @staticmethod
        def connect(_path):
            return LockedConnection()

    original_sqlite = helper.__globals__["sqlite3"]
    output = io.StringIO()
    try:
        helper.__globals__["sqlite3"] = FakeSqlite
        with contextlib.redirect_stderr(output):
            assert helper(23) == 23
    finally:
        helper.__globals__["sqlite3"] = original_sqlite
    assert "database is locked" in output.getvalue()


def check_splitter_resizes_navigation(tree: ast.Module) -> None:
    setup = _function(tree, "setup_ui_components")
    minimum_width = next(
        node.args[0]
        for node in ast.walk(setup)
        if isinstance(node, ast.Call)
        and ast.unparse(node.func) == "left_frame.setMinimumWidth"
    )
    assert ast.literal_eval(minimum_width) >= 270, "the character buttons need a 270 px navigation panel"

    calls = {ast.unparse(node) for node in ast.walk(setup) if isinstance(node, ast.Call)}
    assert "splitter.splitterMoved.connect(lambda *_args: self._schedule_navigation_resize())" in calls
    assert (
        "self._navigation_resize_timer.timeout.connect(self._update_navigation_sizes)" in calls
    ), "the resize timer must call the navigation sizing helper"


def check_navigation_sizes(tree: ast.Module) -> None:
    helper = _function(tree, "_update_navigation_sizes")
    namespace = {}
    exec(compile(ast.Module(body=[helper], type_ignores=[]), str(MAIN), "exec"), namespace)
    update_sizes = namespace["_update_navigation_sizes"]

    for width, height, initial_size, expected_size in (
        (300, 900, 280, 280),
        (220, 900, 280, 204),
        (300, 300, 280, 160),
    ):
        frame_sizes = []
        label_sizes = []
        redraws = []
        window = SimpleNamespace(
            left_frame=SimpleNamespace(width=lambda: width, height=lambda: height),
            minimap_size=initial_size,
            minimap_frame=SimpleNamespace(setFixedSize=lambda w, h: frame_sizes.append((w, h))),
            minimap_label=SimpleNamespace(setFixedSize=lambda w, h: label_sizes.append((w, h))),
            update_minimap=lambda: redraws.append(window.minimap_size),
        )

        update_sizes(window)
        update_sizes(window)
        panel = f"{width}×{height} panel"
        assert window.minimap_size == expected_size, panel
        expected_sizes = [(expected_size, expected_size)] if initial_size != expected_size else []
        assert frame_sizes == label_sizes == expected_sizes, panel
        assert redraws == ([expected_size] if expected_sizes else []), panel

    # An early resize can arrive before the navigation widgets exist.
    window = SimpleNamespace(minimap_label=object(), minimap_size=280)
    update_sizes(window)
    assert window.minimap_size == 280


def main() -> int:
    tree = load_app_tree()
    check_pending_destination_initialization(tree)
    check_missing_settings_table_is_quiet(tree)
    check_other_operational_errors_are_reported(tree)
    check_splitter_resizes_navigation(tree)
    check_navigation_sizes(tree)
    print("startup/layout checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
