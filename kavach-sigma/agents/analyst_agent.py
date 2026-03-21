from typing import List, Dict, Any
from core.classifier import predict_modulation, RFClassifier
import numpy as np

class AnalystAgent:
    """
    Analyzes RF signals to determine their intent and extracts relevant features.
    """

    def __init__(self, model_path: str = "models/rf_classifier.pth"):
        """
        Initializes the AnalystAgent with an RF classifier.

        Args:
            model_path (str): Path to the pre-trained classifier model.
        """
        self.classifier = RFClassifier(num_classes=3, in_channels=2)
        # Placeholder for loading weights if needed
        # self.classifier.load_state_dict(torch.load(model_path))
        self.model_path = model_path

    def analyze_signal(self, signal: np.ndarray) -> Dict[str, Any]:
        """
        Takes raw RF signal and performs initial intent analysis.

        Args:
            signal (np.ndarray): The captured complex RF signal.

        Returns:
            Dict[str, Any]: Extracted features and initial modulation classification.
        """
        modulation_type = predict_modulation(signal, self.classifier)

        # Calculate some signal characteristics
        power = float(np.mean(np.abs(signal)**2))

        return {
            "modulation": modulation_type,
            "power_db": 10 * np.log10(power + 1e-12),
            "intent": "Unknown",
            "confidence": 0.85
        }
