# PPM-SIM 🎮

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)]()

> 🌐 **Language / Język:** [English](README.md) | **Polski**

> **Dekoder sygnału PPM audio z portu trenera aparatury RC na wirtualny kontroler Xbox 360 / DualShock 4 w systemie Windows**

---

## 📖 Opis Projektu

**PPM-SIM** to nowoczesna aplikacja na system Windows, która pozwala na podłączenie dowolnej aparatury RC (np. **RadioMaster MT12**, Boxer, TX16S, Pocket, FlySky, FrSky itp.) do komputera za pomocą standardowego kabla audio jack 3.5 mm (port trenera / DSC) wpiętego do wejścia mikrofonowego lub liniowego karty dźwiękowej.

Program w czasie rzeczywistym dekoduje impulsy 8 kanałów (CH1–CH8) sygnału PPM (Pulse Position Modulation) z dokładnością do mikrosekund i mapuje je na natywny **wirtualny kontroler Xbox 360 / DualShock 4** (za pośrednictwem sterownika ViGEmBus). Zapewnia to 100% kompatybilności plug-and-play ze wszystkimi grami PC, symulatorami wyścigowymi i lotniczymi:
- **Drony / FPV:** *Liftoff, Velocidrone, Uncrashed, DRL Simulator, FPV Freerider, Tryp FPV*
- **Samochody / Sim-Racing:** *Assetto Corsa, BeamNG.drive, Forza Horizon, DiRT Rally 2.0, CarX Drift Racing*
- **Lotnictwo:** *RealFlight, Microsoft Flight Simulator, AccuRC*

---

## 🌟 Główne Funkcje

- **Oscyloskop Sygnału na Żywo:** Wyświetla kształt fali audio PPM w 60 FPS, poziom głośności wejścia (dB) oraz dynamiczne progi detekcji zboczy (przerzutnik Schmitta).
- **Precyzyjny Dekoder 8 Kanałów (CH1–CH8):** Odczyt szerokości impulsów w mikrosekundach (µs) oraz w procentach (-100% do +100%) z sub-samplową interpolacją ułamkową.
- **Natywny Wirtualny Pad Xbox 360 (ViGEmBus):** Wykrywany bezpośrednio przez system Windows i gry platformy Steam bez konieczności stosowania zewnętrznych emulatorów DirectInput.
- **Dedykowane Profile Aparatur:**
  - **RadioMaster MT12 (Surface RC / Auta):** Koło kierownicy na osi X, trigger dzielony (Gaz na RT, Hamulec/Wsteczny na LT), trymery i przyciski funkcyjne.
  - **Mode 2 (Drony / Śmigłowce):** Gaz/Yaw lewy drążek, Roll/Pitch prawy drążek.
  - **Mode 1 (Samoloty):** Lotki/Przepustnica prawy drążek, Wysokość/Kierunek lewy drążek.
  - Własne profile użytkownika zapisywane w formacie JSON.
- **Kreator Kalibracji (Wizard):** 3-stopniowy asystent centrowania drążków (Subtrim), rejestracji zakresów Min/Max, regulacji strefy martwej (Deadband) oraz inwersji osi.
- **Minimalizacja do Zasobnika Systemowego (Tray):** Aplikacja działa w tle podczas rozgrywki bez obciążania procesora.

---

## 🛠️ Konfiguracja Aparatury (EdgeTX / OpenTX)

1. **Podłączenie Kabla:**
   - Użyj standardowego kabla audio mini-jack 3.5 mm (mono lub stereo).
   - Podłącz jeden koniec do gniazda **DSC / Trainer** w aparaturze, a drugi do gniazda **Mikrofonu / Line-In** w komputerze PC.
2. **Ustawienia w Aparaturze (EdgeTX / OpenTX / MT12):**
   - **Model Setup** -> **Trainer Mode:** `Master/Jack`
   - **Channels:** `8CH`
   - **Frame Length:** `22.5ms`
   - **Pulse Delay:** `300us`
   - **Polarity:** `POS (+)` lub `NEG (-)` (PPM-SIM wykrywa polaryzację automatycznie)
   - W modelach samochodowych (MT12): przypisz CH1 = Steering, CH2 = Throttle/Brake, CH3..CH8 = Switches/Trims.

---

## 📦 Wymagania i Instalacja

### Wymagania:
- System operacyjny Windows 10 / 11 (64-bit).
- Python 3.10 lub nowszy.
- Sterownik **ViGEmBus** (standard w Windows dla wirtualnych kontrolerów). Pobierz oficjalny instalator: [Wydania ViGEmBus na GitHubie](https://github.com/nefarius/ViGEmBus/releases).

### Instalacja Pakietów:
```bash
pip install -r requirements.txt
```

### Uruchomienie Aplikacji:
Kliknij dwukrotnie plik:
```cmd
run_ppm_sim.bat
```
Lub uruchom z wiersza poleceń:
```bash
python main.py
```

---

## 🧪 Testy Jednostkowe

Uruchomienie automatycznych testów sprawdzających dekodowanie PPM, histerezę, detekcję polaryzacji i mapowanie kontrolera:
```bash
pytest tests -v
```

---

## 📁 Struktura Projektu

```text
PPM-SIM/
├── main.py                    # Główny punkt startowy aplikacji
├── run_ppm_sim.bat            # Skrypt startowy 1-klik
├── requirements.txt           # Zależności Python (sounddevice, vgamepad, PySide6)
├── config.json                # Plik konfiguracji, profili i kalibracji
├── LICENSE                    # Licencja MIT
├── README.md                  # Dokumentacja w języku angielskim
├── README_PL.md               # Dokumentacja w języku polskim
├── core/
│   ├── audio_capture.py       # Przechwytywanie strumienia audio o niskim opóźnieniu
│   ├── ppm_decoder.py         # Silnik DSP dekodowania impulsów PPM z histerezą
│   ├── controller_mapper.py   # Translator kanałów na wirtualny pad Xbox 360 (ViGEm)
│   └── config_manager.py      # Menedżer zapisu i odczytu konfiguracji
├── ui/
│   ├── main_window.py         # Główne okno graficzne aplikacji (PySide6)
│   ├── oscilloscope_widget.py # Wykres oscyloskopu sygnału audio na żywo
│   ├── channel_bars_widget.py # Paski wskaźników 8 kanałów (µs i %)
│   ├── gamepad_preview.py     # Animowana wektorowa wizualizacja kontrolera
│   ├── calibration_dialog.py  # 3-etapowy interaktywny kreator kalibracji
│   └── theme.py               # Nowoczesny ciemny motyw graficzny QSS
└── tests/
    └── test_ppm_decoder.py    # Zestaw testów jednostkowych
```

---

## 📄 Licencja

Projekt udostępniony na licencji **MIT**. Szczegóły w pliku [LICENSE](LICENSE).
