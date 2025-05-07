from imports import *
from constants import *

class CompassOverlay(QDialog):
    """
    A floating compass window that shows both Direct and Transit routes to a destination,
    sorted by AP cost. Color-coded: Green = Direct, Purple = Transit.
    """

    def __init__(self, direct_route_info, transit_route_info, parent=None):
        """
        Args:
            direct_route_info (tuple): (int ap_cost, str description)
            transit_route_info (tuple): (int ap_cost, str description)
        """
        super().__init__(parent)
        self.setWindowTitle("Compass Routes")
        self.setFixedSize(200, 150)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.direct_route_info = direct_route_info
        self.transit_route_info = transit_route_info

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        header = QLabel("Shortest Available Route:")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)

        self.route_list = QListWidget()
        self.route_list.setFrameShape(QFrame.NoFrame)

        # Track route data
        self.route_mapping = {}

        routes = [
            ("Direct Route", self.direct_route_info[0], self.direct_route_info[1], PySide6.QtGui.QColor("green"), PySide6.QtGui.QColor("white")),
            ("Transit Route", self.transit_route_info[0], self.transit_route_info[1], PySide6.QtGui.QColor(128, 0, 128), PySide6.QtGui.QColor("white")),  # dark purple
        ]
        routes.sort(key=lambda r: r[1])  # sort by AP cost

        for label, cost, desc, bg_color, text_color in routes:
            item = QListWidgetItem(f"{label} — {cost} AP\n{desc}")
            item.setBackground(bg_color)
            item.setForeground(text_color)
            self.route_list.addItem(item)
            path = self.direct_route_info[2] if label == "Direct Route" else self.transit_route_info[2]
            self.route_mapping[label] = (cost, desc, path)

        self.route_list.itemClicked.connect(self.route_selected)  # ✅ Hook click signal
        layout.addWidget(self.route_list)

        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def refresh(self, direct_route_info, transit_route_info):
        """
        Update the overlay with new route data.
        """
        self.direct_route_info = direct_route_info
        self.transit_route_info = transit_route_info

        self.route_list.clear()
        self.route_mapping = {}  # ✅ Reset once outside the loop

        # Unpack only ap + desc, exclude path (3rd element), just like in _init_ui
        routes = [
            ("Direct Route", self.direct_route_info[0], self.direct_route_info[1], PySide6.QtGui.QColor("green"), PySide6.QtGui.QColor("white")),
            ("Transit Route", self.transit_route_info[0], self.transit_route_info[1], PySide6.QtGui.QColor(128, 0, 128), PySide6.QtGui.QColor("white")),
        ]
        routes.sort(key=lambda r: r[1])  # Sort by AP

        for label, cost, desc, bg_color, text_color in routes:
            item = QListWidgetItem(f"{label} — {cost} AP\n{desc}")
            item.setBackground(bg_color)
            item.setForeground(text_color)
            self.route_list.addItem(item)

            # ✅ Preserve path too for selection support
            path = self.direct_route_info[2] if label == "Direct Route" else self.transit_route_info[2]
            self.route_mapping[label] = (cost, desc, path)

    def route_selected(self, item):
        label_text = item.text().split("—")[0].strip()
        route_info = self.route_mapping.get(label_text)
        if route_info and self.parent():
            self.parent().set_compass_display_from_overlay(label_text, route_info)
