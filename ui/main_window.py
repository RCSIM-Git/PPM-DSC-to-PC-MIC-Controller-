"""Main Window for PPM-SIM.
Integrates Audio Stream, PPM Decoder, ViGEm Virtual Gamepad, Oscilloscope, Channel Bars, and UI Controls.
"""

from typing import List
import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from core.audio_capture import AudioCapture
from core.config_manager import ConfigManager
from core.controller_mapper import ControllerMapper
from core.ppm_decoder import PPMDecoder
from ui.calibration_dialog import CalibrationDialog
from ui.channel_bars_widget import ChannelBarsWidget
from ui.gamepad_preview import GamepadPreviewWidget
from ui.oscilloscope_widget import OscilloscopeWidget


class MainWindow(QMainWindow):
    """Main application window for PPM-SIM."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PPM-SIM | RC Radio Audio to Virtual Controller")
        self.resize(1080, 720)
        self.setMinimumSize(920, 600)

        # Initialize Core Components
        self.config_manager = ConfigManager()
        self.decoder = PPMDecoder(
            sample_rate=self.config_manager.get("audio", "sample_rate", 48000),
            num_channels=self.config_manager.get("decoder", "num_channels", 8),
            polarity=self.config_manager.get("decoder", "polarity", "auto"),
            smoothing=self.config_manager.get("decoder", "smoothing", 0.35),
            deadband_us=self.config_manager.get("decoder", "deadband_us", 3.0),
        )
        self.mapper = ControllerMapper(self.config_manager)
        self.audio_capture = AudioCapture(
            callback=self._on_audio_data_received,
            sample_rate=self.decoder.sample_rate,
            block_size=self.config_manager.get("audio", "block_size", 256),
            channel_index=self.config_manager.get("audio", "channel", 0),
        )

        self.cal_dialog = None
        self.init_ui()
        self.init_tray()

        # UI update timer (60 FPS)
        self.ui_timer = QTimer(self)
        self.ui_timer.setInterval(16)  # ~60 Hz
        self.ui_timer.timeout.connect(self._on_ui_tick)
        self.ui_timer.start()

        # Auto-start audio if configured
        self._auto_start()

    def init_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        # 1. Top Control Header Bar
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #161b26;
                border: 1px solid #232d3f;
                border-radius: 8px;
                padding: 6px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(8, 6, 8, 6)
        header_layout.setSpacing(10)

        # Title
        lbl_app = QLabel("PPM-SIM")
        lbl_app.setObjectName("lbl_title")
        header_layout.addWidget(lbl_app)

        # Audio Device Selector
        lbl_dev = QLabel("Microphone:")
        lbl_dev.setStyleSheet("font-weight: 600; color: #94a3b8;")
        header_layout.addWidget(lbl_dev)

        self.combo_devices = QComboBox()
        self.combo_devices.setMinimumWidth(240)
        self._populate_audio_devices()
        header_layout.addWidget(self.combo_devices)

        # Audio Channel Selector
        self.combo_channel = QComboBox()
        self.combo_channel.addItems(["Left (Ch 0)", "Right (Ch 1)", "Auto / Best"])
        current_ch = self.config_manager.get("audio", "channel", 0)
        if current_ch == 0:
            self.combo_channel.setCurrentIndex(0)
        elif current_ch == 1:
            self.combo_channel.setCurrentIndex(1)
        else:
            self.combo_channel.setCurrentIndex(2)
        self.combo_channel.currentIndexChanged.connect(self._on_channel_changed)
        header_layout.addWidget(self.combo_channel)

        # Profile Selector
        lbl_prof = QLabel("Profile:")
        lbl_prof.setStyleSheet("font-weight: 600; color: #94a3b8;")
        header_layout.addWidget(lbl_prof)

        self.combo_profiles = QComboBox()
        profiles = list(self.config_manager.get("profiles", default={}).keys())
        self.combo_profiles.addItems(profiles)
        active_prof = self.config_manager.get("controller", "active_profile", "RadioMaster MT12 (Surface RC)")
        if active_prof in profiles:
            self.combo_profiles.setCurrentText(active_prof)
        self.combo_profiles.currentTextChanged.connect(self._on_profile_changed)
        header_layout.addWidget(self.combo_profiles)

        header_layout.addStretch()

        # Calibration Wizard Button
        self.btn_cal = QPushButton("Calibrate Sticks")
        self.btn_cal.clicked.connect(self.open_calibration_wizard)
        header_layout.addWidget(self.btn_cal)

        # Start / Stop Button
        self.btn_toggle_audio = QPushButton("START")
        self.btn_toggle_audio.setObjectName("btn_start")
        self.btn_toggle_audio.setFixedWidth(100)
        self.btn_toggle_audio.clicked.connect(self.toggle_audio_stream)
        header_layout.addWidget(self.btn_toggle_audio)

        root_layout.addWidget(header_frame)

        # 2. Status Diagnostics Bar
        diag_layout = QHBoxLayout()
        diag_layout.setSpacing(8)

        self.badge_status = QLabel("STATUS: STOPPED")
        self.badge_status.setObjectName("lbl_badge_inactive")
        diag_layout.addWidget(self.badge_status)

        self.badge_quality = QLabel("QUALITY: 0.0%")
        self.badge_quality.setObjectName("lbl_badge")
        diag_layout.addWidget(self.badge_quality)

        self.badge_fps = QLabel("RATE: 0.0 Hz")
        self.badge_fps.setObjectName("lbl_badge")
        diag_layout.addWidget(self.badge_fps)

        self.badge_channels = QLabel("CHANNELS: 8CH")
        self.badge_channels.setObjectName("lbl_badge")
        diag_layout.addWidget(self.badge_channels)

        self.badge_gamepad = QLabel("GAMEPAD: XBOX 360")
        self.badge_gamepad.setObjectName("lbl_badge_active")
        diag_layout.addWidget(self.badge_gamepad)

        diag_layout.addStretch()
        root_layout.addLayout(diag_layout)

        # 3. Main Split Content Area
        splitter = QSplitter(Qt.Horizontal)

        # Left Column: Oscilloscope + Virtual Gamepad Preview
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        self.oscilloscope = OscilloscopeWidget(self)
        left_layout.addWidget(self.oscilloscope, stretch=1)

        self.gamepad_preview = GamepadPreviewWidget(self)
        left_layout.addWidget(self.gamepad_preview, stretch=1)

        splitter.addWidget(left_widget)

        # Right Column: 8-Channel Live Pulse Meters
        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame {
                background-color: #121620;
                border: 1px solid #232d3f;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(6)

        lbl_ch_title = QLabel("8-CHANNEL PPM PULSE MONITORS")
        lbl_ch_title.setStyleSheet("font-weight: bold; color: #00f0ff; font-size: 11px; letter-spacing: 1px;")
        right_layout.addWidget(lbl_ch_title)

        self.channel_bars = ChannelBarsWidget(self)
        right_layout.addWidget(self.channel_bars)
        right_layout.addStretch()

        splitter.addWidget(right_frame)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        root_layout.addWidget(splitter, stretch=1)

        # Apply active profile labels
        self._update_channel_labels()

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)

        # Tray Menu
        tray_menu = self.tray_icon.contextMenu() or QAction(self)
        action_show = QAction("Show PPM-SIM", self)
        action_show.triggered.connect(self.showNormal)
        action_exit = QAction("Exit", self)
        action_exit.triggered.connect(self.close)

        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.addAction(action_show)
        menu.addSeparator()
        menu.addAction(action_exit)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()
                self.activateWindow()

    def _populate_audio_devices(self):
        self.combo_devices.clear()
        devices = self.audio_capture.list_input_devices()
        selected_idx = self.config_manager.get("audio", "device_index", None)

        cur_select_combo = 0
        for i, dev in enumerate(devices):
            self.combo_devices.addItem(dev["display_name"], dev["index"])
            if selected_idx is not None and dev["index"] == selected_idx:
                cur_select_combo = i
            elif selected_idx is None and dev["is_default"]:
                cur_select_combo = i

        if self.combo_devices.count() > 0:
            self.combo_devices.setCurrentIndex(cur_select_combo)
        self.combo_devices.currentIndexChanged.connect(self._on_device_changed)

    def _on_device_changed(self, index):
        dev_idx = self.combo_devices.currentData()
        self.config_manager.set("audio", "device_index", dev_idx)
        if self.audio_capture.is_running:
            self.audio_capture.start(device_index=dev_idx)

    def _on_channel_changed(self, index):
        ch = 0 if index == 0 else (1 if index == 1 else -1)
        self.config_manager.set("audio", "channel", ch)
        self.audio_capture.channel_index = ch

    def _on_profile_changed(self, profile_name):
        self.mapper.set_profile(profile_name)
        self._update_channel_labels()

    def _update_channel_labels(self):
        active_prof = self.combo_profiles.currentText()
        profiles = self.config_manager.get("profiles", default={})
        prof_data = profiles.get(active_prof, {})
        self.channel_bars.set_profile_labels(prof_data.get("channels", {}))

    def _auto_start(self):
        # Auto-start stream on launch
        dev_idx = self.combo_devices.currentData()
        self.audio_capture.start(device_index=dev_idx)
        self._update_start_button_state()

    def toggle_audio_stream(self):
        if self.audio_capture.is_running:
            self.audio_capture.stop()
        else:
            dev_idx = self.combo_devices.currentData()
            self.audio_capture.start(device_index=dev_idx)
        self._update_start_button_state()

    def _update_start_button_state(self):
        if self.audio_capture.is_running:
            self.btn_toggle_audio.setText("STOP")
            self.btn_toggle_audio.setObjectName("btn_stop")
            self.btn_toggle_audio.setStyleSheet("")
            self.badge_status.setText("STATUS: RUNNING")
            self.badge_status.setObjectName("lbl_badge_active")
        else:
            self.btn_toggle_audio.setText("START")
            self.btn_toggle_audio.setObjectName("btn_start")
            self.btn_toggle_audio.setStyleSheet("")
            self.badge_status.setText("STATUS: STOPPED")
            self.badge_status.setObjectName("lbl_badge_inactive")

        # Refresh style
        self.btn_toggle_audio.style().unpolish(self.btn_toggle_audio)
        self.btn_toggle_audio.style().polish(self.btn_toggle_audio)
        self.badge_status.style().unpolish(self.badge_status)
        self.badge_status.style().polish(self.badge_status)

    def _on_audio_data_received(self, audio_mono: np.ndarray):
        """Audio callback running in audio thread."""
        self.decoder.process_audio_block(audio_mono)

    def _on_ui_tick(self):
        """Main UI update loop (~60 FPS)."""
        state = self.decoder.get_state()
        channels_smooth = state["channels_smooth"]
        channels_norm = state["channels_normalized"]

        # Feed mapper to update virtual gamepad & preview state
        preview_state = self.mapper.update_channels(channels_smooth)

        # Update Oscilloscope
        self.oscilloscope.update_plot(
            waveform=self.decoder.scope_waveform,
            high_thresh=state["high_thresh"],
            low_thresh=state["low_thresh"],
            polarity=state["detected_polarity"],
            peak_db=state["audio_peak_db"],
        )

        # Update 8-Channel Bars
        self.channel_bars.update_channels(channels_smooth, channels_norm)

        # Update Gamepad Vector Preview
        self.gamepad_preview.update_gamepad_state(preview_state, self.mapper.is_connected)

        # Update Diagnostics Badges
        fps = state["fps"]
        quality = state["quality"]
        self.badge_fps.setText(f"RATE: {fps:.1f} Hz")
        self.badge_quality.setText(f"QUALITY: {quality:.0f}%")

        if quality >= 80.0:
            self.badge_quality.setStyleSheet("background-color: #064e3b; color: #34d399; font-weight: bold; border-radius: 4px; padding: 3px 8px;")
        elif quality >= 40.0:
            self.badge_quality.setStyleSheet("background-color: #451a03; color: #fbbf24; font-weight: bold; border-radius: 4px; padding: 3px 8px;")
        else:
            self.badge_quality.setStyleSheet("background-color: #1e2638; color: #94a3b8; font-weight: bold; border-radius: 4px; padding: 3px 8px;")

        # Feed live channels to calibration dialog if open
        if self.cal_dialog is not None and self.cal_dialog.isVisible():
            self.cal_dialog.update_live_channels(channels_smooth)

    def open_calibration_wizard(self):
        self.cal_dialog = CalibrationDialog(self.config_manager, self.mapper, self)
        self.cal_dialog.exec()
        self.cal_dialog = None

    def closeEvent(self, event):
        self.audio_capture.stop()
        self.config_manager.save_config()
        event.accept()
