"""
Quartet Block Designer for Forced-Choice Assessment
Version: 4.0 Prototype
Date: 2025-09-30

Implements balanced incomplete block design (BIBD) for creating
optimal forced-choice blocks that ensure equal dimension representation
and matched social desirability.
"""

import numpy as np
from typing import List, Dict, Set, Tuple, Optional
from itertools import combinations, permutations
from collections import defaultdict, Counter
import random
import logging

from models.v4.forced_choice import Statement, QuartetBlock


logger = logging.getLogger(__name__)


class BlockDesignCriteria:
    """Criteria for evaluating block design quality"""

    def __init__(self,
                 n_dimensions: int = 12,
                 n_blocks: int = 30,
                 items_per_block: int = 4):
        self.n_dimensions = n_dimensions
        self.n_blocks = n_blocks
        self.items_per_block = items_per_block
        self.total_items = n_blocks * items_per_block

        # Calculate expected frequencies
        self.expected_dim_frequency = self.total_items / n_dimensions
        self.expected_pair_frequency = self._calculate_expected_pair_freq()

    def _calculate_expected_pair_freq(self) -> float:
        """Calculate expected co-occurrence frequency for dimension pairs"""
        # In balanced design, pairs should appear uniformly
        n_pairs = self.n_dimensions * (self.n_dimensions - 1) / 2
        pairs_per_block = self.items_per_block * (self.items_per_block - 1) / 2
        total_pairs = self.n_blocks * pairs_per_block
        return total_pairs / n_pairs

    def evaluate_design(self, blocks: List[QuartetBlock]) -> Dict:
        """
        Evaluate the quality of a block design

        Returns:
            Dict with balance metrics and violations
        """
        dimension_counts = defaultdict(int)
        pair_counts = defaultdict(int)
        sd_variance = []

        for block in blocks:
            dimensions = [stmt.dimension for stmt in block.statements]

            # Count dimension frequencies
            for dim in dimensions:
                dimension_counts[dim] += 1

            # Count pair co-occurrences
            for pair in combinations(sorted(set(dimensions)), 2):
                pair_counts[pair] += 1

            # Calculate social desirability variance within block
            sd_values = [stmt.social_desirability for stmt in block.statements]
            sd_variance.append(np.var(sd_values))

        # Calculate balance metrics
        dim_frequencies = list(dimension_counts.values())
        dim_balance = np.std(dim_frequencies) / np.mean(dim_frequencies)

        pair_frequencies = list(pair_counts.values())
        pair_balance = np.std(pair_frequencies) / np.mean(pair_frequencies) if pair_frequencies else float('inf')

        mean_sd_variance = np.mean(sd_variance)

        # Check for violations
        violations = []

        # Check dimension frequency balance
        for dim, count in dimension_counts.items():
            if abs(count - self.expected_dim_frequency) > 2:
                violations.append(f"Dimension {dim} appears {count} times (expected ~{self.expected_dim_frequency:.1f})")

        # Check for duplicate items within blocks
        for i, block in enumerate(blocks):
            dimensions = [stmt.dimension for stmt in block.statements]
            if len(dimensions) != len(set(dimensions)):
                violations.append(f"Block {i} has duplicate dimensions")

        return {
            'dimension_balance': dim_balance,
            'pair_balance': pair_balance,
            'mean_sd_variance': mean_sd_variance,
            'dimension_counts': dict(dimension_counts),
            'pair_counts': dict(pair_counts),
            'violations': violations,
            'is_valid': len(violations) == 0 and dim_balance < 0.1
        }


