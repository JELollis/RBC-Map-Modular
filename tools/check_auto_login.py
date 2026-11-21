"""Regression checks for cookie rejection and default-character login paths."""

from __future__ import annotations

import ast
import json
import logging
import shutil
import subprocess
from pathlib import Path


from _app import load_app_tree, load_app_source
ROOT = Path(__file__).resolve().parent.parent
MAIN = Path("modular_app")


def class_method(tree: ast.Module, name: str) -> ast.FunctionDef:
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RBCCommunityMap")
    matches = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == name]
    assert len(matches) == 1, f"expected one {name} method"
    return matches[0]


def check_rejected_cookie_queues_password(tree: ast.Module) -> None:
    method = class_method(tree, "_handle_cookie_login_page")
    namespace = {"logging": logging}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(MAIN), "exec"), namespace)

    calls: list[str] = []
    fake = type("FakeWindow", (), {})()
    fake._pending_cookie_request_id = 4
    fake._pending_cookie_character = "Alice"
    fake._queue_password_login = lambda name: calls.append(f"queue:{name}")
    fake.login_selected_character = lambda: calls.append("login")

    namespace["_handle_cookie_login_page"](fake, 4, "Alice", True)
    assert calls == ["queue:Alice", "login"]
    assert fake._pending_cookie_request_id is None
    assert fake._pending_cookie_character is None

    calls.clear()
    fake._pending_cookie_request_id = 5
    fake._pending_cookie_character = "Alice"
    namespace["_handle_cookie_login_page"](fake, 4, "Alice", True)
    assert calls == [], "stale cookie-page callbacks must not start another login"


def check_password_login_clears_pending_cookie(tree: ast.Module) -> None:
    """Queueing a password login must invalidate a pending cookie check so a
    stale callback cannot clobber the newer login attempt."""
    methods = [
        class_method(tree, "_queue_password_login"),
        class_method(tree, "_handle_cookie_login_page"),
    ]
    namespace = {"logging": logging}
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(MAIN), "exec"), namespace)

    calls: list[str] = []
    fake = type("FakeWindow", (), {})()
    fake._login_request_id = 4
    fake.pending_login = False
    fake._pending_login_character = None
    fake._login_retry_count = 0
    fake._pending_cookie_character = "Alice"
    fake._pending_cookie_request_id = 4
    fake.login_selected_character = lambda: calls.append("login")
    fake._queue_password_login = lambda name: namespace["_queue_password_login"](fake, name)

    # Bob's password login is queued while Alice's cookie check is pending.
    namespace["_queue_password_login"](fake, "Bob")
    assert fake._pending_cookie_character is None
    assert fake._pending_cookie_request_id is None
    # Alice's stale cookie-page callback then arrives.
    namespace["_handle_cookie_login_page"](fake, 4, "Alice", True)

    assert fake._pending_login_character == "Bob"
    assert fake.pending_login is True
    assert calls == [], "stale cookie callback must not start another login"


def check_password_change_and_default_paths(tree: ast.Module) -> None:
    modify_source = ast.unparse(class_method(tree, "modify_character"))
    assert "active_cookie" in modify_source
    assert "delete_secret" in modify_source
    assert "COOKIE_SECRET_NAMESPACE" in modify_source

    default_source = ast.unparse(class_method(tree, "set_default_character"))
    assert "_queue_password_login" in default_source
    assert "switch_to_character" in default_source


def check_login_detector_matches_injector(tree: ast.Module) -> None:
    """Keep cookie detection and credential injection on the same finder."""
    for method in ("on_webview_load_finished", "login_selected_character"):
        source = ast.unparse(class_method(tree, method))
        assert "LOGIN_FORM_FINDER_JS" in source, f"{method} must share the login form finder"


def check_login_finder_behavior(tree: ast.Module) -> None:
    node_executable = shutil.which("node")
    if node_executable is None:
        raise SystemExit(
            "Auto-login regression checks require Node.js. Install Node.js and ensure 'node' is on PATH."
        )

    names = {"LOGIN_FORM_FIELDS", "LOGIN_FORM_FINDER_JS"}
    assignments = [
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id in names
    ]
    namespace = {"json": json}
    exec(compile(ast.Module(body=assignments, type_ignores=[]), str(MAIN), "exec"), namespace)
    subprocess.run(
        [node_executable, str(ROOT / "tools" / "check_login_finder.js")],
        input=namespace["LOGIN_FORM_FINDER_JS"],
        text=True,
        check=True,
    )


def check_pending_map_state_initialized(tree: ast.Module) -> None:
    """AUD-030/L1: __init__ must initialize pending_character_id_for_map
    before any webview loadFinished callback can read it."""
    init = class_method(tree, "__init__")
    assigned = {
        target.attr
        for node in ast.walk(init)
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Name)
        and target.value.id == "self"
    }
    assert "pending_character_id_for_map" in assigned


def main() -> int:
    tree = load_app_tree()
    check_rejected_cookie_queues_password(tree)
    check_password_login_clears_pending_cookie(tree)
    check_password_change_and_default_paths(tree)
    check_login_detector_matches_injector(tree)
    check_login_finder_behavior(tree)
    check_pending_map_state_initialized(tree)
    print("auto-login checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
