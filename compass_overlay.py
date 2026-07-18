from imports import *
from constants import *


@dataclass
class CompassRoute:
    label: str
    ap_cost: int
    description: str
    path: list
    bg_color: PySide6.QtGui.QColor
    text_color: PySide6.QtGui.QColor


class CompassOverlay(QDialog):
    """
    Floating compass window showing Direct and Transit routes,
    sorted by AP cost.
    """

    def __init__(self, direct_route_info, transit_route_info, parent=None):
        """
        Args:
            direct_route_info: (ap_cost, description, path)
            transit_route_info: (ap_cost, description, path)
        """
        super().__init__(parent)

        self.setWindowTitle("Compass Routes")
        self.setFixedSize(200, 150)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowStaysOnTopHint
        )

        self.routes: list[CompassRoute] = []
        self._build_routes(direct_route_info, transit_route_info)
        self._build_ui()

    # =====================================================
    # Route Construction
    # =====================================================

    def _build_routes(self, direct, transit) -> None:
        self.routes = [
            CompassRoute(
                label="Direct Route",
                ap_cost=direct[0],
                description=direct[1],
                path=direct[2],
                bg_color=PySide6.QtGui.QColor("green"),
                text_color=PySide6.QtGui.QColor("white"),
            ),
            CompassRoute(
                label="Transit Route",
                ap_cost=transit[0],
                description=transit[1],
                path=transit[2],
                bg_color=PySide6.QtGui.QColor(128, 0, 128),
                text_color=PySide6.QtGui.QColor("white"),
            ),
        ]

        self.routes.sort(key=lambda r: r.ap_cost)

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        header = QLabel("Shortest Available Route:")
        header.setStyleSheet(
            "font-weight: bold; font-size: 14px;"
        )
        layout.addWidget(header)

        self.route_list = QListWidget()
        self.route_list.setFrameShape(QFrame.NoFrame)
        layout.addWidget(self.route_list)

        self._populate_route_list()

        self.route_list.itemClicked.connect(
            self._route_selected
        )

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _populate_route_list(self) -> None:
        self.route_list.clear()

        for route in self.routes:
            item = QListWidgetItem(
                f"{route.label} — {route.ap_cost} AP\n{route.description}"
            )
            item.setBackground(route.bg_color)
            item.setForeground(route.text_color)
            item.setData(Qt.UserRole, route)
            self.route_list.addItem(item)

    # =====================================================
    # Refresh
    # =====================================================

    def refresh(self, direct_route_info, transit_route_info) -> None:
        """
        Update overlay with new route data.
        """
        self._build_routes(
            direct_route_info,
            transit_route_info,
        )
        self._populate_route_list()

    # =====================================================
    # Selection
    # =====================================================

    def _route_selected(self, item: QListWidgetItem) -> None:
        route: CompassRoute = item.data(Qt.UserRole)

        if route and self.parent():
            self.parent().set_compass_display_from_overlay(
                route.label,
                (route.ap_cost, route.description, route.path),
            )
