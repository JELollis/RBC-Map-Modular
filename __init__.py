"""
RBC Community Map — modular build.

This package is the modular decomposition of the monolithic
``main_0.13.3.0.py`` application. The modules use flat, absolute imports
(``from imports import *``) and are launched via ``main.py``:

    python main.py

Each dialog/component lives in its own module (see ``rbc_community_map.py``
for the main window and the ``*_dialog.py`` / tool modules for the rest).
"""
