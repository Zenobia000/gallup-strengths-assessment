"""
Unit tests for v4.0 Thurstonian IRT prototype
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../main/python'))

import numpy as np
from datetime import datetime
from models.v4.forced_choice import (
    Statement,
    QuartetBlock,
    ForcedChoiceResponse,
    ForcedChoiceBlockResponse
)
from core.v4.irt_scorer import ThurstonianIRTScorer
from core.v4.block_designer import QuartetBlockDesigner


def create_mock_statements():
    """Create mock statements for testing"""
    dimensions = [
        'Achiever', 'Activator', 'Adaptability',
        'Analytical', 'Arranger', 'Belief',
        'Command', 'Communication', 'Competition',
        'Connectedness', 'Consistency', 'Context'
    ]

    statements = []
    statement_id = 0

    for dim in dimensions:
        # Create 4 statements per dimension
        for i in range(4):
            statements.append(Statement(
                statement_id=f"stmt_{statement_id:03d}",
                text=f"I am driven by {dim} (statement {i+1})",
                dimension=dim,
                factor_loading=np.random.uniform(0.5, 0.9),
                social_desirability=np.random.uniform(3.0, 7.0)
            ))
            statement_id += 1

    return statements


def test_block_designer():
    """Test the block designer functionality"""
    print("\n=== Testing Block Designer ===")

    # Create statement pool
    statements = create_mock_statements()
    print(f"Created {len(statements)} statements for {len(set(s.dimension for s in statements))} dimensions")

    # Create block designer
    designer = QuartetBlockDesigner(statements, n_blocks=30, random_seed=42)

    # Generate blocks
    blocks = designer.create_blocks(method='balanced')
    print(f"Generated {len(blocks)} quartet blocks")

    # Validate design
    validation = designer.validate_blocks(blocks)
    print(f"Design validation:")
    print(f"  - Dimension balance: {validation['dimension_balance']:.3f}")
    print(f"  - Pair balance: {validation['pair_balance']:.3f}")
    print(f"  - Mean SD variance: {validation['mean_sd_variance']:.3f}")
    print(f"  - Valid design: {validation['is_valid']}")

    if validation['violations']:
        print(f"  - Violations: {validation['violations'][:3]}")

    # Show sample block
    sample_block = blocks[0]
    print(f"\nSample block (ID: {sample_block.block_id}):")
    for i, stmt in enumerate(sample_block.statements):
        print(f"  {i}: [{stmt.dimension}] {stmt.text[:50]}...")

    return blocks


def test_forced_choice_response():
    """Test forced choice response data structures"""
    print("\n=== Testing Forced Choice Response ===")

    # Create blocks
    statements = create_mock_statements()
    designer = QuartetBlockDesigner(statements, n_blocks=30, random_seed=42)
    blocks = designer.create_blocks()

    # Simulate responses
    responses = []
    for i in range(30):  # Respond to all 30 blocks
        most_idx = np.random.randint(0, 4)
        least_idx = np.random.randint(0, 4)

        # Ensure most != least
        while least_idx == most_idx:
            least_idx = np.random.randint(0, 4)

        responses.append(ForcedChoiceResponse(
            block_id=i,
            most_like_index=most_idx,
            least_like_index=least_idx,
            response_time_ms=np.random.randint(2000, 10000)
        ))

    # Create block response object
    block_response = ForcedChoiceBlockResponse(
        session_id="test_session_001",
        participant_id="participant_001",
        responses=responses,
        blocks=blocks,
        start_time=datetime.now()
    )

    print(f"Created response data:")
    print(f"  - Session: {block_response.session_id}")
    print(f"  - Responses: {len(block_response.responses)}")
    print(f"  - Completion rate: {block_response.completion_rate:.1%}")

    # Test dimension coverage
    coverage = block_response.dimension_coverage
    print(f"  - Dimension coverage: {dict(list(coverage.items())[:3])}...")

    return block_response


def test_irt_scorer():
    """Test IRT scoring functionality"""
    print("\n=== Testing IRT Scorer ===")

    # Create scorer
    scorer = ThurstonianIRTScorer(n_dimensions=12)

    # Get mock response data
    response_data = test_forced_choice_response()

    # Estimate theta
    print("\nEstimating latent traits...")
    theta_estimate = scorer.estimate_theta(response_data, method='MLE', use_prior=True)

    print(f"Estimation results:")
    print(f"  - Convergence: {theta_estimate.convergence}")
    print(f"  - Iterations: {theta_estimate.n_iterations}")
    print(f"  - Log-likelihood: {theta_estimate.log_likelihood:.2f}")

    # Show theta estimates
    dimensions = [
        'Achiever', 'Activator', 'Adaptability',
        'Analytical', 'Arranger', 'Belief',
        'Command', 'Communication', 'Competition',
        'Connectedness', 'Consistency', 'Context'
    ]

    print(f"\nTheta estimates (top 5):")
    theta_with_dims = [(dimensions[i], theta_estimate.theta[i], theta_estimate.se[i])
                       for i in range(12)]
    theta_with_dims.sort(key=lambda x: x[1], reverse=True)

    for i, (dim, theta, se) in enumerate(theta_with_dims[:5]):
        print(f"  {i+1}. {dim}: θ={theta:+.3f} (SE={se:.3f})")

    # Compute normative scores
    norm_scores = scorer.compute_normative_scores(theta_estimate)
    print(f"\nNormative scores (top 5):")
    for i, (dim, _, _) in enumerate(theta_with_dims[:5]):
        dim_idx = dimensions.index(dim)
        print(f"  {dim}: Percentile={norm_scores.percentiles[dim_idx]:.1f}, T={norm_scores.t_scores[dim_idx]:.1f}")

    # Generate report
    report = scorer.generate_report(theta_estimate, norm_scores)
    print(f"\nTop strengths: {', '.join(report['top_strengths'])}")

    return theta_estimate


def run_all_tests():
    """Run all prototype tests"""
    print("=" * 60)
    print("V4.0 THURSTONIAN IRT PROTOTYPE TESTS")
    print("=" * 60)

    try:
        # Test block designer
        blocks = test_block_designer()

        # Test IRT scorer
        theta_estimate = test_irt_scorer()

        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)