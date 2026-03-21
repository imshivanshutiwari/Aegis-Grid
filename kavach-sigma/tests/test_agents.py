import pytest
import numpy as np
from agents.analyst_agent import AnalystAgent
from agents.tactical_agent import TacticalAgent
from agents.elint_agent import ELINTAgent
from memory.vector_store import VectorStoreClient
from memory.knowledge_loader import KnowledgeLoader
from agents.orchestrator import run_orchestrator
import json

def test_analyst_agent():
    """Test the Analyst Agent."""
    agent = AnalystAgent()
    signal = np.random.randn(1024) + 1j * np.random.randn(1024)
    result = agent.analyze_signal(signal)

    assert "modulation" in result
    assert "power_db" in result
    assert "intent" in result
    assert "confidence" in result

def test_tactical_agent():
    """Test the Tactical Agent."""
    roe = ["Prioritize FHSS jamming", "Do not jam BPSK"]
    agent = TacticalAgent(roe)

    threat_data = {"modulation": "FHSS"}
    result = agent.determine_countermeasure(threat_data)

    assert result["countermeasure_action"] == "Initiate wideband barrage jamming."
    assert result["emcon_level"] == "EMCON 1"

    threat_data = {"modulation": "QAM"}
    result = agent.determine_countermeasure(threat_data)

    assert result["countermeasure_action"] == "Initiate targeted spot jamming."
    assert result["emcon_level"] == "EMCON 2"

    threat_data = {"modulation": "BPSK"}
    result = agent.determine_countermeasure(threat_data)

    assert result["countermeasure_action"] == "Monitor and log signal."
    assert result["emcon_level"] == "EMCON 3"

def test_elint_agent():
    """Test the ELINT Agent."""
    client = VectorStoreClient("localhost", 6333)
    agent = ELINTAgent(client)

    signal_features = {"modulation": "FHSS"}
    result = agent.contextualize_signal(signal_features)

    assert "matches" in result
    assert "eob_confidence" in result
    assert isinstance(result["matches"], list)

def test_vector_store_client():
    """Test VectorStoreClient."""
    client = VectorStoreClient("localhost", 6333)
    assert client.create_collection(768) is True

    vectors = np.random.rand(2, 768)
    metadata = [{"meta": "data1"}, {"meta": "data2"}]
    assert client.insert_vectors(vectors, metadata) is True

    results = client.search_vectors("query")
    assert isinstance(results, list)
    assert len(results) > 0

def test_vector_store_client_error():
    """Test VectorStoreClient handles mismatched vector sizes."""
    client = VectorStoreClient("localhost", 6333)
    vectors = np.random.rand(2, 768)
    metadata = [{"meta": "data1"}]
    with pytest.raises(ValueError):
         client.insert_vectors(vectors, metadata)

def test_knowledge_loader(tmp_path):
    """Test KnowledgeLoader."""
    client = VectorStoreClient("localhost", 6333)
    loader = KnowledgeLoader(client)

    # Create temporary json
    json_path = tmp_path / "data.json"
    data = [{"id": 1, "text": "test"}]
    with open(json_path, "w") as f:
        json.dump(data, f)

    loaded = loader.load_from_json(str(json_path))
    assert loaded == data

    # Test error file
    loaded_error = loader.load_from_json("nonexistent.json")
    assert loaded_error == []

    # Test ingest
    assert loader.ingest_to_vector_store(loaded) is True

    # Test ingest empty
    assert loader.ingest_to_vector_store([]) is False

def test_orchestrator():
    """Test the Orchestrator loop."""
    valid_input = json.dumps({"type": "FHSS", "length": 512, "snr": 15.0})
    result = run_orchestrator(valid_input)
    assert result["status"] == "success"
    assert result["signal_parameters"]["length"] == 512
    assert "perception" in result
    assert "action" in result

    invalid_input = "not json"
    result = run_orchestrator(invalid_input)
    assert result["status"] == "success"
    assert result["signal_parameters"]["length"] == 1024
