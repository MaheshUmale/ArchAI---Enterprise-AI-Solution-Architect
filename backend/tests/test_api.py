import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "ArchAI" in response.json()["message"]

@patch("app.api.routes.graph.invoke")
def test_generate_design_mocked(mock_invoke):
    # Mock the graph response with the correct HLDDocument structure
    mock_invoke.return_value = {
        "final_hld": {
            "title": "Mock Design",
            "objective": "Design a test system.",
            "high_level_design": "This is a mocked HLD content.",
            "diagrams": [
                {
                    "view": "logical",
                    "mermaid_code": "graph TD; A-->B;",
                    "description": "Test diagram"
                }
            ],
            "decision_matrix": [],
            "risks_and_mitigations": [],
            "compliance_summary": "Compliant",
            "confidence_score": 95.0
        }
    }

    response = client.post("/api/design", json={
        "objective": "Design a test system."
    })

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Mock Design"
    assert data["confidence_score"] == 95.0
    mock_invoke.assert_called_once()
