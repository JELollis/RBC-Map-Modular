from imports import *
from constants import *
from directories  import *
from logging_setup import *
from cookies import *
from database import *
from scraper import *
from character_dialog import *
from compass_overlay import *
from css_customization_dialog import *
from damage_calculator import *
from database_viewer import *
from discord_server_dialog import *
from log_viewer import *
from powers_dialog import *
from set_destination_dialog import *
from shopping_list_tool import *
from splash import *
from theme_customization_dialog import *


class RBCCommunityMap(QMainWindow):
    """
    Main application class for the RBC Community Map.
    """

    def __init__(self):
        """
        Initialize the RBCCommunityMap and its components efficiently.

        Sets up the main window, scraper, cookie handling, data loading, and UI components
        with proper error handling and asynchronous initialization where possible.
        """
        super().__init__()

        # Core state flags
        self.is_updating_minimap = False
        self.login_needed = True
        self.webview_loaded = False
        self.splash = None

        # Compass route state
        self.selected_route_label = None  # "Direct Route" or "Transit Route"
        self.selected_route_description = None  # Full arrow description shown in the compass label
        self.selected_route_path = None  # List of (x, y) coordinate tuples to draw on minimap

        # Initialize character coordinates
        self.character_x = None
        self.character_y = None
        self.selected_character = None
        self.destination = None

        # Initialize essential components early
        self._init_data()
        self._init_scraper()
        self._init_window_properties()
        self._init_web_profile()

        # UI and character setup
        self._init_ui_state()
        self._init_characters()
        self._init_ui_components()

        # Final setup steps
        self._finalize_setup()

    @splash_message(None)
    def _init_scraper(self) -> None:
        """Initialize the AVITD scraper and start scraping in a separate thread."""
        self.scraper = Scraper()
        # Use QThread for non-blocking scraping (assuming scraper supports it)
        from PySide6.QtCore import QThreadPool
        QThreadPool.globalInstance().start(lambda: self.scraper.scrape_guilds_and_shops())
        logging.debug("Started scraper in background thread")

    @splash_message(None)
    def _init_window_properties(self) -> None:
        """Set up main window properties."""
        try:
            self.setWindowIcon(PySide6.QtGui.QIcon('images/favicon.ico'))
            self.setWindowTitle('RBC Community Map')
            self.setGeometry(100, 100, 1200, 800)
            self.load_theme_settings()
            self.apply_theme()
        except Exception as e:
            logging.error(f"Failed to set window properties: {e}")
            # Fallback to default icon/title if needed
            self.setWindowTitle('RBC Community Map (Fallback)')

    @splash_message(None)
    def _init_web_profile(self) -> None:
        """Set up QWebEngineProfile for cookie handling."""
        self.web_profile = QWebEngineProfile.defaultProfile()
        cookie_storage_path = os.path.join(os.getcwd(), 'sessions')
        try:
            os.makedirs(cookie_storage_path, exist_ok=True)
            # noinspection PyUnresolvedReferences
            self.web_profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
            self.web_profile.setPersistentStoragePath(cookie_storage_path)
            self.setup_cookie_handling()
        except OSError as e:
            logging.error(f"Failed to set up cookie storage at {cookie_storage_path}: {e}")
            # Continue with in-memory cookies if storage fails

    @splash_message(None)
    def _init_data(self) -> None:
        """Load initial data from the database with fallback."""
        try:
            (
                self.columns, self.rows, self.banks_coordinates, self.taverns_coordinates,
                self.transits_coordinates, self.user_buildings_coordinates, self.color_mappings,
                self.shops_coordinates, self.guilds_coordinates, self.places_of_interest_coordinates,
                self.keybind_config, self.current_css_profile,
                self.selected_character, self.destination  # <-- just store, don't update minimap yet
            ) = load_data()

        except sqlite3.Error as e:
            logging.critical(f"Failed to load initial data: {e}")
            # Use fallback data
            self.columns = self.rows = self.banks_coordinates = self.taverns_coordinates = \
                self.transits_coordinates = self.user_buildings_coordinates = \
                self.shops_coordinates = self.guilds_coordinates = self.places_of_interest_coordinates = {}
            self.color_mappings = {'default': PySide6.QtGui.QColor('#000000')}
            self.keybind_config = 1
            self.current_css_profile = "Default"
            self.selected_character = None
            self.destination = None

    @splash_message(None)
    def _init_ui_state(self) -> None:
        """Initialize UI-related state variables."""
        self.zoom_level = 3
        self.load_zoom_level_from_database()  # May override zoom_level
        self.minimap_size = 280
        self.column_start = 0
        self.row_start = 0
        self.destination = None
        self.map_icons = {
            "bank": PySide6.QtGui.QPixmap("images/bank.png"),
            "tavern": PySide6.QtGui.QPixmap("images/saloon.png"),
            "transit": PySide6.QtGui.QPixmap("images/transit.png"),
            "user_building": PySide6.QtGui.QPixmap("images/castle.png"),
            "guild": PySide6.QtGui.QPixmap("images/guild.png"),
            "shop": PySide6.QtGui.QPixmap("images/shop.png"),
            "graveyard": PySide6.QtGui.QPixmap("images/graveyard.png"),
            "hall_binding": PySide6.QtGui.QPixmap("images/binding.png"),
            "hall_severance": PySide6.QtGui.QPixmap("images/severance.png"),
        }

    @splash_message(None)
    def _init_characters(self) -> None:
        """Initialize character-related data and widgets."""
        self.characters = []
        self.character_list = QListWidget()
        self.selected_character = None
        self.load_characters()
        if not self.characters:
            self.firstrun_character_creation()

    @splash_message(None)
    def _init_ui_components(self) -> None:
        """Set up UI components and console logging."""
        self.setup_ui_components()
        self.setup_console_logging()

    @splash_message(None)
    def _finalize_setup(self) -> None:
        """Complete initialization with UI display and final configurations."""
        self.show()

        if self.selected_character and self.destination:
            self.update_minimap()

        self.load_last_active_character()
        self.setup_keybindings()
        # noinspection PyUnresolvedReferences
        self.setFocusPolicy(Qt.StrongFocus)
        if hasattr(self, 'website_frame'):
            # noinspection PyUnresolvedReferences
            self.website_frame.setFocusPolicy(Qt.StrongFocus)
        else:
            logging.warning("website_frame not initialized before focus setup")
        css = self.load_current_css()
        self.apply_custom_css(css)

    def load_current_css(self) -> str:
        """Load CSS for the current profile from the database."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'css_profile'")
                result = cursor.fetchone()
                profile = result[0] if result else "Default"
                cursor.execute("SELECT element, value FROM custom_css WHERE profile_name = ?", (profile,))
                return "\n".join(f"{elem} {{ {val} }}" for elem, val in cursor.fetchall())
        except sqlite3.Error as e:
            logging.error(f"Failed to load CSS: {e}")
            return ""

    # -----------------------
    # Keybindings
    # -----------------------

    def load_keybind_config(self) -> int:
        """
        Load keybind configuration from the database.

        Returns:
            int: Keybind mode (0=Off, 1=WASD, 2=Arrows), defaults to 1 (WASD) if not found.
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'keybind_config'")
                result = cursor.fetchone()
                return int(result[0]) if result else 1  # Default to WASD
        except sqlite3.Error as e:
            logging.error(f"Failed to load keybind config: {e}")
            return 1  # Fallback to WASD on error

    def setup_keybindings(self) -> None:
        """Set up keybindings for character movement based on current config."""
        movement_configs = {
            1: {  # WASD Mode
                Qt.Key.Key_W: 1,  # Top-center
                Qt.Key.Key_A: 3,  # Middle-left
                Qt.Key.Key_S: 7,  # Bottom-center
                Qt.Key.Key_D: 5  # Middle-right
            },
            2: {  # Arrow Keys Mode
                Qt.Key.Key_Up: 1,
                Qt.Key.Key_Left: 3,
                Qt.Key.Key_Down: 7,
                Qt.Key.Key_Right: 5
            },
            0: {}  # Off mode (no keybindings)
        }

        self.movement_keys = movement_configs.get(self.keybind_config, movement_configs[1])
        logging.debug(f"Setting up keybindings: {self.movement_keys}")

        self.clear_existing_keybindings()

        if self.keybind_config == 0:
            logging.info("Keybindings disabled (mode 0)")
            return

        if not hasattr(self, 'website_frame'):
            logging.error("website_frame not initialized; skipping keybinding setup")
            return

        for key, move_index in self.movement_keys.items():
            shortcut = PySide6.QtGui.QShortcut(PySide6.QtGui.QKeySequence(key), self.website_frame,
                                               context=Qt.ShortcutContext.ApplicationShortcut)
            shortcut.activated.connect(lambda idx=move_index: self.move_character(idx))
            logging.debug(f"Bound key {key} to move index {move_index}")

    def move_character(self, move_index: int) -> None:
        """
        Move character to the specified grid position via JavaScript,
        but only if the currently focused widget is not an input field.

        Args:
            move_index (int): Index in the 3x3 movement grid (0-8).
        """
        widget = QApplication.focusWidget()
        if isinstance(widget, (QLineEdit, QComboBox)):
            logging.debug(f"Ignored movement key {move_index} due to focus on input: {widget}")
            return

        if not hasattr(self, 'website_frame') or not self.website_frame.page():
            logging.warning("Cannot move character: website_frame or page not initialized")
            return

        logging.debug(f"Attempting move to grid index: {move_index}")
        js_code = """
            (function() {
                const table = document.querySelector('table table');
                if (!table) return 'No table';
                const spaces = Array.from(table.querySelectorAll('td'));
                if (spaces.length !== 9) return 'Invalid grid size: ' + spaces.length;
                const targetSpace = spaces[%d];
                if (!targetSpace) return 'No target space';
                const form = targetSpace.querySelector('form[action="/blood.pl"][method="POST"]');
                if (!form) return 'No form';
                const x = form.querySelector('input[name="x"]').value;
                const y = form.querySelector('input[name="y"]').value;
                form.submit();
                return 'Submitted to x=' + x + ', y=' + y;
            })();
        """ % move_index
        self.website_frame.page().runJavaScript(js_code, lambda result: logging.debug(f"Move result: {result}"))
        self.website_frame.setFocus()

    def toggle_keybind_config(self, mode: int) -> None:
        """
        Switch between keybinding modes (0=Off, 1=WASD, 2=Arrows) and update settings.

        Args:
            mode (int): Keybind mode to switch to.
        """
        if mode not in {0, 1, 2}:
            logging.warning(f"Invalid keybind mode: {mode}; ignoring")
            return

        self.keybind_config = mode
        mode_text = {0: "Off", 1: "WASD", 2: "Arrow Keys"}[mode]
        logging.info(f"Switching to keybind mode {mode} ({mode_text})")

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (setting_name, setting_value) VALUES ('keybind_config', ?)",
                    (mode,)
                )
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Failed to save keybind config {mode}: {e}")
            return  # Don’t proceed if database fails

        self.setup_keybindings()
        self.update_keybind_menu()
        # noinspection PyArgumentList
        QMessageBox.information(self, "Keybind Config", f"Switched to {mode_text}")

    def update_keybind_menu(self) -> None:
        """Update keybinding menu checkmarks based on current config."""
        if not hasattr(self, 'keybind_wasd_action') or not hasattr(self, 'keybind_arrow_action') or \
                not hasattr(self, 'keybind_off_action'):
            logging.warning("Keybind menu actions not initialized; skipping update")
            return

        self.keybind_wasd_action.setChecked(self.keybind_config == 1)
        self.keybind_arrow_action.setChecked(self.keybind_config == 2)
        self.keybind_off_action.setChecked(self.keybind_config == 0)
        logging.debug(
            f"Updated keybind menu: WASD={self.keybind_config == 1}, Arrows={self.keybind_config == 2}, Off={self.keybind_config == 0}")

    def clear_existing_keybindings(self) -> None:
        """Remove existing shortcuts from website_frame to prevent duplicates."""
        if not hasattr(self, 'website_frame'):
            logging.debug("No website_frame to clear keybindings from")
            return

        shortcuts = list(self.website_frame.findChildren(PySide6.QtGui.QShortcut))
        for shortcut in shortcuts:
            shortcut.setParent(None)
            shortcut.deleteLater()  # Ensure cleanup
        logging.debug(f"Cleared {len(shortcuts)} existing keybindings")

    # -----------------------
    # Load and Apply Customized UI Theme
    # -----------------------

    def load_theme_settings(self) -> None:
        """
        Load theme colors from the color_mappings table into self.color_mappings.
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT type, color FROM color_mappings")
                rows = cursor.fetchall()
                self.color_mappings.update({type_: PySide6.QtGui.QColor(color) for type_, color in rows})
                logging.debug(f"Loaded {len(rows)} theme entries from color_mappings.")
        except sqlite3.Error as e:
            logging.error(f"Failed to load theme from color_mappings: {e}")

    def save_theme_settings(self) -> bool:
        """
        Save current color mappings to the color_mappings table in the database.

        Returns:
            bool: True if saved successfully, False otherwise.
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    '''
                    INSERT INTO color_mappings (type, color)
                    VALUES (?, ?)
                    ON CONFLICT(type) DO UPDATE SET color = excluded.color
                    ''',
                    [(key, color.name()) for key, color in self.color_mappings.items()]
                )
                conn.commit()
                logging.debug("Theme settings saved to color_mappings table.")
                return True
        except sqlite3.Error as e:
            logging.error(f"Failed to save theme to color_mappings: {e}")
            return False

    def apply_theme(self) -> None:
        """Apply current theme settings to the application's stylesheet."""
        try:
            bg_color = self.color_mappings.get("background", PySide6.QtGui.QColor("#d4d4d4")).name()
            text_color = self.color_mappings.get("text_color", PySide6.QtGui.QColor("#000000")).name()
            btn_color = self.color_mappings.get("button_color", PySide6.QtGui.QColor("#b1b1b1")).name()

            stylesheet = (
                f"QWidget {{ background-color: {bg_color}; color: {text_color}; }}"
                f"QPushButton {{ background-color: {btn_color}; color: {text_color}; }}"
                f"QLabel {{ color: {text_color}; }}"
            )
            self.setStyleSheet(stylesheet)
            logging.debug("Theme applied successfully")
        except Exception as e:
            logging.error(f"Failed to apply theme: {e}")
            self.setStyleSheet("")  # Reset to default on failure

    def change_theme(self) -> None:
        """
        Open theme customization dialog and apply/save selected theme.

        Assumes ThemeCustomizationDialog is defined elsewhere with exec() and color_mappings.
        """
        dialog = ThemeCustomizationDialog(self, color_mappings=self.color_mappings)
        if dialog.exec():
            self.color_mappings = dialog.color_mappings
            self.apply_theme()
            if self.save_theme_settings():
                logging.info("Theme updated and saved")
            else:
                logging.warning("Theme applied but not saved due to database error")

    # -----------------------
    # Cookie Handling
    # -----------------------

    def setup_cookie_handling(self) -> None:
        """
        Set up cookie handling by connecting the QWebEngineProfile's cookie store and loading saved cookies.
        """
        self.cookie_store = self.web_profile.cookieStore()
        self.cookie_store.cookieAdded.connect(self.on_cookie_added)
        self.load_cookies()
        logging.debug("Cookie handling initialized")

    def load_cookies(self) -> None:
        """
        Load cookies from the 'cookies' table and inject them into the QWebEngineProfile.
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, domain, path, value, expiration, secure, httponly FROM cookies")
                cookies = cursor.fetchall()

                for name, domain, path, value, expiration, secure, httponly in cookies:
                    cookie = QNetworkCookie(name.encode('utf-8'), value.encode('utf-8'))
                    cookie.setDomain(domain)
                    cookie.setPath(path)
                    cookie.setSecure(bool(secure))
                    cookie.setHttpOnly(bool(httponly))
                    if expiration:
                        try:
                            # Handle both string (ISO) and int (epoch) expiration formats
                            if isinstance(expiration, str):
                                # noinspection PyUnresolvedReferences
                                cookie.setExpirationDate(QDateTime.fromString(expiration, Qt.ISODate))
                            elif isinstance(expiration, int):
                                cookie.setExpirationDate(QDateTime.fromSecsSinceEpoch(expiration))
                            else:
                                logging.warning(f"Invalid expiration type for cookie '{name}': {type(expiration)}")
                        except ValueError as e:
                            logging.warning(f"Failed to parse expiration '{expiration}' for cookie '{name}': {e}")
                    self.cookie_store.setCookie(cookie, QUrl(f"https://{domain}"))
                logging.debug(f"Loaded {len(cookies)} cookies from database")
        except sqlite3.Error as e:
            logging.error(f"Failed to load cookies: {e}")

    def on_cookie_added(self, cookie: QNetworkCookie) -> None:
        name = cookie.name().data().decode()
        value = cookie.value().data().decode()
        domain = cookie.domain().lstrip('.')  # Normalize domain
        path = cookie.path()

        if domain != 'quiz.ravenblack.net':
            return

        if name == 'stamp':
            return  # skip churn cookie

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()

                # Check if this exact cookie already exists
                cursor.execute("""
                    SELECT id FROM cookies 
                    WHERE name = ? AND value = ? AND domain = ? AND path = ?
                """, (name, value, domain, path))
                existing = cursor.fetchone()

                if existing:
                    logging.debug(f"Duplicate cookie '{name}' for value '{value}' not saved.")
                    return

                # Insert new cookie
                cursor.execute("""
                    INSERT INTO cookies (name, value, domain, path, expiration, secure, httponly)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    name, value, domain, path,
                    cookie.expirationDate().toString(Qt.ISODate) if not cookie.isSessionCookie() else None,
                    int(cookie.isSecure()), int(cookie.isHttpOnly())
                ))

                new_cookie_id = cursor.lastrowid
                conn.commit()
                logging.debug(f"Saved new cookie '{name}' (ID {new_cookie_id}) for domain '{domain}'")

                # If it's an ip cookie, consider linking to character
                if name == 'ip' and '#' in value:
                    username, password = value.split('#', 1)
                    is_login = bool(password.strip())

                    logging.debug(
                        f"Captured IP cookie for user '{username}' — {'login' if is_login else 'logout'} state."
                    )

                    # Update character only if this is a login cookie
                    if is_login:
                        cursor.execute("""
                            UPDATE characters SET active_cookie = ? WHERE name = ?
                        """, (new_cookie_id, username))
                        conn.commit()
                        logging.debug(f"Set active_cookie for character '{username}' to cookie ID {new_cookie_id}")

        except Exception as e:
            logging.error(f"Error saving cookie '{name}': {e}")

    def set_ip_cookie(self, name: str, password: str):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()

                value = f"{name}#{password}"
                domain = 'quiz.ravenblack.net'
                path = '/'

                # Avoid duplicate
                cursor.execute("""
                    SELECT id FROM cookies WHERE name = 'ip' AND value = ? AND domain = ? AND path = ?
                """, (value, domain, path))
                row = cursor.fetchone()

                if row:
                    cookie_id = row[0]
                else:
                    cursor.execute('''
                        INSERT INTO cookies (name, value, domain, path, expiration, secure, httponly)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        'ip', value, domain, path,
                        QDateTime.currentDateTime().addDays(30).toString(Qt.ISODate),
                        0, 0
                    ))
                    cookie_id = cursor.lastrowid

                # Set this cookie as active, clear others
                cursor.execute("UPDATE characters SET active_cookie = NULL")
                cursor.execute("UPDATE characters SET active_cookie = ? WHERE name = ?", (cookie_id, name))
                conn.commit()
                logging.debug(f"Set active_cookie ID {cookie_id} for {name}")

        except sqlite3.Error as e:
            logging.error(f"Failed to insert 'ip' cookie for {name}: {e}")

    # -----------------------
    # UI Setup
    # -----------------------

    def setup_ui_components(self):
        """
        Set up the main user interface for the RBC Community Map application.

        This method initializes and arranges the key components of the user interface,
        including the minimap, browser controls, and character management.
        """

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.create_menu_bar()

        # Initialize the QWebEngineView before setting up the browser controls
        self.website_frame = QWebEngineView(self.web_profile)

        # Disable GPU-related features
        self.website_frame.settings().setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)
        self.website_frame.settings().setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, False)
        self.website_frame.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl'))
        self.website_frame.loadFinished.connect(self.on_webview_load_finished)

        # Add Keybindings
        self.setup_keybindings()

        # Browser controls layout
        self.browser_controls_layout = QHBoxLayout()

        # Back button using Qt's built-in style
        back_button = QPushButton()
        back_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setIconSize(QSize(30, 30))
        back_button.setFixedSize(30, 30)
        back_button.setStyleSheet("background-color: transparent; border: none;")
        back_button.clicked.connect(self.website_frame.back)
        self.browser_controls_layout.addWidget(back_button)

        # Forward button using Qt's built-in style
        forward_button = QPushButton()
        forward_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        forward_button.setCursor(Qt.PointingHandCursor)
        forward_button.setIconSize(QSize(30, 30))
        forward_button.setFixedSize(30, 30)
        forward_button.setStyleSheet("background-color: transparent; border: none;")
        forward_button.clicked.connect(self.website_frame.forward)
        self.browser_controls_layout.addWidget(forward_button)

        refresh_button = QPushButton()
        refresh_button.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        refresh_button.setCursor(Qt.PointingHandCursor)
        refresh_button.setIconSize(QSize(30, 30))
        refresh_button.setFixedSize(30, 30)
        refresh_button.setStyleSheet("background-color: transparent; border: none;")
        refresh_button.clicked.connect(lambda: self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl')))
        self.browser_controls_layout.addWidget(refresh_button)

        self.browser_controls_layout.addStretch(1)

        # AP and compass container
        ap_compass_container = QWidget()
        ap_compass_layout = QHBoxLayout(ap_compass_container)
        ap_compass_layout.setContentsMargins(0, 0, 0, 0)
        ap_compass_layout.setSpacing(10)

        # Compass Icon Button
        self.compass_button = QPushButton()
        self.compass_button.setIcon(PySide6.QtGui.QIcon(PySide6.QtGui.QPixmap("images/compass.png")))
        self.compass_button.setIconSize(QSize(28, 28))  # Adjust as needed
        self.compass_button.setFixedSize(34, 34)
        self.compass_button.setStyleSheet("background-color: transparent; border: none;")
        self.compass_button.setToolTip("Open Compass Overlay")
        self.compass_button.clicked.connect(self.show_compass_overlay)
        ap_compass_layout.addWidget(self.compass_button)

        # AP Direction Label
        self.ap_direction_label = QLabel()
        self.ap_direction_label.setAlignment(Qt.AlignCenter)
        self.ap_direction_label.setStyleSheet("color: white; font-weight: bold; font-size: 12pt;")
        ap_compass_layout.addWidget(self.ap_direction_label)

        self.browser_controls_layout.addWidget(ap_compass_container)
        self.browser_controls_layout.addStretch(1)

        # Ko-Fi button with a programmatically generated icon
        kofi_button = QPushButton()
        kofi_icon = PySide6.QtGui.QPixmap(30, 30)
        kofi_icon.fill(Qt.transparent)
        painter = PySide6.QtGui.QPainter(kofi_icon)
        painter.setRenderHint(PySide6.QtGui.QPainter.Antialiasing)
        painter.setPen(PySide6.QtGui.QPen(Qt.black, 2))
        painter.setBrush(PySide6.QtGui.QBrush(PySide6.QtGui.QColor(0, 188, 212)))  # Ko-Fi teal color
        painter.drawEllipse(5, 5, 20, 20)
        painter.setPen(PySide6.QtGui.QPen(Qt.white, 2))
        painter.drawText(kofi_icon.rect(), Qt.AlignCenter, "K")
        painter.end()
        kofi_button.setIcon(PySide6.QtGui.QIcon(kofi_icon))
        kofi_button.setIconSize(QSize(30, 30))
        kofi_button.setToolTip("Support me on Ko-fi")
        # noinspection PyUnresolvedReferences
        kofi_button.setCursor(Qt.PointingHandCursor)
        kofi_button.setFlat(True)
        kofi_button.clicked.connect(lambda: PySide6.QtGui.QDesktopServices.openUrl(QUrl("https://ko-fi.com/jelollis")))

        # Set spacing between buttons to make them closer together
        # Add spacing and the Ko-fi button to the end of the toolbar
        self.browser_controls_layout.setSpacing(5)
        self.browser_controls_layout.addStretch(1)
        self.browser_controls_layout.addWidget(kofi_button)

        # Create a container widget for the webview and controls
        webview_container = QWidget()
        webview_layout = QVBoxLayout(webview_container)
        webview_layout.setContentsMargins(0, 0, 0, 0)
        webview_layout.addLayout(self.browser_controls_layout)
        webview_layout.addWidget(self.website_frame)

        # Main layout for map and controls
        map_layout = QHBoxLayout()
        main_layout.addLayout(map_layout)

        # Left layout containing the minimap and control buttons
        left_layout = QVBoxLayout()
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.Shape.Box)
        left_frame.setFixedWidth(300)
        left_frame.setLayout(left_layout)

        # Minimap setup
        minimap_frame = QFrame()
        minimap_frame.setFrameShape(QFrame.Shape.Box)
        minimap_frame.setFixedSize(self.minimap_size, self.minimap_size)
        minimap_layout = QVBoxLayout()
        minimap_layout.setContentsMargins(0, 0, 0, 0)
        minimap_frame.setLayout(minimap_layout)

        # Label to display the minimap
        self.minimap_label = QLabel()
        self.minimap_label.setFixedSize(self.minimap_size, self.minimap_size)
        self.minimap_label.setStyleSheet("background-color: lightgrey;")
        minimap_layout.addWidget(self.minimap_label)
        left_layout.addWidget(minimap_frame)

        # Information frame to display nearest locations and AP costs
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.Box)
        info_frame.setFixedHeight(260)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        info_frame.setLayout(info_layout)
        left_layout.addWidget(info_frame)

        # Common style for each info label with padding, border, and smaller font size
        label_style = """
            background-color: {color};
            color: white;
            font-weight: bold;
            padding: 5px;
            border: 2px solid black;
            font-size: 12px;
        """

        # Closest Bank Info
        self.bank_label = QLabel("Bank")
        self.bank_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.bank_label.setStyleSheet(label_style.format(color="blue"))
        self.bank_label.setWordWrap(True)
        self.bank_label.setFixedHeight(45)
        info_layout.addWidget(self.bank_label)

        # Closest Transit Info
        self.transit_label = QLabel("Transit")
        self.transit_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.transit_label.setStyleSheet(label_style.format(color="red"))
        self.transit_label.setWordWrap(True)
        self.transit_label.setFixedHeight(45)
        info_layout.addWidget(self.transit_label)

        # Closest Tavern Info
        self.tavern_label = QLabel("Tavern")
        self.tavern_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tavern_label.setStyleSheet(label_style.format(color="orange"))
        self.tavern_label.setWordWrap(True)
        self.tavern_label.setFixedHeight(45)
        info_layout.addWidget(self.tavern_label)

        # Set Destination Info
        self.destination_label = QLabel("Set Destination")
        self.destination_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.destination_label.setStyleSheet(label_style.format(color="green"))
        self.destination_label.setWordWrap(True)
        self.destination_label.setFixedHeight(45)
        info_layout.addWidget(self.destination_label)

        # Transit-Based AP for Set Destination Info
        self.transit_destination_label = QLabel("Set Destination - Transit Route")
        self.transit_destination_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.transit_destination_label.setStyleSheet(label_style.format(color="purple"))
        self.transit_destination_label.setWordWrap(True)
        self.transit_destination_label.setFixedHeight(45)
        info_layout.addWidget(self.transit_destination_label)

        # ComboBox and Go Button
        combo_go_layout = QHBoxLayout()
        combo_go_layout.setSpacing(5)

        # --- Editable, searchable COLUMN ComboBox ---
        self.combo_columns = QComboBox()
        self.combo_columns.setEditable(True)
        self.combo_columns.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo_columns.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.combo_columns.addItem("Select Column")  # Placeholder
        self.combo_columns.addItems(list(columns.keys()))
        self.combo_columns.setCurrentIndex(0)
        self.combo_columns.model().item(0).setEnabled(False)  # Disable placeholder

        column_completer = QCompleter(list(columns.keys()))
        column_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.combo_columns.setCompleter(column_completer)

        # Install event filters for clearing behavior
        self.combo_columns.lineEdit().installEventFilter(self)
        self.combo_columns.installEventFilter(self)

        # --- Editable, searchable ROW ComboBox ---
        self.combo_rows = QComboBox()
        self.combo_rows.setEditable(True)
        self.combo_rows.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo_rows.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.combo_rows.addItem("Select Row")
        self.combo_rows.addItems(list(rows.keys()))
        self.combo_rows.setCurrentIndex(0)
        self.combo_rows.model().item(0).setEnabled(False)

        row_completer = QCompleter(list(rows.keys()))
        row_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.combo_rows.setCompleter(row_completer)

        self.combo_rows.lineEdit().installEventFilter(self)
        self.combo_rows.installEventFilter(self)

        # Go Button
        go_button = QPushButton('Go')
        go_button.setFixedSize(25, 25)
        go_button.clicked.connect(self.go_to_location)

        # Layout assembly
        combo_go_layout.addWidget(self.combo_columns)
        combo_go_layout.addWidget(self.combo_rows)
        combo_go_layout.addWidget(go_button)

        # Label for dropdowns to indicate their function
        dropdown_label = QLabel("Recenter Minimap to Location")
        dropdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dropdown_label.setStyleSheet("font-size: 12px; padding: 5px;")
        left_layout.addWidget(dropdown_label)

        left_layout.addLayout(combo_go_layout)

        # Zoom and action buttons
        zoom_layout = QHBoxLayout()
        button_size = (self.minimap_size - 10) // 3

        zoom_in_button = QPushButton('Zoom in')
        zoom_in_button.setFixedSize(button_size, 25)
        zoom_in_button.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(zoom_in_button)

        zoom_out_button = QPushButton('Zoom out')
        zoom_out_button.setFixedSize(button_size, 25)
        zoom_out_button.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(zoom_out_button)

        set_destination_button = QPushButton('Set Destination')
        set_destination_button.setFixedSize(button_size, 25)
        set_destination_button.clicked.connect(self.open_SetDestinationDialog)
        zoom_layout.addWidget(set_destination_button)

        left_layout.addLayout(zoom_layout)

        # Layout for refresh, discord, and website buttons
        action_layout = QHBoxLayout()

        refresh_button = QPushButton('Refresh')
        refresh_button.setFixedSize(button_size, 25)
        refresh_button.clicked.connect(lambda: self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl')))
        action_layout.addWidget(refresh_button)

        discord_button = QPushButton('Discord')
        discord_button.setFixedSize(button_size, 25)
        discord_button.clicked.connect(self.open_discord)
        action_layout.addWidget(discord_button)

        website_button = QPushButton('Website')
        website_button.setFixedSize(button_size, 25)
        website_button.clicked.connect(self.open_website)
        action_layout.addWidget(website_button)

        left_layout.addLayout(action_layout)

        # Character list frame
        character_frame = QFrame()
        character_frame.setFrameShape(QFrame.Shape.Box)
        character_layout = QVBoxLayout()
        character_frame.setLayout(character_layout)

        character_list_label = QLabel('Character List')
        character_layout.addWidget(character_list_label)

        self.character_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.character_list.itemClicked.connect(self.on_character_selected)
        character_layout.addWidget(self.character_list)

        character_buttons_layout = QHBoxLayout()
        new_button = QPushButton('New')
        new_button.setFixedSize(75, 25)
        new_button.clicked.connect(self.add_new_character)
        modify_button = QPushButton('Modify')
        modify_button.setFixedSize(75, 25)
        modify_button.clicked.connect(self.modify_character)
        delete_button = QPushButton('Delete')
        delete_button.setFixedSize(75, 25)
        delete_button.clicked.connect(self.delete_character)
        character_buttons_layout.addWidget(new_button)
        character_buttons_layout.addWidget(modify_button)
        character_buttons_layout.addWidget(delete_button)
        character_layout.addLayout(character_buttons_layout)

        left_layout.addWidget(character_frame)

        # Add the webview_container and left_frame to the map layout
        map_layout.addWidget(left_frame)
        map_layout.addWidget(webview_container, stretch=1)

        # Make sure the webview expands to fill the remaining space
        self.website_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Directly process coins from HTML within `process_html`
        if self.selected_character:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT id FROM characters WHERE name = ?", (self.selected_character['name'],))
                character_row = cursor.fetchone()
                if character_row:
                    character_id = character_row[0]
                    self.selected_character['id'] = character_id
                    logging.info(f"Character ID {character_id} set for {self.selected_character['name']}.")
                else:
                    logging.error(f"Character '{self.selected_character['name']}' not found in the database.")
            except sqlite3.Error as e:
                logging.error(f"Failed to retrieve character ID: {e}")
            finally:
                connection.close()

                self.show()
                self.update_minimap()

    # -----------------------
    # Browser Controls Setup
    # -----------------------

    def go_back(self):
        """Navigate the web browser back to the previous page."""
        self.website_frame.back()

    def go_forward(self):
        """Navigate the web browser forward to the next page."""
        self.website_frame.forward()

    def refresh_page(self):
        """Refresh the current page displayed in the web browser."""
        self.website_frame.reload()

    def create_menu_bar(self) -> None:
        """
        Create the menu bar with File, Settings, Tools, and Help menus.
        """
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu('File')
        save_webpage_action = PySide6.QtGui.QAction('Save Webpage Screenshot', self)
        save_webpage_action.triggered.connect(self.save_webpage_screenshot)
        file_menu.addAction(save_webpage_action)

        save_app_action = PySide6.QtGui.QAction('Save App Screenshot', self)
        save_app_action.triggered.connect(self.save_app_screenshot)
        file_menu.addAction(save_app_action)

        exit_action = PySide6.QtGui.QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Settings menu
        settings_menu = menu_bar.addMenu('Settings')

        theme_action = PySide6.QtGui.QAction('Change Theme', self)
        theme_action.triggered.connect(self.change_theme)
        settings_menu.addAction(theme_action)

        css_customization_action = PySide6.QtGui.QAction('CSS Customization', self)
        css_customization_action.triggered.connect(self.open_css_customization_dialog)
        settings_menu.addAction(css_customization_action)

        zoom_in_action = PySide6.QtGui.QAction('Zoom In', self)
        zoom_in_action.triggered.connect(self.zoom_in_browser)
        settings_menu.addAction(zoom_in_action)

        zoom_out_action = PySide6.QtGui.QAction('Zoom Out', self)
        zoom_out_action.triggered.connect(self.zoom_out_browser)
        settings_menu.addAction(zoom_out_action)

        # Keybindings Submenu
        keybindings_menu = settings_menu.addMenu("Keybindings")

        self.keybind_wasd_action = PySide6.QtGui.QAction("WASD", self, checkable=True)
        self.keybind_wasd_action.triggered.connect(lambda: self.toggle_keybind_config(1))

        self.keybind_arrow_action = PySide6.QtGui.QAction("Arrow Keys", self, checkable=True)
        self.keybind_arrow_action.triggered.connect(lambda: self.toggle_keybind_config(2))

        self.keybind_off_action = PySide6.QtGui.QAction("Off", self, checkable=True)
        self.keybind_off_action.triggered.connect(lambda: self.toggle_keybind_config(0))

        keybindings_menu.addAction(self.keybind_wasd_action)
        keybindings_menu.addAction(self.keybind_arrow_action)
        keybindings_menu.addAction(self.keybind_off_action)

        # Update checkmark based on current keybind setting
        self.update_keybind_menu()

        # Logging Level Submenu
        log_level_menu = settings_menu.addMenu("Logging Level")

        self.log_level_actions = {}

        log_levels = [
            ("DEBUG", logging.DEBUG),
            ("INFO", logging.INFO),
            ("WARNING", logging.WARNING),
            ("ERROR", logging.ERROR),
            ("CRITICAL", logging.CRITICAL),
            ("OFF", logging.CRITICAL + 10)  # OFF = disables all logging
        ]

        for name, level in log_levels:
            action = PySide6.QtGui.QAction(name, self, checkable=True)
            action.triggered.connect(lambda checked, lvl=level: self.set_log_level(lvl))
            log_level_menu.addAction(action)
            self.log_level_actions[level] = action

        self.update_log_level_menu()

        # Tools menu
        tools_menu = menu_bar.addMenu('Tools')

        database_viewer_action = PySide6.QtGui.QAction('Database Viewer', self)
        database_viewer_action.triggered.connect(self.open_database_viewer)
        tools_menu.addAction(database_viewer_action)

        shopping_list_action = PySide6.QtGui.QAction('Shopping List Generator', self)
        shopping_list_action.triggered.connect(self.open_shopping_list_tool)
        tools_menu.addAction(shopping_list_action)

        damage_calculator_action = PySide6.QtGui.QAction('Damage Calculator', self)
        damage_calculator_action.triggered.connect(self.open_damage_calculator_tool)
        tools_menu.addAction(damage_calculator_action)

        power_reference_action = PySide6.QtGui.QAction('Power Reference Tool', self)
        power_reference_action.triggered.connect(self.open_powers_dialog)
        tools_menu.addAction(power_reference_action)

        logs_action = PySide6.QtGui.QAction('View Logs', self)
        logs_action.triggered.connect(self.open_log_viewer)
        tools_menu.addAction(logs_action)

        # Resources
        resources_menu = menu_bar.addMenu('Resources')

        avitd_action = PySide6.QtGui.QAction('AVITD', self)
        avitd_action.triggered.connect(lambda: webbrowser.open('https://aviewinthedark.net/'))
        resources_menu.addAction(avitd_action)

        rb_wiki_action = PySide6.QtGui.QAction('RB Wiki', self)
        rb_wiki_action.triggered.connect(lambda: webbrowser.open('https://ravenblack.city/'))
        resources_menu.addAction(rb_wiki_action)

        # Help menu
        help_menu = menu_bar.addMenu('Help')

        faq_action = PySide6.QtGui.QAction('FAQ', self)
        faq_action.triggered.connect(lambda: webbrowser.open('https://quiz.ravenblack.net/faq.pl'))
        help_menu.addAction(faq_action)

        how_to_play_action = PySide6.QtGui.QAction('How to Play', self)
        how_to_play_action.triggered.connect(lambda: webbrowser.open('https://quiz.ravenblack.net/bloodhowto.html'))
        help_menu.addAction(how_to_play_action)

        about_action = PySide6.QtGui.QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        credits_action = PySide6.QtGui.QAction('Credits', self)
        credits_action.triggered.connect(self.show_credits_dialog)
        help_menu.addAction(credits_action)

        report_issue_action = PySide6.QtGui.QAction('Report an Issue', self)
        report_issue_action.triggered.connect(lambda: webbrowser.open('https://github.com/JELollis/RBC-Map/issues/new'))
        help_menu.addAction(report_issue_action)

        view_help_action = PySide6.QtGui.QAction('View Help', self)
        view_help_action.setShortcut(PySide6.QtGui.QKeySequence('F1'))
        view_help_action.triggered.connect(self.open_help_file)
        help_menu.addAction(view_help_action)

    def zoom_in_browser(self):
        """Zoom in on the web page displayed in the QWebEngineView."""
        self.website_frame.setZoomFactor(self.website_frame.zoomFactor() + 0.1)

    def zoom_out_browser(self):
        """Zoom out on the web page displayed in the QWebEngineView."""
        self.website_frame.setZoomFactor(self.website_frame.zoomFactor() - 0.1)

    # -----------------------
    # Error Logging
    # -----------------------

    def setup_console_logging(self):
        """
        Set up console logging within the web engine view by connecting the web channel
        to handle JavaScript console messages.
        """
        self.web_channel = QWebChannel(self.website_frame.page())
        self.website_frame.page().setWebChannel(self.web_channel)
        self.web_channel.registerObject("qtHandler", self)

    def inject_console_logging(self):
        """
        Inject JavaScript into the web page to capture console logs and send them to PyQt,
        enabling logging of JavaScript console messages within the Python application.
        """
        script = """
            (function() {
                var console_log = console.log;
                console.log = function(message) {
                    console_log(message);
                    if (typeof qtHandler !== 'undefined' && qtHandler.handleConsoleMessage) {
                        qtHandler.handleConsoleMessage(message);
                    }
                };
            })();
        """
        self.website_frame.page().runJavaScript(script)

    @pyqtSlot(str)
    def handle_console_message(self, message):
        """
        Handle console messages from the web view and log them.

        Args:
            message (str): The console message to be logged.
        """
        print(f"Console message: {message}")
        logging.debug(f"Console message: {message}")

    # -----------------------
    # Menu Control Items
    # -----------------------

    def get_default_screenshot_path(self, suffix: str) -> str:
        pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures", "RBC Map")
        os.makedirs(pictures_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_filename = f"{timestamp}_{suffix}.png"
        return os.path.join(pictures_dir, default_filename)

    def save_webpage_screenshot(self):
        """
        Save the current webpage as a screenshot to Pictures/RBC Map with a timestamped filename.
        """
        default_path = self.get_default_screenshot_path("webpage")
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Webpage Screenshot", default_path,
                                                   "PNG Files (*.png);;All Files (*)")
        if file_name:
            self.website_frame.grab().save(file_name)

    def save_app_screenshot(self):
        """
        Save the current application window as a screenshot to Pictures/RBC Map with a timestamped filename.
        """
        default_path = self.get_default_screenshot_path("app")
        file_name, _ = QFileDialog.getSaveFileName(self, "Save App Screenshot", default_path,
                                                   "PNG Files (*.png);;All Files (*)")
        if file_name:
            self.grab().save(file_name)

    def open_shopping_list_tool(self):
        """
        Opens the ShoppingListTool, using the currently selected character from character_list.
        If no character is selected, it displays an error message.
        """
        # Get the currently selected character from the QListWidget (character_list)
        current_item = self.character_list.currentItem()

        if current_item:
            character_name = current_item.text()
        else:
            # Show an error message if no character is selected
            QMessageBox.warning(self, "No Character Selected", "Please select a character from the list.")
            return

        # Open the ShoppingListTool with the selected character and unified database path
        self.shopping_list_tool = ShoppingListTool(character_name, DB_PATH)
        self.shopping_list_tool.show()

    def open_damage_calculator_tool(self):
        """
        Opens the Damage Calculator dialog within RBCCommunityMap.
        """
        # Initialize the DamageCalculator dialog with the SQLite database connection
        connection = sqlite3.connect(DB_PATH)
        damage_calculator = DamageCalculator(connection)

        # Set the default selection in the combobox to 'No Charisma'
        damage_calculator.charisma_dropdown.setCurrentIndex(0)  # Index 0 corresponds to 'No Charisma'

        # Show the DamageCalculator dialog as a modal
        damage_calculator.exec()

        # Close the database connection after use
        connection.close()

    def display_shopping_list(self, shopping_list):
        """
        Display the shopping list in a dialog.
        """
        shopping_list_text = "\n".join(
            f"{entry['shop']} - {entry['item']} - {entry['quantity']}x - {entry['total_cost']} coins"
            for entry in shopping_list
        )
        total_cost = sum(entry['total_cost'] for entry in shopping_list)
        shopping_list_text += f"\n\nTotal Coins - {total_cost}"
        # noinspection PyArgumentList
        QMessageBox.information(self, "Damage Calculator Shopping List", shopping_list_text)

    def open_powers_dialog(self):
        """
        Opens the Powers Dialog and ensures character coordinates are passed correctly.
        """
        powers_dialog = PowersDialog(self, self.character_x, self.character_y, DB_PATH)  # Ensure correct parameters
        powers_dialog.exec()

    def open_css_customization_dialog(self):
        """Open the CSS customization dialog."""
        dialog = CSSCustomizationDialog(self)
        dialog.exec()

    def update_log_level_menu(self) -> None:
        """
        Update the check state of log level actions based on current level from DB.
        """
        current_level = get_logging_level_from_db()
        for level, action in self.log_level_actions.items():
            action.setChecked(level == current_level)

    def set_log_level(self, level: int) -> None:
        """
        Set the log level and persist it in the database.
        """
        try:
            save_logging_level_to_db(level)

            logger = logging.getLogger()
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)  # <- This ensures file logging follows new level

            self.update_log_level_menu()
            logging.info(f"Log level set to {logging.getLevelName(level)}")

        except Exception as e:
            logging.error(f"Failed to set log level: {e}")

    def open_help_file(self):
        """
        Open the compiled .chm help file from the help folder.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the folder of the current script
        help_path = os.path.join(base_dir, "docs", "help", "RBCMap Help.chm")

        if os.path.exists(help_path):
            os.startfile(help_path)
        else:
            QMessageBox.warning(
                self,
                "Help File Missing",
                f"Could not find help file:\n{help_path}"
            )

    # -----------------------
    # Character Management
    # -----------------------

    def load_characters(self):
        connection = None
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, password FROM characters")
            character_data = cursor.fetchall()
            self.characters = [
                {'id': char_id, 'name': name, 'password': password}
                for char_id, name, password in character_data
            ]

            self.character_list.clear()
            for character in self.characters:
                item = QListWidgetItem(character['name'])
                item.setData(Qt.UserRole, character['id'])  # 🔥 Attach ID!
                self.character_list.addItem(item)

            logging.debug(f"Loaded {len(self.characters)} characters from the database.")
            if not self.characters:
                logging.warning("No characters found in the database.")
                self.selected_character = None

        except sqlite3.Error as e:
            logging.error(f"Failed to load characters from database: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load characters: {e}")
            self.characters = []
            self.selected_character = None
        finally:
            if connection:
                connection.close()

    def save_characters(self):
        connection = None
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            for character in self.characters:
                cursor.execute('''
                    INSERT OR REPLACE INTO characters (id, name, password) VALUES (?, ?, ?)
                ''', (character.get('id'), character['name'], character['password']))
            connection.commit()
            logging.debug("Characters saved successfully to the database in plaintext.")
        except sqlite3.Error as e:
            logging.error(f"Failed to save characters to database: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save characters: {e}")
        finally:
            if connection:
                connection.close()

    def on_character_selected(self, item):
        """
        Handle character selection: set the selected character, load cookie,
        and trigger login + destination load after webview reload.
        """
        character_name = item.text()
        selected_character = next((char for char in self.characters if char['name'] == character_name), None)

        if not selected_character:
            logging.error(f"Character selection failed: {character_name}")
            return

        logging.debug(f"Selected character: {character_name}")
        self.selected_character = selected_character

        # Ensure character has ID
        if 'id' not in self.selected_character:
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM characters WHERE name = ?", (character_name,))
                    row = cursor.fetchone()
                    if row:
                        self.selected_character['id'] = row[0]
            except sqlite3.Error as e:
                logging.error(f"Failed to retrieve character ID for '{character_name}': {e}")
                return

        # Final ID check before proceeding
        character_id = self.selected_character.get('id')
        if not character_id:
            logging.error(f"Character '{character_name}' has no valid ID.")
            return

        # Mark destination and login to be handled on next page load
        self.pending_character_id_for_map = character_id
        self.pending_login = True
        self.save_last_active_character(character_id)
        self.load_last_destination_for_character(character_id)
        self.update_minimap()

        # Inject cookie and trigger page reload
        self.switch_to_character(character_name)

    def switch_to_character(self, character_name: str) -> None:
        """
        Switch to the selected character by loading its saved IP cookie into the WebEngine.
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.active_cookie, k.value 
                    FROM characters c
                    JOIN cookies k ON c.active_cookie = k.id
                    WHERE c.name = ?
                """, (character_name,))
                row = cursor.fetchone()

                if not row:
                    logging.error(f"No saved login cookie found for character '{character_name}'.")
                    return

                cookie_id, cookie_value = row

                ip_cookie = QNetworkCookie(b'ip', cookie_value.encode('utf-8'))
                ip_cookie.setDomain('quiz.ravenblack.net')
                ip_cookie.setPath('/')
                ip_cookie.setExpirationDate(QDateTime.currentDateTime().addDays(30))

                self.cookie_store.setCookie(ip_cookie, QUrl("https://quiz.ravenblack.net"))
                logging.debug(f"Injected saved 'ip' cookie ID {cookie_id} for {character_name}.")

                # Reload page after injecting cookie
                self.website_frame.setUrl(QUrl("https://quiz.ravenblack.net/blood.pl"))

        except sqlite3.Error as e:
            logging.error(f"Failed to switch character '{character_name}': {e}")

    def login_selected_character(self):
        if not self.selected_character:
            logging.warning("No character selected for login.")
            return

        name = self.selected_character['name']
        password = self.selected_character['password']
        logging.debug(f"Injecting login for character: {name} (ID: {self.selected_character.get('id')})")

        login_script = f"""
            var loginForm = document.querySelector('form');
            if (loginForm) {{
                loginForm.iam.value = '{name}';
                loginForm.passwd.value = '{password}';
                loginForm.submit();
            }} else {{
                console.error('Login form not found.');
            }}
        """
        self.website_frame.page().runJavaScript(login_script)

    def firstrun_character_creation(self):
        """
        Handles the first-run character creation, saving the character in plaintext,
        initializing default coin values in the coins table, and setting this character as the last active.
        Then injects login form to let the server issue a valid IP cookie.
        """
        logging.debug("First-run character creation.")
        dialog = CharacterDialog(self)

        if dialog.exec():
            name = dialog.name_edit.text()
            password = dialog.password_edit.text()
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute('INSERT INTO characters (name, password) VALUES (?, ?)', (name, password))
                    character_id = cursor.lastrowid
                    cursor.execute('INSERT INTO coins (character_id, pocket, bank) VALUES (?, 0, 0)', (character_id,))
                    conn.commit()

                    self.save_last_active_character(character_id)

                    # Add to in-memory list and UI
                    character = {'name': name, 'password': password, 'id': character_id}
                    self.characters.append(character)
                    item = QListWidgetItem(name)
                    item.setData(Qt.UserRole, character_id)
                    self.character_list.addItem(item)

                    # Select and login to generate cookie
                    self.selected_character = character
                    self.character_list.setCurrentRow(self.character_list.count() - 1)
                    QTimer.singleShot(1000, self.login_selected_character)

                    logging.debug(f"First-run character '{name}' created and login initiated.")

                except sqlite3.Error as e:
                    logging.error(f"Failed to create character '{name}': {e}")
                    QMessageBox.critical(self, "Error", f"Failed to create character: {e}")
        else:
            sys.exit("No characters added. Exiting the application.")

    def add_new_character(self):
        """
        Add a new character, logout current user, log in new character.
        """
        logging.debug("Adding a new character.")
        dialog = CharacterDialog(self)

        if not dialog.exec():
            return  # User canceled or closed

        name = dialog.name_edit.text().strip()
        password = dialog.password_edit.text().strip()

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO characters (name, password) VALUES (?, ?)', (name, password))
                character_id = cursor.lastrowid
                cursor.execute('INSERT INTO coins (character_id, pocket, bank) VALUES (?, 0, 0)', (character_id,))
                conn.commit()

                character = {'id': character_id, 'name': name, 'password': password}
                self.characters.append(character)
                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, character_id)
                self.character_list.addItem(item)

                self.selected_character = character
                self.character_list.setCurrentRow(self.character_list.count() - 1)
                self.save_last_active_character(character_id)

                logging.debug(f"New character '{name}' added and selected. Logging out current user...")

                # 🚪 Force logout and prepare for JS login
                self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl?action=logout'))

                def delayed_login():
                    self.login_selected_character()

                QTimer.singleShot(1500, delayed_login)

            except sqlite3.Error as e:
                logging.error(f"Failed to add character '{name}': {e}")
                QMessageBox.critical(self, "Error", f"Failed to add character: {e}")

    def modify_character(self):
        """
        Modify the selected character's details, with validation to prevent blank name/password.
        """
        current_item = self.character_list.currentItem()
        if current_item is None:
            logging.warning("No character selected for modification.")
            return

        name = current_item.text()
        character = next((char for char in self.characters if char['name'] == name), None)
        if not character:
            logging.warning(f"Character '{name}' not found for modification.")
            return

        logging.debug(f"Modifying character: {name}")
        dialog = CharacterDialog(self, character)

        if not dialog.exec():
            return  # User canceled

        new_name = dialog.name_edit.text().strip()
        new_password = dialog.password_edit.text().strip()

        if not new_name or not new_password:
            QMessageBox.warning(self, "Validation Error", "Character name and password cannot be empty.")
            return  # 🚨 Do not proceed if fields are blank

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE characters SET name = ?, password = ? WHERE id = ?
                """, (new_name, new_password, character['id']))
                conn.commit()

            # Update in-memory character and UI
            character['name'] = new_name
            character['password'] = new_password
            self.selected_character = character
            current_item.setText(new_name)

            logging.debug(f"Character '{new_name}' modified successfully.")

        except sqlite3.Error as e:
            logging.error(f"Failed to modify character '{name}': {e}")
            QMessageBox.critical(self, "Error", f"Failed to modify character: {e}")

    def delete_character(self):
        """Delete the selected character from the list."""
        current_item = self.character_list.currentItem()
        if current_item is None:
            logging.warning("No character selected for deletion.")
            return

        char_id = current_item.data(Qt.UserRole)  # 🔥 Read ID!

        if char_id is None:
            logging.error("Selected character has no ID associated with it.")
            return

        # Delete from database first
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM characters WHERE id = ?", (char_id,))
                conn.commit()
                logging.debug(f"Character ID {char_id} deleted from database.")
        except sqlite3.Error as e:
            logging.error(f"Failed to delete character ID {char_id} from database: {e}")
            return

        # Then update in-memory list and UI
        self.characters = [char for char in self.characters if char['id'] != char_id]
        self.save_characters()
        self.character_list.takeItem(self.character_list.row(current_item))
        logging.debug(f"Character ID {char_id} deleted from UI.")

    def save_last_active_character(self, character_id):
        """
        Save the last active character's ID to the last_active_character table.
        Ensures that only one entry exists, replacing any previous entry.
        """
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM last_active_character")
                cursor.execute('INSERT INTO last_active_character (character_id) VALUES (?)', (character_id,))
                conn.commit()
                logging.debug(f"Last active character set to character_id: {character_id}")
            except sqlite3.Error as e:
                logging.error(f"Failed to save last active character: {e}")

    def load_last_active_character(self):
        """
        Load the last active character from the database by character_id, set the selected character,
        inject their cookie, and auto-login them on load.
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT character_id FROM last_active_character")
                result = cursor.fetchone()
                if result:
                    character_id = result[0]
                    self.selected_character = next((char for char in self.characters if char.get('id') == character_id),
                                                   None)

                    if self.selected_character:
                        # Highlight in UI
                        for i in range(self.character_list.count()):
                            if self.character_list.item(i).text() == self.selected_character['name']:
                                self.character_list.setCurrentRow(i)
                                break

                        logging.debug(f"Last active character loaded and selected: {self.selected_character['name']}")

                        self.load_last_destination_for_character(character_id)
                        self.update_minimap()

                        # ✅ Inject correct cookie for selected character
                        self.switch_to_character(self.selected_character['name'])

                        # ✅ After injecting cookie, navigate and login
                        def delayed_login():
                            self.login_selected_character()

                        QTimer.singleShot(1500, delayed_login)

                    else:
                        logging.warning(f"Last active character ID '{character_id}' not found in character list.")
                        self.set_default_character()

                else:
                    logging.warning("No last active character found in the database.")
                    self.set_default_character()

        except sqlite3.Error as e:
            logging.error(f"Failed to load last active character from database: {e}")
            self.set_default_character()

    def set_default_character(self):
        """
        Set the first character in the database as the default selected character,
        update the UI, and save it as the last active character.
        """
        if self.characters:
            self.selected_character = self.characters[0]
            self.character_list.setCurrentRow(0)
            logging.debug(f"No valid last active character; defaulting to: {self.selected_character['name']}")
            self.save_last_active_character(self.selected_character['id'])

            self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl'))
        else:
            self.selected_character = None
            logging.warning("No characters available to set as default.")

    def load_last_destination_for_character(self, character_id: int) -> None:
        """Load the last destination from the destinations table."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT col, row FROM destinations WHERE character_id = ? ORDER BY timestamp DESC LIMIT 1",
                    (character_id,)
                )
                result = cursor.fetchone()
                if result:
                    col, row = result
                    self.destination = (col, row)
                    logging.info(f"Loaded last destination ({col}, {row}) for character {character_id}")
                else:
                    self.destination = None
                    logging.info(f"No previous destination for character {character_id}")

        except sqlite3.Error as e:
            logging.error(f"Failed to load last destination: {e}")

    # -----------------------
    # Web View Handling
    # -----------------------

    def refresh_webview(self):
        """Refresh the webview content."""
        self.website_frame.reload()

    def apply_custom_css(self, css: str = None) -> None:
        """
        Apply either the given raw CSS, or load and apply the current profile's CSS from the database.

        Args:
            css (str, optional): If provided, apply this CSS directly. If None, fetch from the database using the current profile.
        """
        if css is None:
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT element, value FROM custom_css WHERE profile_name = ?",
                                   (self.current_css_profile,))
                    css_rules = cursor.fetchall()
            except sqlite3.Error as e:
                logging.error(f"Failed to load CSS rules for profile '{self.current_css_profile}': {e}")
                return

            if not css_rules:
                logging.warning(f"No CSS rules found for profile '{self.current_css_profile}'")
                return

            css = "\n".join(f"{element} {{{value}}}" for element, value in css_rules)

        # Inject the CSS into the web page
        script = f"""
            var style = document.createElement('style');
            style.type = 'text/css';
            style.innerHTML = `{css}`;
            document.head.appendChild(style);
        """
        self.website_frame.page().runJavaScript(script)
        logging.debug("Custom CSS applied.")

    def on_webview_load_finished(self, success):
        if not success:
            logging.error("Failed to load the webpage.")
            QMessageBox.critical(self, "Error", "Failed to load the webpage. Check your network or try again.")
            return

        logging.info("Webpage loaded successfully.")
        self.website_frame.page().toHtml(self.process_html)
        css = self.load_current_css()
        self.apply_custom_css(css)

        if self.login_needed:
            logging.debug("Logging in selected character via JS injection...")
            self.login_selected_character()
            self.pending_login = False
            return  # 🚫 wait for login to finish and reload first

        if self.pending_character_id_for_map:
            logging.debug(f"Loading destination for character {self.pending_character_id_for_map}")
            self.load_destination(self.pending_character_id_for_map)
            self.update_minimap()
            self.pending_character_id_for_map = None

    def process_html(self, html):
        """
        Process the HTML content of the webview to extract coordinates and coin information.

        Args:
            html (str): The HTML content of the page as a string.

        This method calls both the extract_coordinates_from_html and extract_coins_from_html methods.
        """
        try:
            # Extract coordinates for the minimap
            x_coord, y_coord = self.extract_coordinates_from_html(html)
            if x_coord is not None and y_coord is not None:
                # Set character coordinates directly
                self.character_x, self.character_y = x_coord, y_coord
                logging.debug(f"Set character coordinates to x={self.character_x}, y={self.character_y}")

                # Update compass display and route overlay state
                self.refresh_compass_state()

                # Update the minimap center based on new coordinates
                self.recenter_minimap()

            # Update coin info
            self.extract_coins_from_html(html)
            logging.debug("HTML processed successfully for coordinates and coin count.")

        except Exception as e:
            logging.error(f"Unexpected error in process_html: {e}")

    def refresh_compass_state(self):
        if not self.destination:
            self.ap_direction_label.setText("Compass: None")
            return

        direct_route, transit_route = self.get_compass_routes()

        # Determine selected route (manual or shortest)
        if self.selected_route_label == "Direct Route":
            selected = direct_route
        elif self.selected_route_label == "Transit Route":
            selected = transit_route
        else:
            selected = direct_route if direct_route[0] <= transit_route[0] else transit_route
            self.selected_route_label = "Direct Route" if selected == direct_route else "Transit Route"

        self.selected_route_path = selected[2]
        self.selected_route_description = selected[1]
        self.ap_direction_label.setText(f"Compass: {selected[1]}")

        # Ensure overlay updates
        if hasattr(self, "compass_overlay") and self.compass_overlay.isVisible():
            self.compass_overlay.refresh(direct_route, transit_route)

        # ✅ Force minimap redraw with selected route
        self.update_minimap()

    def extract_coordinates_from_html(self, html):

        soup = BeautifulSoup(html, 'html.parser')
        # logging.debug("Extracting coordinates from HTML...")

        # Try to extract the intersection label (like "Aardvark and 1st")
        intersect_span = soup.find('span', class_='intersect')
        text = intersect_span.text.strip() if intersect_span else ""
        # logging.debug(f"Intersection label found: {text}")

        # Check for city limits
        city_limit_cells = soup.find_all('td', class_='cityblock')

        # Extract coordinate inputs
        inputs = soup.find_all('input')
        x_vals = [int(inp['value']) for inp in inputs if
                  inp.get('name') == 'x' and inp.get('value') and inp['value'].isdigit()]
        y_vals = [int(inp['value']) for inp in inputs if
                  inp.get('name') == 'y' and inp.get('value') and inp['value'].isdigit()]
        last_x = max(x_vals) if x_vals else None
        last_y = max(y_vals) if y_vals else None

        # Get the first x/y (center of grid)
        first_x_input = soup.find('input', {'name': 'x'})
        first_y_input = soup.find('input', {'name': 'y'})
        first_x = int(first_x_input['value']) if first_x_input else None
        first_y = int(first_y_input['value']) if first_y_input else None

        logging.debug(f"First detected coordinate: x={first_x}, y={first_y}")
        logging.debug(f"Last detected coordinate: x={last_x}, y={last_y}")

        if city_limit_cells:
            logging.debug(f"Found {len(city_limit_cells)} city limit blocks.")

            # Check for first available coordinates
            first_x_input = soup.find('input', {'name': 'x'})
            first_y_input = soup.find('input', {'name': 'y'})

            first_x = int(first_x_input['value']) if first_x_input else None
            first_y = int(first_y_input['value']) if first_y_input else None

            logging.debug(f"First detected coordinate: x={first_x}, y={first_y}")

            if self.zoom_level == 3:
                if text == "Aardvark and 1st" and len(city_limit_cells) == 5:
                    logging.debug("Top-left corner detected with full border row: Aardvark and 1st")
                    return -1, -1

                if text == "Zestless and 1st" and len(city_limit_cells) == 5:
                    logging.debug("Top-right corner detected: Zestless and 1st")
                    return 198, -1

                if text == "Aardvark and 100th" and len(city_limit_cells) == 5:
                    logging.debug("Bottom-left corner detected: Aardvark and 100th")
                    return -1, 198

                if text == "Zestless and 100th" and len(city_limit_cells) == 5:
                    logging.debug("Bottom-right corner detected: Zestless and 100th")
                    return 198, 198

                # Adjust for Aardvark and NCL
                if len(city_limit_cells) == 3 and first_y == 0 and first_x == 0 and last_x == 2 and last_y == 1:
                    logging.debug(f"Detected Cell 0,1.")
                    return 0, -1

                # Adjust for WCL and 1st (0,1)
                if len(city_limit_cells) == 3 and first_y == 0 and first_x == 0:
                    logging.debug(f"Detected Cell 0,1.")
                    return -1, 0

                # Adjust for ON Zestless and 1st (198,1)
                if len(city_limit_cells) == 3 and first_x == 198 and first_y == 0:
                    logging.debug("Detected special case: on Zestless and 1st")
                    return first_x, first_y

                # Adjust for Northern Edge (Y=0)
                if len(city_limit_cells) == 3 and first_y == 0:
                    logging.debug(f"Detected Northern City Limit at y={first_y}")
                    return first_x, -1

                # Adjust for Western Edge (X=0)
                if len(city_limit_cells) == 3 and first_x == 0:
                    logging.debug(f"Detected Western City Limit at x={first_x}")
                    return -1, first_y

                # If no adjustments, return detected values
                return first_x, first_y

            if self.zoom_level == 5:
                if text == "Aardvark and 1st" and len(city_limit_cells) == 5:
                    logging.debug("Top-left corner detected with full border row: Aardvark and 1st")
                    return -2, -2

                if text == "Zestless and 1st" and len(city_limit_cells) == 5:
                    logging.debug("Top-right corner detected: Zestless and 1st")
                    return 197, -2

                if text == "Aardvark and 100th" and len(city_limit_cells) == 5:
                    logging.debug("Bottom-left corner detected: Aardvark and 100th")
                    return -2, 197

                if text == "Zestless and 100th" and len(city_limit_cells) == 5:
                    logging.debug("Bottom-right corner detected: Zestless and 100th")
                    return 197, 197

                # Adjust for Aardvark and NCL (1,0)
                if len(city_limit_cells) == 3 and first_y == 0 and first_x == 0 and last_x == 2 and last_y == 1:
                    logging.debug(f"Detected Cell 1,0.")
                    return -1, -2

                # Adjust for WCL and 1st (0,1)
                if len(city_limit_cells) == 3 and first_y == 0 and first_x == 0:
                    logging.debug(f"Detected Cell 0,1.")
                    return -2, -1

                # Adjust for ON Zestless and 1st (198,1)
                if len(city_limit_cells) == 3 and first_x == 198 and first_y == 0:
                    logging.debug("Detected special case: on Zestless and 1st")
                    return first_x - 1, first_y - 1

                # Adjust for Northern Edge (Y=0)
                if len(city_limit_cells) == 3 and first_y == 0:
                    logging.debug(f"Detected Northern City Limit at y={first_y}")
                    return first_x - 1, -2

                # Adjust for Western Edge (X=0)
                if len(city_limit_cells) == 3 and first_x == 0:
                    logging.debug(f"Detected Western City Limit at x={first_x}")
                    return -2, first_y - 1

                return first_x - 1, first_y - 1

            if self.zoom_level == 7:
                if text == "Aardvark and 1st" and len(city_limit_cells) == 5:
                    logging.debug("Top-left corner detected with full border row: Aardvark and 1st")
                    return -3, -3

                if text == "Zestless and 1st" and len(city_limit_cells) == 5:
                    logging.debug("Top-right corner detected: Zestless and 1st")
                    return 196, -3

                if text == "Aardvark and 100th" and len(city_limit_cells) == 5:
                    logging.debug("Bottom-left corner detected: Aardvark and 100th")
                    return -3, 196

                if text == "Zestless and 100th" and len(city_limit_cells) == 5:
                    logging.debug("Bottom-right corner detected: Zestless and 100th")
                    return 196, 196

                # Adjust for Aardvark and NCL (1,0)
                if len(city_limit_cells) == 3 and first_y == 0 and first_x == 0 and last_x == 2 and last_y == 1:
                    logging.debug(f"Detected Cell 1,0.")
                    return -2, -3

                # Adjust for WCL and 1st (0,1)
                if len(city_limit_cells) == 3 and first_y == 0 and first_x == 0:
                    logging.debug(f"Detected Cell 0,1.")
                    return -3, -2

                # Adjust for ON Zestless and 1st (198,1)
                if len(city_limit_cells) == 3 and first_x == 198 and first_y == 0:
                    logging.debug("Detected special case: on Zestless and 1st")
                    return first_x - 2, first_y - 2

                # Adjust for Northern Edge (Y=0)
                if len(city_limit_cells) == 3 and first_y == 0:
                    logging.debug(f"Detected Northern City Limit at y={first_y}")
                    return first_x - 2, -3

                # Adjust for Western Edge (X=0)
                if len(city_limit_cells) == 3 and first_x == 0:
                    logging.debug(f"Detected Western City Limit at x={first_x}")
                    return -3, first_y - 2

                return first_x - 2, first_y - 2

        logging.debug(f"Safe Fallback: x={first_x}, y={first_y}")
        return first_x, first_y

    def extract_coins_from_html(self, html):
        """
        Extract bank coins, pocket coins, and handle coin-related actions such as deposits,
        withdrawals, transit handling, and coins gained from hunting or stealing.

        Args:
            html (str): The HTML content as a string.

        This method searches for bank balance, deposits, withdrawals, hunting, robbing, receiving,
        and transit coin actions in the HTML content, updating both bank and pocket coins in the
        SQLite database based on character_id.
        """
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            character_id = self.selected_character['id']
            updates = []

            bank_match = re.search(r"Welcome to Omnibank. Your account has (\d+) coins in it.", html)
            if bank_match:
                bank_coins = int(bank_match.group(1))
                logging.info(f"Bank coins found: {bank_coins}")
                updates.append(("UPDATE coins SET bank = ? WHERE character_id = ?", (bank_coins, character_id)))

            pocket_match = re.search(r"You have (\d+) coins", html) or re.search(r"Money: (\d+) coins", html)
            if pocket_match:
                pocket_coins = int(pocket_match.group(1))
                logging.info(f"Pocket coins found: {pocket_coins}")
                updates.append(("UPDATE coins SET pocket = ? WHERE character_id = ?", (pocket_coins, character_id)))

            deposit_match = re.search(r"You deposit (\d+) coins.", html)
            if deposit_match:
                deposit_coins = int(deposit_match.group(1))
                logging.info(f"Deposit found: {deposit_coins} coins")
                updates.append(
                    ("UPDATE coins SET pocket = pocket - ? WHERE character_id = ?", (deposit_coins, character_id)))

            withdraw_match = re.search(r"You withdraw (\d+) coins.", html)
            if withdraw_match:
                withdraw_coins = int(withdraw_match.group(1))
                logging.info(f"Withdrawal found: {withdraw_coins} coins")
                updates.append(
                    ("UPDATE coins SET pocket = pocket + ? WHERE character_id = ?", (withdraw_coins, character_id)))

            transit_match = re.search(r"It costs 5 coins to ride. You have (\d+).", html)
            if transit_match:
                coins_in_pocket = int(transit_match.group(1))
                logging.info(f"Transit found: Pocket coins updated to {coins_in_pocket}")
                updates.append(("UPDATE coins SET pocket = ? WHERE character_id = ?", (coins_in_pocket, character_id)))

            actions = {
                'hunter': r'You drink the hunter\'s blood.*You also found (\d+) coins',
                'paladin': r'You drink the paladin\'s blood.*You also found (\d+) coins',
                'human': r'You drink the human\'s blood.*You also found (\d+) coins',
                'bag_of_coins': r'The bag contained (\d+) coins',
                'robbing': r'You stole (\d+) coins from (\w+)',
                'silver_suitcase': r'The suitcase contained (\d+) coins',
                'given_coins': r'(\w+) gave you (\d+) coins',
                'getting_robbed': r'(\w+) stole (\d+) coins from you'
            }

            for action, pattern in actions.items():
                match = re.search(pattern, html)
                if match:
                    coin_count = int(match.group(1 if action != 'given_coins' else 2))
                    if action == 'getting_robbed':
                        vamp_name = match.group(1)
                        updates.append(
                            ("UPDATE coins SET pocket = pocket - ? WHERE character_id = ?", (coin_count, character_id)))
                        logging.info(f"Lost {coin_count} coins to {vamp_name}.")
                    else:
                        updates.append(
                            ("UPDATE coins SET pocket = pocket + ? WHERE character_id = ?", (coin_count, character_id)))
                        logging.info(f"Gained {coin_count} coins from {action}.")
                    break

            for query, params in updates:
                cursor.execute(query, params)
            conn.commit()
            logging.info(f"Updated coins for character ID {character_id}.")

    def switch_css_profile(self, profile_name: str) -> None:
        self.current_css_profile = profile_name
        self.apply_custom_css()
        logging.info(f"Switched to profile: {profile_name} and applied CSS")

    # -----------------------
    # Minimap Drawing and Update
    # -----------------------

    def draw_minimap(self) -> None:
        """
        Draws the minimap with various features such as special locations and lines to nearest locations,
        with cell lines and dynamically scaled text size.
        """
        pixmap = PySide6.QtGui.QPixmap(self.minimap_size, self.minimap_size)
        painter = PySide6.QtGui.QPainter(pixmap)
        painter.fillRect(0, 0, self.minimap_size, self.minimap_size, PySide6.QtGui.QColor('lightgrey'))

        block_size = self.minimap_size // self.zoom_level
        font_size = max(8, block_size // 4)  # Dynamically adjust font size, with a minimum of 5
        border_size = 1  # Size of the border around each cell

        font = painter.font()
        font.setPointSize(font_size)
        painter.setFont(font)

        font_metrics = PySide6.QtGui.QFontMetrics(font)

        logging.debug(
            f"Drawing minimap with column_start={self.column_start}, row_start={self.row_start}, "f"zoom_level={self.zoom_level}, block_size={block_size}")

        if self.selected_route_path and len(self.selected_route_path) >= 2:
            color = PySide6.QtGui.QColor(
                "green") if self.selected_route_label == "Direct Route" else PySide6.QtGui.QColor(170, 0, 170)
            pen = PySide6.QtGui.QPen(color, 2)
            painter.setPen(pen)

            for i in range(len(self.selected_route_path) - 1):
                x1, y1 = self.selected_route_path[i]
                x2, y2 = self.selected_route_path[i + 1]

                # Convert map coordinates to screen positions
                col1 = x1 - self.column_start
                row1 = y1 - self.row_start
                col2 = x2 - self.column_start
                row2 = y2 - self.row_start

                tile_size = self.zoom_level  # size in pixels
                cx1 = col1 * tile_size + tile_size // 2
                cy1 = row1 * tile_size + tile_size // 2
                cx2 = col2 * tile_size + tile_size // 2
                cy2 = row2 * tile_size + tile_size // 2

                painter.drawLine(cx1, cy1, cx2, cy2)

        def draw_label_box(x, y, width, base_height, bg_color, text):
            """
            Draws a text label box with a background color, white border, and properly formatted text.
            Allows wrapped text to grow to 2 lines in zoom 5 and 7.
            """
            # Set font based on zoom level
            font = painter.font()
            if self.zoom_level == 3:
                font.setPointSize(max(4, min(8, width // 4)))
            elif self.zoom_level == 5:
                font.setPointSize(max(4, min(7, width // 5)))
            elif self.zoom_level == 7:
                font.setPointSize(max(4, min(6, width // 6)))
            painter.setFont(font)

            # Calculate actual wrapped height using boundingRect
            font_metrics = PySide6.QtGui.QFontMetrics(font)
            if self.zoom_level >= 5:
                # Use a dummy bounding rect to get actual wrapped height
                wrapped_rect = font_metrics.boundingRect(
                    QRect(0, 0, width, 1000),
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
                    text
                )
                max_height = base_height
                label_height = min(wrapped_rect.height() + 4, max_height)
            else:
                label_height = base_height

            # Draw background
            painter.fillRect(QRect(x, y, width, label_height), bg_color)

            # Draw white border
            painter.setPen(PySide6.QtGui.QColor('white'))
            painter.drawRect(QRect(x, y, width, label_height))

            # Draw text
            text_rect = QRect(x, y, width, label_height)
            painter.setPen(PySide6.QtGui.QColor('white'))

            if self.zoom_level >= 5:
                painter.drawText(
                    text_rect,
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
                    text
                )
            else:
                painter.drawText(
                    text_rect,
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                    text
                )

        # Draw the grid
        for i in range(self.zoom_level):
            for j in range(self.zoom_level):
                column_index = self.column_start + j
                row_index = self.row_start + i

                x0, y0 = j * block_size, i * block_size
                logging.debug(
                    f"Drawing grid cell at column_index={column_index}, row_index={row_index}, "f"x0={x0}, y0={y0}")

                # Draw the cell background
                painter.setPen(PySide6.QtGui.QColor('white'))
                painter.drawRect(x0, y0, block_size - border_size, block_size - border_size)

                # Special location handling
                column_name = next((name for name, coord in self.columns.items() if coord == column_index), None)
                row_name = next((name for name, coord in self.rows.items() if coord == row_index), None)

                # Draw cell background color to match in-game city grid
                if column_index < 1 or column_index > 200 or row_index < 1 or row_index > 200:
                    # Map edges (border)
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, PySide6.QtGui.QColor(self.color_mappings["edge"]))
                elif column_index % 2 == 0 or row_index % 2 == 0:
                    # If either coordinate is even → Streets (Gray)
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, PySide6.QtGui.QColor(self.color_mappings["street"]))
                else:
                    # Both coordinates odd → City Blocks (Black)
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, PySide6.QtGui.QColor(self.color_mappings["alley"]))

                if column_name and row_name:
                    label_text = f"{column_name} & {row_name}"
                    label_height = block_size // 3  # Set label height
                    draw_label_box(x0 + 2, y0 + 2, block_size - 4, label_height, self.color_mappings["intersect"],
                                   label_text)

        # Draw special locations (banks with correct offsets)
        for bank_key in self.banks_coordinates.keys():
            if " & " in bank_key:
                col_name, row_name = bank_key.split(" & ")
                col = self.columns.get(col_name, 0)
                row = self.rows.get(row_name, 0)

                if col is not None and row is not None:
                    adjusted_column_index = col + 1
                    adjusted_row_index = row + 1

                    # Dynamically determine label height based on zoom
                    if self.zoom_level >= 5:
                        font = painter.font()
                        font.setPointSize(max(4, min(7, block_size // 5)) if self.zoom_level == 5 else max(4, min(6,
                                                                                                                  block_size // 6)))
                        font_metrics = PySide6.QtGui.QFontMetrics(font)
                        line_height = font_metrics.lineSpacing()
                        label_height = min(line_height * 2 + 4, block_size)
                    else:
                        label_height = block_size // 3

                    draw_label_box(
                        (adjusted_column_index - self.column_start) * block_size,
                        (adjusted_row_index - self.row_start) * block_size,
                        block_size, label_height, self.color_mappings["bank"], "BANK"
                    )
                else:
                    logging.warning(f"Skipping bank at {col_name} & {row_name} due to missing coordinates")
            else:
                logging.warning(f"Skipping invalid bank_key format: {bank_key}")

        # Draw other locations without the offset
        for name, (column_index, row_index) in self.taverns_coordinates.items():
            if column_index is not None and row_index is not None:
                if self.zoom_level >= 5:
                    font = painter.font()
                    font.setPointSize(
                        max(4, min(7, block_size // 5)) if self.zoom_level == 5 else max(4, min(6, block_size // 6)))
                    font_metrics = PySide6.QtGui.QFontMetrics(font)
                    line_height = font_metrics.lineSpacing()
                    label_height = min(line_height * 2 + 4, block_size)
                else:
                    label_height = block_size // 3
                draw_label_box(
                    (column_index - self.column_start) * block_size,
                    (row_index - self.row_start) * block_size,
                    block_size, label_height, self.color_mappings["tavern"], name
                )

        for name, (column_index, row_index) in self.transits_coordinates.items():
            if column_index is not None and row_index is not None:
                if self.zoom_level >= 5:
                    font = painter.font()
                    font.setPointSize(
                        max(4, min(7, block_size // 5)) if self.zoom_level == 5 else max(4, min(6, block_size // 6)))
                    font_metrics = PySide6.QtGui.QFontMetrics(font)
                    line_height = font_metrics.lineSpacing()
                    label_height = min(line_height * 2 + 4, block_size)
                else:
                    label_height = block_size // 3
                draw_label_box(
                    (column_index - self.column_start) * block_size,
                    (row_index - self.row_start) * block_size,
                    block_size, label_height, self.color_mappings["transit"], name
                )

        for name, (column_index, row_index) in self.user_buildings_coordinates.items():
            if column_index is not None and row_index is not None:
                if self.zoom_level >= 5:
                    font = painter.font()
                    font.setPointSize(
                        max(4, min(7, block_size // 5)) if self.zoom_level == 5 else max(4, min(6, block_size // 6)))
                    font_metrics = PySide6.QtGui.QFontMetrics(font)
                    line_height = font_metrics.lineSpacing()
                    label_height = min(line_height * 2 + 4, block_size)
                else:
                    label_height = block_size // 3
                draw_label_box(
                    (column_index - self.column_start) * block_size,
                    (row_index - self.row_start) * block_size,
                    block_size, label_height, self.color_mappings["user_building"], name
                )

        for name, (column_index, row_index) in self.shops_coordinates.items():
            if column_index is not None and row_index is not None:
                if self.zoom_level >= 5:
                    font = painter.font()
                    font.setPointSize(
                        max(4, min(7, block_size // 5)) if self.zoom_level == 5 else max(4, min(6, block_size // 6)))
                    font_metrics = PySide6.QtGui.QFontMetrics(font)
                    line_height = font_metrics.lineSpacing()
                    label_height = min(line_height * 2 + 4, block_size)
                else:
                    label_height = block_size // 3
                draw_label_box(
                    (column_index - self.column_start) * block_size,
                    (row_index - self.row_start) * block_size,
                    block_size, label_height, self.color_mappings["shop"], name
                )

        for name, (column_index, row_index) in self.guilds_coordinates.items():
            if column_index is not None and row_index is not None:
                if self.zoom_level >= 5:
                    font = painter.font()
                    font.setPointSize(
                        max(4, min(7, block_size // 5)) if self.zoom_level == 5 else max(4, min(6, block_size // 6)))
                    font_metrics = PySide6.QtGui.QFontMetrics(font)
                    line_height = font_metrics.lineSpacing()
                    label_height = min(line_height * 2 + 4, block_size)
                else:
                    label_height = block_size // 3
                draw_label_box(
                    (column_index - self.column_start) * block_size,
                    (row_index - self.row_start) * block_size,
                    block_size, label_height, self.color_mappings["guild"], name
                )

        for name, (column_index, row_index) in self.places_of_interest_coordinates.items():
            if column_index is not None and row_index is not None:
                if name.lower() == "graveyard":
                    color = self.color_mappings.get("graveyard", self.color_mappings["placesofinterest"])
                else:
                    color = self.color_mappings["placesofinterest"]

                logging.debug(f"Drawing {name} with color {color.name()}")

                if self.zoom_level >= 5:
                    font = painter.font()
                    font.setPointSize(
                        max(4, min(7, block_size // 5)) if self.zoom_level == 5 else max(4, min(6, block_size // 6)))
                    font_metrics = PySide6.QtGui.QFontMetrics(font)
                    line_height = font_metrics.lineSpacing()
                    label_height = min(line_height * 2 + 4, block_size)
                else:
                    label_height = block_size // 3

                draw_label_box(
                    (column_index - self.column_start) * block_size,
                    (row_index - self.row_start) * block_size,
                    block_size, label_height, color, name
                )

            # Get current location
            current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2

            # Find and draw lines to nearest locations
            nearest_tavern = self.find_nearest_tavern(current_x, current_y)
            nearest_bank = self.find_nearest_bank(current_x, current_y)
            nearest_transit = self.find_nearest_transit(current_x, current_y)

            # Draw nearest tavern line
            if nearest_tavern:
                nearest_tavern_coords = nearest_tavern[0][1]
                painter.setPen(PySide6.QtGui.QPen(PySide6.QtGui.QColor('orange'), 3))
                painter.drawLine(
                    (current_x - self.column_start) * block_size + block_size // 2,
                    (current_y - self.row_start) * block_size + block_size // 2,
                    (nearest_tavern_coords[0] - self.column_start) * block_size + block_size // 2,
                    (nearest_tavern_coords[1] - self.row_start) * block_size + block_size // 2
                )

            # Draw nearest bank line
            if nearest_bank:
                nearest_bank_coords = nearest_bank  # Already a (col, row) tuple
                painter.setPen(PySide6.QtGui.QPen(PySide6.QtGui.QColor('blue'), 3))
                painter.drawLine(
                    (current_x - self.column_start) * block_size + block_size // 2,
                    (current_y - self.row_start) * block_size + block_size // 2,
                    (nearest_bank_coords[0] + 1 - self.column_start) * block_size + block_size // 2,
                    (nearest_bank_coords[1] + 1 - self.row_start) * block_size + block_size // 2
                )

            # Draw nearest transit line
            if nearest_transit:
                nearest_transit_coords = nearest_transit[0][1]
                painter.setPen(PySide6.QtGui.QPen(PySide6.QtGui.QColor('red'), 3))
                painter.drawLine(
                    (current_x - self.column_start) * block_size + block_size // 2,
                    (current_y - self.row_start) * block_size + block_size // 2,
                    (nearest_transit_coords[0] - self.column_start) * block_size + block_size // 2,
                    (nearest_transit_coords[1] - self.row_start) * block_size + block_size // 2
                )

            # Draw selected compass route (green for direct)
            if (
                    self.destination is not None and
                    self.selected_route_label == "Direct Route" and
                    self.selected_route_path and
                    len(self.selected_route_path) >= 2
            ):
                logging.debug(
                    f"Drawing direct route from {self.selected_route_path[0]} to {self.selected_route_path[-1]}")
                painter.setPen(PySide6.QtGui.QPen(PySide6.QtGui.QColor("green"), 3))
                x1, y1 = self.selected_route_path[0]
                x2, y2 = self.selected_route_path[-1]
                painter.drawLine(
                    (current_x - self.column_start) * block_size + block_size // 2,
                    (current_y - self.row_start) * block_size + block_size // 2,
                    (self.destination[0] - self.column_start) * block_size + block_size // 2,
                    (self.destination[1] - self.row_start) * block_size + block_size // 2
                )

            # Draw selected compass route (purple for transit)
            if (
                    self.destination is not None and
                    self.selected_route_label == "Transit Route" and
                    self.selected_route_path and
                    len(self.selected_route_path) >= 2
            ):
                logging.debug(f"Transit route path: {self.selected_route_path}")
                painter.setPen(PySide6.QtGui.QPen(PySide6.QtGui.QColor(170, 0, 170), 3))

                # Current player position
                current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2
                dest_x, dest_y = self.destination
                logging.debug(f"Player position: ({current_x}, {current_y})")
                logging.debug(f"Destination: ({dest_x}, {dest_y})")

                # Find nearest transits
                nearest_transit_to_player = self.find_nearest_transit(current_x, current_y)
                nearest_transit_to_dest = self.find_nearest_transit(dest_x, dest_y)
                logging.debug(f"Nearest transit to player: {nearest_transit_to_player}")
                logging.debug(f"Nearest transit to destination: {nearest_transit_to_dest}")

                # Check if same transit station
                same_transit = False
                if nearest_transit_to_player and nearest_transit_to_dest:
                    same_transit = nearest_transit_to_player[0][1] == nearest_transit_to_dest[0][1]

                if same_transit:
                    logging.debug("Player and destination share same transit. Drawing direct purple route.")
                    px1 = (current_x - self.column_start) * block_size + block_size // 2
                    py1 = (current_y - self.row_start) * block_size + block_size // 2
                    px2 = (dest_x - self.column_start) * block_size + block_size // 2
                    py2 = (dest_y - self.row_start) * block_size + block_size // 2
                    painter.drawLine(px1, py1, px2, py2)

                else:
                    # Segment 1: Player to nearest transit
                    if nearest_transit_to_player:
                        transit_x, transit_y = nearest_transit_to_player[0][1]
                        px1 = (current_x - self.column_start) * block_size + block_size // 2
                        py1 = (current_y - self.row_start) * block_size + block_size // 2
                        px2 = (transit_x - self.column_start) * block_size + block_size // 2
                        py2 = (transit_y - self.row_start) * block_size + block_size // 2
                        logging.debug(f"Segment 1 coords: ({px1}, {py1}) to ({px2}, {py2})")
                        if not (px1 < 0 and px2 < 0) and not (px1 > self.minimap_size and px2 > self.minimap_size) and \
                                not (py1 < 0 and py2 < 0) and not (py1 > self.minimap_size and py2 > self.minimap_size):
                            painter.drawLine(px1, py1, px2, py2)
                        else:
                            logging.debug("Segment 1 skipped: both endpoints off-screen")

                    # Segment 2: Transit near destination to destination
                    if nearest_transit_to_dest and self.destination:
                        transit_x, transit_y = nearest_transit_to_dest[0][1]
                        px1 = (transit_x - self.column_start) * block_size + block_size // 2
                        py1 = (transit_y - self.row_start) * block_size + block_size // 2
                        px2 = (dest_x - self.column_start) * block_size + block_size // 2
                        py2 = (dest_y - self.row_start) * block_size + block_size // 2
                        logging.debug(f"Segment 2 coords: ({px1}, {py1}) to ({px2}, {py2})")
                        if not (px1 < 0 and px2 < 0) and not (px1 > self.minimap_size and px2 > self.minimap_size) and \
                                not (py1 < 0 and py2 < 0) and not (py1 > self.minimap_size and py2 > self.minimap_size):
                            painter.drawLine(px1, py1, px2, py2)
                        else:
                            logging.debug("Segment 2 skipped: both endpoints off-screen")

        painter.end()
        self.minimap_label.setPixmap(pixmap)

    def update_minimap(self):
        """
        Update the minimap.

        Calls draw_minimap and then updates the info frame with any relevant information.
        """
        if not self.is_updating_minimap:
            self.is_updating_minimap = True

            # 🔁 Ensure we always have an updated route label/path/description
            if self.destination and (not self.selected_route_label or not self.selected_route_path):
                self.refresh_compass_state()

            self.draw_minimap()
            self.update_info_frame()

            # Only refresh the overlay if it exists AND we're not mid-selection
            if hasattr(self, 'compass_overlay') and self.compass_overlay.isVisible():
                if not self.selected_route_path:  # ⬅ only re-show if no manual route is selected
                    self.show_compass_overlay()

            self.is_updating_minimap = False

    def find_nearest_location(self, x, y, locations):
        """
        Find the nearest location to the given coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
            locations (list): List of location coordinates.

        Returns:
            list: List of distances and corresponding coordinates.
        """
        distances = [(max(abs(lx - x), abs(ly - y)), (lx, ly)) for lx, ly in locations]
        distances.sort()
        return distances

    def find_nearest_tavern(self, x, y):
        """
        Find the nearest tavern to the given coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            list: List of distances and corresponding coordinates.
        """
        return self.find_nearest_location(x, y, list(self.taverns_coordinates.values()))

    def find_nearest_bank(self, current_x, current_y):
        min_distance = float("inf")
        nearest_bank = None

        for bank_key, (col_name, row_name) in self.banks_coordinates.items():
            if isinstance(bank_key, str):  # Convert from street name format if necessary
                col_name, row_name = bank_key.split(" & ")

            col = self.columns.get(col_name, 0)
            row = self.rows.get(row_name, 0)

            if col and row:
                distance = abs(col - current_x) + abs(row - current_y)
                if distance < min_distance:
                    min_distance = distance
                    nearest_bank = (col, row)  # Return actual coordinates

        return nearest_bank  # Returns (x, y) tuple

    def find_nearest_transit(self, x, y):
        """
        Find the nearest transit station to the given coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            list: List of distances and corresponding coordinates.
        """
        return self.find_nearest_location(x, y, list(self.transits_coordinates.values()))

    def set_destination(self):
        """Open the set destination dialog to select a new destination."""
        dialog = SetDestinationDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Reload the destination from the DB to ensure it's per-character and persisted
            if self.selected_character:
                self.load_last_destination_for_character(self.selected_character['id'])
            self.update_minimap()

    def get_current_destination(self, character_id: int):
        """Retrieve the latest destination for the selected character."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT col, row FROM destinations WHERE character_id = ? ORDER BY timestamp DESC LIMIT 1",
                           (character_id,))
            result = cursor.fetchone()
            return (result[0], result[1]) if result else None

    def load_destination(self, character_id: int | None = None) -> None:
        """
        Load the destination for a given character (or selected character if not provided).
        """
        if character_id is None:
            if not self.selected_character:
                logging.warning("No character selected; cannot load destination.")
                return
            character_id = self.selected_character.get('id')

        if not character_id:
            logging.warning("Character ID missing; cannot load destination.")
            return

        destination_coords = self.get_current_destination(character_id)
        if destination_coords:
            self.destination = destination_coords
            logging.info(f"Loaded destination {self.destination} for character {character_id}")
        else:
            self.destination = None
            logging.info(f"No destination found for character {character_id}")

    # -----------------------
    # Minimap Controls
    # -----------------------

    def zoom_in(self):
        """
        Zoom in the minimap, ensuring the character stays centered.
        """
        if self.zoom_level > 3:
            self.zoom_level -= 2
            self.zoom_level_changed = True
            self.save_zoom_level_to_database()
            self.website_frame.page().toHtml(self.process_html)

    def zoom_out(self):
        """
        Zoom out the minimap, ensuring the character stays centered.
        """
        if self.zoom_level < 7:
            self.zoom_level += 2
            self.zoom_level_changed = True
            self.save_zoom_level_to_database()
            self.website_frame.page().toHtml(self.process_html)

    def save_zoom_level_to_database(self):
        """Save the current zoom level to the settings table in the database."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO settings (setting_name, setting_value)
                    VALUES ('minimap_zoom', ?)
                    ON CONFLICT(setting_name) DO UPDATE SET setting_value = ?;
                """, (self.zoom_level, self.zoom_level))
                conn.commit()
                logging.debug(f"Zoom level saved to database: {self.zoom_level}")
        except sqlite3.Error as e:
            logging.error(f"Failed to save zoom level to database: {e}")

    def load_zoom_level_from_database(self):
        """
        Load the saved zoom level from the settings table in the database.
        If no value is found, set it to the default (3).
        """
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                result = cursor.execute(
                    "SELECT setting_value FROM settings WHERE setting_name = 'minimap_zoom'").fetchone()
                self.zoom_level = int(result[0]) if result else 3
                logging.debug(f"Zoom level loaded from database: {self.zoom_level}")
        except sqlite3.Error as e:
            self.zoom_level = 3  # Fallback default zoom level
            logging.error(f"Failed to load zoom level from database: {e}")

    def recenter_minimap(self):
        """
        Recenter the minimap so that the character's location is at the center cell,
        including visible but non-traversable areas beyond the traversable range.
        """
        if not hasattr(self, 'character_x') or not hasattr(self, 'character_y'):
            logging.error("Character position not set. Cannot recenter minimap.")
            return

        logging.debug(f"Before recentering: character_x={self.character_x}, character_y={self.character_y}")

        # Calculate zoom offset (-1 for 5x5, -2 for 7x7, etc.)
        if self.zoom_level == 3:
            zoom_offset = -1
        elif self.zoom_level == 5:
            zoom_offset = 0
        elif self.zoom_level == 7:
            zoom_offset = 1
        else:
            zoom_offset = -(self.zoom_level // 2)  # Safe fallback
        logging.debug(f"Zoom Level: {self.zoom_level}")
        logging.debug(f"Zoom Offset: {zoom_offset}")
        logging.debug(f"Debug: char_y={self.character_y}, row_start={self.row_start}, zoom_offset={zoom_offset}")
        logging.debug(f"Clamping min: {min(self.character_y + zoom_offset, 200 - self.zoom_level)}")

        self.column_start = self.character_x - zoom_offset
        self.row_start = self.character_y - zoom_offset

        logging.debug(
            f"Recentered minimap: x={self.character_x}, y={self.character_y}, col_start={self.column_start}, row_start={self.row_start}")
        self.update_minimap()

    def go_to_location(self):
        """
        Go to the selected location.
        Adjusts the minimap's starting column and row based on the selected location from the combo boxes.
        """
        column_name = self.combo_columns.currentText()
        row_name = self.combo_rows.currentText()

        if column_name in self.columns:
            self.column_start = self.columns[column_name] - self.zoom_level // 2
            logging.debug(f"Set column_start to {self.column_start} for column '{column_name}'")
        else:
            logging.error(f"Column '{column_name}' not found in self.columns")

        if row_name in self.rows:
            self.row_start = self.rows[row_name] - self.zoom_level // 2
            logging.debug(f"Set row_start to {self.row_start} for row '{row_name}'")
        else:
            logging.error(f"Row '{row_name}' not found in self.rows")

        # Update the minimap after setting the new location
        self.update_minimap()

    def mousePressEvent(self, event: PySide6.QtGui.QMouseEvent):
        """Handle mouse clicks on the minimap to recenter it."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Map global click position to minimap's local coordinates
            local_position = self.minimap_label.mapFromGlobal(event.globalPosition().toPoint())
            click_x, click_y = local_position.x(), local_position.y()

            # Validate click is within the minimap
            if 0 <= click_x < self.minimap_label.width() and 0 <= click_y < self.minimap_label.height():
                # Calculate relative coordinates and block size
                block_size = self.minimap_size // self.zoom_level
                clicked_column = self.column_start + (click_x // block_size)
                clicked_row = self.row_start + (click_y // block_size)
                center_offset = self.zoom_level // 2
                min_start, max_start = -(self.zoom_level // 2), 201 + (self.zoom_level // 2) - self.zoom_level
                self.column_start = max(min_start, min(clicked_column - center_offset, max_start))
                self.row_start = max(min_start, min(clicked_row - center_offset, max_start))
                logging.debug(f"Click at ({click_x}, {click_y}) -> Cell: ({clicked_column}, {clicked_row})")
                logging.debug(f"New minimap start: column={self.column_start}, row={self.row_start}")

                # Update the minimap display
                self.update_minimap()
            else:
                logging.debug(f"Click ({click_x}, {click_y}) is outside the minimap bounds.")

    def cycle_character(self, direction):
        """Cycle through characters in the QListWidget."""
        current_row = self.character_list.currentRow()
        new_row = (current_row + direction) % self.character_list.count()
        if new_row < 0:
            new_row = self.character_list.count() - 1
        self.character_list.setCurrentRow(new_row)
        self.on_character_selected(self.character_list.item(new_row))

    def open_SetDestinationDialog(self):
        """
        Open the set destination dialog.
        Opens a dialog that allows the user to set a destination and updates the minimap if confirmed.
        """
        dialog = SetDestinationDialog(self)

        # Execute dialog and check for acceptance
        if dialog.exec() == QDialog.accepted:
            # Load the newly set destination from the database
            self.load_destination()

            # Update the minimap with the new destination
            self.update_minimap()

    def save_to_recent_destinations(self, character_id: int, col: int, row: int):
        """
        Save the current destination to the recent destinations for the specific character,
        keeping only the last 10 entries per character.

        Args:
            character_id (int): ID of the character.
            col (int): Column coordinate of the destination.
            row (int): Row coordinate of the destination.
        """
        if character_id is None:
            return

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO recent_destinations (character_id, col, row, timestamp)
                    VALUES (?, ?, ?, datetime('now'))
                """, (character_id, col, row))

                cursor.execute("""
                    DELETE FROM recent_destinations 
                    WHERE character_id = ? AND id NOT IN (
                        SELECT id FROM recent_destinations
                        WHERE character_id = ?
                        ORDER BY timestamp DESC LIMIT 10
                    )
                """, (character_id, character_id))

                conn.commit()
                logging.info(f"Destination ({col}, {row}) saved for character ID {character_id}.")

        except sqlite3.Error as e:
            logging.error(f"Failed to save recent destination: {e}")

    def eventFilter(self, source, event):
        # Only clear on actual user interaction, not initial app load
        if event.type() == QEvent.Type.MouseButtonPress:
            if source in (self.combo_columns, self.combo_rows) and source.isEditable():
                source.lineEdit().clear()
                source.lineEdit().setFocus()

        elif event.type() == QEvent.Type.KeyPress:
            if isinstance(source, QLineEdit) and source.text().startswith("Select"):
                source.clear()

        return super().eventFilter(source, event)

    # -----------------------
    # Infobar Management
    # -----------------------

    def calculate_ap_cost(self, start, end):
        """
        Calculate the AP cost of moving from start to end using the Chebyshev distance.

        Args:
            start (tuple): Starting coordinates (x, y).
            end (tuple): Ending coordinates (x, y).

        Returns:
            int: AP cost of moving from start to end.
        """
        return max(abs(start[0] - end[0]), abs(start[1] - end[1]))

    def update_info_frame(self):
        """
        Update the information frame with the closest locations and AP costs.
        """
        current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2

        # Closest Bank
        nearest_bank = self.find_nearest_bank(current_x, current_y)
        if nearest_bank:
            bank_coords = nearest_bank  # No need for `[0][1]`
            adjusted_bank_coords = (bank_coords[0] + 1, bank_coords[1] + 1)
            bank_ap_cost = self.calculate_ap_cost((current_x, current_y), adjusted_bank_coords)
            bank_intersection = self.get_intersection_name(adjusted_bank_coords)
            self.bank_label.setText(f"Bank\n{bank_intersection} - AP: {bank_ap_cost}")

        # Closest Transit
        nearest_transit = self.find_nearest_transit(current_x, current_y)
        if nearest_transit:
            transit_coords = nearest_transit[0][1]
            transit_name = next(name for name, coords in self.transits_coordinates.items() if coords == transit_coords)
            transit_ap_cost = self.calculate_ap_cost((current_x, current_y), transit_coords)
            transit_intersection = self.get_intersection_name(transit_coords)
            self.transit_label.setText(f"Transit - {transit_name}\n{transit_intersection} - AP: {transit_ap_cost}")

        # Closest Tavern
        nearest_tavern = self.find_nearest_tavern(current_x, current_y)
        if nearest_tavern:
            tavern_coords = nearest_tavern[0][1]
            tavern_name = next(name for name, coords in self.taverns_coordinates.items() if coords == tavern_coords)
            tavern_ap_cost = self.calculate_ap_cost((current_x, current_y), tavern_coords)
            tavern_intersection = self.get_intersection_name(tavern_coords)
            self.tavern_label.setText(f"{tavern_name}\n{tavern_intersection} - AP: {tavern_ap_cost}")

        # Set Destination Info
        if self.destination:
            destination_coords = self.destination
            destination_ap_cost = self.calculate_ap_cost((current_x, current_y), destination_coords)
            destination_intersection = self.get_intersection_name(destination_coords)

            # Check for a named place at destination
            place_name = next(
                (name for name, coords in {
                    **self.guilds_coordinates,
                    **self.shops_coordinates,
                    **self.user_buildings_coordinates,
                    **self.places_of_interest_coordinates
                }.items() if coords == destination_coords),
                None
            )

            destination_label_text = place_name if place_name else "Set Destination"
            self.destination_label.setText(
                f"{destination_label_text}\n{destination_intersection} - AP: {destination_ap_cost}"
            )

            # Transit-Based AP Cost for Set Destination
            nearest_transit_to_character = self.find_nearest_transit(current_x, current_y)
            nearest_transit_to_destination = self.find_nearest_transit(destination_coords[0], destination_coords[1])

            if nearest_transit_to_character and nearest_transit_to_destination:
                char_transit_coords = nearest_transit_to_character[0][1]
                dest_transit_coords = nearest_transit_to_destination[0][1]
                char_to_transit_ap = self.calculate_ap_cost((current_x, current_y), char_transit_coords)
                dest_to_transit_ap = self.calculate_ap_cost(destination_coords, dest_transit_coords)
                total_ap_via_transit = char_to_transit_ap + dest_to_transit_ap

                # Get transit names
                char_transit_name = next(
                    name for name, coords in self.transits_coordinates.items() if coords == char_transit_coords)
                dest_transit_name = next(
                    name for name, coords in self.transits_coordinates.items() if coords == dest_transit_coords)

                # Update the transit destination label to include destination name
                destination_name = place_name if place_name else "Set Destination"
                self.transit_destination_label.setText(
                    f"{destination_name} - {char_transit_name} to {dest_transit_name}\n"
                    f"{self.get_intersection_name(dest_transit_coords)} - Total AP: {total_ap_via_transit}"
                )

            else:
                self.transit_destination_label.setText("Transit Route Info Unavailable")

        else:
            # Clear labels when no destination is set
            self.destination_label.setText("No Destination Set")
            self.transit_destination_label.setText("No Destination Set")

        self.update_ap_direction_label()

    def get_intersection_name(self, coords):
        """
        Get the intersection name for the given coordinates, including edge cases.

        Args:
            coords (tuple): Coordinates (x, y).

        Returns:
            str: Readable intersection like "Nickel & 55th" or fallback "x, y".
        """
        x, y = coords

        # Try direct match
        column_name = next((name for name, coord in self.columns.items() if coord == x), None)
        row_name = next((name for name, coord in self.rows.items() if coord == y), None)

        # Fallback to offset-based match
        if not column_name:
            column_name = next((name for name, coord in self.columns.items() if coord == x - 1), None)
        if not row_name:
            row_name = next((name for name, coord in self.rows.items() if coord == y - 1), None)

        if column_name and row_name:
            return f"{column_name} & {row_name}"
        elif column_name:
            return f"{column_name} & Unknown Row"
        elif row_name:
            return f"Unknown Column & {row_name}"
        else:
            return f"{x}, {y}"  # raw coords as fallback

    def update_ap_direction_label(self):
        """
        Update the compass label at the top of the screen.
        Shows either the selected route from overlay or the shortest by default.
        """
        if not self.destination:
            self.ap_direction_label.setText("Compass: None")
            self.selected_route_path = None
            return

        direct_route, transit_route = self.get_compass_routes()

        # Select route: previously chosen, or fallback to shortest
        if self.selected_route_label == "Direct Route":
            selected = direct_route
        elif self.selected_route_label == "Transit Route":
            selected = transit_route
        else:
            selected = direct_route if direct_route[0] <= transit_route[0] else transit_route
            self.selected_route_label = "Direct Route" if selected == direct_route else "Transit Route"

        self.selected_route_description = selected[1]
        self.selected_route_path = selected[2]
        self.ap_direction_label.setText(f"Compass: {selected[1]}")

    # -----------------------
    # Menu Actions
    # -----------------------

    def open_discord(self):
        """Opens a dialog with a listing of public Discord servers for the community"""
        dialog = DiscordServerDialog(self)
        dialog.exec()

    def open_website(self):
        """Open the RBC Website in the system's default web browser."""
        webbrowser.open('https://lollis-home.ddns.net/viewpage.php?page_id=2')

    def show_about_dialog(self):
        """
        Display an "About" dialog with details about the RBC City Map application.
        """
        QMessageBox.about(self, "About RBC City Map",
                          "RBC City Map Application\n\n"
                          f"Version {VERSION_NUMBER}\n\n"
                          "This application allows you to view the city map of RavenBlack City, "
                          "set destinations, and navigate through various locations.\n\n"
                          "Development team shown in credits.\n\n\n"
                          "This program is based on the LIAM² app by Leprichaun")

    def show_credits_dialog(self):
        """
        Display a "Credits" dialog with a list of contributors to the RBC City Map project.
        """
        credits_text = (
            "Credits to the team who made this happen:\n\n"
            "Windows: Jonathan Lollis (Nesmuth), Justin Solivan\n\n"
            "Apple OSx Compatibility: Joseph Lemois\n\n"
            "Linux Compatibility: Josh \"Blaskewitts\" Corse, Fern Lovebond\n\n"
            "Design and Layout: Shuvi, Blair Wilson (Ikunnaprinsess)\n\n\n\n"
            "Special Thanks:\n\n"
            "Cain \"Leprechaun\" McBride for the LIAM² program \nthat inspired this program\n\n"
            "Cliff Burton for A View in the Dark which is \nwhere Shops and Guilds data is retrieved\n\n"
            "Everyone who contributes to the \nRavenBlack Wiki and A View in the Dark\n\n"
            "Anders for RBNav and the help along the way\n\n\n\n"
            "Most importantly, thank YOU for using this app. \nWe all hope it serves you well!"
        )

        credits_dialog = QDialog()
        credits_dialog.setWindowTitle('Credits')
        self.setWindowIcon(APP_ICON)
        credits_dialog.setFixedSize(650, 400)

        layout = QVBoxLayout(credits_dialog)
        scroll_area = QScrollArea()
        scroll_area.setStyleSheet("background-color: black; border: none;")
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(scroll_area)

        credits_label = QLabel(credits_text)
        credits_label.setStyleSheet("font-size: 18px; color: white; background-color: black;")
        credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_label.setWordWrap(True)
        scroll_area.setWidget(credits_label)

        credits_label.setGeometry(0, scroll_area.height(), scroll_area.width(), credits_label.sizeHint().height())
        animation = QPropertyAnimation(credits_label, QByteArray(b"geometry"))
        animation.setDuration(35000)
        animation.setStartValue(QRect(0, scroll_area.height(), scroll_area.width(), credits_label.sizeHint().height()))
        animation.setEndValue(
            QRect(0, -credits_label.sizeHint().height(), scroll_area.width(), credits_label.sizeHint().height()))
        animation.setEasingCurve(QEasingCurve.Type.Linear)

        def close_after_delay():
            QTimer.singleShot(2500, credits_dialog.accept)

        animation.finished.connect(close_after_delay)
        animation.start()

        credits_dialog.exec()

    def open_database_viewer(self):
        """
        Open the database viewer to browse and inspect data from the RBC City Map database.
        """
        try:
            # Create a new SQLite database connection every time the viewer is opened
            database_connection = sqlite3.connect(DB_PATH)

            # Show the database viewer, passing the new connection
            self.database_viewer = DatabaseViewer(database_connection)
            self.database_viewer.show()
        except Exception as e:
            logging.error(f"Error opening Database Viewer: {e}")
            QMessageBox.critical(self, "Error", f"Error opening Database Viewer: {e}")

    def open_log_viewer(self):
        self.log_viewer = LogViewer(self, LOG_DIR)  # or pass None if you want it fully standalone
        self.log_viewer.show()

    def fetch_table_data(self, cursor, table_name):
        """
        Fetch data from the specified table and return it as a list of tuples, including column names.

        Args:
            cursor: SQLite cursor object.
            table_name: Name of the table to fetch data from.

        Returns:
            Tuple: (List of column names, List of table data)
        """
        cursor.execute(f"PRAGMA table_info(`{table_name}`)")
        column_names = [col[1] for col in cursor.fetchall()]
        cursor.execute(f"SELECT * FROM `{table_name}`")
        data = cursor.fetchall()
        return column_names, data

    def show_compass_overlay(self):
        if not self.destination:
            QMessageBox.information(self, "No Destination", "Please set a destination first.")
            return

        direct_route, transit_route = self.get_compass_routes()

        if hasattr(self, 'compass_overlay') and self.compass_overlay.isVisible():
            self.compass_overlay.refresh(direct_route, transit_route)
        else:
            self.compass_overlay = CompassOverlay(direct_route, transit_route, self)
            self.compass_overlay.show()

    def get_compass_routes(self):
        def get_arrow_description(start, end):
            dx = end[0] - start[0]
            dy = end[1] - start[1]

            steps_diagonal = min(abs(dx), abs(dy))
            steps_straight = abs(abs(dx) - abs(dy))

            diagonal_arrow = ''
            if dx < 0 and dy < 0:
                diagonal_arrow = '↖'
            elif dx > 0 and dy < 0:
                diagonal_arrow = '↗'
            elif dx < 0 and dy > 0:
                diagonal_arrow = '↙'
            elif dx > 0 and dy > 0:
                diagonal_arrow = '↘'

            straight_arrow = ''
            if abs(dx) > abs(dy):
                straight_arrow = '→' if dx > 0 else '←'
            elif abs(dy) > abs(dx):
                straight_arrow = '↓' if dy > 0 else '↑'

            parts = []
            if steps_diagonal:
                parts.append(f"{steps_diagonal}{diagonal_arrow}")
            if steps_straight:
                parts.append(f"{steps_straight}{straight_arrow}")
            return " + ".join(parts) if parts else "0⦿"

        current_x = self.column_start + self.zoom_level // 2
        current_y = self.row_start + self.zoom_level // 2

        dest_x, dest_y = self.destination

        # ----------------------------
        # Direct Route
        # ----------------------------
        direct_ap = max(abs(dest_x - current_x), abs(dest_y - current_y))
        direct_desc = get_arrow_description((current_x, current_y), (dest_x, dest_y))
        direct_path = [(current_x, current_y), (dest_x, dest_y)]
        direct_route = (direct_ap, direct_desc, direct_path)

        # ----------------------------
        # Transit Route
        # ----------------------------
        nearest_transit_to_character = self.find_nearest_transit(current_x, current_y)
        nearest_transit_to_destination = self.find_nearest_transit(dest_x, dest_y)

        if nearest_transit_to_character and nearest_transit_to_destination:
            char_transit_coords = nearest_transit_to_character[0][1]
            dest_transit_coords = nearest_transit_to_destination[0][1]

            char_to_transit_ap = self.calculate_ap_cost((current_x, current_y), char_transit_coords)
            dest_to_transit_ap = self.calculate_ap_cost((dest_x, dest_y), dest_transit_coords)
            total_ap_transit = char_to_transit_ap + dest_to_transit_ap

            dir1 = get_arrow_description((current_x, current_y), char_transit_coords)
            dir2 = get_arrow_description(dest_transit_coords, (dest_x, dest_y))

            transit_desc = f"{dir1} + Transit + {dir2}"
            transit_path = [(current_x, current_y), char_transit_coords, dest_transit_coords, (dest_x, dest_y)]
            transit_route = (total_ap_transit, transit_desc, transit_path)
        else:
            transit_route = (9999, "Transit route unavailable", [])

        return direct_route, transit_route

    def set_compass_display_from_overlay(self, label, route_info):
        """
        Called when user clicks a route in CompassOverlay.
        Stores and displays the selected route’s full directional breakdown and path.
        """
        self.selected_route_label = label
        ap_cost, direction_desc, path_coords = route_info
        self.selected_route_description = direction_desc
        self.selected_route_path = path_coords
        self.ap_direction_label.setText(f"Compass: {direction_desc}")

        # Close the overlay if you want to force refresh focus
        if hasattr(self, 'compass_overlay'):
            self.compass_overlay.close()

        self.update_minimap()