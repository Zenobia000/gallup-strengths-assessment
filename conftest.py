"""
Test Configuration and Fixtures - Gallup Strengths Assessment

Global pytest configuration and shared fixtures for all tests.
Follows Linus Torvalds principles: simple, pragmatic, fail-fast.
"""

import sys
import os
import tempfile
import pytest
from pathlib import Path

# Add source directory to Python path for imports
src_path = Path(__file__).parent / "src" / "main" / "python"
sys.path.insert(0, str(src_path))

# Ensure test imports work
test_path = Path(__file__).parent / "src" / "test"
sys.path.insert(0, str(test_path))


@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture(scope="session")
def test_database_path(temp_dir):
    """Provide a temporary database path for testing."""
    return os.path.join(temp_dir, "test_gallup.db")


@pytest.fixture
def cleanup_test_data():
    """Clean up test data after each test."""
    # Setup (before test)
    yield
    # Cleanup (after test)
    # Any cleanup logic can go here


@pytest.fixture
def sample_assessment_responses():
    """Sample assessment responses for testing."""
    return [
        {"item_id": "ipip_001", "response": 7},  # Extraversion
        {"item_id": "ipip_002", "response": 2},  # Extraversion (reversed)
        {"item_id": "ipip_003", "response": 6},  # Extraversion
        {"item_id": "ipip_004", "response": 3},  # Extraversion (reversed)
        {"item_id": "ipip_005", "response": 5},  # Agreeableness
        {"item_id": "ipip_006", "response": 2},  # Agreeableness (reversed)
        {"item_id": "ipip_007", "response": 6},  # Agreeableness
        {"item_id": "ipip_008", "response": 1},  # Agreeableness (reversed)
        {"item_id": "ipip_009", "response": 7},  # Conscientiousness
        {"item_id": "ipip_010", "response": 2},  # Conscientiousness (reversed)
        {"item_id": "ipip_011", "response": 6},  # Conscientiousness
        {"item_id": "ipip_012", "response": 1},  # Conscientiousness (reversed)
        {"item_id": "ipip_013", "response": 3},  # Neuroticism
        {"item_id": "ipip_014", "response": 6},  # Neuroticism (reversed)
        {"item_id": "ipip_015", "response": 2},  # Neuroticism
        {"item_id": "ipip_016", "response": 7},  # Neuroticism (reversed)
        {"item_id": "ipip_017", "response": 6},  # Openness
        {"item_id": "ipip_018", "response": 2},  # Openness (reversed)
        {"item_id": "ipip_019", "response": 7},  # Openness
        {"item_id": "ipip_020", "response": 1},  # Openness (reversed)
    ]


@pytest.fixture
def sample_big_five_scores():
    """Sample Big Five personality scores for testing."""
    return {
        "extraversion": 75,
        "agreeableness": 82,
        "conscientiousness": 88,
        "neuroticism": 25,
        "openness": 90,
        "honesty_humility": 70
    }


@pytest.fixture
def sample_strength_scores():
    """Sample strength scores for testing."""
    return {
        "結構化執行": 85,
        "品質與完備": 78,
        "探索與創新": 92,
        "分析與洞察": 88,
        "影響與倡議": 72,
        "協作與共好": 85,
        "客戶導向": 80,
        "學習與成長": 90,
        "紀律與信任": 82,
        "壓力調節": 75,
        "衝突整合": 70,
        "責任與當責": 88
    }


# Pytest configuration hooks
def pytest_configure(config):
    """Configure pytest session."""
    # Create output directories
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    (output_dir / "logs").mkdir(exist_ok=True)
    (output_dir / "coverage").mkdir(exist_ok=True)


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add unit marker to unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add integration marker to integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add slow marker to tests that might be slow
        if "test_database" in item.name or "test_api" in item.name:
            item.add_marker(pytest.mark.slow)