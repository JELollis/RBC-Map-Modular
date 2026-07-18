"""
Shared imports and runtime environment setup for the RBC Community Map.

This module centralizes every standard-library and third-party import used
across the modular application so individual modules can simply do
``from imports import *``. It mirrors the import surface of the original
monolithic ``main_0.13.3.0.py`` build.
"""

# -----------------------
# Standard Library
# -----------------------

import logging
import logging.handlers
import math
import os
import platform
import re
import sqlite3
import sys
import time
import webbrowser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from functools import wraps
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING, Any, Callable, Dict, List, Optional,
    Tuple, Type, TypeVar, Union, cast,
)

# -----------------------
# Third-Party
# -----------------------

import requests
from bs4 import BeautifulSoup


# -----------------------
# OS-Specific Environment Setup
# -----------------------

def configure_qtwebengine_environment() -> None:
    """
    Apply OS-specific environment variables required for QtWebEngine stability.

    These must be set BEFORE any QtWebEngine components are initialized.
    """
    platform_name = sys.platform

    if platform_name.startswith("linux"):
        # Linux / Proton / containerized environments
        os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")
        os.environ.setdefault(
            "QTWEBENGINE_CHROMIUM_FLAGS",
            "--disable-software-rasterizer",
        )

    elif platform_name == "darwin":
        # macOS (notably VMware / Parallels GPU instability)
        os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")
        os.environ.setdefault(
            "QTWEBENGINE_CHROMIUM_FLAGS",
            "--disable-gpu",
        )
        os.environ.setdefault(
            "QTWEBENGINE_DICTIONARIES_PATH",
            "/tmp",
        )


# Apply environment configuration immediately, before any Qt imports.
configure_qtwebengine_environment()


# -----------------------
# PySide6
# -----------------------

import PySide6.QtGui  # kept for dynamic access
from PySide6 import QtCore
from PySide6.QtCore import (
    QByteArray, QDateTime, QEasingCurve, QEvent, QMimeData,
    QPropertyAnimation, QRect, QSize, Qt, QTimer, QUrl,
    Slot as pyqtSlot, QObject, Signal, QThread,
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QColorDialog, QComboBox, QCompleter,
    QDialog, QFileDialog, QFormLayout, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QMessageBox, QPushButton, QScrollArea, QSplashScreen,
    QStyle, QTabWidget, QTableWidget, QTableWidgetItem, QTextEdit,
    QVBoxLayout, QWidget, QInputDialog, QSizePolicy, QStackedWidget,
)
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtNetwork import QNetworkCookie


# -----------------------
# Type Checking
# -----------------------

if TYPE_CHECKING:
    class Scraper:
        def scrape_guilds_and_shops(self) -> None: ...
        def close_connection(self) -> None: ...

    class MainWindowType(QWidget):
        current_css_profile: str
        selected_character: dict | None
        destination: tuple[int, int] | None
        website_frame: QWebEngineView
        scraper: Scraper

        columns: dict[str, int]
        rows: dict[str, int]

        def apply_custom_css(self, css: str) -> None: ...
        def update_minimap(self) -> None: ...
