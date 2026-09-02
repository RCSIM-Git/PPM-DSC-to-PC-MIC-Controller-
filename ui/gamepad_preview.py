"""Gamepad Preview Widget for PPM-SIM.
Interactive vector drawing of an Xbox 360 controller with animated sticks, triggers, and buttons.
"""

from typing import Any, Dict
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class GamepadCanvas(QWidget):
    """Custom QPainter canvas rendering analog sticks, triggers and buttons."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(280, 180)

        self.lx = 0.0
        self.ly = 0.0
        self.rx = 0.0
        self.ry = 0.0
        self.lt = 0.0
        self.rt = 0.0
        self.buttons: Dict[str, bool] = {}

    def update_state(self, state: Dict[str, Any]):
        self.lx = state.get("left_stick_x", 0.0)
        self.ly = state.get("left_stick_y", 0.0)
        self.rx = state.get("right_stick_x", 0.0)
        self.ry = state.get("right_stick_y", 0.0)
        self.lt = state.get("left_trigger", 0.0)
        self.rt = state.get("right_trigger", 0.0)
        self.buttons = state.get("buttons", {})
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Dark Background
        painter.fillRect(0, 0, w, h, QColor("#121620"))

        # Draw Trigger Bars on Left and Right sides
        self._draw_trigger(painter, x=15, y=20, width=20, height=h - 40, val=self.lt, label="LT")
        self._draw_trigger(painter, x=w - 35, y=20, width=20, height=h - 40, val=self.rt, label="RT")

        # Center area for Sticks & Buttons
        center_x = w / 2.0
        stick_y = h / 2.0 + 10
        stick_radius = 42

        # Left Stick (LX, LY)
        ls_x = center_x - 70
        self._draw_analog_stick(painter, ls_x, stick_y, stick_radius, self.lx, -self.ly, "L-STICK")

        # Right Stick (RX, RY)
        rs_x = center_x + 70
        self._draw_analog_stick(painter, rs_x, stick_y, stick_radius, self.rx, -self.ry, "R-STICK")

        # Buttons (A, B, X, Y) in top center
        self._draw_buttons(painter, center_x, 30)

        # Bumpers (LB, RB)
        self._draw_bumpers(painter, ls_x, rs_x, 15)

    def _draw_trigger(self, painter: QPainter, x: float, y: float, width: float, height: float, val: float, label: str):
        # Trigger frame
        rect = QRectF(x, y, width, height)
        painter.setPen(QPen(QColor("#232d3f"), 1))
        painter.setBrush(QBrush(QColor("#0e1117")))
        painter.drawRoundedRect(rect, 4, 4)

        # Fill level (bottom to top)
        fill_h = height * max(0.0, min(1.0, val))
        if fill_h > 1:
            fill_rect = QRectF(x + 1, y + height - fill_h, width - 2, fill_h)
            grad = QLinearGradient(x, y + height, x, y)
            grad.setColorAt(0.0, QColor("#0077b6"))
            grad.setColorAt(1.0, QColor("#00f0ff"))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(fill_rect, 3, 3)

        # Label
        painter.setPen(QColor("#94a3b8"))
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        painter.drawText(QRectF(x - 5, y + height + 2, width + 10, 15), Qt.AlignCenter, f"{label} {int(val * 100)}%")

    def _draw_analog_stick(self, painter: QPainter, cx: float, cy: float, radius: float, x_val: float, y_val: float, label: str):
        # Outer base circle
        painter.setPen(QPen(QColor("#2a374f"), 2))
        painter.setBrush(QBrush(QColor("#161d2b")))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

        # Crosshairs
        painter.setPen(QPen(QColor("#232d3f"), 1, Qt.DashLine))
        painter.drawLine(int(cx - radius), int(cy), int(cx + radius), int(cy))
        painter.drawLine(int(cx), int(cy - radius), int(cx), int(cy + radius))

        # Thumb position
        max_travel = radius - 12
        thumb_x = cx + x_val * max_travel
        thumb_y = cy + y_val * max_travel

        # Connecting line from center
        painter.setPen(QPen(QColor("#00f0ff"), 1.5))
        painter.drawLine(QPointF(cx, cy), QPointF(thumb_x, thumb_y))

        # Thumb cap
        thumb_grad = QLinearGradient(thumb_x - 12, thumb_y - 12, thumb_x + 12, thumb_y + 12)
        thumb_grad.setColorAt(0.0, QColor("#00f0ff"))
        thumb_grad.setColorAt(1.0, QColor("#0077b6"))
        painter.setPen(QPen(QColor("#ffffff"), 1.5))
        painter.setBrush(QBrush(thumb_grad))
        painter.drawEllipse(QPointF(thumb_x, thumb_y), 11, 11)

        # Label & values
        painter.setPen(QColor("#64748b"))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(QRectF(cx - 50, cy + radius + 3, 100, 15), Qt.AlignCenter, f"X:{x_val:+.2f} Y:{-y_val:+.2f}")

    def _draw_buttons(self, painter: QPainter, cx: float, cy: float):
        btn_defs = [
            ("button_x", cx - 24, cy, "X", QColor("#38bdf8")),
            ("button_y", cx - 8, cy - 14, "Y", QColor("#facc15")),
            ("button_a", cx - 8, cy + 14, "A", QColor("#4ade80")),
            ("button_b", cx + 8, cy, "B", QColor("#f87171")),
        ]

        for key, x, y, char, col in btn_defs:
            is_active = self.buttons.get(key, False)
            btn_radius = 8
            painter.setPen(QPen(col if is_active else QColor("#2a374f"), 1.5))
            painter.setBrush(QBrush(col if is_active else QColor("#161d2b")))
            painter.drawEllipse(QPointF(x, y), btn_radius, btn_radius)

            painter.setPen(QColor("#000000" if is_active else "#94a3b8"))
            painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
            painter.drawText(QRectF(x - 8, y - 8, 16, 16), Qt.AlignCenter, char)

    def _draw_bumpers(self, painter: QPainter, ls_x: float, rs_x: float, y: float):
        # LB
        lb_active = self.buttons.get("button_left_shoulder", False)
        painter.setPen(QPen(QColor("#00f0ff") if lb_active else QColor("#2a374f"), 1))
        painter.setBrush(QBrush(QColor("#00f0ff") if lb_active else QColor("#161d2b")))
        painter.drawRoundedRect(QRectF(ls_x - 20, y - 8, 40, 12), 3, 3)
        painter.setPen(QColor("#000000" if lb_active else "#64748b"))
        painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
        painter.drawText(QRectF(ls_x - 20, y - 8, 40, 12), Qt.AlignCenter, "LB")

        # RB
        rb_active = self.buttons.get("button_right_shoulder", False)
        painter.setPen(QPen(QColor("#00f0ff") if rb_active else QColor("#2a374f"), 1))
        painter.setBrush(QBrush(QColor("#00f0ff") if rb_active else QColor("#161d2b")))
        painter.drawRoundedRect(QRectF(rs_x - 20, y - 8, 40, 12), 3, 3)
        painter.setPen(QColor("#000000" if rb_active else "#64748b"))
        painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
        painter.drawText(QRectF(rs_x - 20, y - 8, 40, 12), Qt.AlignCenter, "RB")


class GamepadPreviewWidget(QFrame):
    """Container frame wrapping the gamepad canvas and status readout."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            GamepadPreviewWidget {
                background-color: #161b26;
                border: 1px solid #232d3f;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Title & status
        header = QHBoxLayout()
        lbl_title = QLabel("VIRTUAL XBOX 360 CONTROLLER")
        lbl_title.setStyleSheet("font-weight: bold; color: #00f0ff; font-size: 11px; letter-spacing: 1px;")
        header.addWidget(lbl_title)
        header.addStretch()

        self.lbl_driver = QLabel("VIGEMBUS: CONNECTED")
        self.lbl_driver.setStyleSheet("background-color: #064e3b; color: #34d399; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        header.addWidget(self.lbl_driver)
        layout.addLayout(header)

        # Canvas
        self.canvas = GamepadCanvas(self)
        layout.addWidget(self.canvas)

    def update_gamepad_state(self, state: Dict[str, Any], is_connected: bool):
        self.canvas.update_state(state)
        if is_connected:
            self.lbl_driver.setText("VIGEMBUS: ACTIVE")
            self.lbl_driver.setStyleSheet("background-color: #064e3b; color: #34d399; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        else:
            self.lbl_driver.setText("VIGEMBUS: OFFLINE (PREVIEW ONLY)")
            self.lbl_driver.setStyleSheet("background-color: #3f1d24; color: #f87171; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
