# PPM-SIM 🎮

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)]()

> **Real-time RC Radio Trainer Port PPM Audio Decoder to Virtual Xbox 360 Controller**  
> *Dekoder sygnału PPM audio z portu trenera aparatury RC na wirtualny kontroler Xbox 360 / DualShock 4 w systemie Windows.*

---

## 🇵🇱 Opis Projektu (Polish)

**PPM-SIM** to nowoczesna aplikacja na system Windows, która pozwala na podłączenie aparatury RC (np. **RadioMaster MT12**, Boxer, TX16S, FlySky, FrSky, TBS Tango itp.) do komputera za pomocą standardowego kabla audio jack 3.5 mm (port trenera / DSC) do wejścia mikrofonowego / liniowego karty dźwiękowej. Program w czasie rzeczywistym dekoduje impulsy 8 kanałów (CH1–CH8) i mapuje je na natywny **wirtualny kontroler Xbox 360 / DualShock 4** (poprzez sterownik ViGEmBus), umożliwiając bezproblemową zabawę we wszystkich grach i symulatorach:
- **Drony / FPV**: *Liftoff, Velocidrone, Uncrashed, DRL, FPV Freerider, Tryp FPV*
- **Samochody / Surface RC**: *Assetto Corsa, BeamNG.drive, Forza Horizon, DiRT Rally, CarX Drift Racing*
- **Lotnictwo / Samoloty**: *RealFlight, Microsoft Flight Simulator, AccuRC*

### 🌟 Główne Funkcje
- **Oscyloskop sygnału na żywo**: Wyświetla kształt fali audio PPM, poziom głośności wejścia (dB) oraz dynamiczne progi detekcji zboczy (Schmitt trigger).
- **Precyzyjny dekoder 8 kanałów (CH1–CH8)**: Odczyt szerokości impulsów w mikrosekundach (µs) oraz w procentach (-100% do +100%) z sub-samplową interpolacją ułamkową.
- **Natywny Wirtualny Pad Xbox 360 (ViGEmBus)**: Natychmiast wykrywany przez 100% gier i platform (Steam, gry bez konfiguracji DirectInput).
- **Dedykowane profile**:
  - **RadioMaster MT12 (Surface RC / Auta)**: Koło kierownicy na osi X, trigger dzielony (Gaz na RT, Hamulec/Wsteczny na LT), trymery i przyciski funkcyjne.
  - **Mode 2 (Drony / Śmigłowce)**: Gaz/Yaw lewy drążek, Roll/Pitch prawy drążek.
  - **Mode 1 (Samoloty)**: Aileron/Throttle prawy drążek, Elevator/Rudder lewy drążek.
  - Własne profile użytkownika w formacie JSON/YAML.
- **Kreator Kalibracji (Wizard)**: 3-stopniowy asystent centrowania, rejestracji pełnych zakresów ruchu (Min / Max), regulacji strefy martwej (Deadband) oraz inwersji osi.
- **Minimalizacja do zasobnika systemowego (Tray)**: Aplikacja działa płynnie w tle podczas gry.

---

## 🇬🇧 English Description

**PPM-SIM** is a Windows desktop application that connects your RC transmitter (**RadioMaster MT12**, Boxer, TX16S, FlySky, FrSky, etc.) via a standard 3.5mm audio cable (DSC / Trainer Port) into your PC's microphone or line-in jack. It decodes the PPM (Pulse Position Modulation) signal in real-time with sub-millisecond precision and maps the channels to a native **virtual Xbox 360 gamepad** (via ViGEmBus).

