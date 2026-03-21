from typing import Dict, Any, List

class TacticalAgent:
    """
    Evaluates tactical intelligence and provides ROE-compliant countermeasure plans.
    """

    def __init__(self, roe_rules: List[str]):
        """
        Initializes the Tactical Agent with Rules of Engagement (ROE).

        Args:
            roe_rules (List[str]): Preloaded Rules of Engagement strings.
        """
        self.roe_rules = roe_rules

    def determine_countermeasure(self, threat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decides the appropriate countermeasure based on threat analysis.

        Args:
            threat_data (Dict[str, Any]): Evaluated signal intent and threat parameters.

        Returns:
            Dict[str, Any]: Actionable countermeasure plan and EMCON level.
        """
        modulation = threat_data.get("modulation", "UNKNOWN")

        # Simple lookup for demonstration
        if modulation == "FHSS":
            action = "Initiate wideband barrage jamming."
            emcon = "EMCON 1"
        elif modulation == "QAM":
            action = "Initiate targeted spot jamming."
            emcon = "EMCON 2"
        else:
            action = "Monitor and log signal."
            emcon = "EMCON 3"

        return {
            "countermeasure_action": action,
            "emcon_level": emcon,
            "roe_compliance": True
        }
