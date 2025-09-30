# Scoring Engine Technical Design Specification

> **Document Version**: 2.0 (Tier-Focused Redesign)
> **Date**: 2025-09-30
> **Author**: TaskMaster Week 2 Design Agent
> **Status**: Ready for Implementation
> **Prerequisites**: `scoring-algorithm-research.md` (v2.0+)

## Executive Summary

This document specifies the technical architecture for the scoring engine, redesigned to be centered around the **Talent Tier Framework**. The system's primary output is no longer a simple set of scores, but a structured **Tiered Talent Profile**. This design follows Linus Torvalds' principles of simplicity and reliability while delivering actionable, hierarchical insights to the user.

## 1. Architecture Overview

### 1.1 System Context (Tier-Focused)

The scoring pipeline is redesigned to explicitly produce a tiered profile, which then feeds into the recommendation engine.

```
┌──────────────┐   ┌───────────┐   ┌───────────┐   ┌───────────────────┐   ┌──────────────────┐
│ User         │──▶│ MiniIPIP  │──▶│ Strengths │──▶│ TalentTier      │──▶│ Tiered Talent    │
│ Responses    │   │ Scorer    │   │ Mapper    │   │ Classifier      │   │ Profile          │
└──────────────┘   └───────────┘   └───────────┘   └───────────────────┘   └──────────────────┘
        (Input)         (Raw Scores)   (Ranked Scores)      (Tiered Output)          │
                                                                                    ▼
                                                                            ┌──────────────────┐
                                                                            │ Recommendation   │
                                                                            │ Engine (Week 3)  │
                                                                            └──────────────────┘
```

### 1.2 Design Principles

**Linus Torvalds Philosophy Applied:**
- **Good Taste**: Eliminate edge cases through elegant algorithms
- **Never Break Userspace**: Maintain compatibility with existing assessment sessions
- **Pragmatic Solutions**: Use proven psychometric methods, not theoretical perfection
- **Simplicity**: Functions do one thing well, maximum 3 levels of indentation

### 1.3 Performance Requirements

- **Scoring Latency**: < 10ms per assessment (20 items)
- **Database Write**: < 50ms per score set
- **Batch Processing**: 100+ assessments per minute
- **Memory Usage**: < 15MB per scoring instance (to accommodate new objects)
- **Reliability**: 99.9% uptime for scoring operations

## 2. Core Components Design (Redesigned)

### 2.1 Data Structures (New)

To support the tier-focused architecture, we introduce new, more descriptive data structures.

```python
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
from models.schemas import ItemResponse, BigFiveScores, HEXACOScores

@dataclass
class Talent:
    """Represents a single talent with its score."""
    name: str
    score: int
    description: Optional[str] = None
    strategy: Optional[str] = None # For lesser talents

@dataclass
class TieredTalentProfile:
    """The primary, structured output of the scoring engine."""
    dominant_talents: List[Talent]
    supporting_talents: List[Talent]
    lesser_talents: List[Talent]
    full_ranking: List[Talent]

@dataclass
class ScoringResult:
    """Complete scoring result with metadata and the final tiered profile."""
    session_id: str
    tiered_profile: TieredTalentProfile
    raw_scores: BigFiveScores
    percentiles: Dict[str, float]
    confidence: float
    quality_flags: List[str]
    processing_time_ms: float
    algorithm_version: str
    calculated_at: datetime
```

### 2.2 MiniIPIPScorer Class
**Location**: `src/main/python/core/scoring/scorer.py`

(The internal logic of `MiniIPIPScorer` remains largely the same as in v1.0, calculating raw and standardized Big Five scores. Its role is now to provide the foundational data for the `StrengthsMapper`.)

