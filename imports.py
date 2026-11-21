"""Shared imports for the RBC Community Map (modular snapshot)."""

#!/usr/bin/env python3
# Filename: main_1.0.0

"""
======================
License Agreement
======================

Copyright 2024–2026 RBC Community Map Team

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


=================================
RBC City Map Application (v1.0.0)
=================================

This application provides an interactive mapping and character management tool
for the browser-based vampire RPG **Vampires! The Dark Alleyway**, set in the
fictional RavenBlack City.

Version 1.0.0 moves all server-owned map locations to launch-time API sync.
While still packaged as a single file, it redacts credentials from logs, adds
request timeouts to the manual data update, fixes two latent bugs, and
consolidates the location-update flow into a single shared code path.

Map Coordinate Convention:
--------------------------
Use screen coordinates (a top-left-origin, Y-down coordinate system) for the
map. X increases to the right/east and Y increases downward/south; moving
left/west decreases X and moving up/north decreases Y. Treat the map origin
as the upper-left reference, preserving existing grid offsets and street
numbering. Use this convention consistently for map data, rendering,
navigation, and coordinate conversions; do not assume Cartesian positive-Y-up
coordinates. Viewport panning changes the visible area, not these directions.

Key Features:
-------------
- **WASD Minimap Navigation**: Move across the city grid using familiar keyboard controls.
- **Character Management**: Add and switch between characters with saved login credentials.
- **Minimap Visualization**: Display current location, nearby banks, taverns, transit stops,
  and AP-based destinations.
- **Discord Bot Data Integration**: Guild and shop location data is pulled from a live
  Discord bot via a secure HTTP endpoint (`locations.json`), replacing in-app scraping and
  supporting next-move countdowns.
- **Nickname Mapping**: Internal names are normalized across dropdowns
  (e.g., "Ace Porn" → "Ace Pawn").
- **Set Destination Dialog Enhancements**:
  - Dropdowns show nicknames, sorted and searchable.
  - Countdown overlays show remaining time to next guild/shop movement.
  - "Update Data" triggers a fresh data pull from the update service.
- **Theming Tools**: Customize UI colors and webview appearance using dedicated dialogs.
- **Log Viewer**: Live, filterable log output with optional debug visibility.
- **Damage Calculator**: Plan combat attacks and calculate required weapon damage.
- **Shopping List Tool**: Calculate item costs and charisma-discounted totals.
- **Power Reference Dialog**: Browse powers and set guild destinations for training.

Updated in v1.0.0:
-------------------
- Redacted the 'ip' cookie password portion in debug logs (login/logout state
  is still distinguishable) so credentials no longer reach on-disk logs.
- Added request timeouts to the manual "Update Data" action so a dead network
  cannot hang the UI thread.
- Fixed the SetDestinationDialog acceptance check (compared against a Qt signal
  instead of QDialog.DialogCode.Accepted) and an aliased fallback-dict bug.
- Consolidated the token -> trigger -> fetch update flow into a shared
  fetch_location_update() helper used by both the startup worker and update_data.

Carried over from v0.13.3.0 / v0.13.2:
- Replaced runtime pip auto-install with fail-fast dependency reporting.
- Request timeout handling for external HTTP calls.
- Hardened JavaScript login injection using safe string construction.

Modules Used:
-------------
- **sys, os**: Core system integration and path handling.
- **requests**: Fetches external JSON data (`locations.json`) from the update service.
- **re**: Regex for parsing and name normalization.
- **datetime**: Countdown and timestamp calculations.
- **bs4 (BeautifulSoup)**: Retained for legacy compatibility (no longer used for scraping).
- **PySide6**: Qt-based GUI framework, dialogs, embedded webview, and event system.
- **sqlite3**: Local data storage for characters, locations, settings, and logs.
- **logging**: Captures logs for display and debugging.
- **math**: AP cost and damage calculations.

=================================
Installation Instructions
=================================

For development environments, install the dependencies listed in
``requirements.txt`` (kept in sync with the in-code ``required_modules`` map):

- PySide6 (bundles the Qt WebEngine modules used by the embedded browser)
- beautifulsoup4
- requests

Packaged builds (e.g., Nuitka executables) include all required dependencies.

This version is distributed as a monolithic .py file or a compiled .exe via Nuitka.

Join the community:

Discord: https://discord.gg/rKamEZvK6X
"""

# -----------------------
# Startup Imports
# -----------------------

import logging

import json

import math

import os

import platform

import re

import sqlite3

import sys

import threading

import time

import uuid

import webbrowser

from datetime import datetime, timedelta, timezone

from pathlib import Path

from typing import TYPE_CHECKING, Tuple, Type, TypeVar, cast


import PySide6.QtGui  # kept for dynamic access

from PySide6 import QtCore


# -----------------------
# Third-Party Imports
# -----------------------

import requests

from bs4 import BeautifulSoup


from PySide6.QtCore import (
    QByteArray, QDateTime, QEasingCurve, QEvent, QMimeData,
    QPropertyAnimation, QRect, QSize, Qt, QTimer, QUrl,
    Slot as pyqtSlot, QObject, Signal, QThread,
)


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
# Splash Messages Decorator
# -----------------------

from functools import wraps

from typing import Callable, Any


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
            "--disable-gpu --disable-gpu-compositing",
        )
        # Virtual machines frequently expose an incomplete GLX/GBM stack.
        # Let Chromium use software rendering instead of failing during view
        # initialization when the host GPU cannot provide a scanout buffer.
        # Keep Qt Quick usable when the VM has no working GLX/EGL context.
        # Disabling the XCB integration entirely also prevents the app's own
        # Qt widgets from rendering, so use Qt's software backend instead.
        os.environ.setdefault("QT_QUICK_BACKEND", "software")
        os.environ.setdefault("QT_OPENGL", "software")

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


# -----------------------
# Damage Calculator Tool
# -----------------------

from dataclasses import dataclass


# -----------------------
# Compass Overlay
# -----------------------

from dataclasses import dataclass
