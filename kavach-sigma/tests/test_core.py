import pytest
import numpy as np
from core.simulator import generate_noise, generate_bpsk, generate_qam, generate_fhss
from core.dsp_utils import compute_fft, compute_stft, denoise_signal
from core.classifier import RFClassifier, predict_modulation
import torch
import json

def test_generate_noise():
    """Test noise generation."""
    noise = generate_noise(1024, 10.0)
    assert len(noise) == 1024
    assert np.iscomplexobj(noise)

def test_generate_bpsk():
    """Test BPSK signal generation."""
    signal = generate_bpsk(1024, 10.0)
    assert len(signal) == 1024
    assert np.iscomplexobj(signal)

def test_generate_qam():
    """Test QAM signal generation."""
    signal = generate_qam(1024, 10.0)
    assert len(signal) == 1024
    assert np.iscomplexobj(signal)

def test_generate_fhss():
    """Test FHSS signal generation."""
    signal = generate_fhss(1024, 10.0)
    assert len(signal) == 1024
    assert np.iscomplexobj(signal)

def test_compute_fft():
    """Test FFT computation."""
    signal = generate_bpsk(1024, 10.0)
    fft_result = compute_fft(signal, 1024)
    assert len(fft_result) == 1024
    assert np.isrealobj(fft_result)

def test_compute_stft():
    """Test STFT computation."""
    signal = generate_bpsk(1024, 10.0)
    stft_result = compute_stft(signal, 256, 128)
    assert stft_result.shape[0] == 256
    assert np.isrealobj(stft_result)

def test_denoise_signal():
    """Test basic signal denoising."""
    signal = generate_bpsk(1024, 10.0)
    denoised = denoise_signal(signal, 0.5)
    assert len(denoised) == 1024
    assert np.iscomplexobj(denoised)

def test_rf_classifier_forward():
    """Test PyTorch classifier forward pass."""
    model = RFClassifier(num_classes=3, in_channels=2)
    # Shape: (batch, channels, length)
    x = torch.randn(1, 2, 1024)
    out = model(x)
    assert out.shape == (1, 3)

def test_predict_modulation():
    """Test prediction inference function."""
    model = RFClassifier()
    signal = generate_bpsk(1024, 10.0)
    prediction = predict_modulation(signal, model)
    assert prediction in ["BPSK", "QAM", "FHSS", "UNKNOWN"]