### 🚀 Key Features
- **Ultra-low latency audio processing** (< 10 ms end-to-end) using `sounddevice`.
- **Adaptive DSP & Schmitt Trigger**: Auto-detects PPM polarity (positive/negative), filters glitches, and smooths jitter (EMA + Deadband).
- **Interactive Oscilloscope**: Real-time 60 FPS hardware-accelerated waveform viewer with adaptive threshold markers.
- **Visual 8-Channel Monitors**: Live µs readouts and bi-directional deflection bars.
- **Vector Controller Preview**: Real-time animated Xbox 360 gamepad showing stick positions, analog triggers (LT/RT), and pressed buttons.
- **Calibration Wizard**: Automatic stick centering (Subtrim) and end-point range calibration.
- **System Tray Integration**: Run silently in the background while gaming.

---

## 🛠️ Konfiguracja Aparatury / Transmitter Setup

1. **Podłączenie Kabla**:
   - Użyj kabla audio mini-jack 3.5 mm (mono lub stereo).
   - Podłącz jeden koniec do gniazda **DSC / Trainer** w aparaturze, a drugi do gniazda **Mikrofonu / Line-In** w komputerze.
2. **Ustawienia w aparaturze (EdgeTX / OpenTX / MT12)**:
   - **Model Setup** -> **Trainer Mode**: `Master/Jack`
   - **Channels**: `8CH`
   - **Frame Length**: `22.5ms`
   - **Pulse Delay**: `300us`
   - **Polarity**: `POS (+)` lub `NEG (-)` (PPM-SIM wykrywa automatycznie)
   - W przypadku modeli samochodowych (MT12): przypisz CH1 = Steering, CH2 = Throttle/Brake, CH3..CH8 = Switches/Trims.

---

## 📦 Wymagania i Instalacja / Installation

### Wymagania / Prerequisites:
- Windows 10 / 11 (64-bit)
- Python 3.10+
- Sterownik **ViGEmBus** (standard w Windows dla wirtualnych kontrolerów). Jeśli nie posiadasz, pobierz oficjalny instalator: [ViGEmBus GitHub Releases](https://github.com/nefarius/ViGEmBus/releases).

### Instalacja pakietów:
```bash
pip install -r requirements.txt
```

### Uruchomienie:
- Kliknij dwukrotnie **`run_ppm_sim.bat`**
- lub z wiersza poleceń:
```bash
python main.py
```

---

## 🧪 Testy Jednostkowe / Testing

Projekt zawiera pełny zestaw testów sprawdzających dekodowanie PPM, histerezę, polaryzację i mapowanie:
```bash
pytest tests -v
```

---

## 📁 Struktura Plików / File Structure

```
PPM-SIM/
├── main.py                    # Punkt startowy aplikacji / Entry point
├── run_ppm_sim.bat            # Skrypt startowy 1-click / 1-click launcher
├── requirements.txt           # Zależności Python / Dependencies
├── config.json                # Konfiguracja, profile i kalibracja / Config
├── LICENSE                    # Licencja MIT / MIT License
├── core/
│   ├── audio_capture.py       # Przechwytywanie dźwięku / Low latency audio stream
│   ├── ppm_decoder.py         # Silnik dekodowania PPM i DSP / PPM DSP engine
│   ├── controller_mapper.py   # Tłumacz kanałów na wirtualny pad Xbox 360 / ViGEm mapper
│   └── config_manager.py      # Menedżer ustawień / Config manager
├── ui/
│   ├── main_window.py         # Główne okno aplikacji / Main GUI window
│   ├── oscilloscope_widget.py # Oscyloskop audio / Signal oscilloscope
│   ├── channel_bars_widget.py # Wskaźniki 8 kanałów / 8CH pulse monitors
│   ├── gamepad_preview.py     # Wizualizacja kontrolera / Vector gamepad canvas
│   ├── calibration_dialog.py  # Kreator kalibracji / Calibration wizard
│   └── theme.py               # Ciemny motyw QSS / Dark theme
└── tests/
    └── test_ppm_decoder.py    # Testy jednostkowe / Unit tests
```

---

## 📄 Licencja / License

Projekt udostępniony na licencji **MIT**. Szczegóły w pliku [LICENSE](LICENSE).
