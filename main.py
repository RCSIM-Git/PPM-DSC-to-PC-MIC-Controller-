"""PPM-SIM Application Entry Point.
Launches the real-time PPM signal decoder & virtual gamepad application with dark theme.
"""

import sys
import os

# Add project root to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.theme import DARK_THEME_QSS


def main():
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName("PPM-SIM")
    app.setOrganizationName("PPM-SIM")

    # Apply modern dark cyber stylesheet
    app.setStyleSheet(DARK_THEME_QSS)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
