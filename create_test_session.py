#!/usr/bin/env python3
"""
Create a complete test session with realistic data
"""

import requests
import json
import random
import time

def create_complete_test_session():
    """Create a complete assessment session with realistic responses"""

    base_url = "http://localhost:8004"

    print("Creating complete test session...")
    print("=" * 50)

    # 1. Get assessment blocks
    print("1. Getting assessment blocks...")
    response = requests.get(f"{base_url}/api/v4/assessment/blocks?block_count=10")

    if response.status_code != 200:
        print(f"❌ Failed to get blocks: {response.status_code}")
        return None

    blocks_data = response.json()
    session_id = blocks_data['session_id']
    blocks = blocks_data['blocks']

    print(f"   ✅ Session created: {session_id}")
    print(f"   ✅ Got {len(blocks)} blocks")

    # 2. Create realistic responses
    print("\n2. Creating realistic responses...")
    responses = []

    for block in blocks:
        # Create a response that favors certain dimensions
        most_like = random.randint(0, 3)
        least_like = random.randint(0, 3)

        # Ensure most and least are different
        while least_like == most_like:
            least_like = random.randint(0, 3)

        responses.append({
            "block_id": block['block_id'],
            "most_like_index": most_like,
            "least_like_index": least_like,
            "response_time_ms": random.randint(3000, 15000)  # 3-15 seconds
        })

    print(f"   ✅ Created {len(responses)} responses")

    # 3. Submit responses
    print("\n3. Submitting responses...")
    submit_data = {
        "session_id": session_id,
        "responses": responses,
        "completion_time_seconds": len(responses) * 8  # Average 8 seconds per block
    }

    response = requests.post(f"{base_url}/api/v4/assessment/submit", json=submit_data)

    if response.status_code != 200:
        print(f"❌ Failed to submit: {response.status_code}")
        print(f"Response: {response.text}")
        return None

    print("   ✅ Responses submitted successfully")

    # 4. Get results
    print("\n4. Getting results...")
    response = requests.get(f"{base_url}/api/v4/assessment/results/{session_id}")

    if response.status_code != 200:
        print(f"❌ Failed to get results: {response.status_code}")
        return None

    results = response.json()
    print("   ✅ Results retrieved successfully")

    # 5. Show summary
    print("\n5. Results summary:")
    print(f"   Session ID: {session_id}")
    print(f"   Completed at: {results.get('completed_at', 'N/A')}")

    norm_scores = results.get('norm_scores', {})
    if norm_scores:
        print(f"   Dimensions scored: {len(norm_scores)}")
        for dim, score in list(norm_scores.items())[:3]:
            percentile = score.get('percentile', 50)
            print(f"      {dim}: {percentile}%")

    profile = results.get('profile', {})
    if profile:
        print(f"   Profile type: {profile.get('profile_type', 'N/A')}")

    print(f"\n🎯 Complete test session created!")
    print(f"📊 View results at: http://localhost:3000/results.html?session={session_id}")

    return session_id

if __name__ == "__main__":
    session_id = create_complete_test_session()
    if session_id:
        print(f"\n✅ SUCCESS: Session {session_id} ready for testing")
    else:
        print("\n❌ FAILED: Could not create test session")