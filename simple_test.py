#!/usr/bin/env python3
"""
Simple Test Script for Core Functionality

This script performs basic validation of the core components
without external dependencies like ReportLab or pytest.

Author: TaskMaster Agent (3.4.3)
Date: 2025-09-30
Version: 1.0
"""

import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'main', 'python'))

def test_scoring_engine():
    """Test scoring engine functionality."""
    print("Testing Scoring Engine...")

    try:
        from core.scoring import ScoringEngine, DimensionScores
        from models.schemas import QuestionResponse

        # Create sample responses
        responses = [
            QuestionResponse(question_id=i, score=3)
            for i in range(1, 21)
        ]

        # Test scoring engine
        engine = ScoringEngine()
        scores_dict = engine.calculate_all_dimensions(responses)

        print(f"  ✓ Generated scores: {scores_dict}")

        # Test dimension scores object
        dimension_scores = engine.create_dimension_scores_object(scores_dict)
        print(f"  ✓ DimensionScores object created: {type(dimension_scores)}")

        return True

    except Exception as e:
        print(f"  ✗ Scoring engine test failed: {e}")
        return False

def test_recommendation_system():
    """Test recommendation system functionality."""
    print("Testing Recommendation System...")

    try:
        from core.recommendation import get_recommendation_engine

        # Sample Big Five scores
        big_five_scores = {
            "openness": 16.0,
            "conscientiousness": 14.0,
            "extraversion": 18.0,
            "agreeableness": 15.0,
            "neuroticism": 12.0
        }

        # Test recommendation engine
        rec_engine = get_recommendation_engine()
        result = rec_engine.generate_recommendations(big_five_scores)

        print(f"  ✓ Recommendation result type: {type(result)}")
        print(f"  ✓ Job recommendations count: {len(result.job_recommendations)}")
        print(f"  ✓ Confidence score: {result.confidence_score:.2f}")

        return True

    except Exception as e:
        print(f"  ✗ Recommendation system test failed: {e}")
        return False

def test_content_generator_basic():
    """Test basic content generator functionality without ReportLab."""
    print("Testing Content Generator (Basic)...")

    try:
        from core.scoring import DimensionScores

        # Create sample scores
        scores = DimensionScores(
            openness=16.0,
            conscientiousness=14.0,
            extraversion=18.0,
            agreeableness=15.0,
            neuroticism=12.0
        )

        print(f"  ✓ DimensionScores created: {scores}")
        print(f"  ✓ Scores dict: {scores.to_dict()}")

        # Test content generator imports (might fail due to ReportLab)
        try:
            from core.report.content_generator import PersonalizedContentGenerator
            print("  ✓ PersonalizedContentGenerator imported")
        except ImportError as ie:
            print(f"  ! PersonalizedContentGenerator import failed (expected): {ie}")

        return True

    except Exception as e:
        print(f"  ✗ Content generator basic test failed: {e}")
        return False

def test_report_template_basic():
    """Test basic report template functionality."""
    print("Testing Report Template (Basic)...")

    try:
        # Test basic imports and data structures
        from core.report.report_template import ReportConfig, ReportSection

        # Create config
        config = ReportConfig()
        print(f"  ✓ ReportConfig created with font: {config.font_family}")

        # Test enum
        section = ReportSection.COVER
        print(f"  ✓ ReportSection enum: {section.value}")

        return True

    except Exception as e:
        print(f"  ✗ Report template basic test failed: {e}")
        return False

def test_data_models():
    """Test data models and schemas."""
    print("Testing Data Models...")

    try:
        from models.schemas import QuestionResponse, BigFiveScores

        # Test QuestionResponse
        response = QuestionResponse(question_id=1, score=4)
        print(f"  ✓ QuestionResponse created: Q{response.question_id}, Score{response.score}")

        # Test BigFiveScores
        scores = BigFiveScores(
            extraversion=70,
            agreeableness=80,
            conscientiousness=75,
            neuroticism=40,
            openness=85
        )
        print(f"  ✓ BigFiveScores created: {scores}")

        return True

    except Exception as e:
        print(f"  ✗ Data models test failed: {e}")
        return False

def main():
    """Run all basic tests."""
    print("=" * 60)
    print("BASIC FUNCTIONALITY TEST SUITE")
    print("=" * 60)

    tests = [
        ("Data Models", test_data_models),
        ("Scoring Engine", test_scoring_engine),
        ("Recommendation System", test_recommendation_system),
        ("Content Generator Basic", test_content_generator_basic),
        ("Report Template Basic", test_report_template_basic),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  ✗ Test suite error: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{status:4} | {test_name}")

    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 All basic tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check dependencies and imports.")
        return 1

if __name__ == "__main__":
    sys.exit(main())