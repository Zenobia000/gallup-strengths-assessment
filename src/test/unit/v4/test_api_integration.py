"""
Test v4.0 API Integration
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../main/python'))

import requests
import json
from pathlib import Path


def test_v4_health():
    """Test v4 health endpoint"""
    response = requests.get("http://localhost:8004/api/v4/health")
    print(f"Health Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    assert response.status_code == 200
    assert response.json()["version"] == "4.0.0"


def test_get_blocks():
    """Test getting assessment blocks"""
    response = requests.get(
        "http://localhost:8004/api/v4/assessment/blocks",
        params={"block_count": 5}
    )

    print(f"Blocks Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Session ID: {data['session_id']}")
        print(f"Total blocks: {data['total_blocks']}")
        print(f"First block: {json.dumps(data['blocks'][0], indent=2)}")
    else:
        print(f"Error: {json.dumps(response.json(), indent=2)}")

    return response.json() if response.status_code == 200 else None


def test_submit_responses():
    """Test submitting assessment responses"""

    # First get blocks
    blocks_data = test_get_blocks()
    if not blocks_data:
        print("Failed to get blocks")
        return

    # Create sample responses
    responses = []
    for i, block in enumerate(blocks_data['blocks']):
        responses.append({
            "block_id": block['block_id'],
            "most_like_index": 0,
            "least_like_index": 3,
            "response_time_ms": 5000 + i * 100
        })

    # Submit responses
    submit_data = {
        "session_id": blocks_data['session_id'],
        "responses": responses,
        "completion_time_seconds": 150
    }

    response = requests.post(
        "http://localhost:8004/api/v4/assessment/submit",
        json=submit_data
    )

    print(f"Submit Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Top Strengths: {data['top_strengths'][:3]}")
        print(f"Profile Type: {data['profile_type']}")
    else:
        print(f"Error: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    print("=" * 60)
    print("V4.0 API Integration Test")
    print("=" * 60)

    print("\n1. Testing Health Endpoint:")
    test_v4_health()

    print("\n2. Testing Blocks Endpoint:")
    blocks = test_get_blocks()

    if blocks:
        print("\n3. Testing Submit Endpoint:")
        test_submit_responses()

    print("\n" + "=" * 60)
    print("Tests Complete!")
    print("=" * 60)