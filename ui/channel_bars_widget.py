"""Channel Bars Widget for PPM-SIM.
Displays real-time multi-channel pulse widths (µs) and bi-directional percentage meters.
"""

from typing import Dict, List
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class ChannelBar(QFrame):
    """A single channel bar with label, µs readout, percentage, and bi-directional visual bar."""

    def __init__(self, ch_num: int, parent=None):
        super().__init__(parent)
        self.ch_num = ch_num
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            ChannelBar {
                background-color: #161b26;
                border: 1px solid #232d3f;
                border-radius: 6px;
                padding: 4px 8px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(10)

        # CH Number & Name
        info_widget = QWidget()
        info_widget.setFixedWidth(110)
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(1)
        self.lbl_ch = QLabel(f"CH{ch_num}")
        self.lbl_ch.setStyleSheet("font-weight: bold; color: #00f0ff; font-size: 12px;")
        self.lbl_name = QLabel("Unassigned")
        self.lbl_name.setStyleSheet("color: #64748b; font-size: 10px;")
        info_layout.addWidget(self.lbl_ch)
        info_layout.addWidget(self.lbl_name)
        layout.addWidget(info_widget)

        # Pulse width in microseconds
        self.lbl_us = QLabel("1500 µs")
        self.lbl_us.setStyleSheet("font-family: monospace; font-size: 12px; font-weight: bold; color: #ffffff;")
        self.lbl_us.setFixedWidth(65)
        self.lbl_us.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.lbl_us)

        # Progress Bar (0..1000 representing 1000µs to 2000µs)
        self.bar = QProgressBar()
        self.bar.setRange(0, 1000)
        self.bar.setValue(500)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(12)
        self.bar.setStyleSheet("""
            QProgressBar {
                background-color: #0e1117;
                border: 1px solid #232d3f;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0077b6, stop:1 #00f0ff);
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.bar, stretch=1)

        # Percentage readout (-100% to +100%)
        self.lbl_pct = QLabel("  0%")
        self.lbl_pct.setStyleSheet("font-family: monospace; font-size: 11px; color: #38bdf8; font-weight: bold;")
        self.lbl_pct.setFixedWidth(45)
        self.lbl_pct.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.lbl_pct)

    def set_mapping_info(self, label: str):
        self.lbl_name.setText(label)

    def update_value(self, raw_us: float, norm_val: float):
        self.lbl_us.setText(f"{raw_us:.0f} µs")

        # Map 1000..2000µs to 0..1000 progress
        bar_val = int(round(norm_val * 500.0 + 500.0))
        bar_val = max(0, min(1000, bar_val))
        self.bar.setValue(bar_val)

        pct = int(round(norm_val * 100.0))
        sign = "+" if pct > 0 else ""
        self.lbl_pct.setText(f"{sign}{pct}%")


class ChannelBarsWidget(QWidget):
    """Grid container for 8 channel bars."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.bars: List[ChannelBar] = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        for i in range(1, 9):
            bar = ChannelBar(i, self)
            self.bars.append(bar)
            layout.addWidget(bar)

    def set_profile_labels(self, channels_config: Dict[str, any]):
        for i, bar in enumerate(self.bars):
            ch_key = f"CH{i + 1}"
            ch_info = channels_config.get(ch_key, {})
            label = ch_info.get("label", ch_info.get("target", f"Channel {i + 1}"))
            bar.set_mapping_info(label)

    def update_channels(self, channels_us: List[float], channels_norm: List[float]):
        for i in range(min(len(self.bars), len(channels_us))):
            us = channels_us[i]
            norm = channels_norm[i] if i < len(channels_norm) else (us - 1500.0) / 500.0
            self.bars[i].update_value(us, norm)
