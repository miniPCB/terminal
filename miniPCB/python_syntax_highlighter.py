import sys
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import QRegularExpression


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