```python
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from models.schemas import ItemResponse, BigFiveScores, HEXACOScores

@dataclass
class ScoringResult:
    """Complete scoring result with metadata"""
    raw_scores: BigFiveScores
    standardized_scores: BigFiveScores
    percentiles: Dict[str, float]
    confidence: float
    quality_flags: List[str]
    processing_time_ms: float
    algorithm_version: str
    calculated_at: datetime

class MiniIPIPScorer:
    """
    Mini-IPIP Big Five personality scorer.

    Implements validated psychometric algorithms following
    Donnellan et al. (2006) methodology.
    """

    # Class constants based on research
    ITEM_FACTOR_MAPPING = {
        "ipip_001": ("extraversion", False),    # Life of party (positive)
        "ipip_002": ("extraversion", True),     # Don't talk much (reverse)
        "ipip_003": ("extraversion", False),    # Comfortable around people
        "ipip_004": ("extraversion", True),     # Keep in background (reverse)
        # ... [complete mapping per research doc]
    }

    REVERSE_SCORED_ITEMS = {
        "ipip_002", "ipip_004", "ipip_006", "ipip_008", "ipip_010",
        "ipip_012", "ipip_014", "ipip_016", "ipip_018", "ipip_020"
    }

    ALGORITHM_VERSION = "v1.0.0"

    def __init__(self, normative_data: Optional[Dict] = None):
        """
        Initialize scorer with optional normative data.

        Args:
            normative_data: Population norms for standardization
        """
        self.norms = normative_data or self._load_default_norms()
        self.quality_checker = ResponseQualityChecker()

    def score_assessment(
        self,
        responses: List[ItemResponse],
        completion_time_seconds: int
    ) -> ScoringResult:
        """
        Complete scoring pipeline for Mini-IPIP assessment.

        Args:
            responses: List of 20 item responses
            completion_time_seconds: Time taken to complete

        Returns:
            ScoringResult with all metrics and quality indicators

        Raises:
            ScoringError: If responses are invalid or insufficient
        """
        start_time = time.perf_counter()

        # Validate inputs
        self._validate_responses(responses)

        # Assess response quality
        quality_flags = self.quality_checker.assess_quality(
            responses, completion_time_seconds
        )

        # Calculate raw scores
        raw_scores = self._calculate_raw_scores(responses)

        # Standardize scores
        standardized_scores, percentiles = self._standardize_scores(raw_scores)

        # Calculate confidence
        confidence = self._calculate_confidence(responses, raw_scores)

        processing_time = (time.perf_counter() - start_time) * 1000

        return ScoringResult(
            raw_scores=raw_scores,
            standardized_scores=standardized_scores,
            percentiles=percentiles,
            confidence=confidence,
            quality_flags=quality_flags,
            processing_time_ms=processing_time,
            algorithm_version=self.ALGORITHM_VERSION,
            calculated_at=datetime.utcnow()
        )

    def _calculate_raw_scores(self, responses: List[ItemResponse]) -> BigFiveScores:
        """
        Calculate raw Big Five scores with reverse scoring.

        Performance target: < 5ms for 20 items
        """
        # Convert to dict for O(1) lookup
        response_dict = {r.item_id: r.response for r in responses}

        # Initialize factor sums
        factor_sums = {
            "extraversion": 0,
            "agreeableness": 0,
            "conscientiousness": 0,
            "neuroticism": 0,
            "openness": 0
        }

        # Process each item
        for item_id, raw_response in response_dict.items():
            factor, is_reverse = self.ITEM_FACTOR_MAPPING[item_id]

            # Apply reverse scoring if needed (7-point scale: 8 - response)
            score = (8 - raw_response) if is_reverse else raw_response
            factor_sums[factor] += score

        return BigFiveScores(**factor_sums)

    def _standardize_scores(
        self,
        raw_scores: BigFiveScores
    ) -> Tuple[BigFiveScores, Dict[str, float]]:
        """
        Convert raw scores to standardized scores and percentiles.

        Uses local norms when available, literature norms as fallback.
        """
        standardized = {}
        percentiles = {}

        for factor in ["extraversion", "agreeableness", "conscientiousness",
                      "neuroticism", "openness"]:
            raw_score = getattr(raw_scores, factor)

            # Get normative data for this factor
            norm_data = self.norms.get(factor, {"mean": 16, "std": 4})

            # Calculate z-score
            z_score = (raw_score - norm_data["mean"]) / norm_data["std"]

            # Convert to T-score (M=50, SD=10)
            t_score = int(50 + (z_score * 10))
            t_score = max(0, min(100, t_score))  # Clamp to 0-100

            # Calculate percentile
            percentile = scipy.stats.norm.cdf(z_score) * 100

            standardized[factor] = t_score
            percentiles[factor] = percentile

        return BigFiveScores(**standardized), percentiles

    def _calculate_confidence(
        self,
        responses: List[ItemResponse],
        raw_scores: BigFiveScores
    ) -> float:
        """
        Calculate scoring confidence based on response patterns.

        Returns:
            float: Confidence score 0.0-1.0
        """
        confidence_factors = []

        # Factor 1: Response consistency within factors
        consistency_score = self._assess_response_consistency(responses)
        confidence_factors.append(consistency_score)

        # Factor 2: Score extremeness (more extreme = more confident)
        extremeness_score = self._assess_score_extremeness(raw_scores)
        confidence_factors.append(extremeness_score)

        # Factor 3: Response variance (not all same response)
        variance_score = self._assess_response_variance(responses)
        confidence_factors.append(variance_score)

        return sum(confidence_factors) / len(confidence_factors)
```

