# Scoring Engine Technical Design Specification

> **Document Version**: 4.0 (Thurstonian IRT Model Upgrade)
> **Date**: 2025-09-30
> **Author**: TaskMaster Design Agent
> **Status**: Ready for Implementation (Pending Calibration)
> **Prerequisites**: `scoring-algorithm-research.md` (v4.0+)

## Executive Summary

This document specifies the technical architecture for the scoring engine, redesigned around a **Thurstonian IRT model** and a **multi-statement forced-choice questionnaire**. This upgrade moves the system from a simple heuristic to a scientifically valid psychometric engine, producing normative, comparable scores. The output remains a structured **Tiered Talent Profile**, but its credibility and accuracy are significantly enhanced.

## 1. Architecture Overview

### 1.1 System Context (IRT-based Pipeline)

The new pipeline incorporates the offline calibration step and a more sophisticated online scoring engine.

```
[Offline Phase: Pre-computation]
┌──────────────────┐   ┌─────────────────┐   ┌─────────────────────────┐
│ Item Pool        │──▶│ Calibration     │──▶│ Pre-calibrated          │
│ (48+ Statements) │   │ Study (n≈500)   │   │ IRT Parameters (.json)  │
└──────────────────┘   └─────────────────┘   └─────────────────────────┘
                                                       │ (Loads)
[Online Phase: Real-time Scoring]                      ▼
┌──────────────┐   ┌───────────────────┐   ┌───────────────────┐   ┌──────────────────┐
│ User Responses │──▶│ IRT Scoring       │──▶│ TalentTier      │──▶│ Tiered Talent    │
│ (Quartet Blocks) │   │ Engine (TIRT)     │   │ Classifier      │   │ Profile          │
└──────────────┘   └───────────────────┘   └───────────────────┘   └──────────────────┘
```

### 1.2 Design Principles
(Unchanged)

### 1.3 Performance Requirements
- **Scoring Latency**: < 50ms per assessment (IRT estimation is more intensive than tallying)
- **Database Write**: < 50ms per profile
- **Memory Usage**: < 50MB per scoring instance (to load IRT parameters)

## 2. Core Components Design (Redesigned)

### 2.1 Data Structures

The input data structure is updated for block-based responses. The output structures remain relevant.

```python
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class ForcedChoiceBlockResponse:
    """Represents a single response from a multi-statement block."""
    block_id: int
    most_like_me_statement_id: str
    least_like_me_statement_id: str

# --- TieredTalentProfile, Talent, and ScoringResult dataclasses remain as defined in v2.0 ---
# Note: The `score` field in the `Talent` object will now represent a percentile (0-100).
```

### 2.2 IRTScorer (New Core Component)
**Location**: `src/main/python/core/scoring/scorer.py`

This class is the new heart of the engine, replacing all previous scoring and mapping logic. It applies a pre-trained statistical model.

```python
class IRTScorer:
    """
    Estimates latent talent traits using a pre-calibrated Thurstonian IRT model.
    """
    def __init__(self, item_param_path: str, norm_param_path: str):
        """
        Initializes the scorer by loading pre-calibrated model parameters.

        Args:
            item_param_path: Path to the JSON file with IRT item parameters.
            norm_param_path: Path to the JSON file with population norm parameters (means/SDs for theta-to-percentile conversion).
        """
        self.item_params = self._load_json(item_param_path)
        self.norm_params = self._load_json(norm_param_path)
        # In a real implementation, this might initialize a more complex
        # object for a library like `cats` or a custom estimation function.

    def estimate_scores(self, responses: List[ForcedChoiceBlockResponse]) -> List[Talent]:
        """
        Takes block responses and returns a ranked list of Talents with percentile scores.

        Returns:
            A list of 12 Talent objects with percentile scores, sorted descending.
        """
        # Step 1: Apply the TIRT model to estimate latent traits (thetas)
        # This is a complex statistical operation. The actual implementation
        # will depend on the chosen psychometric library or custom algorithm.
        # For design purposes, we represent it as a call to a private method.
        latent_thetas = self._estimate_latent_thetas(responses)

        # Step 2: Convert latent thetas to percentiles using population norms
        percentiles = self._convert_thetas_to_percentiles(latent_thetas)

        # Step 3: Create and sort Talent objects
        talents = [Talent(name=name, score=int(round(p))) for name, p in percentiles.items()]
        talents.sort(key=lambda t: t.score, reverse=True)
        
        return talents

    def _estimate_latent_thetas(self, responses: List[ForcedChoiceBlockResponse]) -> Dict[str, float]:
        """
        (Placeholder for the core IRT estimation logic)
        This function would use Maximum Likelihood Estimation (MLE) or
        Bayesian methods (e.g., EAP) to find the most likely theta values
        that would produce the given response pattern.
        """
        # --- This is a placeholder for a complex statistical calculation ---
        # A real implementation would involve matrix operations based on
        # self.item_params and the response vectors.
        print("Applying Thurstonian IRT model...")
        # For demonstration, return mock data.
        mock_thetas = {f"T{i+1}": (i - 5.5) / 3.5 for i in range(12)}
        return mock_thetas

    def _convert_thetas_to_percentiles(self, thetas: Dict[str, float]) -> Dict[str, float]:
        """
        Converts latent trait scores (thetas) to percentiles.
        Requires scipy or a similar stats library.
        """
        from scipy.stats import norm
        percentiles = {}
        for talent_id, theta in thetas.items():
            # Using standard normal distribution (Mean=0, SD=1) for thetas
            percentiles[talent_id] = norm.cdf(theta) * 100
        return percentiles

    def _load_json(self, path: str) -> dict:
        import json
        with open(path, 'r') as f:
            return json.load(f)

```

