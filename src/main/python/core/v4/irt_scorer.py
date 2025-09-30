"""
Thurstonian IRT Scorer Implementation
Version: 4.0 Prototype
Date: 2025-09-30

This implements the scoring algorithm based on the research in
docs/v4_research/irt-theory-foundation.md
"""

import numpy as np
from scipy import optimize, stats
from typing import List, Dict, Tuple, Optional
import json
import logging
from pathlib import Path
from functools import lru_cache
from dataclasses import dataclass

from models.v4.forced_choice import (
    ForcedChoiceBlockResponse,
    ForcedChoiceResponse,
    QuartetBlock,
    IRTParameters
)


logger = logging.getLogger(__name__)


@dataclass
class ThetaEstimate:
    """Estimated latent trait scores with uncertainty"""
    theta: np.ndarray  # 12-dimensional trait vector
    se: np.ndarray  # Standard errors for each dimension
    log_likelihood: float  # Model fit
    convergence: bool  # Whether estimation converged
    n_iterations: int  # Number of iterations used


@dataclass
class NormativeScores:
    """Normative scores derived from theta estimates"""
    percentiles: np.ndarray  # Percentile ranks (0-100)
    t_scores: np.ndarray  # T-scores (mean=50, sd=10)
    stanines: np.ndarray  # Stanine scores (1-9)
    raw_theta: np.ndarray  # Original theta estimates


