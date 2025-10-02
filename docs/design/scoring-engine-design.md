# Scoring Engine Technical Design Specification

> **Document Version**: 5.0 (Hierarchical IRT & Balance Metrics)
> **Date**: 2025-10-01
> **Author**: TaskMaster Design Agent
> **Status**: Ready for Implementation
> **Prerequisites**: `scoring-algorithm-research.md` (v5.0+)

## Executive Summary

This document specifies the technical architecture for the scoring engine, redesigned around a **Hierarchical Thurstonian IRT (H-MIRT) model** and a **balanced multi-statement forced-choice questionnaire**. This upgrade moves the system from a single-layer heuristic to a scientifically valid, two-level psychometric engine. The output is a structured **Tiered Talent Profile** that now includes both **facet and domain scores**, supplemented by **Domain Balance Metrics** for a more holistic interpretation.

## 1. Architecture Overview

### 1.1 System Context (H-MIRT-based Pipeline)

The new pipeline incorporates the offline calibration step and a more sophisticated online scoring engine.

```
[Offline Phase: Pre-computation]
┌──────────────────┐   ┌─────────────────┐   ┌─────────────────────────┐
│ Item Pool        │──▶│ Calibration     │──▶│ Pre-calibrated          │
│ (120+ Statements)│   │ Study (n≈800)   │   │ H-MIRT Parameters (.json)│
└──────────────────┘   └─────────────────┘   └─────────────────────────┘
                                                       │ (Loads)
[Online Phase: Real-time Scoring]                      ▼
┌──────────────┐   ┌───────────────────┐   ┌───────────────────┐   ┌─────────────────────┐
│ User Responses │──▶│ H-MIRT Scoring    │──▶│ TalentTier      │──▶│ Tiered Talent Profile │
│ (Quartet Blocks) │   │ Engine            │   │ Classifier      │   │ (Facets & Domains)  │
└──────────────┘   └───────────────────┘   └───────────────────┘   └─────────────────────┘
                                                       ▲
                                                       │ (Calculates)
                                           ┌───────────────────┐
                                           │ Balance Metrics   │
                                           │ Calculator        │
                                           └───────────────────┘
```

### 1.2 Design Principles
(Unchanged)

### 1.3 Performance Requirements
- **Scoring Latency**: < 100ms per assessment (H-MIRT estimation is more intensive)
- **Database Write**: < 50ms per profile
- **Memory Usage**: < 100MB per scoring instance (to load H-MIRT parameters and Lambda matrix)

## 2. Core Components Design (Redesigned)

### 2.1 Data Structures

The input/output data structures are updated for the new hierarchical results.

```python
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class ForcedChoiceBlockResponse:
    """Represents a single response from a multi-statement block."""
    block_id: int
    most_like_me_statement_id: str
    least_like_me_statement_id: str

# --- TieredTalentProfile and Talent dataclasses are updated ---
@dataclass
class Talent:
    name: str # e.g., T1, T2...
    score: int # Percentile score

@dataclass
class Domain:
    name: str # e.g., EXECUTING...
    score: int # Percentile score
    talents: List[Talent]

@dataclass
class BalanceMetrics:
    dbi: float
    relative_entropy: float
    gini_coefficient: float

@dataclass
class TieredTalentProfile:
    domains: List[Domain]
    balance_metrics: BalanceMetrics
    # The 'dominant', 'supporting', 'lesser' classification can be derived from the full list
```

### 2.2 HMIRTScorer (Revised Core Component)
**Location**: `src/main/python/core/scoring/scorer.py`

This class is the new heart of the engine. It applies a pre-trained hierarchical statistical model.

