from imports import *
from constants import *
from directories import *
from logging_setup import *
from cookies import *
from database import *
from scraper import *
from character_dialog import *
from theme_customization_dialog import *
from set_destination_dialog import *
from powers_dialog import *
from damage_calculator import *
from shopping_list_tool import *

def check_required_modules(modules):
    """
    Check if all required modules are installed.

    Args:
        modules (list): List of module names as strings.

    Returns:
        bool: True if all modules are installed, False otherwise.
    """
    missing_modules = []
    for module in modules:
        if importlib.util.find_spec(module) is None:
            missing_modules.append(module)

    if missing_modules:
        print("The following modules are missing:")
        for mod in missing_modules:
            print(f"- {mod}")
        print("\nYou can install them with:")
        print(f"pip install {' '.join(missing_modules)}")
        return False
    return True


# Check for required modules
if not check_required_modules(required_modules):
    sys.exit("Missing required modules. Please install them and try again.")


# Call the function to ensure directories are present
ensure_directories_exist()


# Call the logging setup function to initialize logging configuration
setup_logging()


# Call database initialization
initialize_database(DB_PATH)


# -----------------------
# RBC Community Map Main Class
# -----------------------
class RBCCommunityMap(QMainWindow):
    """
    Main application class for the RBC Community Map.
    """

    def __init__(self):
        """
        Initialize the RBCCommunityMap and its components.
        """
        super().__init__()

        self.is_updating_minimap = False

        # Early initialization of the scraper
        self.AVITD_scraper = AVITDScraper()
        self.AVITD_scraper.scrape_guilds_and_shops()

        self.login_needed = True

        # Set up the main window properties
        self.setWindowIcon(QIcon('images/favicon.ico'))
        self.setWindowTitle('RBC Community Map')
        self.setGeometry(100, 100, 1200, 800)

        # Apply saved theme settings
        self.load_theme_settings()
        self.apply_theme()

        # Create a QWebEngineProfile for handling cookies
        self.web_profile = QWebEngineProfile.defaultProfile()

        # Enable persistent cookies and set the storage path
        cookie_storage_path = os.path.join(os.getcwd(), 'sessions')
        os.makedirs(cookie_storage_path, exist_ok=True)
        self.web_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        self.web_profile.setPersistentStoragePath(cookie_storage_path)

        # Set up cookie handling and logging
        self.setup_cookie_handling()

        # Load the data
        self.columns, self.rows, self.banks_coordinates, self.taverns_coordinates, self.transits_coordinates, self.user_buildings_coordinates, self.color_mappings, self.shops_coordinates, self.guilds_coordinates, self.places_of_interest_coordinates = load_data(DB_PATH)

        # Set up the UI components
        self.zoom_level = 3
        self.load_zoom_level_from_database()
        self.minimap_size = 280
        self.column_start = 0
        self.row_start = 0
        self.destination = None
        self.color_mappings = color_mappings

        # Initialize characters list and character_list widget early to avoid attribute errors
        self.characters = []
        self.character_list = QListWidget()
        self.selected_character = None
        self.webview_loaded = False  # To prevent multiple loadFinished events

        # Load characters from previous sessions
        self.load_characters()

        if not self.characters:
                self.firstrun_character_creation()

        self.load_destination()
        self.setup_ui()
        self.setup_console_logging()
        self.show()
        self.update_minimap()
        self.load_last_active_character()

    # -----------------------
    # Load and apply customized UI Theme
    # -----------------------

    def load_theme_settings(self):
        """
        Load the theme settings from the SQLite database (settings table).
        Each theme setting is stored individually under the `settings` table.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Query all theme-related settings
            cursor.execute("SELECT setting_name, setting_value FROM settings WHERE setting_name LIKE 'theme_%'")
            settings = cursor.fetchall()

            # Populate color mappings, setting defaults for missing items
            defaults = {
                "theme_background": "#d4d4d4",
                "theme_text_color": "#000000",
                "theme_button_color": "#b1b1b1",
                "theme_bank": "blue",
                "theme_tavern": "orange",
                "theme_transit": "red",
                "theme_user_building": "purple",
                "theme_shop": "green",
                "theme_guild": "yellow",
                "theme_placesofinterest": "purple",
            }

            self.color_mappings = {key.replace("theme_", ""): QColor(value) for key, value in settings}

            # Add missing default values
            for key, default in defaults.items():
                if key.replace("theme_", "") not in self.color_mappings:
                    self.color_mappings[key.replace("theme_", "")] = QColor(default)

            logging.info("Theme settings loaded successfully.")

        except sqlite3.Error as e:
            logging.error(f"Error loading theme settings: {e}")
            # Apply default theme if the database fails
            self.color_mappings = {
                "background": QColor("#d4d4d4"),
                "text_color": QColor("#000000"),
                "button_color": QColor("#b1b1b1"),
            }
        finally:
            connection.close()

    def save_theme_settings(self):
        """
        Save each theme setting individually to the `settings` table in SQLite.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Ensure the settings table exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    setting_name TEXT PRIMARY KEY,
                    setting_value TEXT
                )
            ''')

            # Save each color mapping individually
            for key, color in self.color_mappings.items():
                cursor.execute('''
                    INSERT INTO settings (setting_name, setting_value)
                    VALUES (?, ?)
                    ON CONFLICT(setting_name) DO UPDATE SET setting_value = excluded.setting_value
                ''', (f"theme_{key}", color.name()))  # QColor to hex string

            connection.commit()
            logging.info("Theme settings saved successfully.")

        except sqlite3.Error as e:
            logging.error(f"Error saving theme settings: {e}")
        finally:
            connection.close()

    def apply_theme(self):
        """
        Apply the current theme settings to the application's stylesheet.
        """
        try:
            # Retrieve individual theme settings
            background_color = self.color_mappings.get("background", QColor("#d4d4d4")).name()
            text_color = self.color_mappings.get("text_color", QColor("#000000")).name()
            button_color = self.color_mappings.get("button_color", QColor("#b1b1b1")).name()

            # Apply styles
            self.setStyleSheet(
                f"""
                QWidget {{
                    background-color: {background_color};
                    color: {text_color};
                }}
                QPushButton {{
                    background-color: {button_color};
                    color: {text_color};
                }}
                QLabel {{
                    color: {text_color};
                }}
                """
            )
            logging.info("Theme applied successfully.")
        except Exception as e:
            logging.error(f"Error applying theme: {e}")

    def change_theme(self):
        """
        Open the theme customization dialog and apply the selected theme.

        This method allows the user to customize the application's theme colors and immediately apply the changes.
        """
        dialog = ThemeCustomizationDialog(self, color_mappings=self.color_mappings)
        if dialog.exec():
            # Update local color mappings and persist changes
            self.color_mappings = dialog.color_mappings
            self.apply_theme()
            self.save_theme_settings()
            logging.info("Theme updated and saved.")

    # -----------------------
    # Cookie Handling
    # -----------------------
    def setup_cookie_handling(self):
        """
        Set up cookie handling, including loading and saving cookies from the 'cookies' table in rbc_map_data.db.
        """
        # No need to initialize the cookies table here as it's done during database initialization
        # Ensure that cookies table exists, it's handled by initialize_database()

        # Connect the QWebEngineProfile's cookie store to the application
        self.cookie_store = self.web_profile.cookieStore()
        self.cookie_store.cookieAdded.connect(self.on_cookie_added)

        # Load previously saved cookies from the database
        self.load_cookies()

    def load_cookies(self):
        """
        Load cookies from the 'cookies' table in rbc_map_data.db and inject them into the QWebEngineProfile.
        """
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.execute("SELECT name, domain, path, value, expiration FROM cookies")
        cookies = cursor.fetchall()

        for name, domain, path, value, expiration in cookies:
            cookie = QNetworkCookie()
            cookie.setName(name.encode())
            cookie.setDomain(domain)
            cookie.setPath(path)
            cookie.setValue(value.encode())
            cookie.setExpirationDate(QDateTime.fromSecsSinceEpoch(expiration))
            self.cookie_store.setCookie(cookie, QUrl(f"https://{domain}"))

        connection.close()
        logging.info("Cookies loaded from rbc_map_data.db.")

    def on_cookie_added(self, cookie):
        """
        Save a newly added cookie to the 'cookies' table in rbc_map_data.db.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Convert expiration date to a timestamp if it’s not a session cookie
            expiration = cookie.expirationDate().toSecsSinceEpoch() if not cookie.isSessionCookie() else None

            cursor.execute(''' 
                INSERT INTO cookies (name, domain, path, value, expiration)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                bytes(cookie.name()).decode('utf-8'),  # Convert QByteArray to string
                cookie.domain(),
                cookie.path(),
                bytes(cookie.value()).decode('utf-8'),  # Convert QByteArray to string
                expiration
            ))

            connection.commit()
            logging.debug(f"Cookie added to rbc_map_data.db: {cookie.name().data().decode('utf-8')}")
        except Exception as e:
            logging.error(f"Failed to add cookie to database: {e}")
        finally:
            connection.close()

    # -----------------------
    # UI Setup
    # -----------------------

    def setup_ui(self):
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
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl'))
        self.website_frame.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.website_frame.loadFinished.connect(self.on_webview_load_finished)

        # Create the browser controls layout at the top of the webview
        self.browser_controls_layout = QHBoxLayout()

        # Load images for back, forward, and refresh buttons
        back_button = QPushButton()
        back_button.setIcon(QIcon('./images/back.png'))
        back_button.setIconSize(QSize(30, 30))
        back_button.setFixedSize(30, 30)
        back_button.setStyleSheet("background-color: transparent; border: none;")
        back_button.clicked.connect(self.website_frame.back)
        self.browser_controls_layout.addWidget(back_button)

        forward_button = QPushButton()
        forward_button.setIcon(QIcon('images/forward.png'))
        forward_button.setIconSize(QSize(30, 30))
        forward_button.setFixedSize(30, 30)
        forward_button.setStyleSheet("background-color: transparent; border: none;")
        forward_button.clicked.connect(self.website_frame.forward)
        self.browser_controls_layout.addWidget(forward_button)

        refresh_button = QPushButton()
        refresh_button.setIcon(QIcon('images/refresh.png'))
        refresh_button.setIconSize(QSize(30, 30))
        refresh_button.setFixedSize(30, 30)
        refresh_button.setStyleSheet("background-color: transparent; border: none;")
        refresh_button.clicked.connect(lambda: self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl')))
        self.browser_controls_layout.addWidget(refresh_button)

        # Set spacing between buttons to make them closer together
        self.browser_controls_layout.setSpacing(5)
        self.browser_controls_layout.addStretch(1)

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

        # Information frame to display closest locations and AP costs
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.Box)
        info_frame.setFixedHeight(260)  # Increased height for better spacing
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)  # Space between each label for clarity
        info_frame.setLayout(info_layout)
        left_layout.addWidget(info_frame)

        # Common style for each info label with padding, border, and smaller font size
        label_style = """
            background-color: {color};
            color: white;
            font-weight: bold;
            padding: 5px;
            border: 2px solid black;
            font-size: 12px;  /* Set smaller font size for readability */
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

        self.combo_columns = QComboBox()
        self.combo_columns.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.combo_columns.addItems(columns.keys())

        self.combo_rows = QComboBox()
        self.combo_rows.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.combo_rows.addItems(rows.keys())

        go_button = QPushButton('Go')
        go_button.setFixedSize(25, 25)
        go_button.clicked.connect(self.go_to_location)

        combo_go_layout.addWidget(self.combo_columns)
        combo_go_layout.addWidget(self.combo_rows)
        combo_go_layout.addWidget(go_button)

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
        set_destination_button.clicked.connect(self.open_set_destination_dialog)
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
                    self.selected_character['id'] = character_id  # Ensure character ID is available for coin extraction
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
        """
        Navigate the web browser back to the previous page.
        """
        self.website_frame.back()

    def go_forward(self):
        """
        Navigate the web browser forward to the next page.
        """
        self.website_frame.forward()

    def refresh_page(self):
        """
        Refresh the current page displayed in the web browser.
        """
        self.website_frame.reload()

    def create_menu_bar(self):
        """
        Create the menu bar with File, Settings, Tools, and Help menus.
        """
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu('File')
        save_webpage_action = QAction('Save Webpage Screenshot', self)
        save_webpage_action.triggered.connect(self.save_webpage_screenshot)
        file_menu.addAction(save_webpage_action)

        save_app_action = QAction('Save App Screenshot', self)
        save_app_action.triggered.connect(self.save_app_screenshot)
        file_menu.addAction(save_app_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Settings menu
        settings_menu = menu_bar.addMenu('Settings')
        theme_action = QAction('Change Theme', self)
        theme_action.triggered.connect(self.change_theme)
        settings_menu.addAction(theme_action)

        zoom_in_action = QAction('Zoom In', self)
        zoom_in_action.triggered.connect(self.zoom_in_browser)
        settings_menu.addAction(zoom_in_action)

        zoom_out_action = QAction('Zoom Out', self)
        zoom_out_action.triggered.connect(self.zoom_out_browser)
        settings_menu.addAction(zoom_out_action)

        # Tools menu
        tools_menu = menu_bar.addMenu('Tools')

        # Database Viewer Tool
        database_viewer_action = QAction('Database Viewer', self)
        database_viewer_action.triggered.connect(self.open_database_viewer)
        tools_menu.addAction(database_viewer_action)

        # Shopping List Tool
        shopping_list_action = QAction('Shopping List Generator', self)
        shopping_list_action.triggered.connect(self.open_shopping_list_tool)
        tools_menu.addAction(shopping_list_action)

        # Damage Calculator Tool
        damage_calculator_action = QAction('Damage Calculator', self)
        damage_calculator_action.triggered.connect(self.open_damage_calculator_tool)
        tools_menu.addAction(damage_calculator_action)

        # Power Reference Tool
        power_reference_action = QAction('Power Reference Tool', self)
        power_reference_action.triggered.connect(self.open_powers_dialog)
        tools_menu.addAction(power_reference_action)

        # Help menu
        help_menu = menu_bar.addMenu('Help')
        faq_action = QAction('FAQ', self)
        faq_action.triggered.connect(lambda: webbrowser.open('https://quiz.ravenblack.net/faq.pl'))
        help_menu.addAction(faq_action)

        how_to_play_action = QAction('How to Play', self)
        how_to_play_action.triggered.connect(lambda: webbrowser.open('https://quiz.ravenblack.net/bloodhowto.html'))
        help_menu.addAction(how_to_play_action)

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        credits_action = QAction('Credits', self)
        credits_action.triggered.connect(self.show_credits_dialog)
        help_menu.addAction(credits_action)

    def zoom_in_browser(self):
        """
        Zoom in on the web page displayed in the QWebEngineView.
        """
        self.website_frame.setZoomFactor(self.website_frame.zoomFactor() + 0.1)

    def zoom_out_browser(self):
        """
        Zoom out on the web page displayed in the QWebEngineView.
        """
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

    def save_webpage_screenshot(self):
        """
        Save the current webpage as a screenshot.

        Opens a file dialog to specify the location and filename for saving
        the screenshot in PNG format.
        """
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Webpage Screenshot", "",
                                                   "PNG Files (*.png);;All Files (*)")
        if file_name:
            self.website_frame.grab().save(file_name)

    def save_app_screenshot(self):
        """
        Save the current application window as a screenshot.

        Opens a file dialog to specify the location and filename for saving
        the screenshot in PNG format.
        """
        file_name, _ = QFileDialog.getSaveFileName(self, "Save App Screenshot", "", "PNG Files (*.png);;All Files (*)")
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
            character_name = current_item.text()  # Extract the selected character's name
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

        QMessageBox.information(self, "Damage Calculator Shopping List", shopping_list_text)

    def open_powers_dialog(self):
        """
        Opens the Powers Information dialog.
        """
        # Initialize the PowersDialog with the SQLite database connection
        powers_dialog = PowersDialog(DB_PATH)  # Pass the SQLite connection

        # Show the PowersDialog as a modal
        powers_dialog.exec()

    # -----------------------
    # Character Management
    # -----------------------

    def load_characters(self):
        """
        Load characters from the SQLite database, including IDs for reference.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Ensure the characters table exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    password TEXT
                )
            ''')

            # Fetch characters from the database including id
            cursor.execute("SELECT id, name, password FROM characters")
            character_data = cursor.fetchall()
            self.characters = [
                {'id': char_id, 'name': name, 'password': password}
                for char_id, name, password in character_data
            ]

            # Populate characters list and UI element
            self.character_list.clear()
            for character in self.characters:
                self.character_list.addItem(QListWidgetItem(character['name']))
            logging.debug("Characters loaded successfully from the database.")

            # Automatically select the first character if any exist
            if self.characters:
                self.character_list.setCurrentRow(0)
                self.selected_character = self.characters[0]
                logging.debug(f"Selected character set: {self.selected_character}")
                if 'id' not in self.selected_character:
                    logging.error("Loaded character data lacks 'id'. Check database integrity.")
            else:
                logging.warning("No characters found in the database.")
                self.selected_character = None

        except sqlite3.Error as e:
            logging.error(f"Failed to load characters from database: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load characters: {e}")
            self.characters = []
            self.selected_character = None
        finally:
            connection.close()

    def save_characters(self):
        """
        Save characters to the SQLite database in plaintext.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Ensure the characters table exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS characters (
                    name TEXT PRIMARY KEY,
                    password TEXT
                )
            ''')

            # Insert or update each character without encrypting the password
            for character in self.characters:
                cursor.execute('''
                    INSERT OR REPLACE INTO characters (name, password) VALUES (?, ?)
                ''', (character['name'], character['password']))

            connection.commit()
            logging.debug("Characters saved successfully to the database in plaintext.")

        except sqlite3.Error as e:
            logging.error(f"Failed to save characters to database: {e}")
        finally:
            connection.close()

    def on_character_selected(self, item):
        """
        Handle character selection from the list.

        Args:
            item (QListWidgetItem): The selected item in the list.

        Logs the selected character, saves the last active character,
        logs out the current character, and then logs in the selected one.
        """
        character_name = item.text()
        selected_character = next((char for char in self.characters if char['name'] == character_name), None)

        if selected_character:
            logging.debug(f"Selected character: {character_name}")
            self.selected_character = selected_character

            # Fetch character ID if missing
            if 'id' not in self.selected_character:
                connection = sqlite3.connect(DB_PATH)
                cursor = connection.cursor()
                try:
                    cursor.execute("SELECT id FROM characters WHERE name = ?", (character_name,))
                    character_row = cursor.fetchone()
                    if character_row:
                        self.selected_character['id'] = character_row[0]
                        logging.debug(f"Character '{character_name}' ID set to {self.selected_character['id']}.")
                    else:
                        logging.error(f"Character '{character_name}' not found in characters table.")
                except sqlite3.Error as e:
                    logging.error(f"Failed to retrieve character_id for '{character_name}': {e}")
                finally:
                    connection.close()

            # Save last active character
            if 'id' in self.selected_character:
                self.save_last_active_character(self.selected_character['id'])
            else:
                logging.error(f"Cannot save last active character: ID missing for '{character_name}'.")

            # Logout current character and login the selected one
            self.logout_current_character()
            QTimer.singleShot(1000, self.login_selected_character)
        else:
            logging.error(f"Character '{character_name}' selection failed.")

    def logout_current_character(self):
        """
        Logout the current character by navigating to the logout URL.
        """
        logging.debug("Logging out current character.")
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl?action=logout'))
        QTimer.singleShot(1000, self.login_selected_character)

    def login_selected_character(self):
        if not self.selected_character:
            logging.warning("No character selected for login.")
            return

        logging.debug(
            f"Logging in character: {self.selected_character['name']} with ID: {self.selected_character.get('id')}")
        name = self.selected_character['name']
        password = self.selected_character['password']
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
        """
        logging.debug("First-run character creation.")
        dialog = CharacterDialog(self)

        if dialog.exec():
            name = dialog.name_edit.text()
            password = dialog.password_edit.text()

            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            try:
                # Insert the new character into the characters table
                cursor.execute('''
                    INSERT INTO characters (name, password) VALUES (?, ?)
                ''', (name, password))
                connection.commit()

                # Retrieve the id of the newly inserted character
                character_id = cursor.lastrowid

                # Insert default coin values for the new character in the coins table
                cursor.execute('''
                    INSERT INTO coins (character_id, pocket, bank) VALUES (?, 0, 0)
                ''', (character_id,))
                connection.commit()

                # Set the new character as the last active character
                self.save_last_active_character(character_id)

                # Update the character list in the UI
                self.characters.append({'name': name, 'password': password})
                self.character_list.addItem(QListWidgetItem(name))

                logging.debug(f"Character '{name}' created with initial coin values and set as last active.")

            except sqlite3.Error as e:
                logging.error(f"Failed to create character '{name}': {e}")
            finally:
                connection.close()

        else:
            sys.exit("No characters added. Exiting the application.")

    def add_new_character(self):
        """
        Add a new character to the list, saving the password in plaintext,
        initializing default coin values in the coins table, and setting this character as the last active.
        """
        logging.debug("Adding a new character.")
        dialog = CharacterDialog(self)

        if dialog.exec():
            name = dialog.name_edit.text()
            password = dialog.password_edit.text()

            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            try:
                # Insert the new character into the characters table
                cursor.execute('''
                    INSERT INTO characters (name, password) VALUES (?, ?)
                ''', (name, password))
                connection.commit()

                # Retrieve the id of the newly inserted character
                character_id = cursor.lastrowid

                # Insert default coin values for the new character in the coins table
                cursor.execute('''
                    INSERT INTO coins (character_id, pocket, bank) VALUES (?, 0, 0)
                ''', (character_id,))
                connection.commit()

                # Set the new character as the last active character
                self.save_last_active_character(character_id)

                # Update the character list in the UI
                self.characters.append({'name': name, 'password': password})
                self.character_list.addItem(QListWidgetItem(name))

                logging.debug(f"Character '{name}' added with initial coin values and set as last active.")

            except sqlite3.Error as e:
                logging.error(f"Failed to add character '{name}': {e}")
            finally:
                connection.close()

    def modify_character(self):
        """
        Modify the selected character's details, saving the new password in plaintext.
        """
        current_item = self.character_list.currentItem()
        if current_item is None:
            logging.warning("No character selected for modification.")
            return

        name = current_item.text()
        character = next((char for char in self.characters if char['name'] == name), None)
        if character:
            logging.debug(f"Modifying character: {name}")
            dialog = CharacterDialog(self, character)
            if dialog.exec():
                character['name'] = dialog.name_edit.text()
                character['password'] = dialog.password_edit.text()
                self.save_characters()
                current_item.setText(character['name'])
                logging.debug(f"Character {name} modified.")

    def delete_character(self):
        """
        Delete the selected character from the list.
        """
        current_item = self.character_list.currentItem()
        if current_item is None:
            logging.warning("No character selected for deletion.")
            return

        name = current_item.text()
        self.characters = [char for char in self.characters if char['name'] != name]
        self.save_characters()
        self.character_list.takeItem(self.character_list.row(current_item))
        logging.debug(f"Character {name} deleted.")

    def save_last_active_character(self, character_id):
        """
        Save the last active character's ID to the last_active_character table.
        Ensures that only one entry exists, replacing any previous entry.
        """
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        try:
            # Use REPLACE INTO to ensure there's only one entry for the last active character
            cursor.execute('''
                REPLACE INTO last_active_character (character_id) VALUES (?)
            ''', (character_id,))

            connection.commit()
            logging.debug(f"Last active character set to character_id: {character_id}")

        except sqlite3.Error as e:
            logging.error(f"Failed to save last active character: {e}")
        finally:
            connection.close()

    def load_last_active_character(self):
        """
        Load the last active character from the database by character_id and set the selected character for auto-login.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Retrieve the last active character's ID from the last_active_character table
            cursor.execute("SELECT character_id FROM last_active_character")
            result = cursor.fetchone()

            if result:
                character_id = result[0]

                # Find the character in self.characters by matching 'id'
                self.selected_character = next((char for char in self.characters if char.get('id') == character_id),
                                               None)

                if self.selected_character:
                    logging.debug(f"Last active character loaded: {self.selected_character['name']}")
                    self.login_needed = True  # Set the flag to indicate login is needed
                    self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl'))  # Load the login page
                else:
                    logging.warning(f"Last active character ID '{character_id}' not found in character list.")

            else:
                logging.warning("No last active character found in the database.")

        except sqlite3.Error as e:
            logging.error(f"Failed to load last active character from database: {e}")
        finally:
            connection.close()

    # -----------------------
    # Web View Handling
    # -----------------------

    def on_webview_load_finished(self, success):
        """
        Handle the event when the webview finishes loading.

        Logs an error and shows a message box if the load fails. If successful, the HTML
        content is processed to extract coordinates and update the minimap.
        """
        if not success:
            logging.error("Failed to load the webpage.")
            QMessageBox.critical(self, "Error",
                                 "Failed to load the webpage. Please check your network connection or try again later.")
        else:
            logging.info("Webpage loaded successfully.")
            # Process the HTML if needed
            self.website_frame.page().toHtml(self.process_html)

            # If login is needed, trigger the login process
            if self.login_needed:
                logging.debug("Logging in last active character.")
                self.login_selected_character()
                self.login_needed = False

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

                # Call recenter_minimap to update the minimap based on character's position
                self.recenter_minimap()

            # Call the method to extract bank coins and pocket changes from the HTML
            self.extract_coins_from_html(html)
            logging.debug("HTML processed successfully for coordinates and coin count.")

        except Exception as e:
            logging.error(f"Unexpected error in process_html: {e}")

        except Exception as e:
            logging.error(f"Unexpected error in process_html: {e}")

    def extract_coordinates_from_html(self, html):
        """
        Extract coordinates from the HTML content.

        Args:
            html (str): HTML content as a string.

        Returns:
            tuple: x and y coordinates.

        Parses the HTML using BeautifulSoup to find the input elements that hold the
        x and y coordinates. Returns these coordinates if found, otherwise returns None.
        """
        soup = BeautifulSoup(html, 'html.parser')
        x_input = soup.find('input', {'name': 'x'})
        y_input = soup.find('input', {'name': 'y'})
        if x_input and y_input:
            x_value = int(x_input['value'])
            y_value = int(y_input['value'])
            logging.debug(f"Extracted coordinates from input fields: x={x_value}, y={y_value}")
            return x_value, y_value

        current_location_td = soup.find('td', {'class': 'street', 'style': 'border: solid 1px white;'})

        if current_location_td:
            form = current_location_td.find('form')
            if form:
                x_value = int(form.find('input', {'name': 'x'})['value'])
                y_value = int(form.find('input', {'name': 'y'})['value'])
                logging.debug(f"Extracted coordinates from form: x={x_value}, y={y_value}")
                return x_value, y_value

        logging.debug("No coordinates found in the HTML content.")
        return None, None

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
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Get the character ID for the selected character
        character_id = self.selected_character['id']

        # Search for the bank balance line (found by "Welcome to Omnibank")
        bank_match = re.search(r"Welcome to Omnibank. Your account has (\d+) coins in it.", html)

        # Search for the pocket balance line (found by "You have \d+ coins")
        pocket_match = re.search(r"You have (\d+) coins", html)

        # Handle bank balance update
        if bank_match:
            bank_coins = int(bank_match.group(1))
            logging.info(f"Bank coins found: {bank_coins}")

            # Update the bank coins in the SQLite database
            cursor.execute('''
                UPDATE coins 
                SET bank = ? 
                WHERE character_id = ?
            ''', (bank_coins, character_id))

        # Handle pocket coin balance update
        if pocket_match:
            pocket_coins = int(pocket_match.group(1))
            logging.info(f"Pocket coins found: {pocket_coins}")

            # Update the pocket coins in the SQLite database
            cursor.execute('''
                UPDATE coins 
                SET pocket = ? 
                WHERE character_id = ?
            ''', (pocket_coins, character_id))

        # Handle deposit action (optional, depending on your needs)
        deposit_match = re.search(r"You deposit (\d+) coins.", html)
        if deposit_match:
            deposit_coins = int(deposit_match.group(1))
            logging.info(f"Deposit found: {deposit_coins} coins")

            # Reduce the pocket coins by the deposited amount
            cursor.execute('''
                UPDATE coins
                SET pocket = pocket - ?
                WHERE character_id = ?
            ''', (deposit_coins, character_id))

        # Handle withdrawal action (optional, depending on your needs)
        withdraw_match = re.search(r"You withdraw (\d+) coins.", html)
        if withdraw_match:
            withdraw_coins = int(withdraw_match.group(1))
            logging.info(f"Withdrawal found: {withdraw_coins} coins")

            # Increase the pocket coins by the withdrawn amount
            cursor.execute('''
                UPDATE coins
                SET pocket = pocket + ?
                WHERE character_id = ?
            ''', (withdraw_coins, character_id))

        # Handle transit coin update (optional, depending on your needs)
        transit_match = re.search(r"It costs 5 coins to ride. You have (\d+).", html)
        if transit_match:
            coins_in_pocket = int(transit_match.group(1))
            logging.info(f"Transit found: Pocket coins updated to {coins_in_pocket}")

            # Explicitly set the pocket coin count after transit
            cursor.execute('''
                UPDATE coins
                SET pocket = ?
                WHERE character_id = ?
            ''', (coins_in_pocket, character_id))

        # Handle other coin-related actions (e.g., hunting, robbing, etc.)
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

        # Handle other coin-related actions (e.g., hunting, robbing, etc.)
        for action, pattern in actions.items():
            match = re.search(pattern, html)
            if match:
                coin_count = int(match.group(1))
                if action == 'getting_robbed':
                    # Losing coins when robbed
                    vamp_name = match.group(2)
                    cursor.execute('''
                        UPDATE coins
                        SET pocket = pocket - ?
                        WHERE character_id = ?
                    ''', (coin_count, character_id))
                    logging.info(f"Lost {coin_count} coins to {vamp_name}.")
                else:
                    # Gaining coins from hunting, robbing, etc.
                    cursor.execute('''
                        UPDATE coins
                        SET pocket = pocket + ?
                        WHERE character_id = ?
                    ''', (coin_count, character_id))
                    logging.info(f"Gained {coin_count} coins from {action}.")
                break  # Exit loop after first match

        connection.commit()
        connection.close()
        logging.info(f"Updated coins for character ID {character_id}.")

    def refresh_webview(self):
        """
        Refresh the webview content.

        Reloads the current page displayed in the QWebEngineView.
        """
        self.website_frame.reload()

    # -----------------------
    # Minimap Drawing and Update
    # -----------------------
    def draw_minimap(self):
        """
        Draws the minimap with various features such as special locations and lines to nearest locations,
        with cell lines and dynamically scaled text size.
        """
        pixmap = QPixmap(self.minimap_size, self.minimap_size)
        painter = QPainter(pixmap)
        painter.fillRect(0, 0, self.minimap_size, self.minimap_size, QColor('lightgrey'))

        block_size = self.minimap_size // self.zoom_level
        font_size = max(8, block_size // 4)  # Dynamically adjust font size, with a minimum of 5
        border_size = 1  # Size of the border around each cell

        # Dynamically adjust font size based on block size
        font = painter.font()
        font.setPointSize(font_size)
        painter.setFont(font)

        # Calculate font metrics for centering text
        font_metrics = QFontMetrics(font)

        logging.debug(f"Drawing minimap with column_start={self.column_start}, row_start={self.row_start}, "
                      f"zoom_level={self.zoom_level}, block_size={block_size}")

        def draw_location(column_index, row_index, color, label_text=None):
            """
            Draws a location on the minimap with dynamic scaling and border.

            Args:
                column_index (int): Column index of the location.
                row_index (int): Row index of the location.
                color (QColor): Color to fill the location.
                label_text (str, optional): Label text to draw at the location. Defaults to None.
            """
            logging.debug(f"Location '{label_text}' Initial column_index={column_index}, row_index={row_index}")
            # Adjust offsets specifically for edge cases
            adjusted_column_index = column_index - 1 if column_index == 1 else column_index
            adjusted_row_index = row_index - 1 if row_index == 1 else row_index

            # Calculate cell position on the minimap grid
            x0 = (adjusted_column_index - self.column_start) * block_size
            y0 = (adjusted_row_index - self.row_start) * block_size

            # Edge cases: Ensure edge locations draw correctly at the map edges
            if column_index == 1:
                adjusted_column_index = column_index
                x0 = (column_index - self.column_start) * block_size
            if row_index == 1:
                adjusted_row_index = row_index
                y0 = (row_index - self.row_start) * block_size

            # Ensure the adjusted location is within bounds
            if x0 < 0 or y0 < 0 or x0 >= self.minimap_size or y0 >= self.minimap_size:
                logging.debug(
                    f"Skipping drawing location '{label_text}' at column_index={column_index}, row_index={row_index}, "
                    f"x0={x0}, y0={y0} (out of bounds)")
                return

            logging.debug(f"Drawing location '{label_text}' at column_index={column_index}, row_index={row_index}, "
                          f"x0={x0}, y0={y0}, color={color.name()}")

            # Draw a smaller rectangle within the cell
            inner_margin = block_size // 4
            painter.fillRect(x0 + inner_margin, y0 + inner_margin,
                             block_size - 2 * inner_margin, block_size - 2 * inner_margin, color)

            if label_text:
                # Calculate bounding box for text centering
                text_rect = font_metrics.boundingRect(label_text)
                # Calculate centered position with boundaries
                text_x = x0 + (block_size - text_rect.width()) // 2
                text_y = y0 + (block_size + text_rect.height()) // 2 - font_metrics.descent()

                # Define QRect for wrapping within cell size, ensuring center alignment with bounds
                wrap_rect = QRect(x0, y0, block_size, block_size)
                painter.setPen(QColor('white'))
                painter.drawText(wrap_rect, Qt.AlignCenter | Qt.TextWordWrap, label_text)

        # Draw the grid
        for i in range(self.zoom_level):
            for j in range(self.zoom_level):
                column_index = self.column_start + j
                row_index = self.row_start + i

                x0, y0 = j * block_size, i * block_size
                logging.debug(f"Drawing grid cell at column_index={column_index}, row_index={row_index}, "
                              f"x0={x0}, y0={y0}")

                # Draw the cell background
                painter.setPen(QColor('white'))
                painter.drawRect(x0, y0, block_size - border_size, block_size - border_size)

                # Special location handling
                column_name = next((name for name, coord in self.columns.items() if coord == column_index), None)
                row_name = next((name for name, coord in self.rows.items() if coord == row_index), None)

                # Draw cell background color
                if column_index <= 0 or column_index >= 201 or row_index <= 0 or row_index >= 201:
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, self.color_mappings["edge"])
                elif (column_index % 2 == 1) or (row_index % 2 == 1):
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, self.color_mappings["alley"])
                else:
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, self.color_mappings["default"])

                # Draw labels only at intersections of named streets
                if column_name and row_name:
                    label_text = f"{column_name} & {row_name}"

                    # Set the font size dynamically, ensuring it does not exceed the maximum
                    max_font_size = 8  # Set to desired maximum font size
                    calculated_font_size = max(4, min(block_size // 3, max_font_size))
                    font = painter.font()
                    font.setPointSize(calculated_font_size)
                    painter.setFont(font)

                    # Define text rectangle and enable word wrapping with center alignment
                    text_rect = QRect(x0, y0, block_size, block_size)
                    painter.setPen(QColor('white'))
                    painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, label_text)

        # Draw special locations (banks with correct offsets)
        for (col_name, row_name, _, _) in self.banks_coordinates:
            column_index = self.columns.get(col_name)
            row_index = self.rows.get(row_name)
            if column_index is not None and row_index is not None:
                # Add +1,+1 offset specifically for banks
                adjusted_column_index = column_index + 1
                adjusted_row_index = row_index + 1
                draw_location(adjusted_column_index, adjusted_row_index, self.color_mappings["bank"], "Bank")
            else:
                logging.warning(f"Skipping bank at {col_name} & {row_name} due to missing coordinates")

        # Draw other locations without the offset
        for name, (column_index, row_index) in self.taverns_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["tavern"], name)

        for name, (column_index, row_index) in self.transits_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["transit"], name)

        for name, (column_index, row_index) in self.user_buildings_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["user_building"], name)

        for name, (column_index, row_index) in self.shops_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["shop"], name)

        for name, (column_index, row_index) in self.guilds_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["guild"], name)

        for name, (column_index, row_index) in self.places_of_interest_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["placesofinterest"], name)
            else:
                logging.warning(f"Skipping place of interest '{name}' due to missing coordinates")

        # Get current location
        current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2

        # Find and draw lines to nearest locations
        nearest_tavern = self.find_nearest_tavern(current_x, current_y)
        nearest_bank = self.find_nearest_bank(current_x, current_y)
        nearest_transit = self.find_nearest_transit(current_x, current_y)

        # Draw nearest tavern line
        if nearest_tavern:
            nearest_tavern_coords = nearest_tavern[0][1]
            painter.setPen(QPen(QColor('orange'), 3))  # Set pen color to orange and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_tavern_coords[0] - self.column_start) * block_size + block_size // 2,
                (nearest_tavern_coords[1] - self.row_start) * block_size + block_size // 2
            )

        # Draw nearest bank line
        if nearest_bank:
            nearest_bank_coords = nearest_bank[0][1]
            painter.setPen(QPen(QColor('blue'), 3))  # Set pen color to blue and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_bank_coords[0] + 1 - self.column_start) * block_size + block_size // 2,
                (nearest_bank_coords[1] + 1 - self.row_start) * block_size + block_size // 2
            )

        # Draw nearest transit line
        if nearest_transit:
            nearest_transit_coords = nearest_transit[0][1]
            painter.setPen(QPen(QColor('red'), 3))  # Set pen color to red and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_transit_coords[0] - self.column_start) * block_size + block_size // 2,
                (nearest_transit_coords[1] - self.row_start) * block_size + block_size // 2
            )

        # Draw destination line
        if self.destination:
            painter.setPen(QPen(QColor('green'), 3))  # Set pen color to green and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (self.destination[0] - self.column_start) * block_size + block_size // 2,
                (self.destination[1] - self.row_start) * block_size + block_size // 2
            )

        painter.end()
        self.minimap_label.setPixmap(pixmap)

    def update_minimap(self):
        """
        Update the minimap.

        Calls draw_minimap and then updates the info frame with any relevant information.
        """
        self.draw_minimap()
        self.update_info_frame()

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
        distances = []
        for loc in locations:
            lx, ly = loc
            dist = max(abs(lx - x), abs(ly - y))  # Using Chebyshev distance
            distances.append((dist, (lx, ly)))
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

    def find_nearest_bank(self, x, y):
        """
        Find the nearest bank to the given coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            list: List of distances and corresponding coordinates.
        """
        valid_banks = []
        for col, row, _, _ in self.banks_coordinates:
            try:
                col_index = self.columns[col]
                row_index = self.rows[row]
            except KeyError:
                logging.warning(
                    f"Bank location with column '{col}' and row '{row}' could not be found in the available columns or rows.")
                continue
            valid_banks.append((col_index, row_index))

        if not valid_banks:
            logging.warning("No valid bank locations found.")
            return None

        return self.find_nearest_location(x, y, valid_banks)

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
        """
        Open the set destination dialog to select a new destination.
        """
        dialog = set_destination_dialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.update_minimap()

    def get_current_destination(self):
        """
        Retrieve the latest destination from the SQLite database.
        """
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("SELECT col, row FROM destinations ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()
        connection.close()
        return (result[0], result[1]) if result else None

    def load_destination(self):
        """
        Load the destination from the SQLite database.

        Loads the last set destination coordinates and updates the minimap if available.
        """
        destination_coords = self.get_current_destination()
        if destination_coords:
            self.destination = destination_coords
            logging.info(f"Loaded destination from database: {self.destination}")
        else:
            self.destination = None
            logging.info("No destination found in database. Starting with no destination.")

    # -----------------------
    # Minimap Controls
    # -----------------------
    def zoom_in(self):
        """
        Zoom in the minimap, ensuring the character stays centered.
        """
        if self.zoom_level > 3:
            self.zoom_level -= 2  # Reduce by 2 to keep zoom levels odd-numbered
            self.save_zoom_level_to_database()  # Save the updated zoom level
            self.website_frame.page().toHtml(self.process_html)

    def zoom_out(self):
        """
        Zoom out the minimap, ensuring the character stays centered.
        """
        if self.zoom_level < 7:  # Adjusted max level to improve readability
            self.zoom_level += 2  # Increase by 2 to keep zoom levels odd-numbered
            self.save_zoom_level_to_database()  # Save the updated zoom level
            self.website_frame.page().toHtml(self.process_html)

    def save_zoom_level_to_database(self):
        """
        Save the current zoom level to the settings table in the database.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            query = """
            INSERT INTO settings (setting_name, setting_value)
            VALUES ('minimap_zoom', ?)
            ON CONFLICT(setting_name) DO UPDATE SET setting_value = ?;
            """
            cursor.execute(query, (self.zoom_level, self.zoom_level))
            connection.commit()
            logging.debug(f"Zoom level saved to database: {self.zoom_level}")
        except sqlite3.Error as e:
            logging.error(f"Failed to save zoom level to database: {e}")
        finally:
            connection.close()

    def load_zoom_level_from_database(self):
        """
        Load the saved zoom level from the settings table in the database.
        If no value is found, set it to the default (3).
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            query = "SELECT setting_value FROM settings WHERE setting_name = 'minimap_zoom';"
            result = cursor.execute(query).fetchone()
            if result:
                self.zoom_level = int(result[0])
                logging.debug(f"Zoom level loaded from database: {self.zoom_level}")
            else:
                self.zoom_level = 3  # Default zoom level
                logging.debug("No saved zoom level found. Defaulting to 3.")
        except sqlite3.Error as e:
            self.zoom_level = 3  # Fallback default zoom level
            logging.error(f"Failed to load zoom level from database: {e}")
        finally:
            connection.close()

    def recenter_minimap(self):
        """
        Recenter the minimap so that the character's location is at the center cell,
        including visible but non-traversable areas beyond the traversable range.
        """
        if not hasattr(self, 'character_x') or not hasattr(self, 'character_y'):
            logging.error("Character position not set. Cannot recenter minimap.")
            return

        # Calculate zoom offset (-1 for 5x5, -2 for 7x7, etc.)
        zoom_offset = (self.zoom_level - 4) // 2

        # Calculate starting positions to center the character
        column_start = self.character_x - zoom_offset
        row_start = self.character_y - zoom_offset

        # Allow visible but non-traversable cells up to 203,203 for 7x7 zoom
        column_start = max(-1, min(column_start, 203 - self.zoom_level))
        row_start = max(-1, min(row_start, 203 - self.zoom_level))

        logging.debug(f"Recentered minimap: character_x={self.character_x}, character_y={self.character_y}, "
                      f"column_start={column_start}, row_start={row_start}, zoom_level={self.zoom_level}")

        # Update minimap start positions
        self.column_start = column_start
        self.row_start = row_start

        # Refresh the minimap
        self.update_minimap()

    def go_to_location(self):
        """
        Go to the selected location.

        Adjusts the minimap's starting column and row based on the selected location from the combo boxes,
        then updates the minimap.
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

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # Map global click position to minimap's local coordinates
            local_position = self.minimap_label.mapFromGlobal(event.globalPosition().toPoint())
            click_x, click_y = local_position.x(), local_position.y()

            # Validate click is within the minimap
            if 0 <= click_x < self.minimap_label.width() and 0 <= click_y < self.minimap_label.height():
                # Calculate relative coordinates and block size
                block_size = self.minimap_size // self.zoom_level
                relative_x = click_x
                relative_y = click_y

                # Determine clicked cell
                clicked_column = self.column_start + (relative_x // block_size)
                clicked_row = self.row_start + (relative_y // block_size)

                # Calculate new center positions
                center_offset = self.zoom_level // 2

                # Allow extended bounds
                min_start = -(self.zoom_level // 2)
                max_start = 201 + (self.zoom_level // 2) - self.zoom_level

                new_column_start = clicked_column - center_offset
                new_row_start = clicked_row - center_offset

                # Clamp to extended valid ranges
                new_column_start = max(min_start, min(new_column_start, max_start))
                new_row_start = max(min_start, min(new_row_start, max_start))

                # Update minimap start positions
                self.column_start = new_column_start
                self.row_start = new_row_start

                # Debug logs
                logging.debug(f"Click at ({click_x}, {click_y}) -> Cell: ({clicked_column}, {clicked_row})")
                logging.debug(f"New minimap start: column={self.column_start}, row={self.row_start}")

                # Update the minimap display
                self.update_minimap()
            else:
                logging.debug(f"Click ({click_x}, {click_y}) is outside the minimap bounds.")

    def open_set_destination_dialog(self):
        """
        Open the set destination dialog.

        Opens a dialog that allows the user to set a destination. If the user confirms the destination,
        it loads the destination and updates the minimap.
        """
        dialog = set_destination_dialog(self)

        # Execute dialog and check for acceptance
        if dialog.exec() == QDialog.Accepted:
            # Load the newly set destination from the database
            self.load_destination()

            # Update the minimap with the new destination
            self.update_minimap()

    def save_to_recent_destinations(self, destination_coords, character_id):
        """
        Save the current destination to the recent destinations for the specific character,
        keeping only the last 10 entries per character.

        Args:
            destination_coords (tuple): Coordinates of the destination to save.
            character_id (int): ID of the character for which to save the destination.
        """
        if destination_coords is None or character_id is None:
            return

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        try:
            # Insert the new destination with character_id
            cursor.execute("INSERT INTO recent_destinations (character_id, col, row) VALUES (?, ?, ?)",
                           (character_id, *destination_coords))

            # Keep only the 10 most recent destinations per character
            cursor.execute("""
                DELETE FROM recent_destinations 
                WHERE character_id = ? AND id NOT IN (
                    SELECT id FROM recent_destinations WHERE character_id = ? ORDER BY timestamp DESC LIMIT 10
                )
            """, (character_id, character_id))

            connection.commit()
            logging.info(
                f"Destination {destination_coords} saved to recent destinations for character ID {character_id}.")
        except sqlite3.Error as e:
            logging.error(f"Failed to save recent destination: {e}")
        finally:
            connection.close()

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
            bank_coords = nearest_bank[0][1]
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
                (name for name, coords in self.places_of_interest_coordinates.items() if coords == destination_coords),
                None
            )
            destination_label_text = f"Set Destination - {place_name}" if place_name else "Set Destination"
            self.destination_label.setText(
                f"{destination_label_text}\n{destination_intersection} - AP: {destination_ap_cost}")

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

                # Update the transit destination label
                self.transit_destination_label.setText(
                    f"Set Destination - {char_transit_name} to {dest_transit_name}\n"
                    f"{self.get_intersection_name(dest_transit_coords)} - Total AP: {total_ap_via_transit}"
                )
            else:
                self.transit_destination_label.setText("Transit Route Info Unavailable")

        else:
            # Clear labels when no destination is set
            self.destination_label.setText("No Destination Set")
            self.transit_destination_label.setText("No Destination Set")

    def get_intersection_name(self, coords):
        """
        Get the intersection name for the given coordinates, including special cases for map edges.

        Args:
            coords (tuple): Coordinates (x, y).

        Returns:
            str: Intersection name.
        """
        x, y = coords

        # Special cases for edges of the map
        if x <= min(self.columns.values()) - 1:
            column_name = "Edge of Map"
        else:
            column_name = next((name for name, coord in self.columns.items() if coord == x - 1), "Edge of Map")

        if y <= min(self.rows.values()) - 1:
            row_name = "Edge of Map"
        else:
            row_name = next((name for name, coord in self.rows.items() if coord == y - 1), "Edge of Map")

        if column_name == "Edge of Map" or row_name == "Edge of Map":
            return "Edge of Map"
        else:
            return f"{column_name} & {row_name}"

    # -----------------------
    # Menu Actions
    # -----------------------

    def open_discord(self):
        """
        Open the RBC Discord invite link in the system's default web browser.
        """
        webbrowser.open('https://discord.gg/nwEa8FaTDS')

    def open_website(self):
        """
        Open the RBC Website in the system's default web browser.
        """
        webbrowser.open('https://lollis-home.ddns.net/viewpage.php?page_id=1')

    def show_about_dialog(self):
        """
        Display an "About" dialog with details about the RBC City Map application.

        The dialog includes information about the application version, its purpose,
        and a brief description of its features.
        """
        QMessageBox.about(self, "About RBC City Map",
                          "RBC City Map Application\n\n"
                          "Version 0.9.0\n\n"
                          "This application allows you to view the city map of RavenBlack City, "
                          "set destinations, and navigate through various locations.\n\n"
                          "Development team shown in credits.\n\n\n"
                          "This program is based on the LIAM\u00B2 app by Leprichaun")

    from PySide6.QtCore import QTimer

    def show_credits_dialog(self):
        """
        Display a "Credits" dialog with a list of contributors to the RBC City Map project.

        The credits are presented in a scrolling animation, acknowledging contributions
        from different individuals for various parts of the project.
        """
        credits_text = (
            "Credits to the team who made this happen:\n\n"
            "Windows: Jonathan Lollis (Nesmuth), Justin Solivan\n\n"
            "Apple OSx Compatibility: Joseph Lemois\n\n"
            "Linux Compatibility: Josh \"Blaskewitts\" Corse, Fern Lovebond\n\n"
            "Design and Layout: Shuvi, Blair Wilson (Ikunnaprinsess)\n\n\n\n"
            "Special Thanks:\n\n"
            "Cain \"Leprechaun\" McBride for the LIAM\u00B2 program \nthat inspired this program\n\n"
            "Cliff Burton for A View in the Dark which is \nwhere Shops and Guilds data is retrieved\n\n"
            "Everyone who contributes to the \nRavenBlack Wiki and A View in the Dark\n\n"
            "Anders for RBNav and the help along the way\n\n\n\n"
            "Most importantly, thank YOU for using this app. \nWe all hope it serves you well!"
        )

        credits_dialog = QDialog()
        credits_dialog.setWindowTitle('Credits')
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

        # Create and start the scrolling animation
        animation = QPropertyAnimation(credits_label, b"geometry")
        animation.setDuration(35000)  # 30 seconds
        animation.setStartValue(QRect(0, scroll_area.height(), scroll_area.width(), credits_label.sizeHint().height()))
        animation.setEndValue(
            QRect(0, -credits_label.sizeHint().height(), scroll_area.width(), credits_label.sizeHint().height()))
        animation.setEasingCurve(QEasingCurve.Type.Linear)

        # Close dialog 5 seconds after the animation finishes
        def close_after_delay():
            QTimer.singleShot(2500, credits_dialog.accept)  # Wait 2.5 seconds before closing

        animation.finished.connect(close_after_delay)
        animation.start()

        credits_dialog.exec()

    # -----------------------
    # Database Viewer
    # -----------------------
    def open_database_viewer(self):
        """
        Open the database viewer to browse and inspect data from the RBC City Map database.

        This method connects to the SQLite database, fetches the data from specified tables,
        and displays it in a new DatabaseViewer window.
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
