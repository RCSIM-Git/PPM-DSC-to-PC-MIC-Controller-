"""Real-time Oscilloscope Widget for PPM Audio Signal Visualization."""

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class OscilloscopeWidget(QWidget):
    """Oscilloscope displaying the raw PPM audio signal and edge thresholds."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paused = False

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Header bar with info & controls
        header = QHBoxLayout()
        header.setSpacing(8)

        self.lbl_title = QLabel("SIGNAL OSCILLOSCOPE")
        self.lbl_title.setStyleSheet("font-weight: bold; color: #00f0ff; font-size: 11px; letter-spacing: 1px;")
        header.addWidget(self.lbl_title)

        header.addStretch()

        # Polarity badge
        self.lbl_polarity = QLabel("POLARITY: AUTO")
        self.lbl_polarity.setStyleSheet("background-color: #1a2233; color: #38bdf8; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold;")
        header.addWidget(self.lbl_polarity)

        # Level dB meter
        self.lbl_db = QLabel("MIC: -60 dB")
        self.lbl_db.setStyleSheet("color: #94a3b8; font-size: 11px; font-family: monospace;")
        header.addWidget(self.lbl_db)

        self.pb_level = QProgressBar()
        self.pb_level.setRange(-60, 0)
        self.pb_level.setValue(-60)
        self.pb_level.setTextVisible(False)
        self.pb_level.setFixedSize(60, 10)
        self.pb_level.setStyleSheet("""
            QProgressBar { background-color: #161d2b; border: 1px solid #28354d; border-radius: 2px; }
            QProgressBar::chunk { background-color: #10b981; }
        """)
        header.addWidget(self.pb_level)

        # Pause / Run button
        self.btn_pause = QPushButton("Freeze")
        self.btn_pause.setFixedHeight(22)
        self.btn_pause.setStyleSheet("padding: 2px 8px; font-size: 11px;")
        self.btn_pause.clicked.connect(self.toggle_pause)
        header.addWidget(self.btn_pause)

        layout.addLayout(header)

        # PyQtGraph Plot Widget
        pg.setConfigOptions(antialias=True)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("#0e1117")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.15)
        self.plot_widget.setYRange(-1.05, 1.05, padding=0)
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.hideAxis("bottom")
        self.plot_widget.hideAxis("left")

        # Zero reference line
        zero_line = pg.InfiniteLine(pos=0.0, angle=0, pen=pg.mkPen(color="#1f293d", width=1, style=Qt.DashLine))
        self.plot_widget.addItem(zero_line)

        # Threshold lines (High & Low)
        self.line_high = pg.InfiniteLine(pos=0.2, angle=0, pen=pg.mkPen(color="#ffb700", width=1, style=Qt.DotLine))
        self.line_low = pg.InfiniteLine(pos=-0.2, angle=0, pen=pg.mkPen(color="#ff8800", width=1, style=Qt.DotLine))
        self.plot_widget.addItem(self.line_high)
        self.plot_widget.addItem(self.line_low)

        # Signal curve
        pen_signal = pg.mkPen(color="#00f0ff", width=1.5)
        self.curve = self.plot_widget.plot(pen=pen_signal)

        layout.addWidget(self.plot_widget)

    def toggle_pause(self):
        self.paused = not self.paused
        self.btn_pause.setText("Resume" if self.paused else "Freeze")
        self.btn_pause.setStyleSheet(
            "padding: 2px 8px; font-size: 11px; background-color: #ffb700; color: #000000; font-weight: bold;"
            if self.paused
            else "padding: 2px 8px; font-size: 11px;"
        )

    def update_plot(self, waveform: np.ndarray, high_thresh: float, low_thresh: float, polarity: str, peak_db: float):
        if self.paused:
            return

        if waveform is not None and len(waveform) > 0:
            self.curve.setData(waveform)

        self.line_high.setPos(high_thresh)
        self.line_low.setPos(low_thresh)

        # Update badge & level
        self.lbl_polarity.setText(f"POLARITY: {polarity.upper()}")
        self.lbl_db.setText(f"MIC: {peak_db:.0f} dB")
        self.pb_level.setValue(int(peak_db))

        # Color the mic bar if clipping or good
        if peak_db > -3.0:
            self.pb_level.setStyleSheet("""
                QProgressBar { background-color: #161d2b; border: 1px solid #28354d; border-radius: 2px; }
                QProgressBar::chunk { background-color: #ef4444; }
            """)
        elif peak_db > -18.0:
            self.pb_level.setStyleSheet("""
                QProgressBar { background-color: #161d2b; border: 1px solid #28354d; border-radius: 2px; }
                QProgressBar::chunk { background-color: #10b981; }
            """)
        else:
            self.pb_level.setStyleSheet("""
                QProgressBar { background-color: #161d2b; border: 1px solid #28354d; border-radius: 2px; }
                QProgressBar::chunk { background-color: #3b82f6; }
            """)
