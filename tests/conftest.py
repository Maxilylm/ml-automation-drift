"""Shared pytest fixtures for ml-automation-drift."""

import pytest


@pytest.fixture
def mock_llm_response():
    """LLM-response dict fixture."""
    return {
        "content": "Test response",
        "model": "claude-3-haiku",
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 10, "output_tokens": 20},
    }


@pytest.fixture
def sample_dataset():
    """10 row dicts fixture."""
    return [
        {"id": 1, "feature_a": 1.5, "feature_b": "cat", "target": 0},
        {"id": 2, "feature_a": 2.3, "feature_b": "dog", "target": 1},
        {"id": 3, "feature_a": 1.2, "feature_b": "cat", "target": 0},
        {"id": 4, "feature_a": 3.1, "feature_b": "bird", "target": 1},
        {"id": 5, "feature_a": 2.8, "feature_b": "dog", "target": 1},
        {"id": 6, "feature_a": 1.9, "feature_b": "cat", "target": 0},
        {"id": 7, "feature_a": 2.5, "feature_b": "bird", "target": 0},
        {"id": 8, "feature_a": 3.2, "feature_b": "dog", "target": 1},
        {"id": 9, "feature_a": 1.1, "feature_b": "cat", "target": 0},
        {"id": 10, "feature_a": 2.7, "feature_b": "bird", "target": 1},
    ]


@pytest.fixture
def temp_workspace(tmp_path):
    """Returns tmp_path fixture for temporary workspace."""
    return tmp_path
