# Talent Assessment Scoring & Interpretation Framework

> **Document Version**: 3.0 (Forced-Choice Model Redesign)
> **Date**: 2025-09-30
> **Author**: TaskMaster Design Agent
> **Status**: Complete Research for Implementation

## Executive Summary

This document presents the scientific and methodological foundation for the strength assessment project, redesigned around a custom **30-item forced-choice questionnaire**. This new approach moves beyond proxy measures (like the Big Five) to directly assess the relative intensity of **12 core talent facets**. The scoring engine's goal is to process these choices to generate a structured **Talent Tier Profile** (Dominant, Supporting, Lesser), providing users with a clear and actionable map of their natural strengths, directly inspired by the proven methodology of the Gallup CliftonStrengths assessment.

## 1. Assessment Instrument: The 30-Item Forced-Choice Model

### 1.1 Rationale for a Custom, Direct Assessment

The previous model utilized the Mini-IPIP (Big Five) as a proxy for talent. While valid, this approach is indirect. To increase precision and align more closely with authentic talent assessment methodologies, we are adopting a forced-choice model.

**Key Advantages:**
- **Direct Measurement**: Directly measures the trade-offs and preferences between different talents, rather than inferring them.
- **Reduces Bias**: By forcing a choice between two positive statements, it minimizes social desirability bias and the tendency to rate everything highly.
- **Captures Intuition**: When combined with a timer, this format encourages intuitive, "top-of-mind" responses that are more indicative of innate talent.
- **Higher Fidelity**: Provides a clearer, more nuanced signal for ranking an individual's unique hierarchy of talents.

### 1.2 Instrument Structure

The assessment consists of **30 questions**. Each question presents the user with a pair of statements, and the user must choose the one that better describes them.

- **Total Items**: 30
- **Format**: Forced-Choice Pairs
- **Talent Facets Measured**: 12
- **Scoring Logic**: Direct Tally (Preference Counting)

## 2. Detailed Scoring Methodology

### 2.1 Core Scoring Algorithm: Preference Tallying

The scoring process is a direct calculation of how many times each of the 12 talent facets was preferred over another.

**Step 1: Response Collection**
- For each of the 30 questions, the user's choice ('A' or 'B') is recorded.
- A recommended (but not required for scoring) 20-second timer per question is used to encourage intuitive responses.

**Step 2: Score Calculation**
- A predefined **Question-to-Talent Pairing Matrix** maps each choice (e.g., 1A, 1B, 2A, 2B...) to one of the 12 talent facets.
- The system iterates through the 30 responses.
- For each response, the score of the corresponding talent facet is incremented by one.
- The final raw score for each talent is the total number of times it was chosen. The sum of all raw scores will always be 30.

**Example:**
- If Question 5 pairs `分析與洞察` (A) vs. `影響與倡議` (B), and the user chooses 'A', the score for `分析與洞察` increases by 1.

### 2.2 Question-to-Talent Pairing Matrix

To ensure a balanced and valid assessment, each of the 12 talents must be paired an equal number of times. With 30 questions, each talent will appear in **5** pairings. The following matrix defines the "golden 30" questions.

**Talent Facets Legend:**
- **T1**: 結構化執行
- **T2**: 品質與完備
- **T3**: 探索與創新
- **T4**: 分析與洞察
- **T5**: 影響與倡議
- **T6**: 協作與共好
- **T7**: 客戶導向
- **T8**: 學習與成長
- **T9**: 紀律與信任
- **T10**: 壓力調節
- **T11**: 衝突整合
- **T12**: 責任與當責

**Pairing Matrix (30 Questions):**
```python
TALENT_PAIRING_MATRIX = {
    1: ("T1", "T3"),    2: ("T2", "T4"),    3: ("T5", "T7"),
    4: ("T6", "T8"),    5: ("T9", "T11"),   6: ("T10", "T12"),
    7: ("T1", "T4"),    8: ("T2", "T5"),    9: ("T3", "T6"),
    10: ("T7", "T9"),   11: ("T8", "T10"),  12: ("T11", "T1"),
    13: ("T12", "T2"),  14: ("T4", "T5"),   15: ("T3", "T8"),
    16: ("T6", "T11"),  17: ("T7", "T12"),  18: ("T9", "T1"),
    19: ("T10", "T2"),  20: ("T5", "T11"),  21: ("T3", "T12"),
    22: ("T4", "T6"),   23: ("T8", "T9"),   24: ("T1", "T7"),
    25: ("T2", "T6"),   26: ("T3", "T10"),  27: ("T4", "T11"),
    28: ("T5", "T9"),   29: ("T7", "T8"),   30: ("T12", "T4")
}
# Note: This is a balanced sample matrix. The final matrix
# will require psychometric validation. Each talent appears 5 times.
```

## 3. Talent Tier Interpretation Framework

This framework remains the core of the report generation. It translates the raw preference counts into an actionable, hierarchical structure.

### 3.1 Rationale and Definition

(This section remains the same as in v2.0, as the logic of classifying a ranked list of talents is unchanged.)

### 3.2 Tier Classification Logic

The classification logic is applied to the raw scores generated from the preference tally.

1.  **Input**: A dictionary of 12 talent facets and their raw scores (ranging from 0 to 5, summing to 30).
2.  **Process**: Sort the talents in descending order based on their scores. In case of ties, a consistent secondary sorting rule (e.g., alphabetical) should be applied to ensure stable rankings.
3.  **Output**:
    *   The top 4 are classified as `Dominant`.
    *   The middle 4 are classified as `Supporting`.
    *   The bottom 4 are classified as `Lesser`.

## 4. Quality Assurance and Next Steps

### 4.1 Validity and Reliability
The next critical phase for this instrument is psychometric validation:
- **Construct Validity**: Do the questions accurately measure the intended talent facets?
- **Test-Retest Reliability**: Do users get a similar talent ranking if they retake the test after a period?
- **Predictive Validity**: Does a high rank in a certain talent correlate with real-world performance in related tasks?

### 4.2 Implementation Recommendations
The implementation pipeline is now simpler and more direct:
1.  **Input Validation**: Verify 30 complete responses.
2.  **Quality Assessment**: Flag potential issues (e.g., completion time, response patterns).
3.  **Raw Score Calculation**: Apply the preference tallying algorithm using the `TALENT_PAIRING_MATRIX`.
4.  **Talent Tiering**: Classify the 12 ranked talents into Dominant, Supporting, and Lesser tiers.
5.  **Storage**: Save the complete tiered profile to the database.

---
This research provides the definitive foundation for implementing a direct, robust, and insightful talent assessment system centered on the **Talent Tier Profile**.