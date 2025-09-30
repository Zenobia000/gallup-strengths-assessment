# Scoring Engine Technical Design Specification

> **Document Version**: 3.0 (Forced-Choice Model Redesign)
> **Date**: 2025-09-30
> **Author**: TaskMaster Design Agent
> **Status**: Ready for Implementation
> **Prerequisites**: `scoring-algorithm-research.md` (v3.0+)

## Executive Summary

This document specifies the technical architecture for the scoring engine, redesigned around a **30-item forced-choice questionnaire**. The system's primary output is a structured **Tiered Talent Profile**, generated directly from user preferences. This design is simpler, more robust, and provides higher-fidelity insights than the previous proxy-based model.

## 1. Architecture Overview

### 1.1 System Context (Direct Assessment Pipeline)

The new pipeline is significantly streamlined. It directly translates user choices into a ranked talent profile, which is then classified into tiers.

```
┌──────────────┐   ┌───────────────────┐   ┌───────────────────┐   ┌──────────────────┐
│ 30 Forced-   │──▶│ ForcedChoice      │──▶│ TalentTier      │──▶│ Tiered Talent    │
│ Choice       │   │ Scorer            │   │ Classifier      │   │ Profile          │
│ Responses    │   │ (Tallying Engine) │   │                   │   │ (Final Output)   │
└──────────────┘   └───────────────────┘   └───────────────────┘   └──────────────────┘
        (Input)            (Ranked Talents)      (Tiered Profile)         │
                                                                         ▼
                                                                 ┌──────────────────┐
                                                                 │ Recommendation   │
                                                                 │ Engine (Week 3)  │
                                                                 └──────────────────┘
```

### 1.2 Design Principles
(Unchanged from v2.0)

### 1.3 Performance Requirements
- **Scoring Latency**: < 5ms per assessment (The new algorithm is computationally simpler)
- **Database Write**: < 50ms per profile
- **Memory Usage**: < 10MB per scoring instance
- **Reliability**: 99.9% uptime for scoring operations

## 2. Core Components Design (Redesigned)

### 2.1 Data Structures

The final-output data structures (`Talent`, `TieredTalentProfile`, `ScoringResult`) from v2.0 remain perfectly suited for this new architecture. However, the input data structure changes.

```python
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class ForcedChoiceResponse:
    """Represents a single response from the 30-item questionnaire."""
    question_id: int  # 1-30
    chosen_option: str  # "A" or "B"

# ... TieredTalentProfile, Talent, and ScoringResult dataclasses remain as defined in v2.0 ...
```

### 2.2 ForcedChoiceScorer (New Core Component)
**Location**: `src/main/python/core/scoring/scorer.py`

This class replaces the previous `MiniIPIPScorer` and `StrengthsMapper`. It is the new heart of the scoring engine.

```python
from collections import defaultdict

class ForcedChoiceScorer:
    """
    Calculates raw talent scores directly from 30 forced-choice responses.
    """
    TALENT_PAIRING_MATRIX = {
        # The 30-item matrix from the research document
        1: ("T1", "T3"), 2: ("T2", "T4"), 3: ("T5", "T7"),
        4: ("T6", "T8"), 5: ("T9", "T11"), 6: ("T10", "T12"),
        7: ("T1", "T4"), 8: ("T2", "T5"), 9: ("T3", "T6"),
        10: ("T7", "T9"), 11: ("T8", "T10"), 12: ("T11", "T1"),
        13: ("T12", "T2"), 14: ("T4", "T5"), 15: ("T3", "T8"),
        16: ("T6", "T11"), 17: ("T7", "T12"), 18: ("T9", "T1"),
        19: ("T10", "T2"), 20: ("T5", "T11"), 21: ("T3", "T12"),
        22: ("T4", "T6"), 23: ("T8", "T9"), 24: ("T1", "T7"),
        25: ("T2", "T6"), 26: ("T3", "T10"), 27: ("T4", "T11"),
        28: ("T5", "T9"), 29: ("T7", "T8"), 30: ("T12", "T4")
    }
    
    TALENT_IDS = [f"T{i}" for i in range(1, 13)]

    def calculate_scores(self, responses: List[ForcedChoiceResponse]) -> List[Talent]:
        """
        Takes 30 forced-choice responses and returns a ranked list of Talents.

        Args:
            responses: A list of 30 ForcedChoiceResponse objects.

        Returns:
            A list of 12 Talent objects, sorted by score in descending order.
        """
        if len(responses) != 30:
            raise ValueError("Expected exactly 30 responses.")

        talent_scores = defaultdict(int)

        for response in responses:
            q_id = response.question_id
            choice = response.chosen_option
            
            if q_id not in self.TALENT_PAIRING_MATRIX:
                continue # Or raise error for invalid question_id

            talent_pair = self.TALENT_PAIRING_MATRIX[q_id]
            chosen_talent_id = talent_pair[0] if choice == "A" else talent_pair[1]
            talent_scores[chosen_talent_id] += 1

        # Create a sorted list of Talent objects
        # Ensure all talents are present, even if their score is 0
        final_scores = {talent_id: talent_scores.get(talent_id, 0) for talent_id in self.TALENT_IDS}

        sorted_talents = sorted(
            final_scores.items(),
            key=lambda item: item[1],
            reverse=True
        )

        return [Talent(name=name, score=score) for name, score in sorted_talents]
```

