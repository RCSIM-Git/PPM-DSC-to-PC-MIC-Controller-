"""Audio Capture Module for PPM-SIM.
Captures real-time low-latency audio from selected input device using sounddevice.
"""

from typing import Callable, Dict, List, Optional
import numpy as np
import sounddevice as sd


class AudioCapture:
    """Manages audio input stream for PPM signal reception."""

    def __init__(
        self,
        callback: Optional[Callable[[np.ndarray], None]] = None,
        device_index: Optional[int] = None,
        sample_rate: int = 48000,
        block_size: int = 256,
        channel_index: int = 0,  # 0 = Left, 1 = Right, -1 = Mix/Max
    ):
        self.callback = callback
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.channel_index = channel_index

        self.stream: Optional[sd.InputStream] = None
        self.is_running = False
        self.last_error: Optional[str] = None

    @staticmethod
    def list_input_devices() -> List[Dict[str, any]]:
        """Returns list of all available audio input devices."""
        devices = []
        try:
            dev_list = sd.query_devices()
            host_apis = sd.query_hostapis()
            default_in = sd.default.device[0]

            for idx, dev in enumerate(dev_list):
                if dev.get("max_input_channels", 0) > 0:
                    api_name = host_apis[dev["hostapi"]]["name"] if "hostapi" in dev else "Audio"
                    is_default = (idx == default_in)
                    devices.append({
                        "index": idx,
                        "name": dev.get("name", f"Device {idx}"),
                        "hostapi": api_name,
                        "channels": dev.get("max_input_channels", 1),
                        "default_samplerate": int(dev.get("default_samplerate", 48000)),
                        "is_default": is_default,
                        "display_name": f"[{idx}] {dev.get('name', 'Mic')} ({api_name})"
                    })
        except Exception as e:
            print(f"[AudioCapture] Error querying audio devices: {e}")
        return devices

    def start(self, device_index: Optional[int] = None, sample_rate: Optional[int] = None) -> bool:
        """Starts real-time audio capture."""
        if self.is_running:
            self.stop()

        if device_index is not None:
            self.device_index = device_index
        if sample_rate is not None:
            self.sample_rate = sample_rate

        self.last_error = None

        try:
            # Query device info
            dev_info = sd.query_devices(self.device_index, "input") if self.device_index is not None else sd.query_devices(kind="input")
            channels = min(2, max(1, dev_info.get("max_input_channels", 1)))

            def _audio_callback(indata, frames, time_info, status):
                if status:
                    # e.g. input overflow
                    pass
                if not self.is_running or self.callback is None:
                    return

                # Extract target channel
                if indata.ndim == 2:
                    if self.channel_index == 0:
                        mono = indata[:, 0]
                    elif self.channel_index == 1 and indata.shape[1] > 1:
                        mono = indata[:, 1]
                    else:
                        # Auto: pick channel with highest peak energy
                        if np.max(np.abs(indata[:, 0])) >= (np.max(np.abs(indata[:, 1])) if indata.shape[1] > 1 else 0):
                            mono = indata[:, 0]
                        else:
                            mono = indata[:, 1]
                else:
                    mono = indata.flatten()

                self.callback(mono)

            self.stream = sd.InputStream(
                device=self.device_index,
                channels=channels,
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                dtype="float32",
                latency="low",
                callback=_audio_callback,
            )
            self.stream.start()
            self.is_running = True
            print(f"[AudioCapture] Stream started on device {self.device_index} @ {self.sample_rate}Hz (block size: {self.block_size})")
            return True

        except Exception as e:
            self.last_error = str(e)
            self.is_running = False
            print(f"[AudioCapture] Failed to start audio stream: {e}")
            return False

    def stop(self) -> None:
        """Stops the audio stream."""
        self.is_running = False
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                print(f"[AudioCapture] Error closing stream: {e}")
            finally:
                self.stream = None
        print("[AudioCapture] Stream stopped.")
