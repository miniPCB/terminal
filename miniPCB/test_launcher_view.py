import os
import sys
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QPlainTextEdit, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QColor


class TestLauncherView(QWidget):
    def __init__(self, test_programs_dir):
        super().__init__()
        self.test_programs_dir = test_programs_dir

        # Layout to hold the script list and output pane side by side
        main_layout = QHBoxLayout()

        # Left pane: Script list and buttons
        left_pane = QVBoxLayout()
        self.test_script_list = QListWidget()
        self.test_script_list.setFixedWidth(200)
        self.test_script_list.itemDoubleClicked.connect(self.run_selected_script)
        left_pane.addWidget(self.test_script_list)

        self.clear_output_button = QPushButton("Clear Output")
        self.clear_output_button.clicked.connect(self.clear_output)
        left_pane.addWidget(self.clear_output_button)

        # Right pane: Test output
        self.test_output = QPlainTextEdit()
        self.test_output.setReadOnly(True)
        self.test_output.setFont(QFont("Cascadia Code", 10))
        self.test_output.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4;")

        # Add panes to main layout
        main_layout.addLayout(left_pane)
        main_layout.addWidget(self.test_output)

        self.setLayout(main_layout)
        self.apply_dark_theme()

        # Load scripts
        self.load_test_scripts()

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QListWidget { background-color: #282A36; color: #F8F8F2; }
            QPushButton { background-color: #3A3F4B; color: #F8F8F2; }
            QPushButton::hover { background-color: #44475A; }
        """)

    def load_test_scripts(self):
        self.test_script_list.clear()
        if os.path.exists(self.test_programs_dir):
            for file_name in os.listdir(self.test_programs_dir):
                if file_name.endswith(".py") and file_name not in ['__init__.py','dwfconstants.py', 'Enumerate.py']:
                    self.test_script_list.addItem(file_name)
        else:
            QMessageBox.warning(self, "Directory Not Found", f"{self.test_programs_dir} not found.")

    def run_selected_script(self, item):
        script_path = os.path.join(self.test_programs_dir, item.text())
        self.run_script(script_path)

    def clear_output(self):
        self.test_output.clear()

    def run_script(self, script_path):
        self.test_output.clear()
        self.test_output.appendPlainText(f"Running test: {script_path}\n")
        self.process = QProcess(self)
        self.process.setProgram(sys.executable)
        self.process.setArguments([script_path])
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        self.process.start()

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.test_output.appendPlainText(data)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.test_output.appendPlainText(data)

    def process_finished(self):
        exit_code = self.process.exitCode()
        self.test_output.appendPlainText(f"\nTest finished with exit code: {exit_code}")
