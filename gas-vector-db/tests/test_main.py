import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_chroma():
    with patch("src.core.vector_store.chromadb.HttpClient") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def client(mock_chroma):
    from src.main import app
    from src.core.vector_store import VectorStore
    
    # We patch vector store to not really connect during app init
    with patch("src.main.VectorStore") as MockStore:
        mock_store_instance = MagicMock()
        MockStore.return_value = mock_store_instance
        app.state.store = mock_store_instance
        with TestClient(app) as client:
            yield client

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
