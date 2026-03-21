import json
import logging
from typing import List, Dict, Any
from memory.vector_store import VectorStoreClient
import numpy as np

logger = logging.getLogger(__name__)

class KnowledgeLoader:
    """
    Handles the ingestion and vectorization of military signal specifications (EOB).
    """

    def __init__(self, vector_store: VectorStoreClient):
        """
        Initializes the KnowledgeLoader with a connected VectorStoreClient.

        Args:
            vector_store (VectorStoreClient): Client for storing the vectorized knowledge.
        """
        self.vector_store = vector_store

    def load_from_json(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Reads a JSON file containing signal specifications.

        Args:
            filepath (str): Path to the JSON file.

        Returns:
            List[Dict[str, Any]]: List of dictionary entries representing the EOB.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} records from {filepath}")
            return data
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            return []

    def ingest_to_vector_store(self, data: List[Dict[str, Any]]) -> bool:
        """
        Converts the data to mock embeddings and inserts them into the vector database.

        Args:
            data (List[Dict[str, Any]]): The loaded metadata from a file.

        Returns:
            bool: True if ingestion was successful.
        """
        if not data:
            logger.warning("No data provided for ingestion.")
            return False

        # Generate mock embeddings for the text data
        vector_size = 768
        mock_embeddings = np.random.rand(len(data), vector_size)

        # Ensure collection exists before inserting
        self.vector_store.create_collection(vector_size=vector_size)

        return self.vector_store.insert_vectors(mock_embeddings, data)
