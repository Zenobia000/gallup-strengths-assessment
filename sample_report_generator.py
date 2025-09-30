#!/usr/bin/env python3
"""
Sample Report Generator - Testing and Demonstration

This script generates sample PDF reports to test and demonstrate
the complete report generation system functionality.

Usage:
    python sample_report_generator.py [--output-dir OUTPUT_DIR] [--user-name USER_NAME]

Features:
- Generates sample assessment responses
- Creates complete PDF reports
- Provides generation statistics
- Demonstrates error handling

Author: TaskMaster Agent (3.4.3)
Date: 2025-09-30
Version: 1.0
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
import json

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'main', 'python'))

try:
    from core.scoring import DimensionScores, ScoringEngine
    from core.report.pdf_generator import (
        PDFReportGenerator, PDFGenerationOptions,
        create_pdf_generator, generate_quick_report
    )
    from core.report.report_template import ReportConfig
    from models.schemas import QuestionResponse
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running from the project root directory")
    sys.exit(1)


class SampleDataGenerator:
    """Generate sample assessment data for testing."""

    def __init__(self, seed: int = 42):
        """Initialize with random seed for reproducible results."""
        random.seed(seed)

    def generate_sample_responses(self, personality_type: str = "balanced") -> List[QuestionResponse]:
        """
        Generate sample Mini-IPIP responses based on personality type.

        Args:
            personality_type: Type of personality profile to simulate
                            ("balanced", "high_openness", "high_extraversion", etc.)

        Returns:
            List of 20 QuestionResponse objects
        """
        responses = []

        # Define personality type templates
        templates = {
            "balanced": {
                "openness": 3.0,
                "conscientiousness": 3.5,
                "extraversion": 3.2,
                "agreeableness": 3.8,
                "neuroticism": 2.5
            },
            "high_openness": {
                "openness": 4.5,
                "conscientiousness": 3.0,
                "extraversion": 3.5,
                "agreeableness": 3.5,
                "neuroticism": 2.8
            },
            "high_extraversion": {
                "openness": 3.2,
                "conscientiousness": 3.8,
                "extraversion": 4.7,
                "agreeableness": 4.2,
                "neuroticism": 2.3
            },
            "analytical": {
                "openness": 4.2,
                "conscientiousness": 4.5,
                "extraversion": 2.8,
                "agreeableness": 3.2,
                "neuroticism": 2.5
            },
            "creative": {
                "openness": 4.8,
                "conscientiousness": 2.8,
                "extraversion": 3.8,
                "agreeableness": 3.5,
                "neuroticism": 3.2
            }
        }

        template = templates.get(personality_type, templates["balanced"])

        # Generate responses for each dimension
        dimension_questions = {
            "openness": [1, 2, 3, 4],
            "conscientiousness": [5, 6, 7, 8],
            "extraversion": [9, 10, 11, 12],
            "agreeableness": [13, 14, 15, 16],
            "neuroticism": [17, 18, 19, 20]
        }

        for dimension, base_score in template.items():
            question_ids = dimension_questions[dimension]
            for q_id in question_ids:
                # Add some random variation around the base score
                variation = random.uniform(-0.8, 0.8)
                score = max(1, min(5, round(base_score + variation)))
                responses.append(QuestionResponse(question_id=q_id, score=score))

        # Sort by question_id to ensure proper order
        responses.sort(key=lambda x: x.question_id)
        return responses

    def generate_user_context(self, context_type: str = "tech_professional") -> Dict[str, Any]:
        """
        Generate sample user context for personalized recommendations.

        Args:
            context_type: Type of user context to simulate

        Returns:
            Dictionary with user context information
        """
        contexts = {
            "tech_professional": {
                "industry": "Technology",
                "experience_years": random.randint(3, 8),
                "current_role": "Software Engineer",
                "education_level": "Bachelor's",
                "interests": ["Programming", "Innovation", "Problem Solving"],
                "career_goals": ["Technical Leadership", "Product Development"]
            },
            "business_analyst": {
                "industry": "Consulting",
                "experience_years": random.randint(2, 6),
                "current_role": "Business Analyst",
                "education_level": "Master's",
                "interests": ["Data Analysis", "Strategy", "Process Improvement"],
                "career_goals": ["Management Consulting", "Strategy Development"]
            },
            "creative_professional": {
                "industry": "Media & Entertainment",
                "experience_years": random.randint(1, 5),
                "current_role": "Graphic Designer",
                "education_level": "Bachelor's",
                "interests": ["Design", "Art", "Innovation"],
                "career_goals": ["Creative Direction", "Brand Strategy"]
            },
            "recent_graduate": {
                "industry": "Various",
                "experience_years": 0,
                "current_role": "Student",
                "education_level": "Bachelor's",
                "interests": ["Learning", "Growth", "Exploration"],
                "career_goals": ["Career Exploration", "Skill Development"]
            }
        }

        return contexts.get(context_type, contexts["tech_professional"])


class ReportTestSuite:
    """Test suite for report generation functionality."""

    def __init__(self, output_dir: str = "sample_reports"):
        """Initialize test suite with output directory."""
        self.output_dir = output_dir
        self.data_generator = SampleDataGenerator()
        self.results = []

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

    def run_basic_generation_test(self) -> Dict[str, Any]:
        """Test basic report generation functionality."""
        print("Running basic generation test...")

        try:
            # Generate sample data
            responses = self.data_generator.generate_sample_responses("balanced")
            user_name = "張小明"

            # Generate report using quick function
            output_path = os.path.join(self.output_dir, "basic_test_report.pdf")
            result_path = generate_quick_report(responses, user_name, output_path)

            result = {
                "test_name": "basic_generation",
                "success": True,
                "output_path": result_path,
                "file_size": os.path.getsize(result_path),
                "error": None
            }

            print(f"✓ Basic test completed: {result_path}")
            return result

        except Exception as e:
            result = {
                "test_name": "basic_generation",
                "success": False,
                "output_path": None,
                "file_size": None,
                "error": str(e)
            }
            print(f"✗ Basic test failed: {e}")
            return result

    def run_advanced_generation_test(self) -> Dict[str, Any]:
        """Test advanced report generation with custom options."""
        print("Running advanced generation test...")

        try:
            # Create custom configuration
            config = ReportConfig()
            config.primary_color = (0.1, 0.3, 0.7)  # Custom blue
            config.font_family = "Helvetica"

            # Create generator with custom config
            generator = create_pdf_generator(config=config)

            # Generate sample data
            responses = self.data_generator.generate_sample_responses("analytical")
            user_name = "李小華"
            user_context = self.data_generator.generate_user_context("tech_professional")

            # Custom generation options
            options = PDFGenerationOptions(
                include_charts=True,
                include_watermark=True,
                watermark_text="樣本報告",
                quality="high"
            )

            # Generate report
            result = generator.generate_report_from_responses(
                responses,
                user_name,
                assessment_date=datetime.now() - timedelta(days=1),
                user_context=user_context,
                options=options
            )

            if result.success:
                # Move file to output directory
                output_path = os.path.join(self.output_dir, "advanced_test_report.pdf")
                os.rename(result.file_path, output_path)

                test_result = {
                    "test_name": "advanced_generation",
                    "success": True,
                    "output_path": output_path,
                    "file_size": result.file_size_bytes,
                    "generation_time": result.generation_time_seconds,
                    "report_id": result.report_id,
                    "error": None
                }

                print(f"✓ Advanced test completed: {output_path}")
                return test_result
            else:
                raise Exception(result.error_message)

        except Exception as e:
            result = {
                "test_name": "advanced_generation",
                "success": False,
                "output_path": None,
                "file_size": None,
                "error": str(e)
            }
            print(f"✗ Advanced test failed: {e}")
            return result

    def run_personality_variation_tests(self) -> List[Dict[str, Any]]:
        """Test report generation with different personality types."""
        print("Running personality variation tests...")

        personality_types = [
            ("high_openness", "王創新"),
            ("high_extraversion", "陳外向"),
            ("creative", "林創意"),
            ("analytical", "黃分析")
        ]

        results = []

        for personality_type, user_name in personality_types:
            try:
                print(f"  Testing {personality_type} personality...")

                # Generate responses for this personality type
                responses = self.data_generator.generate_sample_responses(personality_type)

                # Generate report
                output_path = os.path.join(
                    self.output_dir,
                    f"{personality_type}_report.pdf"
                )
                result_path = generate_quick_report(responses, user_name, output_path)

                result = {
                    "test_name": f"personality_{personality_type}",
                    "personality_type": personality_type,
                    "user_name": user_name,
                    "success": True,
                    "output_path": result_path,
                    "file_size": os.path.getsize(result_path),
                    "error": None
                }

                results.append(result)
                print(f"    ✓ {personality_type} completed")

            except Exception as e:
                result = {
                    "test_name": f"personality_{personality_type}",
                    "personality_type": personality_type,
                    "user_name": user_name,
                    "success": False,
                    "output_path": None,
                    "file_size": None,
                    "error": str(e)
                }
                results.append(result)
                print(f"    ✗ {personality_type} failed: {e}")

        return results

    def run_error_handling_tests(self) -> List[Dict[str, Any]]:
        """Test error handling in various scenarios."""
        print("Running error handling tests...")

        results = []

        # Test 1: Invalid responses
        try:
            print("  Testing invalid responses...")
            invalid_responses = [
                QuestionResponse(question_id=1, score=6)  # Invalid score
            ]
            generate_quick_report(invalid_responses, "測試用戶")

            # Should not reach here
            results.append({
                "test_name": "error_invalid_responses",
                "success": False,
                "error": "Should have failed with invalid responses"
            })

        except Exception as e:
            results.append({
                "test_name": "error_invalid_responses",
                "success": True,  # Expected to fail
                "error": str(e),
                "note": "Correctly caught invalid input"
            })
            print(f"    ✓ Correctly caught invalid responses: {e}")

        # Test 2: Incomplete responses
        try:
            print("  Testing incomplete responses...")
            incomplete_responses = [
                QuestionResponse(question_id=i, score=3)
                for i in range(1, 10)  # Only 9 responses instead of 20
            ]
            generate_quick_report(incomplete_responses, "測試用戶")

            results.append({
                "test_name": "error_incomplete_responses",
                "success": False,
                "error": "Should have failed with incomplete responses"
            })

        except Exception as e:
            results.append({
                "test_name": "error_incomplete_responses",
                "success": True,  # Expected to fail
                "error": str(e),
                "note": "Correctly caught incomplete responses"
            })
            print(f"    ✓ Correctly caught incomplete responses: {e}")

        return results

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites and return comprehensive results."""
        print("Starting comprehensive report generation test suite...")
        print(f"Output directory: {os.path.abspath(self.output_dir)}")
        print("=" * 60)

        start_time = datetime.now()

        # Run all test suites
        basic_result = self.run_basic_generation_test()
        self.results.append(basic_result)

        advanced_result = self.run_advanced_generation_test()
        self.results.append(advanced_result)

        personality_results = self.run_personality_variation_tests()
        self.results.extend(personality_results)

        error_results = self.run_error_handling_tests()
        self.results.extend(error_results)

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        # Compile summary
        successful_tests = len([r for r in self.results if r["success"]])
        total_tests = len(self.results)

        summary = {
            "test_suite": "PDF Report Generation",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_time_seconds": total_time,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "output_directory": os.path.abspath(self.output_dir),
            "detailed_results": self.results
        }

        # Print summary
        print("=" * 60)
        print("TEST SUITE SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Total Time: {total_time:.2f} seconds")
        print(f"Output Directory: {summary['output_directory']}")

        # List generated files
        generated_files = [r["output_path"] for r in self.results
                          if r["success"] and r.get("output_path")]
        if generated_files:
            print("\nGenerated Reports:")
            for file_path in generated_files:
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                print(f"  - {os.path.basename(file_path)} ({file_size:,} bytes)")

        return summary

    def save_test_results(self, summary: Dict[str, Any], filename: str = "test_results.json"):
        """Save test results to JSON file."""
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"\nTest results saved to: {output_path}")


