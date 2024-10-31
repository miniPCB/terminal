import os
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QPlainTextEdit, QFileDialog
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from miniPCB.python_syntax_highlighter import PythonSyntaxHighlighter


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
