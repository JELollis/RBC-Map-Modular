from imports import *
from constants import *

class LogViewer(QDialog):
    """A dialog window to view and optionally send application logs."""

    def __init__(self, parent: QWidget, log_directory: str, color_mappings: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Log Viewer")
        self.setWindowIcon(APP_ICON)
        self.resize(900, 600)

        self.color_mappings = color_mappings or {}
        self.log_directory = LOG_DIR
        self.current_log_lines = []

        # Layouts
        main_layout = QHBoxLayout(self)
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # File List
        self.log_list = QListWidget()
        self.log_list.itemClicked.connect(self.load_log)
        left_layout.addWidget(QLabel("Available Logs"))
        left_layout.addWidget(self.log_list)

        # Populate Log Files
        for file in sorted(os.listdir(log_directory), reverse=True):
            if file.endswith(".log"):
                self.log_list.addItem(file)

        # Log Viewer Text Area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        # Filter checkboxes
        self.levels = {
            "DEBUG": QCheckBox("DEBUG"),
            "INFO": QCheckBox("INFO"),
            "WARNING": QCheckBox("WARNING"),
            "ERROR": QCheckBox("ERROR"),
            "CRITICAL": QCheckBox("CRITICAL")
        }
        for cb in self.levels.values():
            cb.setChecked(True)
            cb.stateChanged.connect(self.apply_filter)

        filter_box = QGroupBox("Log Level Filters")
        filter_layout = QHBoxLayout()
        for cb in self.levels.values():
            filter_layout.addWidget(cb)
        filter_box.setLayout(filter_layout)

        # Buttons
        delete_button = QPushButton("Delete Log")
        delete_button.clicked.connect(self.delete_log)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addWidget(delete_button)
        button_layout.addStretch(1)
        button_layout.addWidget(close_button)

        # Assemble Right Layout
        right_layout.addWidget(QLabel("Log Contents"))
        right_layout.addWidget(self.log_text)
        right_layout.addWidget(filter_box)
        right_layout.addLayout(button_layout)

        # Final Layout
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 5)

        # Apply theme if provided
        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

    def load_log(self, item: QListWidgetItem):
        file_path = os.path.join(self.log_directory, item.text())
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.current_log_lines = f.readlines()
            self.apply_filter()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {e}")

    def apply_filter(self):
        enabled_levels = [level for level, cb in self.levels.items() if cb.isChecked()]
        filtered = [
            line for line in self.current_log_lines
            if any(level in line for level in enabled_levels)
        ]
        self.log_text.setPlainText("".join(filtered))

    def delete_log(self):
        selected_item = self.log_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No File Selected", "Please select a log file first.")
            return

        filename = selected_item.text()
        file_path = os.path.join(self.log_directory, filename)

        confirm = QMessageBox.warning(
            self, "WARNING!",
            "Are you sure you want to delete this log file?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            os.remove(file_path)
            self.log_list.takeItem(self.log_list.currentRow())
            self.log_text.clear()
            self.current_log_lines = []
            # noinspection PyUnresolvedReferences
            QMessageBox.information(self, "Deleted", f"Successfully deleted: {filename}", QMessageBox.Ok)

        except Exception as delete_error:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.truncate(0)
                self.current_log_lines = []
                self.log_text.clear()
                # noinspection PyUnresolvedReferences
                QMessageBox.information(
                    self, "Cleared Instead",
                    f"Could not delete '{filename}' (in use), so its contents were cleared instead.",QMessageBox.Ok
                )
            except Exception as clear_error:
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to delete or clear the log file:\n{delete_error}\n\nAlso failed to clear contents:\n{clear_error}"
                )

    def copy_log_file_to_clipboard(self, file_path: str):
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(file_path)])
        QApplication.clipboard().setMimeData(mime_data)