### 2.3 Response Quality Checker

```python
class ResponseQualityChecker:
    """
    Validates response quality for psychometric standards.

    Implements multiple quality checks to flag potentially invalid responses.
    """

    def assess_quality(
        self,
        responses: List[ItemResponse],
        completion_time: int
    ) -> List[str]:
        """
        Comprehensive quality assessment.

        Returns list of quality flags (empty list = good quality).
        """
        flags = []

        # Check completion time
        if completion_time < 60:
            flags.append("COMPLETION_TOO_FAST")
        elif completion_time > 1800:  # 30 minutes
            flags.append("COMPLETION_TOO_SLOW")

        # Check response patterns
        response_values = [r.response for r in responses]

        # All same response
        if len(set(response_values)) == 1:
            flags.append("ALL_SAME_RESPONSE")

        # Extreme response bias
        extreme_count = response_values.count(1) + response_values.count(7)
        if extreme_count > 15:  # >75% extreme responses
            flags.append("EXTREME_RESPONSE_BIAS")

        # Straight-line responding
        if self._has_straight_line_pattern(response_values):
            flags.append("STRAIGHT_LINE_RESPONDING")

        # Response variance too low
        if statistics.stdev(response_values) < 0.5:
            flags.append("LOW_RESPONSE_VARIANCE")

        return flags

    def _has_straight_line_pattern(self, responses: List[int]) -> bool:
        """Check for consecutive identical responses (5+ in a row)"""
        consecutive_count = 1
        max_consecutive = 1

        for i in range(1, len(responses)):
            if responses[i] == responses[i-1]:
                consecutive_count += 1
                max_consecutive = max(max_consecutive, consecutive_count)
            else:
                consecutive_count = 1

        return max_consecutive >= 5
```

### 2.4 Strengths Mapper

