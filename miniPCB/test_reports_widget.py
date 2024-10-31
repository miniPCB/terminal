import os
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QTabWidget
)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
import json


class TestReportsWidget(QWidget):
    def __init__(self, reports_dir):
        super().__init__()
        self.reports_dir = reports_dir
        self.setup_ui()
        self.load_reports()
    
    def setup_ui(self):
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Left Section (Narrow)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(Qt.AlignTop)
        
        # Barcode Input Label with dark mode styling
        barcode_label = QLabel("Barcode Input:")
        barcode_label.setStyleSheet("color: #F8F8F2; font-weight: bold; padding-bottom: 5px;")
        left_layout.addWidget(barcode_label)

        # Barcode Input Field with dark mode
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Enter Barcode...")
        self.barcode_input.setStyleSheet("background-color: #3A3F4B; color: #F8F8F2; padding: 6px;")
        left_layout.addWidget(self.barcode_input)
        
        # Connect barcode input to update_report_list
        self.barcode_input.textChanged.connect(self.update_report_list)
        
        # Load Report Button with dark mode
        self.load_button = QPushButton("Load Report")
        self.load_button.setStyleSheet(
            "background-color: #3A3F4B; color: #F8F8F2; padding: 6px;"
            "border: 1px solid #5C5C5C; border-radius: 4px;"
        )
        self.load_button.clicked.connect(self.load_report)
        left_layout.addWidget(self.load_button)
        
        # Available Reports Label with dark mode styling
        reports_label = QLabel("Available Reports:")
        reports_label.setStyleSheet("color: #F8F8F2; font-weight: bold; padding-top: 10px; padding-bottom: 5px;")
        left_layout.addWidget(reports_label)

        # Report List Pane with dark mode
        self.report_list = QListWidget()
        self.report_list.setStyleSheet(
            "background-color: #282A36; color: #F8F8F2; padding: 6px; "
            "border: 1px solid #5C5C5C; border-radius: 4px;"
        )
        self.report_list.itemDoubleClicked.connect(self.display_selected_report)
        left_layout.addWidget(self.report_list)
        
        # Set fixed width for the left section
        left_widget.setFixedWidth(300)
        
        # Right Section (Wide) with Tab Widget
        self.right_tab_widget = QTabWidget()
        self.right_tab_widget.setStyleSheet(
            "QTabWidget::pane { border: 1px solid #44475A; }"
            "QTabBar::tab { background: #3A3F4B; color: #F8F8F2; padding: 8px; }"
            "QTabBar::tab:selected { background: #44475A; }"
            "QTabBar::tab:hover { background: #50586C; }"
        )

        # Test Reports Tab
        self.test_reports_display = QTextEdit()
        self.test_reports_display.setReadOnly(True)
        self.test_reports_display.setFont(QFont("Courier New", 10))
        self.test_reports_display.setStyleSheet("background-color: #282A36; color: #F8F8F2;")
        self.right_tab_widget.addTab(self.test_reports_display, "Test Reports")

        # Process Messages Tab
        self.process_messages_display = QTextEdit()
        self.process_messages_display.setReadOnly(True)
        self.process_messages_display.setFont(QFont("Courier New", 10))
        self.process_messages_display.setStyleSheet("background-color: #282A36; color: #F8F8F2;")
        self.right_tab_widget.addTab(self.process_messages_display, "Process Messages")

        # Red Tag Messages Tab
        self.red_tag_messages_display = QTextEdit()
        self.red_tag_messages_display.setReadOnly(True)
        self.red_tag_messages_display.setFont(QFont("Courier New", 10))
        self.red_tag_messages_display.setStyleSheet("background-color: #282A36; color: #F8F8F2;")
        self.right_tab_widget.addTab(self.red_tag_messages_display, "Red Tag Messages")

        # Images Tab
        self.images_display = QTextEdit()
        self.images_display.setReadOnly(True)
        self.images_display.setFont(QFont("Courier New", 10))
        self.images_display.setStyleSheet("background-color: #282A36; color: #F8F8F2;")
        self.right_tab_widget.addTab(self.images_display, "Images")
        
        # Add left and right sections to the main layout
        main_layout.addWidget(left_widget)
        main_layout.addWidget(self.right_tab_widget)
        
        # Apply dark mode palette
        self.set_dark_palette()

    def set_dark_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#282A36"))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor("#282A36"))
        palette.setColor(QPalette.AlternateBase, QColor("#3A3F4B"))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, QColor("#F8F8F2"))
        palette.setColor(QPalette.Button, QColor("#3A3F4B"))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor("#44475A"))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)

    def load_reports(self):
        """Load available reports into the report list."""
        if os.path.exists(self.reports_dir):
            reports = [f for f in os.listdir(self.reports_dir) if f.endswith('.json')]
            if reports:
                self.report_list.addItems(reports)
            else:
                self.display_placeholder("No reports available.")
        else:
            self.display_placeholder("Reports directory not found.")

    def update_report_list(self):
        """Filter reports based on barcode input."""
        barcode_text = self.barcode_input.text().lower()
        self.report_list.clear()
        if os.path.exists(self.reports_dir):
            reports = [f for f in os.listdir(self.reports_dir) if barcode_text in f.lower()]
            if reports:
                self.report_list.addItems(reports)
            else:
                self.display_placeholder("No matching reports.")
        else:
            self.display_placeholder("Reports directory not found.")

    def load_report(self):
        """Load and display the report based on the selected barcode."""
        selected_item = self.report_list.currentItem()
        if selected_item:
            report_name = selected_item.text()
            report_path = os.path.join(self.reports_dir, report_name)
            self.display_report_content(report_path)

    def display_selected_report(self, item):
        """Display the content of the report selected from the list."""
        report_path = os.path.join(self.reports_dir, item.text())
        self.display_report_content(report_path)

    def display_report_content(self, report_path):
        """Display the content of the specified report in the Test Reports tab."""
        try:
            with open(report_path, 'r') as file:
                report_content = file.read()
            # Display in the Test Reports tab
            self.test_reports_display.setPlainText(report_content)
            # Placeholder for other tabs
            self.process_messages_display.setPlainText("Process messages for this report.")
            self.red_tag_messages_display.setPlainText("Red tag messages for this report.")
            self.images_display.setPlainText("Images associated with this report.")
        except Exception as e:
            print(f"Error loading report: {e}")
            self.test_reports_display.setPlainText(f"Error loading report: {e}")

    def display_placeholder(self, text):
        """Display placeholder text when no reports are available or matching."""
        placeholder_item = QListWidgetItem(text)
        placeholder_item.setFlags(placeholder_item.flags() & ~Qt.ItemIsSelectable)
        self.report_list.addItem(placeholder_item)