def main():
    """Main entry point for sample report generation."""
    parser = argparse.ArgumentParser(
        description="Generate sample PDF reports for testing"
    )
    parser.add_argument(
        "--output-dir",
        default="sample_reports",
        help="Output directory for generated reports"
    )
    parser.add_argument(
        "--user-name",
        default="測試用戶",
        help="User name for single report generation"
    )
    parser.add_argument(
        "--single",
        action="store_true",
        help="Generate single report instead of full test suite"
    )
    parser.add_argument(
        "--personality-type",
        default="balanced",
        choices=["balanced", "high_openness", "high_extraversion", "analytical", "creative"],
        help="Personality type for single report generation"
    )

    args = parser.parse_args()

    if args.single:
        # Generate single report
        print(f"Generating single report for {args.user_name}...")

        data_generator = SampleDataGenerator()
        responses = data_generator.generate_sample_responses(args.personality_type)

        output_path = os.path.join(args.output_dir, f"single_report_{args.personality_type}.pdf")
        os.makedirs(args.output_dir, exist_ok=True)

        try:
            result_path = generate_quick_report(responses, args.user_name, output_path)
            print(f"✓ Report generated successfully: {result_path}")
            print(f"  File size: {os.path.getsize(result_path):,} bytes")
        except Exception as e:
            print(f"✗ Report generation failed: {e}")
            return 1

    else:
        # Run full test suite
        test_suite = ReportTestSuite(args.output_dir)
        summary = test_suite.run_all_tests()
        test_suite.save_test_results(summary)

        # Return appropriate exit code
        return 0 if summary["failed_tests"] == 0 else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())