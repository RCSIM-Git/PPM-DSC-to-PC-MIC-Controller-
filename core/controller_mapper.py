"""Controller Mapper Module for PPM-SIM.
Translates decoded PPM channels into virtual Xbox 360 / DualShock 4 gamepad inputs via ViGEmBus.
"""

from typing import Any, Dict, List, Optional
import numpy as np

# Try importing vgamepad
try:
    import vgamepad as vg
    HAS_VGAMEPAD = True
except Exception as e:
    vg = None
    HAS_VGAMEPAD = False
    print(f"[ControllerMapper] vgamepad not available: {e}")


class ControllerMapper:
    """Handles channel calibration, profile mapping, and virtual gamepad output."""

    BUTTON_MAP = {
        "button_a": getattr(vg.XUSB_BUTTON, "XUSB_GAMEPAD_A", 0x1000) if vg else 0x1000,
        "button_b": getattr(vg.XUSB_BUTTON, "XUSB_GAMEPAD_B", 0x2000) if vg else 0x2000,
        "button_x": getattr(vg.XUSB_BUTTON, "XUSB_GAMEPAD_X", 0x4000) if vg else 0x4000,
        "button_y": getattr(vg.XUSB_BUTTON, "XUSB_GAMEPAD_Y", 0x8000) if vg else 0x8000,
        "button_left_shoulder": getattr(vg.XUSB_BUTTON, "XUSB_GAMEPAD_LEFT_SHOULDER", 0x0100) if vg else 0x0100,
        "button_right_shoulder": getattr(vg.XUSB_BUTTON, "XUSB_GAMEPAD_RIGHT_SHOULDER", 0x0200) if vg else 0x0200,
        "button_back": getattr(vg.XUSB_BUTTON, "XUSB_GAMEPAD_BACK", 0x0020) if vg else 0x0020,
        "button_start": getattr(vg.XUSB_BUTTON, "XUSB_GAMEPAD_START", 0x0010) if vg else 0x0010,
        "button_left_thumb": getattr(vg.XUSB_BUTTON, "XUSB_GAMEPAD_LEFT_THUMB", 0x0040) if vg else 0x0040,
        "button_right_thumb": getattr(vg.XUSB_BUTTON, "XUSB_GAMEPAD_RIGHT_THUMB", 0x0080) if vg else 0x0080,
        "dpad_up": getattr(vg.XUSB_BUTTON, "XUSB_GAMEPAD_DPAD_UP", 0x0001) if vg else 0x0001,
        "dpad_down": getattr(vg.XUSB_BUTTON, "XUSB_GAMEPAD_DPAD_DOWN", 0x0002) if vg else 0x0002,
        "dpad_left": getattr(vg.XUSB_BUTTON, "XUSB_GAMEPAD_DPAD_LEFT", 0x0004) if vg else 0x0004,
        "dpad_right": getattr(vg.XUSB_BUTTON, "XUSB_GAMEPAD_DPAD_RIGHT", 0x0008) if vg else 0x0008,
    }

    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.gamepad = None
        self.is_connected = False
        self.active_profile_name = "RadioMaster MT12 (Surface RC)"
        self.profile_data: Dict[str, Any] = {}
        self.calibration_data: Dict[str, Any] = {}

        # Current state for UI preview
        self.preview_state: Dict[str, Any] = {
            "left_stick_x": 0.0,
            "left_stick_y": 0.0,
            "right_stick_x": 0.0,
            "right_stick_y": 0.0,
            "left_trigger": 0.0,
            "right_trigger": 0.0,
            "buttons": {k: False for k in self.BUTTON_MAP.keys()},
        }

        self.load_from_config()
        self.initialize_gamepad()

    def load_from_config(self) -> None:
        """Loads calibration and profile definitions from config manager."""
        if self.config_manager:
            self.calibration_data = self.config_manager.get("calibration", default={})
            self.active_profile_name = self.config_manager.get("controller", "active_profile", default="RadioMaster MT12 (Surface RC)")
            profiles = self.config_manager.get("profiles", default={})
            self.profile_data = profiles.get(self.active_profile_name, {})

    def initialize_gamepad(self) -> bool:
        """Initializes virtual Xbox 360 controller via ViGEmBus."""
        if not HAS_VGAMEPAD:
            self.is_connected = False
            return False

        try:
            if self.gamepad is None:
                self.gamepad = vg.VX360Gamepad()
                self.is_connected = True
                print("[ControllerMapper] Virtual Xbox 360 Gamepad connected successfully via ViGEmBus.")
            return True
        except Exception as e:
            print(f"[ControllerMapper] Could not create virtual gamepad: {e}")
            self.is_connected = False
            self.gamepad = None
            return False

    def calibrate_channel_value(self, ch_key: str, raw_us: float) -> float:
        """Calibrates raw pulse (µs) to normalized range [-1.0 .. +1.0]."""
        cal = self.calibration_data.get(ch_key, {
            "min_us": 1000,
            "center_us": 1500,
            "max_us": 2000,
            "reversed": False,
            "deadband": 0.02,
            "expo": 0.0,
        })

        min_us = float(cal.get("min_us", 1000))
        center_us = float(cal.get("center_us", 1500))
        max_us = float(cal.get("max_us", 2000))
        is_reversed = bool(cal.get("reversed", False))
        deadband = float(cal.get("deadband", 0.02))
        expo = float(cal.get("expo", 0.0))

        # Range normalization around center
        if raw_us < center_us:
            span = max(1.0, center_us - min_us)
            norm = (raw_us - center_us) / span
        else:
            span = max(1.0, max_us - center_us)
            norm = (raw_us - center_us) / span

        norm = float(np.clip(norm, -1.0, 1.0))

        # Deadband around center
        if abs(norm) < deadband:
            norm = 0.0
        else:
            sign = 1.0 if norm > 0 else -1.0
            norm = sign * (abs(norm) - deadband) / (1.0 - deadband)

        # Inversion
        if is_reversed:
            norm = -norm

        # Exponential curve
        if expo != 0.0:
            norm = (1.0 - expo) * norm + expo * (norm ** 3)

        return float(np.clip(norm, -1.0, 1.0))

    def update_channels(self, channels_us: List[float]) -> Dict[str, Any]:
        """Processes channel pulses, updates virtual gamepad and preview state."""
        # Reset preview state
        lx, ly = 0.0, 0.0
        rx, ry = 0.0, 0.0
        lt, rt = 0.0, 0.0
        pressed_buttons = set()

        channels_config = self.profile_data.get("channels", {})

        for i, raw_us in enumerate(channels_us):
            ch_key = f"CH{i + 1}"
            norm_val = self.calibrate_channel_value(ch_key, raw_us)
            ch_map = channels_config.get(ch_key, {})
            target = ch_map.get("target", "")
            target_type = ch_map.get("type", "axis")
            invert = ch_map.get("invert", False)
            if invert:
                norm_val = -norm_val

            if target_type == "axis":
                if target == "left_joystick_x":
                    lx = norm_val
                elif target == "left_joystick_y":
                    ly = norm_val
                elif target == "right_joystick_x":
                    rx = norm_val
                elif target == "right_joystick_y":
                    ry = norm_val
                elif target == "left_trigger":
                    lt = (norm_val + 1.0) / 2.0  # -1..1 -> 0..1
                elif target == "right_trigger":
                    rt = (norm_val + 1.0) / 2.0  # -1..1 -> 0..1

            elif target_type == "trigger_split":
                # MT12 throttle trigger: >0 is Gas (RT), <0 is Brake/Reverse (LT)
                if norm_val > 0.0:
                    rt = norm_val
                    lt = 0.0
                else:
                    lt = -norm_val
                    rt = 0.0

            elif target_type == "button":
                threshold = ch_map.get("threshold", 1600)
                if raw_us >= threshold:
                    pressed_buttons.add(target)

        # Update preview state
        self.preview_state["left_stick_x"] = round(lx, 3)
        self.preview_state["left_stick_y"] = round(ly, 3)
        self.preview_state["right_stick_x"] = round(rx, 3)
        self.preview_state["right_stick_y"] = round(ry, 3)
        self.preview_state["left_trigger"] = round(lt, 3)
        self.preview_state["right_trigger"] = round(rt, 3)
        for btn in self.BUTTON_MAP.keys():
            self.preview_state["buttons"][btn] = (btn in pressed_buttons)

        # Update physical virtual controller via ViGEmBus
        if self.is_connected and self.gamepad:
            try:
                self.gamepad.left_joystick_float(x_value_float=lx, y_value_float=ly)
                self.gamepad.right_joystick_float(x_value_float=rx, y_value_float=ry)
                self.gamepad.left_trigger_float(value_float=lt)
                self.gamepad.right_trigger_float(value_float=rt)

                # Update buttons
                for btn_name, xusb_btn in self.BUTTON_MAP.items():
                    if btn_name in pressed_buttons:
                        self.gamepad.press_button(button=xusb_btn)
                    else:
                        self.gamepad.release_button(button=xusb_btn)

                self.gamepad.update()
            except Exception as e:
                # Driver disconnected or update error
                pass

        return self.preview_state

    def set_profile(self, profile_name: str) -> bool:
        """Switches active mapping profile."""
        if self.config_manager:
            profiles = self.config_manager.get("profiles", default={})
            if profile_name in profiles:
                self.active_profile_name = profile_name
                self.profile_data = profiles[profile_name]
                self.config_manager.set("controller", "active_profile", profile_name)
                return True
        return False
