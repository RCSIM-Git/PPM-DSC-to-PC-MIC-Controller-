"""Modern Dark Theme and Stylesheet for PPM-SIM.
Cyberpunk / Carbon / Neon accents design.
"""

DARK_THEME_QSS = """
/* Global Window & Fonts */
QWidget {
    background-color: #0e1117;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'SF Pro Display', Roboto, 'Helvetica Neue', sans-serif;
    font-size: 13px;
    selection-background-color: #00f0ff;
    selection-color: #000000;
}

/* Group Boxes / Cards */
QGroupBox {
    background-color: #161b26;
    border: 1px solid #232d3f;
    border-radius: 8px;
    margin-top: 24px;
    padding: 14px 10px 10px 10px;
    font-weight: bold;
    font-size: 13px;
    color: #00f0ff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: 4px;
    padding: 2px 8px;
    background-color: #1c2333;
    border: 1px solid #2d3b54;
    border-radius: 4px;
    color: #00f0ff;
}

/* Buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1f293d, stop:1 #161d2b);
    border: 1px solid #2f3e5c;
    border-radius: 6px;
    color: #ffffff;
    padding: 7px 16px;
    font-weight: 600;
    min-height: 20px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2a3752, stop:1 #1e283b);
    border: 1px solid #00f0ff;
    color: #00f0ff;
}

QPushButton:pressed {
    background-color: #00f0ff;
    color: #0e1117;
    border: 1px solid #00f0ff;
}

QPushButton:disabled {
    background-color: #131720;
    border: 1px solid #1c2230;
    color: #4a5568;
}

QPushButton#btn_primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00b4d8, stop:1 #0077b6);
    border: 1px solid #00f0ff;
    color: #ffffff;
    font-weight: bold;
}

QPushButton#btn_primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f0ff, stop:1 #0096c7);
    color: #000000;
}

QPushButton#btn_start {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981);
    border: 1px solid #34d399;
    color: #ffffff;
    font-weight: bold;
    font-size: 14px;
    min-height: 28px;
}

QPushButton#btn_start:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #34d399);
    color: #000000;
}

QPushButton#btn_stop {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #dc2626, stop:1 #ef4444);
    border: 1px solid #f87171;
    color: #ffffff;
    font-weight: bold;
    font-size: 14px;
    min-height: 28px;
}

QPushButton#btn_stop:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #f87171);
    color: #000000;
}

/* ComboBox */
QComboBox {
    background-color: #161b26;
    border: 1px solid #2b384e;
    border-radius: 6px;
    padding: 6px 12px;
    color: #e2e8f0;
    min-height: 20px;
}

QComboBox:hover {
    border: 1px solid #00f0ff;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #2b384e;
}

QComboBox QAbstractItemView {
    background-color: #161b26;
    border: 1px solid #00f0ff;
    selection-background-color: #00f0ff;
    selection-color: #000000;
    color: #e2e8f0;
    outline: 0px;
}

/* Slider */
QSlider::groove:horizontal {
    height: 6px;
    background: #1c2333;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0077b6, stop:1 #00f0ff);
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #00f0ff;
    border: 2px solid #ffffff;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #ffffff;
    border: 2px solid #00f0ff;
}

/* Progress Bars / Meters */
QProgressBar {
    background-color: #121620;
    border: 1px solid #232d3f;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
    font-size: 11px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00b4d8, stop:1 #00f0ff);
    border-radius: 3px;
}

/* Labels */
QLabel {
    color: #94a3b8;
}

QLabel#lbl_title {
    font-size: 18px;
    font-weight: bold;
    color: #00f0ff;
}

QLabel#lbl_badge {
    background-color: #1e2638;
    border: 1px solid #2f3e5c;
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: bold;
    color: #e2e8f0;
}

QLabel#lbl_badge_active {
    background-color: #064e3b;
    border: 1px solid #10b981;
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: bold;
    color: #34d399;
}

QLabel#lbl_badge_inactive {
    background-color: #3f1d24;
    border: 1px solid #ef4444;
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: bold;
    color: #f87171;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #0e1117;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #242c3d;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #00f0ff;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #232d3f;
    background-color: #121620;
    border-radius: 6px;
    top: -1px;
}

QTabBar::tab {
    background-color: #161b26;
    border: 1px solid #232d3f;
    border-bottom: none;
    padding: 8px 18px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 600;
    color: #94a3b8;
}

QTabBar::tab:selected {
    background-color: #121620;
    border-top: 2px solid #00f0ff;
    color: #00f0ff;
}

QTabBar::tab:hover:!selected {
    background-color: #1f2737;
    color: #e2e8f0;
}

/* Status Bar */
QStatusBar {
    background-color: #0b0e14;
    border-top: 1px solid #1a2233;
    color: #64748b;
    font-size: 12px;
}
"""
