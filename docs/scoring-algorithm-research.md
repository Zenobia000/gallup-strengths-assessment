# Talent Assessment Scoring & Interpretation Framework

> **Document Version**: 4.0 (Thurstonian IRT Model Upgrade)
> **Date**: 2025-09-30
> **Author**: TaskMaster Design Agent
> **Status**: Ready for Implementation (Pending Calibration)

## Executive Summary

This document outlines the scientific foundation for the strength assessment system, refactored to incorporate a state-of-the-art **Thurstonian Item Response Theory (TIRT) model**. We are moving from a simple tallying method to a robust psychometric framework that addresses the limitations of ipsative data. The assessment will now use **multi-statement blocks (e.g., quartets)** instead of pairs, allowing for a more balanced design and richer data collection. The final output remains a **Talent Tier Profile**, but it is now backed by normative scores that are comparable across individuals, providing a scientifically defensible and highly reliable talent map.

## 1. Assessment Instrument: Multi-Statement Forced-Choice Model

### 1.1 Rationale for the Upgraded Design

While the v3.0 forced-choice model was a step in the right direction, scholarly research highlights two critical limitations of a simple tallying approach:
1.  **Ipsative Data Limitation**: Simple tallying produces scores that are only meaningful for intra-personal comparison (ranking one's own traits) but are not comparable across individuals.
2.  **Design Imbalance**: A 30-item, 12-facet pairwise design is mathematically impossible to balance perfectly (as per Block Design theory, λ(v-1)=r(k-1) does not yield an integer).

To overcome these, we are adopting an industry-standard and academically validated approach.

### 1.2 Upgraded Instrument Structure

The assessment instrument is evolved from pairs to blocks of statements.

- **Format**: **Forced-Choice Blocks (Quartets)**. Each question presents 4 statements. The user chooses the statement that is **"Most Like Me"** and **"Least Like Me"**.
- **Total Blocks**: To be determined, but a common design is 28-30 blocks.
- **Talent Facets Measured**: 12
- **Scoring Logic**: **Thurstonian Item Response Theory (TIRT)**

This "pick most/least from 4" format provides significantly more psychometric information per item than a simple pairwise choice.

## 2. Detailed Scoring Methodology

### 2.1 Core Scoring Algorithm: Thurstonian IRT (TIRT)

We are replacing the "Preference Tallying" algorithm with a Thurstonian IRT model. This is the cornerstone of the v4.0 redesign.

**Core Concept:**
Instead of just counting preferences, the TIRT model assumes that each statement has a certain "utility" or attractiveness for an individual based on their underlying latent traits. By analyzing the patterns of which statements are chosen as "most" and "least" liked across numerous blocks, the model can statistically estimate the strength of the 12 underlying latent talent traits (θ scores).

**Key Advantages:**
- **Solves the Ipsative Problem**: The model's primary output is a set of **normative trait scores**, which exist on an interval scale and are comparable across different individuals.
- **Scientifically Valid**: This approach is extensively documented and validated in psychometric literature (e.g., Brown & Maydeu-Olivares, 2011).

**Scoring Process Overview:**
1.  **Response Collection**: For each block, the user's "most" and "least" choices are recorded.
2.  **Apply Pre-calibrated IRT Model**: The scoring engine applies a pre-calibrated TIRT model to the full set of responses. This involves complex statistical estimation, likely using a library capable of IRT analysis (e.g., `mirt` in R, or Python equivalents).
3.  **Estimate Latent Traits (θ)**: The model outputs a vector of 12 latent trait scores (thetas) for the user. These scores represent the user's standing on each talent facet relative to the calibration sample.
4.  **Convert to Normative Scores**: The theta scores are then converted into more interpretable normative scores, such as T-scores (Mean=50, SD=10) or Percentiles (0-100).

### 2.2 Block Design: Approximating Balance

The design of the statement blocks is critical for the model's accuracy. We will move away from the simple pairwise matrix to an **approximately balanced incomplete block design (BIBD)**.

- **Block Size (k)**: **4** statements per block.
- **Goal**:
    1.  Each of the 12 talent facets should appear a roughly equal number of times across all blocks.
    2.  Each possible *pair* of talents should be compared a roughly equal number of times.
    3.  Within each block, the four statements should be matched for social desirability to avoid obvious "good" or "bad" choices.

This requires a dedicated psychometric design phase, but it is essential for the validity of the final scores.

## 3. Pre-computation Step: Item Calibration

A TIRT model cannot be applied without first having parameters that describe the psychometric properties of each statement. This requires a one-time, offline **Item Calibration** study.

**Process:**
1.  **Develop Item Pool**: Create a large pool of statements for each of the 12 talent facets.
2.  **Pre-test**: Administer the full set of items to a sufficiently large and representative sample of the target population (n ≈ 300-800).
3.  **Parameter Estimation**: Use the pre-test data to run an IRT analysis and estimate the parameters (e.g., utility, discrimination) for each statement.
4.  **Finalize Instrument**: Select the best-performing statements and arrange them into the final set of approximately balanced blocks for the live assessment.

The output of this phase is a set of item parameters that the live scoring engine will use.

## 4. Talent Tier Interpretation Framework (Refined)

The tiered framework remains central, but its application is now more nuanced and statistically sound.

### 4.1 Tier Classification Logic

1.  **Input**: A vector of 12 normative scores (e.g., percentiles) for the talent facets.
2.  **Process**: The scores are already on a comparable scale. We can now define tiers based on percentile thresholds, which are more meaningful than fixed ranks.
3.  **Output**:
    *   **Dominant**: Talents falling above a certain threshold (e.g., > 75th percentile).
    *   **Supporting**: Talents in the middle range (e.g., 25th to 75th percentile).
    *   **Lesser**: Talents falling below a certain threshold (e.g., < 25th percentile).

**Handling Ties**: Since scores are now continuous latent trait estimates, true ties are rare. Any apparent ties in rounded percentiles can be resolved by referring back to the more precise underlying theta scores.

## 5. Implementation Recommendations

The implementation pipeline must be updated to reflect this new, sophisticated model.

1.  **Offline Phase (Pre-requisite)**:
    *   Design and execute the Item Calibration study.
    *   Generate and validate the final IRT item parameter file.
2.  **Online Scoring Pipeline**:
    *   **Input Validation**: Verify complete responses for all blocks.
    *   **Quality Assessment**: Assess response time and patterns. Consider adding person-fit statistics from the IRT model to flag aberrant response patterns.
    *   **Score Estimation**: Load the pre-calibrated IRT parameters and apply the model to the user's responses to estimate the 12 latent trait scores (thetas).
    *   **Score Transformation**: Convert thetas to percentiles.
    *   **Talent Tiering**: Classify the percentiles into Dominant, Supporting, and Lesser tiers based on thresholds.
    *   **Storage**: Save the complete tiered profile, including the normative scores and confidence intervals, to the database.

---
This updated research document provides the foundation for a psychometrically robust, professional-grade talent assessment. It replaces a simple heuristic with a validated scientific model, ensuring the results are reliable, comparable, and truly insightful.