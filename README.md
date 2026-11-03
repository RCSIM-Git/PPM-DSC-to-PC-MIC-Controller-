# PPM-SIM 🎮

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)]()

> 🌐 **Language / Język:** **English** | [Polski](README_PL.md)

> **Real-time RC Radio Trainer Port PPM Audio Decoder to Virtual Xbox 360 Controller**

---

## 📖 Project Overview

**PPM-SIM** is a Windows desktop application that bridges any standard R/C radio transmitter (**RadioMaster MT12**, Boxer, TX16S, Pocket, FlySky, FrSky, etc.) directly to your PC using a standard 3.5mm audio cable (DSC / Trainer port) plugged into the PC microphone or Line-In jack.

The software decodes the 8-channel (CH1–CH8) PPM (Pulse Position Modulation) audio signal in real time with sub-millisecond precision and translates it into a native **virtual Xbox 360 / DualShock 4 controller** (via the ViGEmBus driver). This delivers seamless, zero-hardware plug-and-play compatibility across all PC games, racing simulators, and flight simulators:
- **FPV Drones:** *Liftoff, Velocidrone, Uncrashed, DRL Simulator, FPV Freerider, Tryp FPV*
- **Surface & Sim-Racing:** *Assetto Corsa, BeamNG.drive, Forza Horizon, DiRT Rally 2.0, CarX Drift Racing*
- **Aviation:** *RealFlight, Microsoft Flight Simulator, AccuRC*

---

## 🌟 Key Features

- **Real-Time Signal Oscilloscope:** 60 FPS hardware-accelerated waveform viewer displaying the audio signal, input volume level (dB), and adaptive Schmitt trigger edge detection thresholds.
- **High-Precision 8-Channel Decoder:** Reads channel pulse widths in microseconds (µs) and percentages (-100% to +100%) with fractional sub-sample interpolation.
- **Native Virtual Xbox 360 Pad (ViGEmBus):** Instantly recognized by Windows and 100% of Steam and non-Steam games without requiring DirectInput emulator wrappers.
- **Preconfigured Transmitter Profiles:**
  - **RadioMaster MT12 (Surface RC / Cars):** Steering wheel on X axis, split trigger (Throttle on RT, Brake/Reverse on LT), trimmers, and functional toggle switches.
  - **Mode 2 (Drones / Helicopters):** Throttle/Yaw on left stick, Roll/Pitch on right stick.
  - **Mode 1 (Airplanes):** Aileron/Throttle on right stick, Elevator/Rudder on left stick.
  - Custom user profiles stored in clean JSON format.
- **Interactive Calibration Wizard:** 3-step assistant for stick/wheel centering (Subtrim), travel range registration (Min/Max), deadband adjustment, and axis inversion.
- **System Tray Integration:** Runs silently in the background while gaming.

---

## 🛠️ Transmitter Configuration (EdgeTX / OpenTX)

1. **Hardware Connection:**
   - Use a standard 3.5mm audio mini-jack cable (mono or stereo).
   - Plug one end into the **DSC / Trainer** jack on your transmitter and the other into the PC **Microphone / Line-In** port.
2. **Radio Model Setup (EdgeTX / OpenTX / MT12):**
   - **Model Setup** -> **Trainer Mode:** `Master/Jack`
   - **Channels:** `8CH`
   - **Frame Length:** `22.5ms`
   - **Pulse Delay:** `300us`
   - **Polarity:** `POS (+)` or `NEG (-)` (PPM-SIM auto-detects polarity)
   - For surface models (MT12): CH1 = Steering, CH2 = Throttle/Brake, CH3..CH8 = Switches/Trims.

---

## 📦 Requirements & Installation

### Prerequisites:
- Windows 10 / 11 (64-bit).
- Python 3.10+.
- **ViGEmBus Driver** (standard virtual gamepad bus on Windows). Download the official installer: [ViGEmBus GitHub Releases](https://github.com/nefarius/ViGEmBus/releases).

### Install Python Dependencies:
```bash
pip install -r requirements.txt
```

### Launch:
Double-click:
```cmd
run_ppm_sim.bat
```
Or execute via command prompt:
```bash
python main.py
```

---

## 🧪 Unit Testing

Run the automated test suite verifying PPM decoding, hysteresis, polarity detection, and controller mapping:
```bash
pytest tests -v
```

---

## 📁 Project Structure

```text
PPM-SIM/
├── main.py                    # Application entry point
├── run_ppm_sim.bat            # 1-click launcher script
├── requirements.txt           # Python dependencies (sounddevice, vgamepad, PySide6)
├── config.json                # User profiles and calibration storage
├── LICENSE                    # MIT License
├── README.md                  # English documentation
├── README_PL.md               # Polish documentation
├── core/
│   ├── audio_capture.py       # Low-latency audio stream engine
│   ├── ppm_decoder.py         # PPM DSP decoding engine with Schmitt trigger
│   ├── controller_mapper.py   # ViGEmBus virtual Xbox 360 controller translator
│   └── config_manager.py      # Configuration persistence manager
├── ui/
│   ├── main_window.py         # Main GUI window (PySide6)
│   ├── oscilloscope_widget.py # Real-time audio waveform oscilloscope
│   ├── channel_bars_widget.py # 8-channel pulse width monitor bars
│   ├── gamepad_preview.py     # Real-time animated vector Xbox gamepad
│   ├── calibration_dialog.py  # 3-step interactive calibration wizard
│   └── theme.py               # Modern dark QSS styling
└── tests/
    └── test_ppm_decoder.py    # Automated test cases
```

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.
