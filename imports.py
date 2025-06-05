import logging
import logging.handlers
import subprocess
import sys

# List of required modules with pip package names (some differ from import names)
required_modules = {
    'PySide6.QtCore': 'PySide6',
    'PySide6.QtGui': 'PySide6',
    'PySide6.QtNetwork': 'PySide6',
    'PySide6.QtWebChannel': 'PySide6',
    'PySide6.QtWebEngineWidgets': 'PySide6',
    'PySide6.QtWidgets': 'PySide6',
    'bs4': 'beautifulsoup4',
    'datetime': 'datetime',        # Built-in
    're': 're',                    # Built-in
    'discord': 'discord.py',
    'requests': 'requests',
    'sqlite3': 'sqlite3',          # Built-in
    'time': 'time',                # Built-in
    'webbrowser': 'webbrowser'     # Built-in
}

def check_and_install_modules(modules: dict[str, str]) -> bool:
    missing_modules = []
    pip_installable = []

    for module, pip_name in modules.items():
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
            if pip_name not in ('re', 'time', 'sqlite3', 'webbrowser', 'datetime'):
                pip_installable.append(pip_name)

    if not missing_modules:
        return True

    print("The following modules are missing:")
    for mod in missing_modules:
        print(f"- {mod}")

    if not pip_installable:
        print("All missing modules are built-ins that should come with Python.")
        return False

    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        _ = QApplication(sys.argv)
        response = QMessageBox.question(
            None, "Missing Modules",
            f"Missing modules: {', '.join(missing_modules)}\n\nInstall with pip?",
            QMessageBox.Yes | QMessageBox.No
        )
        if response != QMessageBox.Yes:
            return False
    except ImportError:
        response = input(f"\nInstall missing modules ({', '.join(set(pip_installable))}) with pip? (y/n): ").strip().lower()
        if response != 'y':
            return False

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + list(set(pip_installable)))
        for module in missing_modules:
            __import__(module)
        return True
    except Exception as e:
        print(f"Failed to install or import modules: {e}")
        return False


if not check_and_install_modules(required_modules):
    sys.exit("Missing required modules. Please install and retry.")

# -----------------------
# Actual Imports
# -----------------------

# Built-in / stdlib
import math
import os
import re
import sqlite3
import webbrowser
from collections.abc import KeysView
from datetime import datetime, timedelta, timezone

# Third-party
import discord
import requests
from bs4 import BeautifulSoup

# PySide6 Core
from PySide6.QtCore import (
    QByteArray, QDateTime, QEasingCurve, QEvent, QMimeData,
    QPoint, QPropertyAnimation, QRect, QSize, Qt, QTimer, QUrl,
    Slot as pyqtSlot
)

# PySide6 GUI
import PySide6.QtGui  # Keep for dynamic access
from PySide6.QtGui import QIcon

# PySide6 Widgets
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QColorDialog, QComboBox, QCompleter,
    QDialog, QFileDialog, QFormLayout, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QMessageBox, QPushButton, QScrollArea, QSplashScreen,
    QStyle, QTabWidget, QTableWidget, QTableWidgetItem, QTextEdit,
    QVBoxLayout, QWidget, QInputDialog, QSizePolicy
)

# PySide6 Web
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView

# PySide6 Network
from PySide6.QtNetwork import QNetworkCookie

# Typing
from typing import TYPE_CHECKING, List, Tuple, Type, TypeVar, cast
