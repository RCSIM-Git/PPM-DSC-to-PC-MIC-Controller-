"""PPM (Pulse Position Modulation) Signal Decoder.
Decodes real-time audio streams from RC transmitter trainer ports into multi-channel values.
Supports adaptive thresholding, edge detection, sub-sample interpolation, polarity auto-detection,
glitch rejection, and jitter smoothing.
"""

import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


class PPMDecoder:
    """High-performance real-time PPM signal decoder."""

    def __init__(
        self,
        sample_rate: int = 48000,
        num_channels: int = 8,
        min_pulse_us: float = 750.0,
        max_pulse_us: float = 2250.0,
        sync_min_us: float = 3000.0,
        polarity: str = "auto",  # "auto", "positive", "negative"
        smoothing: float = 0.35,  # 0.0 to 1.0 (EMA factor)
        deadband_us: float = 3.0,
    ):
        self.sample_rate = sample_rate
        self.num_channels = num_channels
        self.min_pulse_us = min_pulse_us
        self.max_pulse_us = max_pulse_us
        self.sync_min_us = sync_min_us
        self.polarity_config = polarity
        self.detected_polarity = "positive"
        self.smoothing = smoothing
        self.deadband_us = deadband_us

        # State machine variables
        self.last_state = 0  # 0 = Low, 1 = High
        self.last_edge_sample = 0.0  # Float for sub-sample accuracy
        self.current_sample_idx = 0
        self.current_channel_idx = 0
        self.temp_channels: List[float] = [1500.0] * self.num_channels

        # Output channels (smoothed and raw)
        self.channels_raw: List[float] = [1500.0] * self.num_channels
        self.channels_smooth: List[float] = [1500.0] * self.num_channels
        self.channels_normalized: List[float] = [0.0] * self.num_channels  # -1.0 to +1.0

        # Adaptive thresholding
        self.peak_pos = 0.5
        self.peak_neg = -0.5
        self.high_thresh = 0.2
        self.low_thresh = -0.2
        self.manual_threshold = 0.0
        self.adaptive_mode = True

        # Diagnostics & metrics
        self.frame_count = 0
        self.valid_frame_count = 0
        self.error_frame_count = 0
        self.fps = 0.0
        self.quality = 0.0  # 0.0 to 100.0%
        self.audio_peak_db = -60.0
        self.last_fps_time = time.time()
        self.fps_frame_counter = 0

        # Waveform oscilloscope buffer (ring buffer of last N samples)
        self.scope_buffer_size = 2048
        self.scope_waveform = np.zeros(self.scope_buffer_size, dtype=np.float32)
        self.scope_edges: List[int] = []

    def set_sample_rate(self, sample_rate: int) -> None:
        """Updates sample rate and resets timing state."""
        self.sample_rate = max(8000, sample_rate)
        self.reset()

    def reset(self) -> None:
        """Resets decoder internal state."""
        self.last_state = 0
        self.last_edge_sample = 0.0
        self.current_sample_idx = 0
        self.current_channel_idx = 0
        self.temp_channels = [1500.0] * self.num_channels
        self.channels_raw = [1500.0] * self.num_channels
        self.channels_smooth = [1500.0] * self.num_channels
        self.channels_normalized = [0.0] * self.num_channels
        self.frame_count = 0
        self.valid_frame_count = 0
        self.error_frame_count = 0

    def process_audio_block(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Processes a block of 1D float32 audio samples (range -1.0 to 1.0).

        Returns current channels and diagnostics dict.
        """
        if audio_data is None or len(audio_data) == 0:
            return self.get_state()

        samples = audio_data.flatten()
        n_samples = len(samples)

        # Update oscilloscope ring buffer
        if n_samples >= self.scope_buffer_size:
            self.scope_waveform[:] = samples[-self.scope_buffer_size:]
        else:
            self.scope_waveform = np.roll(self.scope_waveform, -n_samples)
            self.scope_waveform[-n_samples:] = samples

        # Update peak amplitude & dBFS
        max_abs = float(np.max(np.abs(samples))) if n_samples > 0 else 0.0
        if max_abs > 1e-5:
            self.audio_peak_db = 20.0 * np.log10(max(1e-5, max_abs))
        else:
            self.audio_peak_db = -60.0

        # Update adaptive thresholds
        if self.adaptive_mode:
            current_max = float(np.max(samples))
            current_min = float(np.min(samples))
            self.peak_pos = 0.95 * self.peak_pos + 0.05 * current_max
            self.peak_neg = 0.95 * self.peak_neg + 0.05 * current_min
            mid = (self.peak_pos + self.peak_neg) / 2.0
            span = max(0.05, (self.peak_pos - self.peak_neg))
            self.high_thresh = mid + span * 0.20
            self.low_thresh = mid - span * 0.20
        else:
            self.high_thresh = self.manual_threshold + 0.1
            self.low_thresh = self.manual_threshold - 0.1

        # Determine active polarity
        active_polarity = self.polarity_config
        if active_polarity == "auto":
            # Heuristic: Sync gap occupies majority of idle time.
            # If idle signal is positive, falling edges define pulses (negative polarity).
            # If idle signal is negative, rising edges define pulses (positive polarity).
            active_polarity = self.detected_polarity

        us_per_sample = 1_000_000.0 / self.sample_rate

        # Process samples through Schmitt Trigger
        for i in range(n_samples):
            val = samples[i]
            sample_pos = self.current_sample_idx + i

            if self.last_state == 0 and val >= self.high_thresh:
                # Rising edge detected (0 -> 1)
                self.last_state = 1
                # Sub-sample interpolation
                prev_val = samples[i - 1] if i > 0 else self.low_thresh
                frac = 0.0
                if abs(val - prev_val) > 1e-6:
                    frac = (self.high_thresh - prev_val) / (val - prev_val)
                    frac = np.clip(frac, 0.0, 1.0)
                edge_exact = (sample_pos - 1.0) + frac

                if active_polarity in ("positive", "auto"):
                    self._handle_pulse_edge(edge_exact, us_per_sample, edge_type="rising")

            elif self.last_state == 1 and val <= self.low_thresh:
                # Falling edge detected (1 -> 0)
                self.last_state = 0
                # Sub-sample interpolation
                prev_val = samples[i - 1] if i > 0 else self.high_thresh
                frac = 0.0
                if abs(prev_val - val) > 1e-6:
                    frac = (prev_val - self.low_thresh) / (prev_val - val)
                    frac = np.clip(frac, 0.0, 1.0)
                edge_exact = (sample_pos - 1.0) + frac

                if active_polarity in ("negative", "auto"):
                    self._handle_pulse_edge(edge_exact, us_per_sample, edge_type="falling")

        self.current_sample_idx += n_samples

        # Periodically compute FPS and Quality metrics
        now = time.time()
        dt = now - self.last_fps_time
        if dt >= 0.5:
            self.fps = self.fps_frame_counter / dt
            total = self.valid_frame_count + self.error_frame_count
            if total > 0:
                self.quality = (self.valid_frame_count / total) * 100.0
            else:
                self.quality = 0.0
            self.fps_frame_counter = 0
            self.valid_frame_count = 0
            self.error_frame_count = 0
            self.last_fps_time = now

        return self.get_state()

    def _handle_pulse_edge(self, edge_sample: float, us_per_sample: float, edge_type: str) -> None:
        """Processes an edge timestamp in samples."""
        if self.last_edge_sample <= 0.0:
            self.last_edge_sample = edge_sample
            return

        delta_samples = edge_sample - self.last_edge_sample
        self.last_edge_sample = edge_sample

        pulse_us = delta_samples * us_per_sample

        # Check if this pulse is a Sync gap (> sync_min_us, typically > 3000-4000µs)
        if pulse_us >= self.sync_min_us:
            # End of PPM frame!
            if self.current_channel_idx >= 4:
                # Valid frame detected with at least 4 channels
                self._commit_frame()
                self.valid_frame_count += 1
                self.fps_frame_counter += 1
                if self.polarity_config == "auto":
                    self.detected_polarity = "positive" if edge_type == "rising" else "negative"
            else:
                self.error_frame_count += 1

            # Reset channel counter for next frame
            self.current_channel_idx = 0
            self.frame_count += 1

        elif self.min_pulse_us <= pulse_us <= self.max_pulse_us:
            # Valid channel pulse
            if self.current_channel_idx < self.num_channels:
                self.temp_channels[self.current_channel_idx] = pulse_us
                self.current_channel_idx += 1
        else:
            # Glitch / noise pulse (< min_pulse_us or > max_pulse_us but < sync_min_us)
            pass

    def _commit_frame(self) -> None:
        """Validates and updates smoothed channel outputs upon sync gap."""
        alpha = self.smoothing
        for i in range(self.num_channels):
            raw_val = self.temp_channels[i]
            self.channels_raw[i] = raw_val

            # Apply deadband to reject micro-jitter
            prev_smooth = self.channels_smooth[i]
            if abs(raw_val - prev_smooth) < self.deadband_us:
                val = prev_smooth
            else:
                # EMA filter
                val = alpha * raw_val + (1.0 - alpha) * prev_smooth

            self.channels_smooth[i] = val

            # Normalize to -1.0 .. +1.0 (assuming standard 1000µs to 2000µs center 1500µs)
            norm = (val - 1500.0) / 500.0
            self.channels_normalized[i] = float(np.clip(norm, -1.0, 1.0))

    def get_state(self) -> Dict[str, Any]:
        """Returns dictionary of all current channels and diagnostics."""
        return {
            "channels_raw": list(self.channels_raw),
            "channels_smooth": list(self.channels_smooth),
            "channels_normalized": list(self.channels_normalized),
            "num_channels": self.num_channels,
            "fps": round(self.fps, 1),
            "quality": round(self.quality, 1),
            "audio_peak_db": round(self.audio_peak_db, 1),
            "detected_polarity": self.detected_polarity,
            "high_thresh": round(self.high_thresh, 3),
            "low_thresh": round(self.low_thresh, 3),
            "frame_count": self.frame_count,
        }
