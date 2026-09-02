"""Calibration Wizard and Settings Dialog for PPM-SIM."""

from typing import Any, Dict, List
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class CalibrationDialog(QDialog):
    """Step-by-step wizard and fine-tuning dialog for radio stick/switch calibration."""

    def __init__(self, config_manager, controller_mapper, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.controller_mapper = controller_mapper
        self.setWindowTitle("Stick & Channel Calibration Wizard")
        self.resize(680, 520)

        self.current_channels: List[float] = [1500.0] * 8
        self.captured_mins: List[float] = [1500.0] * 8
        self.captured_centers: List[float] = [1500.0] * 8
        self.captured_maxs: List[float] = [1500.0] * 8
        self.is_recording_ranges = False

        self.init_ui()
        self.load_calibration_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        self.tabs = QTabWidget()

        # Tab 1: Wizard
        tab_wizard = QWidget()
        wiz_layout = QVBoxLayout(tab_wizard)
        wiz_layout.setSpacing(14)

        # Step 1 Box
        grp_step1 = QGroupBox("Step 1: Center All Controls")
        s1_layout = QVBoxLayout(grp_step1)
        lbl_s1_desc = QLabel(
            "1. Release all sticks, steering wheel, and throttle trigger so they are in their natural resting (center) position.\n"
            "2. Put 3-position switches in middle position.\n"
            "3. Click 'Capture Center Positions'."
        )
        lbl_s1_desc.setWordWrap(True)
        s1_layout.addWidget(lbl_s1_desc)

        h1 = QHBoxLayout()
        self.btn_capture_center = QPushButton("Capture Center Positions")
        self.btn_capture_center.setObjectName("btn_primary")
        self.btn_capture_center.clicked.connect(self.on_capture_centers)
        h1.addWidget(self.btn_capture_center)
        self.lbl_s1_status = QLabel("Ready")
        self.lbl_s1_status.setStyleSheet("color: #38bdf8; font-weight: bold;")
        h1.addWidget(self.lbl_s1_status)
        h1.addStretch()
        s1_layout.addLayout(h1)
        wiz_layout.addWidget(grp_step1)

        # Step 2 Box
        grp_step2 = QGroupBox("Step 2: Calibrate Full Travel Ranges")
        s2_layout = QVBoxLayout(grp_step2)
        lbl_s2_desc = QLabel(
            "1. Click 'Start Range Recording'.\n"
            "2. Move steering wheel/sticks fully in all directions (left, right, top, bottom).\n"
            "3. Pull throttle trigger fully (Gas) and push fully (Brake/Reverse).\n"
            "4. Toggle all switches to their extreme positions.\n"
            "5. Click 'Stop Range Recording'."
        )
        lbl_s2_desc.setWordWrap(True)
        s2_layout.addWidget(lbl_s2_desc)

        h2 = QHBoxLayout()
        self.btn_toggle_recording = QPushButton("Start Range Recording")
        self.btn_toggle_recording.clicked.connect(self.on_toggle_recording)
        h2.addWidget(self.btn_toggle_recording)
        self.lbl_s2_status = QLabel("Idle")
        self.lbl_s2_status.setStyleSheet("color: #64748b; font-weight: bold;")
        h2.addWidget(self.lbl_s2_status)
        h2.addStretch()
        s2_layout.addLayout(h2)
        wiz_layout.addWidget(grp_step2)

        wiz_layout.addStretch()
        self.tabs.addTab(tab_wizard, "Quick Calibration Wizard")

        # Tab 2: Manual Fine Tuning Table
        tab_manual = QWidget()
        man_layout = QVBoxLayout(tab_manual)

        self.table = QTableWidget(8, 6)
        self.table.setHorizontalHeaderLabels(["Channel", "Min (µs)", "Center (µs)", "Max (µs)", "Invert", "Deadband %"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        man_layout.addWidget(self.table)

        self.tabs.addTab(tab_manual, "Manual Channel Tuning")
        main_layout.addWidget(self.tabs)

        # Bottom buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        self.btn_save = QPushButton("Save Calibration")
        self.btn_save.setObjectName("btn_primary")
        self.btn_save.clicked.connect(self.on_save)
        btn_box.addWidget(self.btn_save)

        main_layout.addLayout(btn_box)

    def load_calibration_data(self):
        cal = self.config_manager.get("calibration", default={})
        for row in range(8):
            ch_key = f"CH{row + 1}"
            ch_data = cal.get(ch_key, {"min_us": 1000, "center_us": 1500, "max_us": 2000, "reversed": False, "deadband": 0.02})

            # Name Item
            item_name = QTableWidgetItem(ch_key)
            item_name.setFlags(Qt.ItemIsEnabled)
            item_name.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item_name)

            # Min SpinBox
            sb_min = QSpinBox()
            sb_min.setRange(500, 2500)
            sb_min.setValue(int(ch_data.get("min_us", 1000)))
            self.table.setCellWidget(row, 1, sb_min)

            # Center SpinBox
            sb_center = QSpinBox()
            sb_center.setRange(500, 2500)
            sb_center.setValue(int(ch_data.get("center_us", 1500)))
            self.table.setCellWidget(row, 2, sb_center)

            # Max SpinBox
            sb_max = QSpinBox()
            sb_max.setRange(500, 2500)
            sb_max.setValue(int(ch_data.get("max_us", 2000)))
            self.table.setCellWidget(row, 3, sb_max)

            # Invert Checkbox
            cb_invert = QCheckBox()
            cb_invert.setChecked(bool(ch_data.get("reversed", False)))
            cb_invert.setStyleSheet("margin-left: 50%;")
            self.table.setCellWidget(row, 4, cb_invert)

            # Deadband SpinBox
            sb_dead = QDoubleSpinBox()
            sb_dead.setRange(0.0, 20.0)
            sb_dead.setSingleStep(0.5)
            sb_dead.setSuffix(" %")
            sb_dead.setValue(float(ch_data.get("deadband", 0.02)) * 100.0)
            self.table.setCellWidget(row, 5, sb_dead)

    def update_live_channels(self, channels_us: List[float]):
        self.current_channels = list(channels_us)
        if self.is_recording_ranges:
            for i in range(min(8, len(channels_us))):
                us = channels_us[i]
                if 750 <= us <= 2250:
                    self.captured_mins[i] = min(self.captured_mins[i], us)
                    self.captured_maxs[i] = max(self.captured_maxs[i], us)

    def on_capture_centers(self):
        for i in range(min(8, len(self.current_channels))):
            us = self.current_channels[i]
            self.captured_centers[i] = round(us)
            sb_center = self.table.cellWidget(i, 2)
            if sb_center:
                sb_center.setValue(int(round(us)))

        self.lbl_s1_status.setText(f"Centers Captured! (CH1: {self.captured_centers[0]:.0f} µs)")
        self.lbl_s1_status.setStyleSheet("color: #10b981; font-weight: bold;")

    def on_toggle_recording(self):
        if not self.is_recording_ranges:
            # Start
            self.is_recording_ranges = True
            self.captured_mins = list(self.current_channels)
            self.captured_maxs = list(self.current_channels)
            self.btn_toggle_recording.setText("Stop Range Recording")
            self.btn_toggle_recording.setStyleSheet("background-color: #ef4444; color: #ffffff;")
            self.lbl_s2_status.setText("RECORDING... Move sticks to extremes!")
            self.lbl_s2_status.setStyleSheet("color: #facc15; font-weight: bold;")
        else:
            # Stop
            self.is_recording_ranges = False
            self.btn_toggle_recording.setText("Start Range Recording")
            self.btn_toggle_recording.setStyleSheet("")
            self.lbl_s2_status.setText("Ranges Recorded and Applied!")
            self.lbl_s2_status.setStyleSheet("color: #10b981; font-weight: bold;")

            for i in range(8):
                sb_min = self.table.cellWidget(i, 1)
                sb_max = self.table.cellWidget(i, 3)
                if sb_min:
                    sb_min.setValue(int(round(self.captured_mins[i])))
                if sb_max:
                    sb_max.setValue(int(round(self.captured_maxs[i])))

    def on_save(self):
        new_cal = {}
        for row in range(8):
            ch_key = f"CH{row + 1}"
            sb_min = self.table.cellWidget(row, 1)
            sb_center = self.table.cellWidget(row, 2)
            sb_max = self.table.cellWidget(row, 3)
            cb_invert = self.table.cellWidget(row, 4)
            sb_dead = self.table.cellWidget(row, 5)

            new_cal[ch_key] = {
                "name": f"Channel {row + 1}",
                "min_us": sb_min.value() if sb_min else 1000,
                "center_us": sb_center.value() if sb_center else 1500,
                "max_us": sb_max.value() if sb_max else 2000,
                "reversed": cb_invert.isChecked() if cb_invert else False,
                "deadband": (sb_dead.value() / 100.0) if sb_dead else 0.02,
                "expo": 0.0,
            }

        self.config_manager.set("calibration", None, new_cal)
        self.controller_mapper.load_from_config()
        self.accept()
