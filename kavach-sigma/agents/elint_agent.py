import logging
from typing import Dict, Any, List
from memory.vector_store import VectorStoreClient

logger = logging.getLogger(__name__)

class ELINTAgent:
    """
    RAG-based agent for retrieving known military signal specifications (EOB).
    """

    def __init__(self, qdrant_client: VectorStoreClient):
        """
        Initializes the ELINT Agent with access to the Qdrant vector database.

        Args:
            qdrant_client (VectorStoreClient): Initialized client for the vector database.
        """
        self.vector_store = qdrant_client

    def query_eob(self, query: str) -> List[Dict[str, Any]]:
        """
        Queries the Electronic Order of Battle (EOB) vector database.

        Args:
            query (str): The search query, typically a description of the signal.

        Returns:
            List[Dict[str, Any]]: Matched known signal signatures.
        """
        logger.info(f"Querying EOB with: {query}")
        return self.vector_store.search_vectors(query, limit=3)

    def contextualize_signal(self, signal_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieves context for a signal based on "Red Zone" locations or features.

        Args:
            signal_features (Dict[str, Any]): Dictionary of extracted features.

        Returns:
            Dict[str, Any]: Additional context from the knowledge base.
        """
        modulation = signal_features.get("modulation", "UNKNOWN")
        query = f"Known adversaries using {modulation} modulation"
        matches = self.query_eob(query)

        return {
            "matches": matches,
            "eob_confidence": 0.9 if matches else 0.1
        }