```python
class HMIRTScorer:
    """
    Estimates latent talent and domain traits using a pre-calibrated H-MIRT model.
    """
    def __init__(self, item_param_path: str, lambda_matrix_path: str):
        """
        Initializes the scorer by loading pre-calibrated model parameters.

        Args:
            item_param_path: Path to the JSON file with IRT item parameters.
            lambda_matrix_path: Path to the JSON file with the 12x4 Lambda loading matrix.
        """
        self.item_params = self._load_json(item_param_path)
        self.lambda_matrix = self._load_json(lambda_matrix_path) # Or numpy array
        # In a real implementation, this would initialize a statistical model object

    def estimate_scores(self, responses: List[ForcedChoiceBlockResponse]) -> Dict[str, Dict[str, float]]:
        """
        Takes block responses and returns latent trait scores for facets and domains.

        Returns:
            A dictionary containing facet thetas and domain etas.
        """
        # Step 1: Apply the Thurstonian IRT model to estimate latent facet traits (thetas)
        facet_thetas = self._estimate_latent_facet_thetas(responses)

        # Step 2: Use the Lambda matrix to estimate domain scores (etas)
        # This is a simplification; in a true H-MIRT, this is done jointly.
        # Here, we simulate a two-step process for design clarity.
        domain_etas = self._estimate_latent_domain_etas(facet_thetas)
        
        return {"facets": facet_thetas, "domains": domain_etas}

    def _estimate_latent_facet_thetas(self, responses: List[ForcedChoiceBlockResponse]) -> Dict[str, float]:
        """(Placeholder for the core Thurstonian IRT estimation logic)"""
        # --- This is a placeholder for a complex statistical calculation (e.g., MLE/EAP) ---
        print("Applying Thurstonian IRT model for 12 facets...")
        # Mock data for demonstration purposes
        mock_thetas = {f"T{i+1}": (i - 5.5) / 3.5 for i in range(12)}
        return mock_thetas

    def _estimate_latent_domain_etas(self, facet_thetas: Dict[str, float]) -> Dict[str, float]:
        """(Placeholder for estimating domain scores from facet scores)"""
        # In a real H-MIRT, etas and thetas are estimated simultaneously.
        # This function represents the aggregation step guided by the Lambda matrix.
        print("Aggregating to 4 domain scores using Lambda matrix...")
        # Mock data for demonstration
        mock_etas = {
            "EXECUTING": 0.8, "INFLUENCING": -0.2,
            "RELATIONSHIP_BUILDING": 0.5, "STRATEGIC_THINKING": 1.1
        }
        return mock_etas

    def _load_json(self, path: str) -> dict:
        import json
        with open(path, 'r') as f:
            return json.load(f)
```

### 2.3 BalanceCalculator (New Component)
**Location**: `src/main/python/core/scoring/balance.py`

A dedicated component for calculating the domain balance metrics.

```python
import numpy as np

class BalanceCalculator:
    """Calculates domain balance metrics from domain percentile scores."""
    
    def calculate(self, domain_percentiles: Dict[str, int]) -> BalanceMetrics:
        """
        Takes domain percentiles (0-100) and returns balance metrics.
        """
        p = np.array(list(domain_percentiles.values())) / 100.0
        
        # DBI
        var_max = np.var([1, 0, 0, 0])
        dbi = 1 - (np.var(p) / var_max) if var_max > 0 else 1.0
        
        # Relative Entropy
        p_norm = p / p.sum() if p.sum() > 0 else np.full(p.shape, 1/len(p))
        entropy = -np.sum(p_norm * np.log(p_norm + 1e-9))
        rel_entropy = entropy / np.log(len(p))
        
        # Gini Coefficient
        num = np.sum(np.abs(p[:, None] - p[None, :]))
        den = 2 * len(p) * np.sum(p)
        gini = num / den if den > 0 else 0.0
        
        return BalanceMetrics(
            dbi=dbi,
            relative_entropy=rel_entropy,
            gini_coefficient=gini
        )
```

### 2.4 TalentTierClassifier
(This component is now simplified. It takes percentile scores and maps them to tiers based on thresholds, but the main data structure is the nested `TieredTalentProfile`.)

## 3. Database Schema
(The v2.0 schema is still valid, but the JSONB column `strengths_profile` will now store the more complex `TieredTalentProfile` object, including domain scores and balance metrics.)

## 4. API Integration Points

### 4.1 Scoring Service (Conceptual)
The service now orchestrates the H-MIRT scorer and the balance calculator.

