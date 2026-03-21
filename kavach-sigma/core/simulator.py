import numpy as np

def generate_noise(length: int, snr_db: float) -> np.ndarray:
    """
    Generate complex white Gaussian noise.

    Args:
        length (int): Length of the noise sequence.
        snr_db (float): Signal-to-noise ratio in decibels.

    Returns:
        np.ndarray: Complex numpy array containing the noise.
    """
    # Calculate noise power based on SNR
    noise_power = 10 ** (-snr_db / 10.0)
    noise = (np.random.normal(scale=np.sqrt(noise_power / 2.0), size=length) +
             1j * np.random.normal(scale=np.sqrt(noise_power / 2.0), size=length))
    return noise

def generate_bpsk(length: int, snr_db: float) -> np.ndarray:
    """
    Generate a synthetic BPSK signal with additive white Gaussian noise.

    Args:
        length (int): Number of samples to generate.
        snr_db (float): Signal-to-noise ratio in decibels.

    Returns:
        np.ndarray: Complex numpy array representing the simulated BPSK signal.
    """
    symbols = np.random.choice([-1, 1], size=length)
    noise = generate_noise(length, snr_db)
    return symbols + noise

def generate_qam(length: int, snr_db: float) -> np.ndarray:
    """
    Generate a synthetic 16-QAM signal with additive white Gaussian noise.

    Args:
        length (int): Number of samples to generate.
        snr_db (float): Signal-to-noise ratio in decibels.

    Returns:
        np.ndarray: Complex numpy array representing the simulated 16-QAM signal.
    """
    qam_symbols = np.array([-3-3j, -3-1j, -3+3j, -3+1j,
                            -1-3j, -1-1j, -1+3j, -1+1j,
                             3-3j,  3-1j,  3+3j,  3+1j,
                             1-3j,  1-1j,  1+3j,  1+1j])

    # Normalize power to 1
    qam_symbols = qam_symbols / np.sqrt(10)

    symbols = np.random.choice(qam_symbols, size=length)
    noise = generate_noise(length, snr_db)
    return symbols + noise

def generate_fhss(length: int, snr_db: float) -> np.ndarray:
    """
    Generate a synthetic FHSS (Frequency Hopping Spread Spectrum) signal.
    Simplified as a multi-tone signal for simulation purposes.

    Args:
        length (int): Number of samples to generate.
        snr_db (float): Signal-to-noise ratio in decibels.

    Returns:
        np.ndarray: Complex numpy array representing the simulated FHSS signal.
    """
    t = np.arange(length)
    # Hop across a few random frequencies
    frequencies = np.random.uniform(0.1, 0.4, size=5)
    signal = np.zeros(length, dtype=complex)

    hop_length = length // 5
    for i in range(5):
        start = i * hop_length
        end = (i + 1) * hop_length if i < 4 else length
        signal[start:end] = np.exp(2j * np.pi * frequencies[i] * t[start:end])

    noise = generate_noise(length, snr_db)
    return signal + noise
