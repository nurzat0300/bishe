"""
样式表定义
"""

STYLESHEET = """
QMainWindow {
    background-color: #f5f5f5;
}

QTabWidget::pane {
    border: 1px solid #d0d0d0;
    background-color: white;
}

QTabBar::tab {
    background-color: #e0e0e0;
    color: #333333;
    padding: 8px 20px;
    border: 1px solid #d0d0d0;
    margin-right: 2px;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: white;
    color: #0066cc;
    border: 1px solid #0066cc;
    border-bottom: 2px solid #0066cc;
}

QPushButton {
    background-color: #0066cc;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 15px;
    font-weight: bold;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #0052a3;
}

QPushButton:pressed {
    background-color: #003d7a;
}

QLabel {
    color: #333333;
    font-size: 12px;
}

QLineEdit, QSpinBox, QComboBox {
    padding: 5px;
    border: 1px solid #cccccc;
    border-radius: 3px;
    background-color: white;
    selection-background-color: #0066cc;
    font-size: 11px;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 2px solid #0066cc;
}

QTableWidget {
    gridline-color: #e0e0e0;
    border: 1px solid #d0d0d0;
    background-color: white;
    alternate-background-color: #f9f9f9;
}

QTableWidget::item {
    padding: 4px;
    border-right: 1px solid #e0e0e0;
}

QTableWidget::item:selected {
    background-color: #0066cc;
    color: white;
}

QHeaderView::section {
    background-color: #0066cc;
    color: white;
    padding: 5px;
    border: none;
    font-weight: bold;
}

QTextEdit {
    border: 1px solid #cccccc;
    border-radius: 3px;
    background-color: white;
    padding: 5px;
    font-family: 'Courier New', monospace;
    font-size: 10px;
}

QStatusBar {
    background-color: #f0f0f0;
    color: #333333;
    border-top: 1px solid #d0d0d0;
}

QMessageBox QLabel {
    color: #333333;
}

QMessageBox QPushButton {
    min-width: 60px;
    min-height: 25px;
}

QDialog {
    background-color: #f5f5f5;
}
"""


def apply_stylesheet(app_or_widget):
    """应用样式表"""
    app_or_widget.setStyleSheet(STYLESHEET)
