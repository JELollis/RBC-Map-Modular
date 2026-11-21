"""Shared imports for the RBC Community Map (modular snapshot)."""

#!/usr/bin/env python3
# Filename: main_0.13.2

"""
======================
License Agreement
======================

Copyright 2024-2025 RBC Community Map Team

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


=================================
RBC City Map Application (v0.13.2)
=================================

This application provides an interactive mapping and character management tool for the browser-based vampire RPG
**Vampires! The Dark Alleyway**, set in the fictional RavenBlack City.

Version 0.13.2 represents a small security and robustness update on v0.13.1.
While still packaged as a single file, upgrades include safer JavaScript login injection, request timeouts to
avoid blocking background threads, and removal of runtime pip auto-install behavior (packagers should provide
dependencies).

Key Features:
-------------
- **WASD Minimap Navigation**: Move across the city grid using familiar keyboard controls.
- **Character Management**: Add and switch between characters with saved login credentials.
- **Minimap Visualization**: Display current location, nearby banks, taverns, transit stops, and AP-based destinations.
- **Discord API Integration**: All guild/shop location data now pulled from a live Discord bot (`locations.json`)—
  replaces in-app scraping and adds support for next move countdowns.
- **Nickname Mapping**: Internal names are now fully normalized across dropdowns (e.g., "Ace Porn" → "Ace Pawn").
- **Set Destination Dialog Enhancements**:
  - Dropdowns show nicknames, sorted and searchable.
  - Countdown overlays show remaining time to next guild/shop movement.
  - "Update Data" triggers the Discord bot API for a fresh scrape.
- **Theming Tools**: Customize UI colors and webview appearance using dedicated dialogs.
- **Log Viewer**: Live filterable log output with optional debug visibility.
- **Damage Calculator**: Plan combat attacks and see total required weapon damage.
- **Shopping List Tool**: Calculate item costs and charisma-discounted totals.
- **Power Reference Dialog**: Browse powers and set guild destinations for training.

Updated in v0.13.2:
-------------------
- Replace runtime pip auto-install with fail-fast dependency reporting (packaging must provide dependencies).
- Add request timeouts (default 10s) for external HTTP calls to improve robustness.
- Use json.dumps to safely construct JS string literals for login script injection (avoids accidental JS injection).

Modules Used:
-------------
- **sys, os**: Core system integration and path handling.
- **requests**: API fetches from external JSON (locations.json).
- **re**: Regex for parsing and name normalization.
- **datetime**: Countdown and timestamp calculations.
- **bs4 (BeautifulSoup)**: Retained for legacy compatibility (no longer used for scraping).
- **PySide6**: Provides the full Qt GUI, dialogs, embedded webview, and event system.
- **sqlite3**: Local data storage for characters, locations, settings, and logs.
- **logging**: Captures logs for display and debugging.
- **math**: AP cost and damage calculations.

=================================
Installation Instructions
=================================
To install required dependencies:
```bash
pip install requests bs4 PySide6 PySide6-WebEngine
```

This version is distributed as a monolithic .py file or a compiled .exe via Nuitka.

Join the community:

Discord: https://discord.gg/rKamEZvK6X

"""


# -----------------------
# Startup Imports
# -----------------------

import logging

import logging.handlers

import platform

import time


from PySide6 import QtCore



# -----------------------
# Imports Handling
# -----------------------
import sys


# -----------------------
# Actual Imports
# -----------------------

# Built-in / stdlib
import math

import os

import re

import sqlite3

import threading

import webbrowser

from collections.abc import KeysView

from datetime import datetime, timedelta, timezone


# Third-party
import requests

from bs4 import BeautifulSoup


# PySide6 Core
from PySide6.QtCore import (
    QByteArray, QDateTime, QEasingCurve, QEvent, QMimeData,
    QPoint, QPropertyAnimation, QRect, QSize, Qt, QTimer, QUrl,
    Slot as pyqtSlot, QObject, QThread, Signal, QThreadPool
)


# PySide6 GUI
import PySide6.QtGui  # Keep for dynamic access


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
