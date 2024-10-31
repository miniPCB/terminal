import sys
import os
import subprocess
from PyQt5.QtWidgets import QMainWindow, QSplitter, QAction, QMenu, QMessageBox
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
from miniPCB.python_editor import PythonEditor
from miniPCB.test_launcher_view import TestLauncherView
from miniPCB.test_reports_widget import TestReportsWidget


class MinipcbTerminal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("miniPCB Terminal")
        self.setGeometry(300, 300, 800, 600)
        self.test_programs_dir = "test_programs"

        # Initialize main components
        self.editor = PythonEditor()
        self.test_launcher = TestLauncherView(self.test_programs_dir)
        self.reports_dir = "reports"
        self.test_reports = TestReportsWidget(self.reports_dir)

        # Set up main layout with splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        self.apply_dark_theme()
        self.create_menu()

        # Show the editor by default
        self.show_text_editor()

    def apply_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor("#282A36"))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor("#282A36"))
        dark_palette.setColor(QPalette.AlternateBase, QColor("#3A3F4B"))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, QColor("#F8F8F2"))
        dark_palette.setColor(QPalette.Button, QColor("#282A36"))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.Highlight, QColor("#44475A"))
        dark_palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(dark_palette)

        self.setStyleSheet("""
            QMenuBar { background-color: #3A3F4B; color: #F8F8F2; }
            QMenuBar::item:selected { background: #44475A; }
            QMenu { background-color: #3A3F4B; color: #F8F8F2; }
            QMenu::item:selected { background-color: #44475A; color: #FFFFFF; }
        """)

    def create_menu(self):
        menu_bar = self.menuBar()

        # View Menu
        self.view_menu = QMenu("View", self)
        self.view_menu_action = menu_bar.addMenu(self.view_menu)

        view_text_editor_action = QAction("Text Editor", self)
        view_text_editor_action.triggered.connect(self.show_text_editor)
        self.view_menu.addAction(view_text_editor_action)

        view_test_launcher_action = QAction("Test Launcher", self)
        view_test_launcher_action.triggered.connect(self.show_test_launcher)
        self.view_menu.addAction(view_test_launcher_action)

        view_test_reports_action = QAction("Test Reports", self)
        view_test_reports_action.triggered.connect(self.show_test_reports)
        self.view_menu.addAction(view_test_reports_action)

        # File Menu (Create but do not add yet)
        self.file_menu = QMenu("File", self)

        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.editor.new_file)
        self.file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.editor.open_file)
        self.file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.editor.save_file)
        self.file_menu.addAction(save_action)

        save_close_action = QAction("Save and Close", self)
        save_close_action.triggered.connect(self.editor.save_and_close)
        self.file_menu.addAction(save_close_action)

        # Add the File menu after the View menu if in Text Editor
        if isinstance(self.splitter.widget(0), PythonEditor):
            self.add_file_menu()

    def add_file_menu(self):
        # Add the File menu after the View menu
        menu_bar = self.menuBar()
        actions = menu_bar.actions()
        # Find the index of the View menu
        view_menu_index = actions.index(self.view_menu.menuAction())
        # Check if View menu is the last menu
        if view_menu_index + 1 < len(actions):
            # Insert the File menu before the action that comes after the View menu
            menu_bar.insertMenu(actions[view_menu_index + 1], self.file_menu)
        else:
            # View menu is the last menu; add File menu at the end
            menu_bar.addMenu(self.file_menu)

    def remove_file_menu(self):
        # Remove the File menu if it's present
        menu_bar = self.menuBar()
        if self.file_menu.menuAction() in menu_bar.actions():
            menu_bar.removeAction(self.file_menu.menuAction())

    def clear_splitter(self):
        while self.splitter.count():
            widget = self.splitter.widget(0)
            widget.setParent(None)

    def show_text_editor(self):
        self.clear_splitter()
        self.splitter.addWidget(self.editor)
        self.remove_file_menu()  # Ensure no duplicate File menu
        self.add_file_menu()

    def show_test_launcher(self):
        self.clear_splitter()
        self.splitter.addWidget(self.test_launcher)
        self.remove_file_menu()

    def show_test_reports(self):
        self.clear_splitter()
        self.splitter.addWidget(self.test_reports)
        self.remove_file_menu()

    def check_for_updates(self):
        # Path to the local repository (assuming it's the current working directory)
        repo_path = os.getcwd()

        # Fetch updates from the remote repository
        fetch_process = subprocess.run(['git', 'fetch'], cwd=repo_path, capture_output=True, text=True)

        if fetch_process.returncode != 0:
            QMessageBox.warning(self, "Update Error", f"Git fetch failed:\n{fetch_process.stderr}")
            return

        # Check if local repository is behind the remote
        status_process = subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD..origin/main'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )

        if status_process.returncode != 0:
            QMessageBox.warning(self, "Update Error", f"Git status failed:\n{status_process.stderr}")
            return

        behind_count = int(status_process.stdout.strip())

        if behind_count > 0:
            # Pull updates
            pull_process = subprocess.run(['git', 'pull'], cwd=repo_path, capture_output=True, text=True)

            if pull_process.returncode != 0:
                QMessageBox.warning(self, "Update Error", f"Git pull failed:\n{pull_process.stderr}")
                return

            # Prompt the user to restart the application
            reply = QMessageBox.question(
                self,
                "Updates Applied",
                "Updates have been applied. The application needs to restart. Restart now?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.restart_application()
        else:
            # No updates found
            pass  # You can display a message if desired

    def restart_application(self):
        # Get the executable and arguments
        python = sys.executable
        os.execl(python, python, *sys.argv)
