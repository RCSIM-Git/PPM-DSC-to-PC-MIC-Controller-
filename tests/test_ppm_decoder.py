"""Unit tests for PPMDecoder and ControllerMapper."""

import numpy as np
import pytest
from core.ppm_decoder import PPMDecoder
from core.controller_mapper import ControllerMapper
from core.config_manager import ConfigManager


def generate_synthetic_ppm(
    channels_us: list[float],
    sample_rate: int = 48000,
    frame_period_ms: float = 22.5,
    pulse_sep_us: float = 300.0,
    polarity: str = "positive",
    noise_amplitude: float = 0.02,
) -> np.ndarray:
    """Generates a synthetic audio waveform representing a stream of PPM frames."""
    total_frame_us = frame_period_ms * 1000.0
    channel_sum_us = sum(channels_us)
    sync_gap_us = total_frame_us - channel_sum_us

    # Generate 3 consecutive frames
    full_signal = []
    us_per_sample = 1_000_000.0 / sample_rate

    for _ in range(4):
        # Generate N channel pulses
        for ch_us in channels_us:
            active_us = ch_us - pulse_sep_us
            n_sep = int(round(pulse_sep_us / us_per_sample))
            n_active = int(round(active_us / us_per_sample))

            if polarity == "positive":
                # Positive PPM: pulse is HIGH for separator, LOW for rest of channel
                full_signal.extend([0.8] * n_sep)
                full_signal.extend([-0.8] * n_active)
            else:
                # Negative PPM: pulse is LOW for separator, HIGH for rest of channel
                full_signal.extend([-0.8] * n_sep)
                full_signal.extend([0.8] * n_active)

        # Stop pulse (Pulse N+1) marking the end of last channel and beginning of sync
        n_sep = int(round(pulse_sep_us / us_per_sample))
        if polarity == "positive":
            full_signal.extend([0.8] * n_sep)
            # Sync gap stays LOW until next frame
            n_sync = int(round((sync_gap_us - pulse_sep_us) / us_per_sample))
            full_signal.extend([-0.8] * n_sync)
        else:
            full_signal.extend([-0.8] * n_sep)
            # Sync gap stays HIGH until next frame
            n_sync = int(round((sync_gap_us - pulse_sep_us) / us_per_sample))
            full_signal.extend([0.8] * n_sync)

    samples = np.array(full_signal, dtype=np.float32)
    # Add subtle white noise
    noise = np.random.normal(0.0, noise_amplitude, size=len(samples)).astype(np.float32)
    return np.clip(samples + noise, -1.0, 1.0)


def test_ppm_decoder_positive_waveform():
    """Verifies that PPMDecoder accurately recovers channel widths from positive PPM."""
    sample_rate = 48000
    expected_channels = [1000.0, 1200.0, 1500.0, 1750.0, 2000.0, 1500.0, 1100.0, 1900.0]

    audio = generate_synthetic_ppm(expected_channels, sample_rate=sample_rate, polarity="positive")
    decoder = PPMDecoder(sample_rate=sample_rate, num_channels=8, polarity="positive", smoothing=0.8)

    # Process in realistic block sizes (256 samples per block)
    block_size = 256
    for i in range(0, len(audio), block_size):
        block = audio[i:i + block_size]
        decoder.process_audio_block(block)

    state = decoder.get_state()
    decoded = state["channels_raw"]

    for ch_idx, (exp, dec) in enumerate(zip(expected_channels, decoded)):
        # Accuracy tolerance: ±25µs (within 1-2 audio samples at 48kHz)
        assert abs(exp - dec) < 30.0, f"Channel {ch_idx + 1}: Expected {exp}µs, got {dec}µs"


def test_ppm_decoder_negative_waveform():
    """Verifies that PPMDecoder accurately recovers channel widths from negative PPM."""
    sample_rate = 48000
    expected_channels = [1500.0, 1000.0, 2000.0, 1500.0, 1300.0, 1700.0, 1500.0, 1500.0]

    audio = generate_synthetic_ppm(expected_channels, sample_rate=sample_rate, polarity="negative")
    decoder = PPMDecoder(sample_rate=sample_rate, num_channels=8, polarity="negative", smoothing=0.8)

    block_size = 256
    for i in range(0, len(audio), block_size):
        block = audio[i:i + block_size]
        decoder.process_audio_block(block)

    state = decoder.get_state()
    decoded = state["channels_raw"]

    for ch_idx, (exp, dec) in enumerate(zip(expected_channels, decoded)):
        assert abs(exp - dec) < 30.0, f"Channel {ch_idx + 1}: Expected {exp}µs, got {dec}µs"


def test_controller_mapper_calibration():
    """Verifies channel calibration, deadband, and normalization."""
    config_mgr = ConfigManager()
    mapper = ControllerMapper(config_mgr)

    # Test center (1500µs -> 0.0)
    assert mapper.calibrate_channel_value("CH1", 1500.0) == 0.0

    # Test deadband near center (1505µs -> 0.0)
    assert mapper.calibrate_channel_value("CH1", 1505.0) == 0.0

    # Test full min (1000µs -> -1.0)
    assert mapper.calibrate_channel_value("CH1", 1000.0) == -1.0

    # Test full max (2000µs -> +1.0)
    assert mapper.calibrate_channel_value("CH1", 2000.0) == 1.0


def test_controller_mapper_mt12_profile():
    """Verifies MT12 surface RC split trigger and steering wheel mapping."""
    config_mgr = ConfigManager()
    mapper = ControllerMapper(config_mgr)
    mapper.set_profile("RadioMaster MT12 (Surface RC)")

    # CH1 = 2000µs (Full Right Steering), CH2 = 2000µs (Full Throttle)
    channels = [2000.0, 2000.0, 1500.0, 1500.0, 1000.0, 1000.0, 1000.0, 1000.0]
    preview = mapper.update_channels(channels)

    assert preview["left_stick_x"] == 1.0
    assert preview["right_trigger"] == 1.0
    assert preview["left_trigger"] == 0.0

    # CH2 = 1000µs (Full Brake/Reverse)
    channels[1] = 1000.0
    preview = mapper.update_channels(channels)
    assert preview["right_trigger"] == 0.0
    assert preview["left_trigger"] == 1.0
