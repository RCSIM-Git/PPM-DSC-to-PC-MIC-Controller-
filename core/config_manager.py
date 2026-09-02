"""Configuration Manager for PPM-SIM.
Handles saving and loading user preferences, calibration data, and controller mappings.
"""

import json
import os
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "audio": {
        "device_index": None,          # None = Default device
        "sample_rate": 48000,          # 48000, 96000, 192000
        "block_size": 256,             # Low latency audio buffer
        "channel": 0,                  # 0 = Left, 1 = Right, -1 = Auto/Max
        "threshold_mode": "adaptive",  # adaptive / manual
        "manual_threshold": 0.2,       # threshold level if manual (-1.0 to 1.0)
    },
    "decoder": {
        "num_channels": 8,
        "min_pulse_us": 750,
        "max_pulse_us": 2250,
        "sync_min_us": 3000,
        "polarity": "auto",            # "auto", "positive", "negative"
        "smoothing": 0.35,             # Exponential Moving Average factor (0.0=raw, 0.9=heavy smooth)
        "deadband_us": 4,              # Jitter filter threshold in microseconds
    },
    "controller": {
        "enabled": True,
        "type": "xbox360",             # "xbox360" or "ds4"
        "active_profile": "RadioMaster MT12 (Surface RC)",
    },
    "calibration": {
        f"CH{i}": {
            "name": f"Channel {i}",
            "min_us": 1000,
            "center_us": 1500,
            "max_us": 2000,
            "reversed": False,
            "deadband": 0.02,
            "expo": 0.0,
        }
        for i in range(1, 9)
    },
    "profiles": {
        "RadioMaster MT12 (Surface RC)": {
            "description": "RadioMaster MT12 car/surface transmitter profile",
            "channels": {
                "CH1": {"target": "left_joystick_x", "type": "axis", "label": "Steering"},
                "CH2": {"target": "trigger_split", "type": "trigger_split", "label": "Throttle / Brake"},
                "CH3": {"target": "right_joystick_y", "type": "axis", "label": "Aux 1 (Dial/Trim)"},
                "CH4": {"target": "right_joystick_x", "type": "axis", "label": "Aux 2 (Trim)"},
                "CH5": {"target": "button_a", "type": "button", "label": "Switch A / Horn", "threshold": 1600},
                "CH6": {"target": "button_b", "type": "button", "label": "Switch B / Handbrake", "threshold": 1600},
                "CH7": {"target": "button_x", "type": "button", "label": "Switch C", "threshold": 1600},
                "CH8": {"target": "button_y", "type": "button", "label": "Switch D", "threshold": 1600},
            },
        },
        "Mode 2 (Drone / FPV / Heli)": {
            "description": "Standard Mode 2: Throttle/Yaw Left, Roll/Pitch Right",
            "channels": {
                "CH1": {"target": "right_joystick_x", "type": "axis", "label": "Roll (Aileron)"},
                "CH2": {"target": "right_joystick_y", "type": "axis", "label": "Pitch (Elevator)", "invert": True},
                "CH3": {"target": "left_joystick_y", "type": "axis", "label": "Throttle"},
                "CH4": {"target": "left_joystick_x", "type": "axis", "label": "Yaw (Rudder)"},
                "CH5": {"target": "button_a", "type": "button", "label": "Arm (AUX1)", "threshold": 1600},
                "CH6": {"target": "button_b", "type": "button", "label": "Mode (AUX2)", "threshold": 1600},
                "CH7": {"target": "button_left_shoulder", "type": "button", "label": "Buzzer (AUX3)", "threshold": 1600},
                "CH8": {"target": "button_right_shoulder", "type": "button", "label": "Turtle (AUX4)", "threshold": 1600},
            },
        },
        "Mode 1 (Airplane)": {
            "description": "Mode 1: Rudder/Elevator Left, Aileron/Throttle Right",
            "channels": {
                "CH1": {"target": "right_joystick_x", "type": "axis", "label": "Aileron (Roll)"},
                "CH2": {"target": "right_joystick_y", "type": "axis", "label": "Throttle"},
                "CH3": {"target": "left_joystick_y", "type": "axis", "label": "Elevator (Pitch)", "invert": True},
                "CH4": {"target": "left_joystick_x", "type": "axis", "label": "Rudder (Yaw)"},
                "CH5": {"target": "button_a", "type": "button", "label": "Switch 1", "threshold": 1600},
                "CH6": {"target": "button_b", "type": "button", "label": "Switch 2", "threshold": 1600},
                "CH7": {"target": "button_x", "type": "button", "label": "Switch 3", "threshold": 1600},
                "CH8": {"target": "button_y", "type": "button", "label": "Switch 4", "threshold": 1600},
            },
        },
    },
}

CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")


class ConfigManager:
    """Manages application settings persistence."""

    def __init__(self, config_path: str = CONFIG_FILE_PATH):
        self.config_path = os.path.abspath(config_path)
        self.config: Dict[str, Any] = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Loads configuration from JSON file or returns default."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                return self._deep_merge(DEFAULT_CONFIG.copy(), loaded)
            except Exception as e:
                print(f"[ConfigManager] Error reading config: {e}. Using defaults.")
        return json.loads(json.dumps(DEFAULT_CONFIG))

    def save_config(self) -> bool:
        """Saves current configuration to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ConfigManager] Error saving config: {e}")
            return False

    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """Retrieves a configuration value."""
        sec = self.config.get(section, {})
        if key is None:
            return sec
        return sec.get(key, default)

    def set(self, section: str, key: str, value: Any, auto_save: bool = True) -> None:
        """Sets a configuration value."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        if auto_save:
            self.save_config()

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Recursively merges override dict into base dict."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base