```python
class StrengthsMapper:
    """
    Maps Big Five scores to 12 Gallup-style strength dimensions.

    Implements research-validated formulas for strength prediction.
    """

    STRENGTH_FORMULAS = {
        "結構化執行": lambda scores: 0.8 * scores.conscientiousness + 0.2 * (100 - scores.neuroticism),
        "品質與完備": lambda scores: 0.7 * scores.conscientiousness + 0.3 * scores.openness,
        "探索與創新": lambda scores: 0.8 * scores.openness + 0.2 * scores.extraversion,
        "分析與洞察": lambda scores: 0.6 * scores.openness + 0.4 * scores.conscientiousness,
        "影響與倡議": lambda scores: 0.7 * scores.extraversion + 0.3 * scores.conscientiousness,
        "協作與共好": lambda scores: 0.7 * scores.agreeableness + 0.3 * scores.extraversion,
        "客戶導向": lambda scores: 0.6 * scores.agreeableness + 0.4 * scores.extraversion,
        "學習與成長": lambda scores: 0.7 * scores.openness + 0.3 * scores.conscientiousness,
        "紀律與信任": lambda scores: 0.8 * scores.conscientiousness + 0.2 * scores.agreeableness,
        "壓力調節": lambda scores: 0.8 * (100 - scores.neuroticism) + 0.2 * scores.conscientiousness,
        "衝突整合": lambda scores: 0.6 * scores.agreeableness + 0.4 * (100 - scores.neuroticism),
        "責任與當責": lambda scores: 0.7 * scores.conscientiousness + 0.3 * scores.agreeableness,
    }

    def map_to_strengths(self, big_five_scores: BigFiveScores) -> List[Talent]:
        """Convert Big Five scores to a ranked list of 12 strength Talents."""
        strength_values = {}

        for strength_name, formula in self.STRENGTH_FORMULAS.items():
            raw_score = formula(big_five_scores)
            strength_values[strength_name] = int(max(0, min(100, raw_score)))

        # Sort by score to create a ranked list
        sorted_strengths = sorted(
            strength_values.items(),
            key=lambda item: item[1],
            reverse=True
        )

        return [Talent(name=name, score=score) for name, score in sorted_strengths]
```

### 2.5 TalentTierClassifier (New Core Component)

```python
class TalentTierClassifier:
    """
    Classifies a ranked list of talents into a structured, tiered profile.
    """
    DOMINANT_COUNT = 4
    SUPPORTING_COUNT = 4

    def classify(self, ranked_talents: List[Talent]) -> TieredTalentProfile:
        """
        Creates a TieredTalentProfile from a ranked list of talents.

        Args:
            ranked_talents: A list of Talent objects, sorted by score descending.

        Returns:
            A TieredTalentProfile object with talents categorized into tiers.
        """
        if len(ranked_talents) != 12:
            raise ValueError("Expected 12 ranked talents for classification.")

        dominant = ranked_talents[:self.DOMINANT_COUNT]
        supporting = ranked_talents[self.DOMINANT_COUNT : self.DOMINANT_COUNT + self.SUPPORTING_COUNT]
        lesser = ranked_talents[self.DOMINANT_COUNT + self.SUPPORTING_COUNT:]

        # Optionally, add descriptions and strategies here
        self._add_context(dominant, supporting, lesser)

        return TieredTalentProfile(
            dominant_talents=dominant,
            supporting_talents=supporting,
            lesser_talents=lesser,
            full_ranking=ranked_talents
        )

    def _add_context(self, dominant: List[Talent], supporting: List[Talent], lesser: List[Talent]):
        """Placeholder for adding descriptions and management strategies."""
        for talent in dominant:
            talent.description = f"This is a key driver for you..."
        for talent in lesser:
            talent.strategy = f"Partner with others who excel in {talent.name}..."
```

## 3. Database Schema Extensions (Redesigned)

### 3.1 Enhanced Scores Table

The `scores` table will be adapted to store the full, structured `TieredTalentProfile` as JSON, which is more aligned with the system's purpose.

```sql
-- Existing scores table structure is assumed.
-- Key change is to the `strengths_profile` column.
ALTER TABLE scores ADD COLUMN strengths_profile JSON; -- Was TEXT or other

-- We will store the full TieredTalentProfile object in `strengths_profile`.
-- Other columns like `raw_scores`, `percentiles`, `scoring_confidence` remain.

-- Example JSON structure for `strengths_profile`:
-- {
--   "dominant_talents": [{"name": "...", "score": 92}, ...],
--   "supporting_talents": [...],
--   "lesser_talents": [...],
--   "full_ranking": [...]
-- }
```

### 3.2 New Normative Data Table

