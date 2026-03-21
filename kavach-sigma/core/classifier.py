import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class RFClassifier(nn.Module):
    """
    A PyTorch model for real-time RF modulation detection and classification.
    Classifies raw signals into BPSK, QAM, FHSS, etc.
    """

    def __init__(self, num_classes: int = 3, in_channels: int = 2):
        """
        Initialize the PyTorch classifier architecture.

        Args:
            num_classes (int): Number of modulation classes to predict.
            in_channels (int): Input feature channels (e.g., I and Q components).
        """
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels=in_channels, out_channels=64, kernel_size=8, padding="same")
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=4, padding="same")

        self.pool = nn.MaxPool1d(kernel_size=2)

        # For a sequence length of 1024:
        # padding="same" keeps length at 1024 for convolutions.
        # Pool 1 (kernel_size=2): 1024 -> 512
        # Pool 2 (kernel_size=2): 512 -> 256
        # Output channels from conv2 is 128. Flattened size = 256 * 128 = 32768
        # However, for lengths of 256, it would be 256 -> 128 -> 64. 64 * 128 = 8192
        # To make it dynamic, we can compute the flatten size dynamically in forward,
        # but nn.Linear requires in_features at init.
        # So we use an adaptive pooling layer instead.
        self.adaptive_pool = nn.AdaptiveAvgPool1d(256)
        self.fc1 = nn.Linear(128 * 256, 128)
        self.fc2 = nn.Linear(128, num_classes)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for the PyTorch RF modulation classifier.

        Args:
            x (torch.Tensor): Input tensor of shape (batch, channels, seq_length).

        Returns:
            torch.Tensor: Logits for the predicted modulation classes.
        """
        x = F.relu(self.conv1(x))
        x = self.pool(x)

        x = F.relu(self.conv2(x))
        x = self.pool(x)

        # Adaptive pooling to ensure fixed size before dense layer
        x = self.adaptive_pool(x)

        # Flatten the features for the dense layers
        x = torch.flatten(x, start_dim=1)

        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)

        return x

def predict_modulation(signal: np.ndarray, model: nn.Module) -> str:
    """
    Inference loop that classifies a given signal using the PyTorch model.

    Args:
        signal (np.ndarray): Complex numpy array of the input signal.
        model (nn.Module): Trained PyTorch classifier model.

    Returns:
        str: Predicted modulation type as a string label.
    """
    model.eval()

    # Preprocess I/Q components
    i_comp = np.real(signal)
    q_comp = np.imag(signal)

    # Expand dims to match (batch, channels, seq_length)
    input_tensor = torch.tensor(np.stack((i_comp, q_comp)), dtype=torch.float32).unsqueeze(0)

    # Forward pass and predict
    with torch.no_grad():
        logits = model(input_tensor)
        predicted_idx = torch.argmax(logits, dim=1).item()

    class_map = {0: "BPSK", 1: "QAM", 2: "FHSS"}
    return class_map.get(predicted_idx, "UNKNOWN")