### 2.3 TalentTierClassifier
(This component's design from v2.0 is still valid. It now ingests `Talent` objects with percentile scores and classifies them based on pre-defined percentile thresholds, e.g., >75th, 25-75th, <25th.)

## 3. Database Schema
(The v2.0 schema is still valid. The `strengths_profile` JSON column will now store the `TieredTalentProfile` containing talents with percentile scores.)

## 4. API Integration Points

### 4.1 Scoring Service (Conceptual)

The service now depends on the pre-calibrated parameter files.

```python
class ScoringService:
    def __init__(self):
        # These paths would come from a configuration file
        ITEM_PARAM_PATH = "resources/irt_item_params_v1.json"
        NORM_PARAM_PATH = "resources/population_norms_v1.json"
        
        self.scorer = IRTScorer(ITEM_PARAM_PATH, NORM_PARAM_PATH)
        self.quality_checker = ResponseQualityChecker()
        self.classifier = TalentTierClassifier()

    def process_assessment(
        self,
        session_id: str,
        responses: List[ForcedChoiceBlockResponse],
        completion_time: int
    ) -> ScoringResult:
        """Orchestrates the IRT-based scoring pipeline."""
        # ... quality checks ...
        ranked_talents_with_percentiles = self.scorer.estimate_scores(responses)
        tiered_profile = self.classifier.classify(ranked_talents_with_percentiles)
        # ... create and save ScoringResult ...
            return result
```

### 4.2 API Endpoints
(The `/profile/{session_id}` endpoint from v2.0 remains the ideal interface.)

## 5. Testing Strategy (Updated)

Testing for the `IRTScorer` is different; it's about validating the *implementation* of the model, not the model's parameters themselves (which are validated offline).

- **`TestIRTScorer` (New & Critical)**:
    - Test that it correctly loads parameter files.
    - Create a known set of responses and a pre-computed, expected set of theta scores (calculated externally in R or a trusted tool). Assert that the Python implementation yields the same thetas within a small tolerance.
    - Test the theta-to-percentile conversion against known statistical values.
- **Integration & E2E Tests**: Update to send `ForcedChoiceBlockResponse` objects as input.

## 6. Implementation Checklist (Updated)

- [ ] **Task 0 (Critical Pre-requisite)**: Conduct the offline item calibration study and produce the `irt_item_params.json` and `population_norms.json` files.
- [ ] **Task 1**: Implement the `ForcedChoiceBlockResponse` input data structure.
- [ ] **Task 2**: Implement the new `IRTScorer`, including the logic for loading parameters and a placeholder or actual implementation of the IRT estimation algorithm.
- [ ] **Task 3**: Implement the `TalentTierClassifier` with percentile-based thresholds.
- [ ] **Task 4**: Update the `ScoringService` to orchestrate the new pipeline.
- [ ] **Task 5-7**: Update database logic, API endpoints, and tests as per the new design.

---
**Document Status**: Design Complete ✅

This v4.0 design provides a blueprint for a truly professional-grade psychometric engine. It is scientifically defensible, produces comparable normative scores, and aligns with the highest standards in modern talent assessment.