```sql
CREATE TABLE normative_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    factor TEXT NOT NULL,
    sample_size INTEGER NOT NULL,
    mean_score REAL NOT NULL,
    std_deviation REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,

    CONSTRAINT valid_factor CHECK (factor IN (
        'extraversion', 'agreeableness', 'conscientiousness',
        'neuroticism', 'openness'
    )),
    CONSTRAINT valid_stats CHECK (
        sample_size > 0 AND std_deviation > 0
    ),
    UNIQUE(version, factor)
);

-- Seed with initial literature-based norms
INSERT INTO normative_data (version, factor, sample_size, mean_score, std_deviation) VALUES
('literature_v1.0', 'extraversion', 1000, 16.0, 4.2),
('literature_v1.0', 'agreeableness', 1000, 17.5, 3.8),
('literature_v1.0', 'conscientiousness', 1000, 18.2, 4.1),
('literature_v1.0', 'neuroticism', 1000, 15.3, 4.6),
('literature_v1.0', 'openness', 1000, 16.8, 4.0);
```

## 4. API Integration Points (Redesigned)

### 4.1 Scoring Service (Conceptual)

The overall service orchestrates the new pipeline.

```python
class ScoringService:
    def __init__(self):
        self.scorer = MiniIPIPScorer()
        self.quality_checker = ResponseQualityChecker()
        self.mapper = StrengthsMapper()
        self.classifier = TalentTierClassifier()

    def process_assessment(
        self,
        session_id: str,
        responses: List[ItemResponse],
        completion_time: int
    ) -> ScoringResult:
        """Orchestrates the new, tier-focused scoring pipeline."""
        start_time = time.perf_counter()

        quality_flags = self.quality_checker.assess_quality(responses, completion_time)
        raw_scores, standardized_scores, percentiles = self.scorer.score(responses)
        ranked_talents = self.mapper.map_to_strengths(standardized_scores)
        tiered_profile = self.classifier.classify(ranked_talents)

        # ... calculate confidence, etc. ...

        result = ScoringResult(
            session_id=session_id,
            tiered_profile=tiered_profile,
            # ... other metadata fields
        )

        self._save_profile_to_db(session_id, result)
        return result
```

### 4.2 API Endpoints (Crucial Change)

The primary API endpoint is redesigned to deliver the `TieredTalentProfile`.

```python
# In api/routes/scoring.py (or a new file)
from models.schemas import TieredTalentProfileResponse # New Pydantic model for response

@router.get("/profile/{session_id}", response_model=APIResponse)
async def get_talent_profile(session_id: str):
    """
    Get the complete, structured Tiered Talent Profile for a session.
    This is the primary endpoint for retrieving assessment results.
    """
    profile_data = db.get_profile(session_id) # Fetches the stored JSON
    if not profile_data:
        raise HTTPException(404, "Talent profile not found")

    # Assuming profile_data is the JSON of TieredTalentProfile
    return APIResponse(
        success=True,
        data=profile_data
    )

# Example Response JSON:
# {
#   "success": true,
#   "data": {
#     "dominant_talents": [
#       { "name": "結構化執行", "score": 92, "description": "...", "strategy": null },
#       { "name": "分析與洞察", "score": 88, "description": "...", "strategy": null }
#     ],
#     "supporting_talents": [
#       { "name": "學習與成長", "score": 79, "description": "...", "strategy": null }
#     ],
#     "lesser_talents": [
#       { "name": "影響與倡議", "score": 45, "description": null, "strategy": "Partner with others..." }
#     ],
#     "full_ranking": [
#       { "name": "結構化執行", "score": 92, ... },
#       ...
#     ]
#   }
# }
```

## 5. Testing Strategy (Updated)

Testing must now validate the tiering logic and the new data structures.

### 5.1 Unit Testing
- `TestMiniIPIPScorer`: Unchanged.
- `TestStrengthsMapper`: Update tests to assert that the output is a sorted list of `Talent` objects.
- `TestTalentTierClassifier` (New):
    - Test with a standard list of 12 talents, ensure correct classification.
    - Test with edge cases (e.g., ties in scores).
    - Test with invalid input (e.g., not 12 talents).