```python
class ScoringService:
    def __init__(self):
        # These paths would come from a configuration file
        ITEM_PARAM_PATH = "resources/hmirt_item_params_v1.json"
        LAMBDA_MATRIX_PATH = "resources/lambda_matrix_v1.json"
        
        self.scorer = HMIRTScorer(ITEM_PARAM_PATH, LAMBDA_MATRIX_PATH)
        self.quality_checker = ResponseQualityChecker()
        self.balance_calculator = BalanceCalculator()
        self.norm_converter = NormConverter() # Converts thetas/etas to percentiles

    def process_assessment(
        self,
        session_id: str,
        responses: List[ForcedChoiceBlockResponse]
    ) -> ScoringResult:
        """Orchestrates the H-MIRT based scoring pipeline."""
        # ... quality checks ...
        
        # 1. Get latent scores from H-MIRT model
        latent_scores = self.scorer.estimate_scores(responses)
        
        # 2. Convert latent scores to percentiles
        facet_percentiles = self.norm_converter.to_percentiles(latent_scores["facets"])
        domain_percentiles = self.norm_converter.to_percentiles(latent_scores["domains"])
        
        # 3. Calculate balance metrics
        balance_metrics = self.balance_calculator.calculate(domain_percentiles)
        
        # 4. Assemble the final profile object
        profile = self._assemble_profile(facet_percentiles, domain_percentiles, balance_metrics)
        
        # ... create and save ScoringResult with the new profile ...
        return result
```

### 4.2 API Endpoints
The API endpoint `/api/v5/assessment/results/{session_id}` will now return the new `TieredTalentProfile` structure including `domains` (with nested `talents`) and `balance_metrics`.

## 5. Testing Strategy (Updated)

Testing for the `HMIRTScorer` is different; it's about validating the *implementation* of the model, not the model's parameters themselves (which are validated offline).

- **`TestHMIRTScorer` (New & Critical)**:
    - Test that it correctly loads parameter files.
    - Create a known set of responses and pre-computed theta and eta scores. Assert that the Python implementation yields the same scores within a small tolerance.
    - Test the theta/eta-to-percentile conversion against known statistical values.
- **`TestBalanceCalculator` (New)**:
    - Test with known input vectors (e.g., `[100,0,0,0]`, `[25,25,25,25]`) and assert that the DBI, entropy, and Gini results match expected mathematical outcomes.
- **Integration & E2E Tests**: Update to send `ForcedChoiceBlockResponse` objects and validate the new, nested JSON response structure.

## 6. Implementation Checklist (Updated)

- [ ] **Task 0 (Pre-requisite)**: Conduct the offline item calibration study to produce the `hmirt_item_params.json` and `lambda_matrix.json` files.
- [ ] **Task 1**: Implement the updated data structures (`Talent`, `Domain`, `BalanceMetrics`, `TieredTalentProfile`).
- [ ] **Task 2**: Implement the new `HMIRTScorer`, including logic for loading parameters and applying the hierarchical model.
- [ ] **Task 3**: Implement the new `BalanceCalculator` component and its unit tests.
- [ ] **Task 4**: Update the `ScoringService` to orchestrate the new pipeline.
- [ ] **Task 5-7**: Update database logic, API endpoints to handle the new data structure, and write comprehensive integration tests.

---
## 7. Appendix: Item Generation Constraints (New)

The generation of the assessment booklet (questionnaire) shall be guided by Integer Linear Programming (ILP) or a similar combinatorial optimization method to ensure balance. The constraints should be implemented as specified in the provided `YAML`/`JSON` definition files.

**Key Design Parameters:**
- Talents (v): 12
- Blocks (b): 30
- Options per block (k): 4
- Appearances per talent (r): 10

**Primary Optimization Objectives:**
1.  Minimize the variance of the talent pairwise co-occurrence matrix.
2.  Minimize the variance of the domain inter-domain co-occurrence matrix.
3.  Ensure each block has statements from at least 3 different domains.

Refer to the `ilp-constraints.yml` file for the formal specification.

---
**Document Status**: Design Complete ✅

This v5.0 design provides a blueprint for a truly professional-grade psychometric engine. It is scientifically defensible, produces comparable normative scores at multiple levels, and provides novel insights through balance metrics.