import numpy as np

def compute_fft(signal: np.ndarray, nfft: int = 1024) -> np.ndarray:
    """
    Compute the Fast Fourier Transform (FFT) of a given signal.

    Args:
        signal (np.ndarray): Complex or real signal array.
        nfft (int, optional): Number of FFT points. Defaults to 1024.

    Returns:
        np.ndarray: Computed FFT magnitude array.
    """
    # Calculate the normalized magnitude spectrum
    spectrum = np.abs(np.fft.fftshift(np.fft.fft(signal, n=nfft)))
    return 20 * np.log10(spectrum + 1e-12)

def compute_stft(signal: np.ndarray, window_size: int = 256, overlap: int = 128) -> np.ndarray:
    """
    Compute the Short-Time Fourier Transform (STFT) for spectrogram generation.

    Args:
        signal (np.ndarray): Input complex or real signal array.
        window_size (int, optional): Window length for the STFT. Defaults to 256.
        overlap (int, optional): Number of overlapping points between segments. Defaults to 128.

    Returns:
        np.ndarray: 2D array representing the spectrogram magnitude.
    """
    # A simplified implementation of STFT for DSP analysis
    step = window_size - overlap
    num_segments = (len(signal) - window_size) // step + 1

    spectrogram = np.zeros((window_size, num_segments))
    window = np.hanning(window_size)

    for i in range(num_segments):
        start_idx = i * step
        segment = signal[start_idx:start_idx + window_size] * window
        fft_result = np.fft.fft(segment)
        spectrogram[:, i] = np.abs(np.fft.fftshift(fft_result))

    return 20 * np.log10(spectrogram + 1e-12)

def denoise_signal(signal: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """
    Apply a basic soft-thresholding to denoise a signal in the frequency domain.

    Args:
        signal (np.ndarray): Input complex or real signal.
        threshold (float, optional): Threshold value for filtering. Defaults to 0.5.

    Returns:
        np.ndarray: Denoised time-domain signal.
    """
    fft_signal = np.fft.fft(signal)

    # Simple hard thresholding based on magnitude
    magnitude = np.abs(fft_signal)
    max_mag = np.max(magnitude)
    mask = magnitude > (threshold * max_mag)

    filtered_fft = fft_signal * mask
    denoised_signal = np.fft.ifft(filtered_fft)

    return denoised_signal