### 5.2 Integration Testing
- `TestScoringIntegration`: The end-to-end test must now verify the final `TieredTalentProfile` structure. Assert that `dominant_talents` contains the highest-scoring items.

### 5.3 Performance Testing
- The pipeline now has an extra step. Benchmark the `TalentTierClassifier`, which should be very fast (< 1ms). Ensure the total scoring latency remains under the 15ms target.

## 6. Monitoring and Analytics (Updated)

Metrics should be adapted to the tiered model.

- **Monitor Tier Distribution**: Track the population-level frequency of each talent appearing in the `Dominant` tier. This can reveal interesting insights about your user base.
- **Track Lesser Talent Patterns**: Analyze which talents most commonly appear in the `Lesser` tier, which can inform training or team-building recommendations.

## 7. Error Handling and Recovery

### 7.1 Comprehensive Error Types

```python
class ScoringError(Exception):
    """Base exception for scoring operations."""
    def __init__(self, message: str, code: str, context: Dict = None):
        self.message = message
        self.code = code
        self.context = context or {}
        super().__init__(self.message)

class InvalidResponseError(ScoringError):
    """Raised when responses fail validation."""
    pass

class QualityThresholdError(ScoringError):
    """Raised when response quality is too low for reliable scoring."""
    pass

class NormativeDataError(ScoringError):
    """Raised when normative data is unavailable or invalid."""
    pass
```

### 7.2 Graceful Degradation

```python
class RobustScorer:
    """Scoring engine with fallback strategies."""

    def score_with_fallback(self, responses: List[ItemResponse]) -> ScoringResult:
        """Score with multiple fallback strategies."""
        try:
            return self.primary_scorer.score_assessment(responses, 300)
        except NormativeDataError:
            # Fallback to literature norms
            return self.fallback_scorer.score_assessment(responses, 300)
        except QualityThresholdError as e:
            # Return scores with quality warnings
            result = self._calculate_best_effort_scores(responses)
            result.quality_flags.append(f"QUALITY_WARNING: {e.message}")
            return result
```

## 8. Implementation Checklist (Updated)

### 8.1 Week 2 Development Tasks

- [ ] **Task 3.2.2**: Refactor `MiniIPIPScorer` and define new data structures (`Talent`, `TieredTalentProfile`).
- [ ] **Task 3.2.3**: Implement `ResponseQualityChecker` (as before).
- [ ] **Task 3.2.4**: Update `StrengthsMapper` to return a ranked list of `Talent` objects.
- [ ] **Task 3.2.5 (New)**: Implement the new `TalentTierClassifier` component.
- [ ] **Task 3.2.6**: Update database logic to store and retrieve the `TieredTalentProfile` JSON.
- [ ] **Task 3.2.7**: Implement the new `/profile/{session_id}` API endpoint and response model.
- [ ] **Task 3.2.8**: Update all tests to reflect the new architecture and data structures.
- [ ] **Task 3.2.9**: Add monitoring for tier distribution.

### 8.2 Quality Gates

Each task must pass:
- [ ] **Unit tests**: > 90% coverage
- [ ] **Performance tests**: Meet latency targets
- [ ] **Integration tests**: End-to-end functionality
- [ ] **Code review**: Linus principles compliance
- [ ] **Documentation**: Complete API docs

### 8.3 Ready for Week 3

After completion, system will support:
- [ ] Real-time personality scoring
- [ ] Strength dimension calculation
- [ ] Quality assessment and confidence metrics
- [ ] Performance monitoring
- [ ] Robust error handling
- [ ] Foundation for recommendation engine

---

**Document Status**: Design Complete ✅
**Implementation Ready**: All components and interfaces are specified for the tier-focused architecture.
**Quality Assured**: Comprehensive testing strategy is adapted for the new design.

This technical design provides the complete blueprint for implementing a scoring engine that is fundamentally oriented around producing an actionable, hierarchical **Tiered Talent Profile**.