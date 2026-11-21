"""Check that power selection fills values without repeating field captions."""

from __future__ import annotations

import ast
import os
import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path
from typing import Type
from unittest.mock import Mock

from _app import load_app_tree, load_app_source
MAIN = Path("modular_app")

_QT_WIDGET_NAMES = (
    "QApplication", "QDialog", "QHBoxLayout", "QLabel", "QListWidget",
    "QListWidgetItem", "QPushButton", "QTextEdit", "QVBoxLayout",
)
_QT_PROVISION_MARKER = Path("/tmp/.rbc-map-qt-native-provisioned")


def _provision_qt_native_libs() -> bool:
    """Install Qt native libraries on CI runners, at most once per runner."""
    if _QT_PROVISION_MARKER.exists():
        return True
    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(
            ["sudo", "apt-get", "install", "-y",
             "libegl1", "libgl1", "libxkbcommon0", "libfontconfig1"],
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Qt native library provisioning failed: {exc}")
        return False
    _QT_PROVISION_MARKER.touch()
    return True


def _bind_qt() -> bool:
    try:
        from PySide6 import QtCore, QtWidgets
    except (ImportError, OSError) as exc:
        print(f"Qt import failed: {exc}")
        return False
    globals().update(Qt=QtCore.Qt, **{name: getattr(QtWidgets, name) for name in _QT_WIDGET_NAMES})
    return True


_QT_PROBE = (
    "import os; os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen');"
    "from PySide6.QtCore import Qt;"
    "from PySide6.QtWidgets import QApplication;"
    "app = QApplication.instance() or QApplication([])"
)


def _probe_qt() -> bool:
    """Verify Qt imports and the offscreen plugin loads, in a subprocess so
    a platform-plugin abort cannot kill this checker before provisioning."""
    result = subprocess.run(
        [sys.executable, "-c", _QT_PROBE],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Qt offscreen probe failed (exit {result.returncode}): {result.stderr.strip()[-400:]}")
        return False
    return True


def _ensure_qt() -> bool:
    """Use Qt when it works; on CI, provision native libs and re-verify."""
    if _probe_qt() and _bind_qt():
        return True
    if not os.environ.get("CI") or not _provision_qt_native_libs():
        return False
    return _probe_qt() and _bind_qt()


def main() -> None:
    if not _ensure_qt():
        message = "powers details checks skipped: Qt unavailable"
        if os.environ.get("CI"):
            raise SystemExit(f"{message} (CI requires Qt; install native Qt libraries)")
        print(message)
        return
    tree = load_app_tree()
    dialog = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "PowersDialog")
    names = {"_build_ui", "_create_labeled_field", "load_power_info"}
    methods = [node for node in dialog.body if isinstance(node, ast.FunctionDef) and node.name in names]
    namespace = {**globals(), "T": object}
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(MAIN), "exec"), namespace)

    class TestPanel(QDialog):
        _build_ui = namespace["_build_ui"]
        _create_labeled_field = namespace["_create_labeled_field"]
        load_power_info = namespace["load_power_info"]

        def set_destination(self):
            raise AssertionError("the rendering test must not set a destination")

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    with closing(sqlite3.connect(":memory:")) as conn:
        conn.execute("CREATE TABLE powers (name, guild, cost, quest_info, skill_info)")
        conn.executemany(
            "INSERT INTO powers VALUES (?, ?, ?, ?, ?)",
            [("Power A", "Guild A", 0, "Quest", "Skill"), ("Power B", None, None, None, None)],
        )
        panel = TestPanel()
        panel.db_connection = conn
        panel._resolve_destination_for_power = Mock()
        panel._build_ui()
        widgets = [
            panel.details_panel.itemAt(i).widget()
            for i in range(panel.details_panel.count())
        ]
        captions = (
            ("<b>Power:</b>", panel.power_name_label),
            ("<b>Guild:</b>", panel.guild_label),
            ("<b>Cost:</b>", panel.cost_label),
        )
        for caption, value_widget in captions:
            matches = [i for i, widget in enumerate(widgets) if isinstance(widget, QLabel) and widget.text() == caption]
            assert len(matches) == 1, caption
            assert widgets[matches[0] + 1] is value_widget, caption

        for name, guild, cost, quest, skill in (
            ("Power A", "Guild A", "0 coins", "Quest", "Skill"),
            ("Power B", "Unknown", "Unknown", "None", "None"),
        ):
            panel.load_power_info(QListWidgetItem(name))
            assert panel.power_name_label.text() == name
            assert panel.guild_label.text() == guild
            assert panel.cost_label.text() == cost
            assert panel.quest_info_text.toPlainText() == quest
            assert panel.skill_info_text.toPlainText() == skill
        panel._resolve_destination_for_power.assert_called_with("Power B", None)
        panel.close()
    app.processEvents()
    print("powers details checks passed")


if __name__ == "__main__":
    main()
