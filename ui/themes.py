"""
Strict Monochrome (Black & White) Industrial Styling for BMS Telemetry Dashboard
Clean, minimal, high-contrast, zero AI-slop, no stickers/emojis.
"""

BLACK_WHITE_THEME = """
QWidget {
    background-color: #000000;
    color: #ffffff;
    font-family: 'Segoe UI Variable', 'Segoe UI', -apple-system, Roboto, sans-serif;
    font-size: 12px;
}

/* Card Containers */
QFrame#card {
    background-color: #0c0c0c;
    border: 1px solid #242424;
    border-radius: 6px;
}

QFrame#cardAlt {
    background-color: #121212;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
}

QFrame#kpiCard {
    background-color: #0c0c0c;
    border: 1px solid #242424;
    border-radius: 6px;
}

/* Push Buttons */
QPushButton {
    background-color: #121212;
    color: #ffffff;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 11px;
}

QPushButton:hover {
    background-color: #1c1c1c;
    border-color: #666666;
}

QPushButton:pressed {
    background-color: #ffffff;
    color: #000000;
    border-color: #ffffff;
}

/* Primary Action Button (Solid White) */
QPushButton#primaryBtn {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #ffffff;
    border-radius: 4px;
    font-weight: 700;
    font-size: 11px;
}

QPushButton#primaryBtn:hover {
    background-color: #e5e5e5;
    border-color: #e5e5e5;
}

QPushButton#primaryBtn:pressed {
    background-color: #cccccc;
    border-color: #cccccc;
}

/* Input Fields & Combos */
QLineEdit, QComboBox {
    background-color: #121212;
    color: #ffffff;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 24px;
    font-size: 11px;
}

QComboBox:editable QLineEdit {
    background-color: transparent;
    color: #ffffff;
    border: none;
    padding: 0px;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #ffffff;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #242424;
}

QComboBox QAbstractItemView {
    background-color: #0c0c0c;
    color: #ffffff;
    border: 1px solid #333333;
    selection-background-color: #242424;
    selection-color: #ffffff;
    outline: none;
    border-radius: 4px;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #000000;
    width: 6px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #333333;
    min-height: 20px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #555555;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Terminal Log Console */
QTextEdit#terminalConsole {
    background-color: #050505;
    color: #e5e5e5;
    border: 1px solid #242424;
    border-radius: 4px;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 11px;
    padding: 8px;
}

/* Monochrome Badges & Labels */
QLabel#badgeNormal {
    background-color: #121212;
    color: #ffffff;
    border: 1px solid #383838;
    border-radius: 3px;
    padding: 2px 6px;
    font-weight: 700;
    font-size: 9px;
    letter-spacing: 0.5px;
}

QLabel#badgeHighlight {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #ffffff;
    border-radius: 3px;
    padding: 2px 6px;
    font-weight: 700;
    font-size: 9px;
    letter-spacing: 0.5px;
}

QLabel#badgeWarning {
    background-color: #1a1a1a;
    color: #ffffff;
    border: 1px dashed #ffffff;
    border-radius: 3px;
    padding: 2px 6px;
    font-weight: 700;
    font-size: 9px;
    letter-spacing: 0.5px;
}

QLabel#sectionTitle {
    color: #888888;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.8px;
}

QProgressBar {
    background-color: #1c1c1c;
    border-radius: 2px;
    border: none;
    max-height: 4px;
}
QProgressBar::chunk {
    background-color: #ffffff;
    border-radius: 2px;
}
"""

WHITE_BLACK_THEME = """
QWidget {
    background-color: #f7f7f7;
    color: #000000;
    font-family: 'Segoe UI Variable', 'Segoe UI', -apple-system, Roboto, sans-serif;
    font-size: 12px;
}

/* Card Containers */
QFrame#card {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
}

QFrame#cardAlt {
    background-color: #f2f2f2;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
}

QFrame#kpiCard {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
}

/* Push Buttons */
QPushButton {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 11px;
}

QPushButton:hover {
    background-color: #f0f0f0;
    border-color: #999999;
}

QPushButton:pressed {
    background-color: #000000;
    color: #ffffff;
    border-color: #000000;
}

/* Primary Action Button (Solid Black) */
QPushButton#primaryBtn {
    background-color: #000000;
    color: #ffffff;
    border: 1px solid #000000;
    border-radius: 4px;
    font-weight: 700;
    font-size: 11px;
}

QPushButton#primaryBtn:hover {
    background-color: #262626;
    border-color: #262626;
}

QPushButton#primaryBtn:pressed {
    background-color: #404040;
    border-color: #404040;
}

/* Input Fields & Combos */
QLineEdit, QComboBox {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 24px;
    font-size: 11px;
}

QComboBox:editable QLineEdit {
    background-color: transparent;
    color: #000000;
    border: none;
    padding: 0px;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #000000;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #e0e0e0;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #cccccc;
    selection-background-color: #e5e5e5;
    selection-color: #000000;
    outline: none;
    border-radius: 4px;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #f7f7f7;
    width: 6px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #cccccc;
    min-height: 20px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #999999;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Terminal Log Console */
QTextEdit#terminalConsole {
    background-color: #1a1a1a;
    color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 4px;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 11px;
    padding: 8px;
}

/* Monochrome Badges & Labels */
QLabel#badgeNormal {
    background-color: #f2f2f2;
    color: #000000;
    border: 1px solid #cccccc;
    border-radius: 3px;
    padding: 2px 6px;
    font-weight: 700;
    font-size: 9px;
    letter-spacing: 0.5px;
}

QLabel#badgeHighlight {
    background-color: #000000;
    color: #ffffff;
    border: 1px solid #000000;
    border-radius: 3px;
    padding: 2px 6px;
    font-weight: 700;
    font-size: 9px;
    letter-spacing: 0.5px;
}

QLabel#badgeWarning {
    background-color: #ffffff;
    color: #000000;
    border: 1px dashed #000000;
    border-radius: 3px;
    padding: 2px 6px;
    font-weight: 700;
    font-size: 9px;
    letter-spacing: 0.5px;
}

QLabel#sectionTitle {
    color: #666666;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.8px;
}

QProgressBar {
    background-color: #e5e5e5;
    border-radius: 2px;
    border: none;
    max-height: 4px;
}
QProgressBar::chunk {
    background-color: #000000;
    border-radius: 2px;
}
"""
