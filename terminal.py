import sys
import os
import subprocess
import json
import shutil
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPlainTextEdit, QAction,
    QTabWidget, QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QMessageBox, QMenu, QLineEdit, QTabWidget, QTextEdit, QVBoxLayout
)
from PyQt5.QtGui import (
    QFont, QTextCharFormat, QSyntaxHighlighter, QColor, QPalette
)
from PyQt5.QtCore import QRegularExpression, Qt, QProcess, QUrl

class PythonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlight_rules = []

        # Define colors for syntax highlighting matching VS Code Dark+ theme
        variable_format = QTextCharFormat()
        variable_format.setForeground(QColor("#9CDCFE"))
        self.highlight_rules.append((QRegularExpression(r'\b[a-z_][a-z0-9_]*(?!\s*\()'), variable_format))

        method_format = QTextCharFormat()
        method_format.setForeground(QColor("#D19A66"))
        self.highlight_rules.append((QRegularExpression(r'\b\w+(?=\()'), method_format))

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#C586C0"))
        keywords = ["def", "class", "if", "in", "else", "elif", "import", "from", "for", "while",
                    "return", "try", "except", "with", "as", "pass", "break", "continue", "yield",
                    "assert", "finally"]
        for keyword in keywords:
            self.highlight_rules.append((QRegularExpression(f"\\b{keyword}\\b"), keyword_format))

        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4EC9B0"))
        self.highlight_rules.append((QRegularExpression(r'\bclass\s+\w+'), class_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlight_rules.append((QRegularExpression("#[^\n]*"), comment_format))

        color_code_format = QTextCharFormat()
        color_code_format.setForeground(QColor("#FFD700"))
        self.highlight_rules.append((QRegularExpression(r"#\b(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})\b"), color_code_format))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlight_rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlight_rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlight_rules.append((QRegularExpression(r'\b[0-9]+(?:\.[0-9]+)?\b'), number_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlight_rules:
            expression = QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

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
        
        # Barcode Input Field with dark mode
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Enter Barcode...")
        self.barcode_input.setStyleSheet("background-color: #3A3F4B; color: #F8F8F2; padding: 6px;")
        left_layout.addWidget(QLabel("Barcode Input:"))
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
        
        # "Available Reports" Label and Report List Pane with dark mode
        left_layout.addWidget(QLabel("Available Reports:"))
        self.report_list = QListWidget()
        self.report_list.setStyleSheet(
            "background-color: #282A36; color: #F8F8F2; padding: 6px; "
            "border: 1px solid #5C5C5C; border-radius: 4px;"  # Add border styling
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

        # Apply dark mode to the overall widget
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
                if file_name.endswith(".py"):
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
        self.process.setProgram("python3")
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


class PythonEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.current_file_paths = {}
        self.is_saved = {}

        # Initialize views
        self.tabs = QTabWidget()  # Text Editor view
        self.init_text_editor()

        self.apply_dark_theme()

    def init_text_editor(self):
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setStyleSheet("background-color: #282A36;")
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.new_file()

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QTabWidget::pane { background-color: #282A36; }
            QTabBar::tab { background: #3A3F4B; color: #F8F8F2; padding: 8px; }
            QTabBar::tab:selected { background: #44475A; }
            QTabBar::tab:hover { background: #50586C; }
            QPlainTextEdit { background-color: #282A36; color: #F8F8F2; }
        """)

    def new_file(self):
        editor = QPlainTextEdit()
        editor.setFont(QFont("Cascadia Code", 12))
        editor.setStyleSheet("background-color: #282A36; color: #F8F8F2;")
        highlighter = PythonSyntaxHighlighter(editor.document())
        self.is_saved[editor] = True

        # Define a safe rehighlighting function to prevent potential recursion
        def rehighlight_safely():
            editor.blockSignals(True)
            highlighter.rehighlight()
            editor.blockSignals(False)

        editor.textChanged.connect(rehighlight_safely)
        editor.textChanged.connect(lambda: self.mark_unsaved(editor))

        tab_index = self.tabs.addTab(editor, "New File")
        self.tabs.setCurrentIndex(tab_index)
        self.current_file_paths[editor] = None

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Python File", "", "Python Files (*.py);;All Files (*)")
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
            editor = QPlainTextEdit()
            editor.setPlainText(content)
            editor.setFont(QFont("Cascadia Code", 12))
            editor.setStyleSheet("background-color: #282A36; color: #F8F8F2;")
            highlighter = PythonSyntaxHighlighter(editor.document())
            self.is_saved[editor] = True

            # Define a safe rehighlighting function to prevent potential recursion
            def rehighlight_safely():
                editor.blockSignals(True)
                highlighter.rehighlight()
                editor.blockSignals(False)

            editor.textChanged.connect(rehighlight_safely)
            editor.textChanged.connect(lambda: self.mark_unsaved(editor))

            tab_index = self.tabs.addTab(editor, os.path.basename(file_path))
            self.tabs.setCurrentIndex(tab_index)
            self.current_file_paths[editor] = file_path

    def mark_unsaved(self, editor):
        if self.is_saved.get(editor, True):
            self.is_saved[editor] = False
            tab_index = self.tabs.indexOf(editor)
            tab_title = self.tabs.tabText(tab_index)
            if not tab_title.startswith("*"):
                self.tabs.setTabText(tab_index, f"*{tab_title}")

    def save_file(self):
        current_widget = self.tabs.currentWidget()
        file_path = self.current_file_paths.get(current_widget)
        if file_path:
            self._save_to_path(file_path, current_widget)
        else:
            self.save_file_as()

    def save_file_as(self):
        current_widget = self.tabs.currentWidget()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", "", "Python Files (*.py);;All Files (*)")
        if file_path:
            self._save_to_path(file_path, current_widget)
            self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(file_path))
            self.current_file_paths[current_widget] = file_path

    def _save_to_path(self, file_path, editor):
        if isinstance(editor, QPlainTextEdit):
            with open(file_path, "w") as file:
                file.write(editor.toPlainText())
            self.is_saved[editor] = True
            tab_index = self.tabs.indexOf(editor)
            tab_title = self.tabs.tabText(tab_index)
            if tab_title.startswith("*"):
                self.tabs.setTabText(tab_index, tab_title[1:])

    def save_and_close(self):
        current_index = self.tabs.currentIndex()
        if current_index != -1:
            current_widget = self.tabs.widget(current_index)
            file_path = self.current_file_paths.get(current_widget)
            if file_path:
                self._save_to_path(file_path, current_widget)
            else:
                self.save_file_as()
            self.close_tab(current_index)

    def close_tab(self, index):
        editor = self.tabs.widget(index)
        if editor in self.current_file_paths:
            del self.current_file_paths[editor]
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.new_file()


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

    def select_and_run_test_script(self):
        pass  # Removed as "Run Test" is no longer part of the File menu

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


def main():
    app = QApplication(sys.argv)
    terminal = MinipcbTerminal()
    terminal.check_for_updates()  # Check for updates before showing the window
    terminal.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
