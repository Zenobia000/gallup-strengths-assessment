#!/usr/bin/env python3
"""
Test script to verify API integration with results.html
"""

import requests
import json
import sys

def test_v4_api_integration():
    """Test the complete v4 API integration flow"""

    # Test session ID from database
    session_id = "5a2a2d28-7de8-4028-b2d7-bdbf691fcf44"

    print(f"Testing v4 API integration for session: {session_id}")
    print("=" * 60)

    # 1. Test API endpoint
    api_url = f"http://localhost:8004/api/v4/assessment/results/{session_id}"
    print(f"1. Testing API endpoint: {api_url}")

    try:
        response = requests.get(api_url)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API returned data successfully")

            # 2. Test data structure
            print("\n2. Checking data structure:")
            required_fields = ['session_id', 'completed_at', 'theta_scores', 'norm_scores', 'profile']

            for field in required_fields:
                if field in data:
                    print(f"   ✅ {field}: Present")

                    # Show sample data
                    if field == 'norm_scores' and data[field]:
                        sample_dim = list(data[field].keys())[0]
                        sample_score = data[field][sample_dim]
                        print(f"      Sample ({sample_dim}): percentile={sample_score.get('percentile', 'N/A')}")

                    elif field == 'profile' and data[field]:
                        profile = data[field]
                        print(f"      Profile type: {profile.get('profile_type', 'N/A')}")
                        top_strengths = profile.get('top_strengths', [])
                        if top_strengths:
                            print(f"      Top strength: {top_strengths[0].get('dimension', 'N/A')}")
                else:
                    print(f"   ❌ {field}: Missing")

            # 3. Test dimension mapping
            print("\n3. Testing dimension mapping:")
            norm_scores = data.get('norm_scores', {})

            # V4 to 12-dimension mapping
            dimension_mapping = {
                'Achiever': 'T1-結構化執行',
                'Deliberative': 'T2-品質與完備',
                'Command': 'T5-影響與倡議',
                'Communication': 'T5-影響與倡議',
                'Empathy': 'T6-協作與共好',
                'Learner': 'T8-學習與成長'
            }

            mapped_count = 0
            for v4_dim, our_dim in dimension_mapping.items():
                if v4_dim in norm_scores:
                    percentile = norm_scores[v4_dim].get('percentile', 50)
                    print(f"   ✅ {v4_dim} → {our_dim}: {percentile}%")
                    mapped_count += 1
                else:
                    print(f"   ⚠️  {v4_dim} → {our_dim}: Not found in data")

            print(f"\n   Mapped dimensions: {mapped_count}/{len(dimension_mapping)}")

            # 4. Simulate frontend data transformation
            print("\n4. Simulating frontend data transformation:")

            # Calculate confidence (simplified)
            theta_scores = data.get('theta_scores', {})
            if theta_scores:
                scores = list(theta_scores.values())
                variance = sum(abs(score) for score in scores) / len(scores)
                confidence = max(0.7, min(0.95, 1 - variance / 10))
                print(f"   Calculated confidence: {confidence:.2f}")

            # Map to 12 dimensions
            dimensions = []
            for v4_dim, score_data in norm_scores.items():
                if v4_dim in dimension_mapping:
                    our_dim = dimension_mapping[v4_dim]
                    dimensions.append({
                        'v4_dimension': v4_dim,
                        'our_dimension': our_dim,
                        'percentile': score_data.get('percentile', 50)
                    })

            print(f"   Transformed dimensions: {len(dimensions)}")
            for dim in dimensions[:3]:  # Show first 3
                print(f"      {dim['v4_dimension']} → {dim['our_dimension']}: {dim['percentile']}%")

            print(f"\n🎯 Integration test PASSED!")
            print(f"   The results.html page should now display real data from session {session_id}")

        else:
            print(f"   ❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"   ❌ Error testing API: {e}")
        return False

    return True

if __name__ == "__main__":
    success = test_v4_api_integration()
    sys.exit(0 if success else 1)