class ThurstonianIRTScorer:
    """
    Thurstonian IRT model for scoring forced-choice assessments

    This implementation uses Maximum Likelihood Estimation (MLE) with
    optional Bayesian priors for regularization.
    """

    def __init__(self,
                 n_dimensions: int = 12,
                 parameters_path: Optional[Path] = None):
        """
        Initialize the IRT scorer

        Args:
            n_dimensions: Number of latent dimensions (strength themes)
            parameters_path: Path to pre-calibrated parameters JSON file
        """
        self.n_dimensions = n_dimensions
        self.parameters: Optional[IRTParameters] = None
        self.norm_data: Optional[Dict] = None

        if parameters_path:
            self.load_parameters(parameters_path)

    def load_parameters(self, path: Path):
        """Load pre-calibrated IRT parameters"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                params_dict = json.load(f)

            # Convert to IRTParameters object
            from datetime import datetime
            self.parameters = IRTParameters(
                item_parameters=params_dict['item_parameters'],
                block_parameters=params_dict['block_parameters'],
                dimension_thresholds=params_dict['dimension_thresholds'],
                normative_data=params_dict['normative_data'],
                calibration_sample_size=params_dict['calibration_sample_size'],
                calibration_date=datetime.fromisoformat(params_dict['calibration_date']),
                model_version=params_dict.get('model_version', '4.0-prototype')
            )

            # Extract normative data for scoring
            self.norm_data = params_dict['normative_data']

            logger.info(f"Loaded IRT parameters from {path}")

        except Exception as e:
            logger.error(f"Failed to load parameters: {e}")
            raise

    def estimate_theta(self,
                      response_data: ForcedChoiceBlockResponse,
                      method: str = 'MLE',
                      use_prior: bool = True) -> ThetaEstimate:
        """
        Estimate latent trait scores from responses

        Args:
            response_data: Complete forced-choice response data
            method: Estimation method ('MLE' or 'EAP')
            use_prior: Whether to use Bayesian prior

        Returns:
            ThetaEstimate object with theta scores and diagnostics
        """
        # Convert responses to internal format
        responses = response_data.to_irt_format()

        # Get initial estimates using simple counting
        initial_theta = self._get_initial_estimate(response_data)

        # Perform estimation based on method
        if method == 'MLE':
            theta, se, convergence, n_iter = self._mle_estimate(
                responses,
                response_data.blocks,
                initial_theta,
                use_prior
            )
        elif method == 'EAP':
            theta, se, convergence, n_iter = self._eap_estimate(
                responses,
                response_data.blocks,
                initial_theta
            )
        else:
            raise ValueError(f"Unknown estimation method: {method}")

        # Calculate final log-likelihood
        ll = self._log_likelihood(theta, responses, response_data.blocks)

        return ThetaEstimate(
            theta=theta,
            se=se,
            log_likelihood=ll,
            convergence=convergence,
            n_iterations=n_iter
        )

    def _get_initial_estimate(self,
                            response_data: ForcedChoiceBlockResponse) -> np.ndarray:
        """
        Get initial theta estimates using simple counting

        This provides a reasonable starting point for iterative estimation
        """
        dimension_scores = np.zeros(self.n_dimensions)
        dimension_counts = np.zeros(self.n_dimensions)

        # Map dimension names to indices
        dim_to_idx = {
            'Achiever': 0, 'Activator': 1, 'Adaptability': 2,
            'Analytical': 3, 'Arranger': 4, 'Belief': 5,
            'Command': 6, 'Communication': 7, 'Competition': 8,
            'Connectedness': 9, 'Consistency': 10, 'Context': 11
        }

        for response in response_data.responses:
            block = next((b for b in response_data.blocks
                         if b.block_id == response.block_id), None)
            if not block:
                continue

            # Add point for "most like" dimension
            most_stmt = block.statements[response.most_like_index]
            if most_stmt.dimension in dim_to_idx:
                idx = dim_to_idx[most_stmt.dimension]
                dimension_scores[idx] += 1
                dimension_counts[idx] += 1

            # Subtract point for "least like" dimension
            least_stmt = block.statements[response.least_like_index]
            if least_stmt.dimension in dim_to_idx:
                idx = dim_to_idx[least_stmt.dimension]
                dimension_scores[idx] -= 1
                dimension_counts[idx] += 1

        # Normalize by counts and scale to standard normal
        initial_theta = np.zeros(self.n_dimensions)
        for i in range(self.n_dimensions):
            if dimension_counts[i] > 0:
                initial_theta[i] = dimension_scores[i] / dimension_counts[i]

        # Scale to approximate standard normal
        initial_theta = initial_theta * 0.5

        return initial_theta

    def _mle_estimate(self,
                     responses: List[Dict],
                     blocks: List[QuartetBlock],
                     initial_theta: np.ndarray,
                     use_prior: bool) -> Tuple[np.ndarray, np.ndarray, bool, int]:
        """
        Maximum Likelihood Estimation of theta
        """
        # Define objective function (negative log-likelihood)
        def objective(theta):
            ll = self._log_likelihood(theta, responses, blocks)

            # Add prior if requested (MAP estimation)
            if use_prior:
                # Standard normal prior
                prior_ll = -0.5 * np.sum(theta ** 2)
                ll += prior_ll

            return -ll  # Minimize negative log-likelihood

        # Optimization bounds (reasonable range for trait scores)
        bounds = [(-3, 3)] * self.n_dimensions

        # Perform optimization
        result = optimize.minimize(
            objective,
            initial_theta,
            method='L-BFGS-B',
            bounds=bounds,
            options={
                'maxiter': 200,
                'ftol': 1e-6
            }
        )

        # Estimate standard errors using Hessian
        if result.success:
            # Approximate Hessian at solution
            hessian = self._compute_hessian(result.x, responses, blocks)

            # Standard errors are sqrt of diagonal of inverse Hessian
            try:
                inv_hessian = np.linalg.inv(hessian)
                se = np.sqrt(np.diagonal(inv_hessian))
            except np.linalg.LinAlgError:
                # If Hessian is singular, use default SE
                se = np.ones(self.n_dimensions) * 0.5
        else:
            se = np.ones(self.n_dimensions) * 0.5

        return result.x, se, result.success, result.nit

    def _eap_estimate(self,
                     responses: List[Dict],
                     blocks: List[QuartetBlock],
                     initial_theta: np.ndarray) -> Tuple[np.ndarray, np.ndarray, bool, int]:
        """
        Expected A Posteriori (Bayesian) estimation

        This uses numerical integration over the posterior distribution
        """
        # For prototype, fallback to MLE with prior
        # Full EAP implementation would use MCMC or quadrature
        return self._mle_estimate(responses, blocks, initial_theta, use_prior=True)

    def _log_likelihood(self,
                       theta: np.ndarray,
                       responses: List[Dict],
                       blocks: List[QuartetBlock]) -> float:
        """
        Calculate log-likelihood of responses given theta
        """
        ll = 0.0

        for response in responses:
            # Get block
            block = next((b for b in blocks if b.block_id == response['block_id']), None)
            if not block:
                continue

            # Compute utilities for each statement
            utilities = self._compute_utilities(theta, block)

            # Calculate probability of observed choice
            prob = self._choice_probability(
                utilities,
                response['most_like'],
                response['least_like']
            )

            # Add to log-likelihood (with small epsilon to avoid log(0))
            ll += np.log(prob + 1e-10)

        return ll

    def _compute_utilities(self, theta: np.ndarray, block: QuartetBlock) -> np.ndarray:
        """
        Compute latent utilities for statements in a block
        """
        utilities = np.zeros(4)

        # Map dimension names to theta indices
        dim_to_idx = {
            'Achiever': 0, 'Activator': 1, 'Adaptability': 2,
            'Analytical': 3, 'Arranger': 4, 'Belief': 5,
            'Command': 6, 'Communication': 7, 'Competition': 8,
            'Connectedness': 9, 'Consistency': 10, 'Context': 11
        }

        for i, stmt in enumerate(block.statements):
            if stmt.dimension in dim_to_idx:
                dim_idx = dim_to_idx[stmt.dimension]
                # Utility = factor_loading * theta + error
                # For deterministic utility, ignore error term
                utilities[i] = stmt.factor_loading * theta[dim_idx]

        return utilities

    def _choice_probability(self,
                          utilities: np.ndarray,
                          most_idx: int,
                          least_idx: int) -> float:
        """
        Calculate probability of selecting specific most/least items

        Uses Bradley-Terry-Luce extension for forced-choice
        """
        # Softmax for "most like" probability
        exp_utils = np.exp(utilities - np.max(utilities))  # Subtract max for stability
        p_most = exp_utils[most_idx] / np.sum(exp_utils)

        # For "least like", use inverse utilities
        # Remove the selected "most like" item
        remaining_utils = utilities.copy()
        remaining_utils[most_idx] = -np.inf  # Exclude from least selection

        # Softmax on negative utilities for "least like"
        exp_neg_utils = np.exp(-remaining_utils - np.max(-remaining_utils[remaining_utils > -np.inf]))
        exp_neg_utils[most_idx] = 0  # Ensure excluded

        if np.sum(exp_neg_utils) > 0:
            p_least = exp_neg_utils[least_idx] / np.sum(exp_neg_utils)
        else:
            p_least = 1/3  # Uniform if numerical issues

        # Joint probability
        return p_most * p_least

    def _compute_hessian(self,
                        theta: np.ndarray,
                        responses: List[Dict],
                        blocks: List[QuartetBlock]) -> np.ndarray:
        """
        Compute Hessian matrix for standard error estimation

        Uses finite differences approximation
        """
        n = self.n_dimensions
        hessian = np.zeros((n, n))
        eps = 1e-5

        # Base log-likelihood
        base_ll = self._log_likelihood(theta, responses, blocks)

        # Compute second derivatives
        for i in range(n):
            for j in range(i, n):
                theta_pp = theta.copy()
                theta_pp[i] += eps
                theta_pp[j] += eps

                theta_pm = theta.copy()
                theta_pm[i] += eps
                theta_pm[j] -= eps

                theta_mp = theta.copy()
                theta_mp[i] -= eps
                theta_mp[j] += eps

                theta_mm = theta.copy()
                theta_mm[i] -= eps
                theta_mm[j] -= eps

                # Finite difference approximation
                ll_pp = self._log_likelihood(theta_pp, responses, blocks)
                ll_pm = self._log_likelihood(theta_pm, responses, blocks)
                ll_mp = self._log_likelihood(theta_mp, responses, blocks)
                ll_mm = self._log_likelihood(theta_mm, responses, blocks)

                hessian[i, j] = (ll_pp - ll_pm - ll_mp + ll_mm) / (4 * eps * eps)

                if i != j:
                    hessian[j, i] = hessian[i, j]

        return -hessian  # Negative for Hessian of log-likelihood

    def compute_normative_scores(self, theta_estimate: ThetaEstimate) -> NormativeScores:
        """
        Convert theta estimates to normative scores
        """
        if not self.norm_data:
            # If no norm data, return raw scores
            return NormativeScores(
                percentiles=np.zeros(self.n_dimensions),
                t_scores=50 * np.ones(self.n_dimensions),
                stanines=5 * np.ones(self.n_dimensions),
                raw_theta=theta_estimate.theta
            )

        # Extract normative parameters
        means = np.array(self.norm_data.get('means', np.zeros(self.n_dimensions)))
        sds = np.array(self.norm_data.get('sds', np.ones(self.n_dimensions)))

        # Calculate z-scores
        z_scores = (theta_estimate.theta - means) / sds

        # Convert to various norm-referenced scores
        percentiles = stats.norm.cdf(z_scores) * 100
        t_scores = 50 + 10 * z_scores

        # Stanines (1-9 scale)
        stanines = np.zeros(self.n_dimensions)
        stanine_cuts = [-np.inf, -1.75, -1.25, -0.75, -0.25, 0.25, 0.75, 1.25, 1.75, np.inf]
        for i, z in enumerate(z_scores):
            for s in range(9):
                if stanine_cuts[s] <= z < stanine_cuts[s+1]:
                    stanines[i] = s + 1
                    break

        return NormativeScores(
            percentiles=percentiles,
            t_scores=t_scores,
            stanines=stanines,
            raw_theta=theta_estimate.theta
        )

    def generate_report(self,
                       theta_estimate: ThetaEstimate,
                       normative_scores: NormativeScores) -> Dict:
        """
        Generate structured scoring report
        """
        dimension_names = [
            'Achiever', 'Activator', 'Adaptability',
            'Analytical', 'Arranger', 'Belief',
            'Command', 'Communication', 'Competition',
            'Connectedness', 'Consistency', 'Context'
        ]

        report = {
            'model_version': self.parameters.model_version if self.parameters else '4.0-prototype',
            'estimation_method': 'Thurstonian IRT',
            'convergence': theta_estimate.convergence,
            'model_fit': {
                'log_likelihood': theta_estimate.log_likelihood,
                'n_iterations': theta_estimate.n_iterations
            },
            'dimensions': []
        }

        for i, name in enumerate(dimension_names):
            report['dimensions'].append({
                'name': name,
                'theta': float(theta_estimate.theta[i]),
                'se': float(theta_estimate.se[i]),
                'percentile': float(normative_scores.percentiles[i]),
                't_score': float(normative_scores.t_scores[i]),
                'stanine': int(normative_scores.stanines[i])
            })

        # Sort dimensions by percentile for reporting top strengths
        report['dimensions'].sort(key=lambda x: x['percentile'], reverse=True)

        # Add top 5 strengths summary
        report['top_strengths'] = [d['name'] for d in report['dimensions'][:5]]

        return report