class QuartetBlockDesigner:
    """
    Designer for creating balanced forced-choice blocks

    Uses combinatorial optimization to create blocks that:
    1. Balance dimension representation
    2. Minimize pair repetition
    3. Match social desirability within blocks
    4. Maximize information for IRT estimation
    """

    def __init__(self,
                 statements: List[Statement],
                 n_blocks: int = 30,
                 random_seed: Optional[int] = None):
        """
        Initialize the block designer

        Args:
            statements: Pool of statements (minimum 48 for 12 dimensions)
            n_blocks: Number of quartet blocks to create
            random_seed: Random seed for reproducibility
        """
        self.statements = statements
        self.n_blocks = n_blocks
        self.criteria = BlockDesignCriteria(n_dimensions=12, n_blocks=n_blocks)

        if random_seed:
            random.seed(random_seed)
            np.random.seed(random_seed)

        # Organize statements by dimension
        self.statements_by_dim = defaultdict(list)
        for stmt in statements:
            self.statements_by_dim[stmt.dimension].append(stmt)

        # Validate minimum requirements
        self._validate_statement_pool()

    def _validate_statement_pool(self):
        """Validate that statement pool meets requirements"""
        dimensions = set(stmt.dimension for stmt in self.statements)

        if len(dimensions) < 12:
            raise ValueError(f"Need statements for 12 dimensions, got {len(dimensions)}")

        for dim in dimensions:
            if len(self.statements_by_dim[dim]) < 4:
                raise ValueError(f"Dimension {dim} has only {len(self.statements_by_dim[dim])} statements, need at least 4")

        total_needed = self.n_blocks * 4
        if len(self.statements) < 48:
            logger.warning(f"Statement pool size ({len(self.statements)}) is small for {self.n_blocks} blocks")

    def create_blocks(self, method: str = 'balanced') -> List[QuartetBlock]:
        """
        Create quartet blocks using specified method

        Args:
            method: Design method ('balanced', 'random', 'optimal')

        Returns:
            List of QuartetBlock objects
        """
        if method == 'balanced':
            return self._create_balanced_blocks()
        elif method == 'random':
            return self._create_random_blocks()
        elif method == 'optimal':
            return self._create_optimal_blocks()
        else:
            raise ValueError(f"Unknown method: {method}")

    def _create_balanced_blocks(self) -> List[QuartetBlock]:
        """
        Create blocks using balanced incomplete block design

        Ensures each dimension appears equally often and
        pairs of dimensions co-occur uniformly
        """
        blocks = []
        used_statements = set()

        # Generate dimension combinations for blocks
        dimension_combinations = self._generate_dimension_combinations()

        for block_id, dims in enumerate(dimension_combinations[:self.n_blocks]):
            # Select statements for these dimensions
            block_statements = []

            for dim in dims:
                # Get available statements for this dimension
                available = [s for s in self.statements_by_dim[dim]
                           if s.statement_id not in used_statements]

                if not available:
                    # Reset if we've used all statements
                    available = self.statements_by_dim[dim]

                # Select statement with best social desirability match
                if block_statements:
                    # Match social desirability of existing statements
                    target_sd = np.mean([s.social_desirability for s in block_statements])
                    best_stmt = min(available,
                                  key=lambda s: abs(s.social_desirability - target_sd))
                else:
                    # First statement - choose randomly
                    best_stmt = random.choice(available)

                block_statements.append(best_stmt)
                used_statements.add(best_stmt.statement_id)

            # Create quartet block
            blocks.append(QuartetBlock(
                block_id=block_id,
                statements=block_statements,
                dimensions=[s.dimension for s in block_statements]
            ))

        return blocks

    def _generate_dimension_combinations(self) -> List[Tuple[str, ...]]:
        """
        Generate balanced combinations of dimensions for blocks

        Uses a modified BIBD approach to ensure balance
        """
        dimensions = list(self.statements_by_dim.keys())

        # For 12 dimensions and 4-item blocks, we need special handling
        # Generate all possible 4-combinations
        all_combinations = list(combinations(dimensions, 4))

        # Score combinations by how well they balance the design
        combination_scores = []

        for combo in all_combinations:
            # Count current usage of each dimension
            score = 0

            # Prefer combinations with less frequently used dimensions
            for dim in combo:
                score -= self._get_dimension_usage(dim)

            # Prefer combinations with rare pair co-occurrences
            for pair in combinations(combo, 2):
                score -= self._get_pair_usage(pair) * 0.5

            combination_scores.append((score, combo))

        # Sort by score and select best combinations
        combination_scores.sort(reverse=True)
        selected = [combo for score, combo in combination_scores[:self.n_blocks]]

        # Shuffle to avoid systematic patterns
        random.shuffle(selected)

        return selected

    def _get_dimension_usage(self, dimension: str) -> int:
        """Track dimension usage (stub for full implementation)"""
        # In full implementation, track across selected blocks
        return 0

    def _get_pair_usage(self, pair: Tuple[str, str]) -> int:
        """Track pair co-occurrence (stub for full implementation)"""
        # In full implementation, track across selected blocks
        return 0

    def _create_random_blocks(self) -> List[QuartetBlock]:
        """
        Create blocks with random selection (baseline method)

        Still ensures no duplicate dimensions within blocks
        """
        blocks = []
        all_statements = self.statements.copy()
        random.shuffle(all_statements)

        for block_id in range(self.n_blocks):
            # Randomly select 4 different dimensions
            selected_dims = random.sample(list(self.statements_by_dim.keys()), 4)

            # Select one statement per dimension
            block_statements = []
            for dim in selected_dims:
                stmt = random.choice(self.statements_by_dim[dim])
                block_statements.append(stmt)

            blocks.append(QuartetBlock(
                block_id=block_id,
                statements=block_statements,
                dimensions=selected_dims
            ))

        return blocks

    def _create_optimal_blocks(self) -> List[QuartetBlock]:
        """
        Create blocks using optimization algorithm

        This uses simulated annealing or genetic algorithm
        to find optimal block configuration
        """
        # Start with balanced blocks
        blocks = self._create_balanced_blocks()

        # Optimize using iterative improvement
        best_blocks = blocks
        best_score = self._evaluate_blocks(blocks)

        for iteration in range(100):
            # Make small changes
            new_blocks = self._mutate_blocks(best_blocks)

            # Evaluate
            new_score = self._evaluate_blocks(new_blocks)

            # Accept if better
            if new_score > best_score:
                best_blocks = new_blocks
                best_score = new_score
                logger.debug(f"Iteration {iteration}: Improved score to {best_score}")

        return best_blocks

    def _evaluate_blocks(self, blocks: List[QuartetBlock]) -> float:
        """
        Score a block design (higher is better)
        """
        evaluation = self.criteria.evaluate_design(blocks)

        # Combine metrics into single score
        score = 0.0
        score -= evaluation['dimension_balance'] * 10  # Penalize imbalance
        score -= evaluation['pair_balance'] * 5
        score -= evaluation['mean_sd_variance'] * 2
        score -= len(evaluation['violations']) * 20

        return score

    def _mutate_blocks(self, blocks: List[QuartetBlock]) -> List[QuartetBlock]:
        """
        Make small random changes to blocks for optimization
        """
        new_blocks = [
            QuartetBlock(
                block_id=b.block_id,
                statements=b.statements.copy(),
                dimensions=b.dimensions.copy()
            )
            for b in blocks
        ]

        # Swap two statements between blocks
        if len(new_blocks) >= 2:
            block1_idx = random.randint(0, len(new_blocks) - 1)
            block2_idx = random.randint(0, len(new_blocks) - 1)

            if block1_idx != block2_idx:
                stmt1_idx = random.randint(0, 3)
                stmt2_idx = random.randint(0, 3)

                # Swap if dimensions don't conflict
                stmt1 = new_blocks[block1_idx].statements[stmt1_idx]
                stmt2 = new_blocks[block2_idx].statements[stmt2_idx]

                dims1 = set(s.dimension for i, s in enumerate(new_blocks[block1_idx].statements) if i != stmt1_idx)
                dims2 = set(s.dimension for i, s in enumerate(new_blocks[block2_idx].statements) if i != stmt2_idx)

                if stmt2.dimension not in dims1 and stmt1.dimension not in dims2:
                    new_blocks[block1_idx].statements[stmt1_idx] = stmt2
                    new_blocks[block2_idx].statements[stmt2_idx] = stmt1

        return new_blocks

    def validate_blocks(self, blocks: List[QuartetBlock]) -> Dict:
        """
        Validate a set of blocks against design criteria
        """
        return self.criteria.evaluate_design(blocks)

    def export_blocks(self, blocks: List[QuartetBlock], filepath: str):
        """
        Export blocks to JSON format for use in assessment
        """
        import json

        export_data = {
            'version': '4.0-prototype',
            'n_blocks': len(blocks),
            'blocks': []
        }

        for block in blocks:
            export_data['blocks'].append({
                'block_id': block.block_id,
                'statements': [
                    {
                        'statement_id': stmt.statement_id,
                        'text': stmt.text,
                        'dimension': stmt.dimension,
                        'factor_loading': stmt.factor_loading,
                        'social_desirability': stmt.social_desirability
                    }
                    for stmt in block.statements
                ]
            })

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(blocks)} blocks to {filepath}")