### 2.3 TalentTierClassifier
**Location**: `src/main/python/core/scoring/tier.py`

(This component's design from v2.0 is **perfectly reusable** as-is. Its function is to take a ranked list of `Talent` objects and classify them, which is exactly what the new `ForcedChoiceScorer` provides.)

## 3. Database Schema
(The schema defined in v2.0 is **perfectly reusable**. The decision to store the final `TieredTalentProfile` as a JSON object in the `scores` table means no changes are needed here.)

## 4. API Integration Points (Simplified)

### 4.1 Scoring Service (Conceptual)

The orchestration service is now much simpler.

```python
class ScoringService:
    def __init__(self):
        self.scorer = ForcedChoiceScorer()
        self.quality_checker = ResponseQualityChecker() # Still useful for timing, patterns
        self.classifier = TalentTierClassifier()

    def process_assessment(
        self,
        session_id: str,
        responses: List[ForcedChoiceResponse],
        completion_time: int
    ) -> ScoringResult:
        """Orchestrates the new, direct scoring pipeline."""
        quality_flags = self.quality_checker.assess_quality(responses, completion_time)
        ranked_talents = self.scorer.calculate_scores(responses)
        tiered_profile = self.classifier.classify(ranked_talents)

        result = ScoringResult(
            session_id=session_id,
            tiered_profile=tiered_profile,
            # ... other metadata fields like confidence, quality_flags, etc.
        )
        
        self._save_profile_to_db(session_id, result)
        return result
```

### 4.2 API Endpoints
(The `/profile/{session_id}` endpoint defined in v2.0 remains the **ideal interface**. No changes are needed, as it is already designed to serve the final `TieredTalentProfile` object, regardless of how it was calculated.)

## 5. Testing Strategy (Updated)

Testing is now more focused.

### 5.1 Unit Testing
- **`TestForcedChoiceScorer` (New & Critical)**:
    - Create a mock response list where one talent is chosen 5 times and others less. Assert it is ranked first.
    - Create a response list where scores are tied. Assert a consistent secondary sort order.
    - Test with invalid input (e.g., 29 responses, invalid `chosen_option`).
- **`TestTalentTierClassifier`**: Tests from v2.0 are still valid.

### 5.2 Integration Testing
- The end-to-end test must be rewritten to provide a list of 30 `ForcedChoiceResponse` objects and assert that the final `TieredTalentProfile` is correctly structured and reflects the input choices.

## 6. Implementation Checklist (Updated)

- [ ] **Task 1**: Implement the `ForcedChoiceResponse` input data structure.
- [ ] **Task 2**: Implement the new `ForcedChoiceScorer` with the full 30-item pairing matrix.
- [ ] **Task 3**: Implement the `TalentTierClassifier` (reusing v2.0 design).
- [ ] **Task 4**: Update the main `ScoringService` to orchestrate the new, simpler pipeline.
- [ ] **Task 5**: Update the database logic to save the profile (reusing v2.0 design).
- [ ] **Task 6**: Implement the `/profile/{session_id}` API endpoint (reusing v2.0 design).
- [ ] **Task 7**: Write comprehensive unit and integration tests for the `ForcedChoiceScorer`.

---
**Document Status**: Design Complete ✅

This technical design provides a complete blueprint for a more direct, robust, and elegant talent assessment engine. By moving to the 30-item forced-choice model, the system's accuracy and alignment with proven psychometric principles are significantly enhanced.