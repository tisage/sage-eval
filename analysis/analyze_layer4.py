"""
Systematic Analysis of Layer 4 (Cultural Representation) Results
==================================================================

This script performs comprehensive analysis of Layer 4 evaluation data.

Data source: SAGE_FINAL_DATASET JSON (post-repair authoritative data).
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

from load_sage_data import load_layer_data

# Load data from authoritative JSON source
df = load_layer_data(layer=4)

print("=" * 100)
print("LAYER 4 (CULTURAL REPRESENTATION) - SYSTEMATIC ANALYSIS")
print("=" * 100)

# ========================================
# 1. BASIC STATISTICS
# ========================================
print("\n" + "=" * 100)
print("1. BASIC DATASET STATISTICS")
print("=" * 100)

print(f"\nTotal evaluations: {len(df)}")
print(f"Total unique stories: {df['story_id'].nunique()}")
print(f"Modes: {df['mode'].unique()}")

category_counts = df[df['mode'] == 'content-limit']['category'].value_counts()
print(f"\nStory categories:")
for cat, count in category_counts.items():
    print(f"  {cat}: {count}")

# ========================================
# 2. OVERALL SCORE ANALYSIS
# ========================================
print("\n" + "=" * 100)
print("2. OVERALL SCORE ANALYSIS")
print("=" * 100)

for mode in ['content-limit', 'title-limit']:
    mode_df = df[df['mode'] == mode]
    print(f"\n{mode.upper()}:")
    print(f"  Iterative Overall Score: {mode_df['iterative_overall_score'].mean():.3f} ± {mode_df['iterative_overall_score'].std():.3f}")
    print(f"  Validator Overall Score: {mode_df['validator_overall_score'].mean():.3f} ± {mode_df['validator_overall_score'].std():.3f}")
    print(f"  Mean absolute difference: {mode_df['overall_score_diff'].mean():.3f}")

    # By category
    print(f"\n  By Category:")
    for cat in ['canonical', 'pulp', 'llm_generated']:
        cat_df = mode_df[mode_df['category'] == cat]
        if len(cat_df) > 0:
            print(f"    {cat}: {cat_df['iterative_overall_score'].mean():.3f} ± {cat_df['iterative_overall_score'].std():.3f}")

# ========================================
# 3. DIMENSION-LEVEL ANALYSIS
# ========================================
print("\n" + "=" * 100)
print("3. DIMENSION-LEVEL SCORE ANALYSIS")
print("=" * 100)

dimensions = ['IPD', 'CVP', 'CSP', 'CPC']
dim_names = {
    'IPD': 'Intersectional Power Dynamics',
    'CVP': 'Cultural Voice & Perspective',
    'CSP': 'Cultural Specificity',
    'CPC': 'Cultural Pattern Complexity'
}

for dim in dimensions:
    print(f"\n{dim} - {dim_names[dim]}")
    print("-" * 80)

    for mode in ['content-limit', 'title-limit']:
        mode_df = df[df['mode'] == mode]
        iter_col = f'iterative_{dim}_score'
        val_col = f'validator_{dim}_score'
        diff_col = f'{dim}_score_diff'

        print(f"\n  {mode.upper()}:")
        print(f"    Iterative: {mode_df[iter_col].mean():.3f} ± {mode_df[iter_col].std():.3f}")
        print(f"    Validator: {mode_df[val_col].mean():.3f} ± {mode_df[val_col].std():.3f}")
        print(f"    MAD: {mode_df[diff_col].mean():.3f}")

        # By category
        for cat in ['canonical', 'pulp', 'llm_generated']:
            cat_df = mode_df[mode_df['category'] == cat]
            if len(cat_df) > 0:
                print(f"      {cat:15s}: {cat_df[iter_col].mean():.3f} ± {cat_df[iter_col].std():.3f}")

# ========================================
# 4. INTER-RATER RELIABILITY
# ========================================
print("\n" + "=" * 100)
print("4. INTER-RATER RELIABILITY (Iterative vs Validator)")
print("=" * 100)

for mode in ['content-limit', 'title-limit']:
    mode_df = df[df['mode'] == mode]
    print(f"\n{mode.upper()}:")

    # Overall score agreement
    overall_mad = mode_df['overall_score_diff'].mean()
    agreement_rate = (mode_df['overall_score_diff'] < 0.5).sum() / len(mode_df) * 100
    print(f"  Overall Score:")
    print(f"    Mean Absolute Difference: {overall_mad:.3f}")
    print(f"    Agreement Rate (MAD < 0.5): {agreement_rate:.1f}%")

    # Dimension-level agreement
    print(f"\n  Dimension-level MAD:")
    for dim in dimensions:
        diff_col = f'{dim}_score_diff'
        mad = mode_df[diff_col].mean()
        agreement = (mode_df[diff_col] < 0.5).sum() / len(mode_df) * 100
        print(f"    {dim}: MAD={mad:.3f}, Agreement={agreement:.1f}%")

# ========================================
# 5. CONVERGENCE ANALYSIS
# ========================================
print("\n" + "=" * 100)
print("5. CONVERGENCE ANALYSIS (Round 4 → Round 5)")
print("=" * 100)

for mode in ['content-limit', 'title-limit']:
    mode_df = df[df['mode'] == mode]
    print(f"\n{mode.upper()}:")

    print(f"  Dimension Convergence Rates:")
    for dim in dimensions:
        conv_col = f'{dim}_convergence_r4_r5'
        converged = (mode_df[conv_col] == 0.0).sum()
        rate = converged / len(mode_df) * 100
        print(f"    {dim}: {rate:.1f}% ({converged}/{len(mode_df)})")

    print(f"\n  Stories with N stable dimensions:")
    for n in range(5):
        count = (mode_df['num_stable_dimensions'] == n).sum()
        pct = count / len(mode_df) * 100
        print(f"    {n} dimensions: {count} ({pct:.1f}%)")

# ========================================
# 6. CONFIDENCE ANALYSIS
# ========================================
print("\n" + "=" * 100)
print("6. CONFIDENCE RATINGS ANALYSIS")
print("=" * 100)

for mode in ['content-limit', 'title-limit']:
    mode_df = df[df['mode'] == mode]
    print(f"\n{mode.upper()}:")

    # Overall confidence
    print(f"  Iterative Overall Confidence: {mode_df['iterative_overall_confidence'].mean():.2f} ± {mode_df['iterative_overall_confidence'].std():.2f}")
    print(f"  Convergence Overall Confidence: {mode_df['convergence_overall_confidence'].mean():.2f} ± {mode_df['convergence_overall_confidence'].std():.2f}")

    # Dimension-level confidence
    print(f"\n  Dimension Confidence (Iterative):")
    for dim in dimensions:
        conf_col = f'iterative_{dim}_confidence'
        print(f"    {dim}: {mode_df[conf_col].mean():.2f} ± {mode_df[conf_col].std():.2f}")

# ========================================
# 7. CATEGORY COMPARISON
# ========================================
print("\n" + "=" * 100)
print("7. CATEGORY COMPARISON (T-Tests)")
print("=" * 100)

for mode in ['content-limit', 'title-limit']:
    mode_df = df[df['mode'] == mode]
    print(f"\n{mode.upper()}:")

    # Overall score comparisons
    canonical_df = mode_df[mode_df['category'] == 'canonical']
    pulp_df = mode_df[mode_df['category'] == 'pulp']
    llm_df = mode_df[mode_df['category'] == 'llm_generated']

    # First show category means
    print(f"\n  Category Means (Overall Score):")
    print(f"    Canonical:     {canonical_df['iterative_overall_score'].mean():.3f} ± {canonical_df['iterative_overall_score'].std():.3f} (n={len(canonical_df)})")
    print(f"    Pulp:          {pulp_df['iterative_overall_score'].mean():.3f} ± {pulp_df['iterative_overall_score'].std():.3f} (n={len(pulp_df)})")
    print(f"    LLM-Generated: {llm_df['iterative_overall_score'].mean():.3f} ± {llm_df['iterative_overall_score'].std():.3f} (n={len(llm_df)})")

    print(f"\n  Pairwise Comparisons (Overall Score):")

    # Canonical vs Pulp
    t_stat, p_val = stats.ttest_ind(
        canonical_df['iterative_overall_score'],
        pulp_df['iterative_overall_score']
    )
    cohens_d = (canonical_df['iterative_overall_score'].mean() - pulp_df['iterative_overall_score'].mean()) / \
               np.sqrt((canonical_df['iterative_overall_score'].std()**2 + pulp_df['iterative_overall_score'].std()**2) / 2)
    print(f"    Canonical vs Pulp:          t={t_stat:6.3f}, p={p_val:.4f}, d={cohens_d:6.3f}")

    # Canonical vs LLM
    t_stat, p_val = stats.ttest_ind(
        canonical_df['iterative_overall_score'],
        llm_df['iterative_overall_score']
    )
    cohens_d = (canonical_df['iterative_overall_score'].mean() - llm_df['iterative_overall_score'].mean()) / \
               np.sqrt((canonical_df['iterative_overall_score'].std()**2 + llm_df['iterative_overall_score'].std()**2) / 2)
    print(f"    Canonical vs LLM-Generated: t={t_stat:6.3f}, p={p_val:.4f}, d={cohens_d:6.3f}")

    # Pulp vs LLM
    t_stat, p_val = stats.ttest_ind(
        pulp_df['iterative_overall_score'],
        llm_df['iterative_overall_score']
    )
    cohens_d = (pulp_df['iterative_overall_score'].mean() - llm_df['iterative_overall_score'].mean()) / \
               np.sqrt((pulp_df['iterative_overall_score'].std()**2 + llm_df['iterative_overall_score'].std()**2) / 2)
    print(f"    Pulp vs LLM-Generated:      t={t_stat:6.3f}, p={p_val:.4f}, d={cohens_d:6.3f}")

    # Dimension-level category comparisons
    print(f"\n  Category Comparisons by Dimension:")
    for dim in dimensions:
        print(f"\n    {dim} - {dim_names[dim]}:")
        iter_col = f'iterative_{dim}_score'

        # Category means
        print(f"      Category Means:")
        print(f"        Canonical:     {canonical_df[iter_col].mean():.3f} ± {canonical_df[iter_col].std():.3f}")
        print(f"        Pulp:          {pulp_df[iter_col].mean():.3f} ± {pulp_df[iter_col].std():.3f}")
        print(f"        LLM-Generated: {llm_df[iter_col].mean():.3f} ± {llm_df[iter_col].std():.3f}")

        # Pairwise comparisons
        print(f"      Pairwise Comparisons:")

        # Canonical vs Pulp
        t_stat, p_val = stats.ttest_ind(canonical_df[iter_col], pulp_df[iter_col])
        cohens_d = (canonical_df[iter_col].mean() - pulp_df[iter_col].mean()) / \
                   np.sqrt((canonical_df[iter_col].std()**2 + pulp_df[iter_col].std()**2) / 2)
        print(f"        Canonical vs Pulp:          t={t_stat:6.3f}, p={p_val:.4f}, d={cohens_d:6.3f}")

        # Canonical vs LLM
        t_stat, p_val = stats.ttest_ind(canonical_df[iter_col], llm_df[iter_col])
        cohens_d = (canonical_df[iter_col].mean() - llm_df[iter_col].mean()) / \
                   np.sqrt((canonical_df[iter_col].std()**2 + llm_df[iter_col].std()**2) / 2)
        print(f"        Canonical vs LLM-Generated: t={t_stat:6.3f}, p={p_val:.4f}, d={cohens_d:6.3f}")

        # Pulp vs LLM
        t_stat, p_val = stats.ttest_ind(pulp_df[iter_col], llm_df[iter_col])
        cohens_d = (pulp_df[iter_col].mean() - llm_df[iter_col].mean()) / \
                   np.sqrt((pulp_df[iter_col].std()**2 + llm_df[iter_col].std()**2) / 2)
        print(f"        Pulp vs LLM-Generated:      t={t_stat:6.3f}, p={p_val:.4f}, d={cohens_d:6.3f}")

# ========================================
# 8. DIMENSION CORRELATIONS
# ========================================
print("\n" + "=" * 100)
print("8. DIMENSION INTER-CORRELATIONS")
print("=" * 100)

for mode in ['content-limit', 'title-limit']:
    mode_df = df[df['mode'] == mode]
    print(f"\n{mode.upper()}:")

    # Create correlation matrix
    dim_scores = mode_df[[f'iterative_{dim}_score' for dim in dimensions]]
    dim_scores.columns = dimensions
    corr_matrix = dim_scores.corr()

    print("\n  Correlation Matrix:")
    print("       ", "  ".join([f"{d:>6s}" for d in dimensions]))
    for i, dim1 in enumerate(dimensions):
        row = [f"{corr_matrix.loc[dim1, dim2]:6.3f}" for dim2 in dimensions]
        print(f"  {dim1}  " + "  ".join(row))

# ========================================
# 9. MODE COMPARISON (Content-Limit vs Title-Limit)
# ========================================
print("\n" + "=" * 100)
print("9. MODE COMPARISON (Content-Limit vs Title-Limit)")
print("=" * 100)

# Merge content and title data
content_df = df[df['mode'] == 'content-limit'].copy()
title_df = df[df['mode'] == 'title-limit'].copy()

merged = content_df.merge(
    title_df,
    on='story_id',
    suffixes=('_content', '_title')
)

print(f"\nOverall Score Mode Differences:")
print(f"  Paired t-test:")
t_stat, p_val = stats.ttest_rel(
    merged['iterative_overall_score_content'],
    merged['iterative_overall_score_title']
)
mean_diff = (merged['iterative_overall_score_content'] - merged['iterative_overall_score_title']).mean()
print(f"    t={t_stat:.3f}, p={p_val:.4f}")
print(f"    Mean difference (content - title): {mean_diff:.3f}")

print(f"\nDimension-level Mode Differences:")
for dim in dimensions:
    t_stat, p_val = stats.ttest_rel(
        merged[f'iterative_{dim}_score_content'],
        merged[f'iterative_{dim}_score_title']
    )
    mean_diff = (merged[f'iterative_{dim}_score_content'] - merged[f'iterative_{dim}_score_title']).mean()
    print(f"  {dim}: t={t_stat:.3f}, p={p_val:.4f}, mean_diff={mean_diff:.3f}")

# By category analysis
print(f"\nMode Differences by Category:")
for cat in ['canonical', 'pulp', 'llm_generated']:
    cat_merged = merged[merged['category_content'] == cat]
    if len(cat_merged) > 0:
        print(f"\n  {cat.upper().replace('_', ' ')}:")

        # Overall score
        t_stat, p_val = stats.ttest_rel(
            cat_merged['iterative_overall_score_content'],
            cat_merged['iterative_overall_score_title']
        )
        mean_content = cat_merged['iterative_overall_score_content'].mean()
        mean_title = cat_merged['iterative_overall_score_title'].mean()
        mean_diff = mean_content - mean_title
        abs_diff = (cat_merged['iterative_overall_score_content'] - cat_merged['iterative_overall_score_title']).abs().mean()

        print(f"    Overall: content={mean_content:.3f}, title={mean_title:.3f}, diff={mean_diff:.3f}, |diff|={abs_diff:.3f}, t={t_stat:.3f}, p={p_val:.4f}")

        # Dimension-level
        for dim in dimensions:
            mean_content_dim = cat_merged[f'iterative_{dim}_score_content'].mean()
            mean_title_dim = cat_merged[f'iterative_{dim}_score_title'].mean()
            mean_diff_dim = mean_content_dim - mean_title_dim
            print(f"      {dim}: content={mean_content_dim:.3f}, title={mean_title_dim:.3f}, diff={mean_diff_dim:.3f}")

# ========================================
# 10. VALIDATOR TRUST LEVELS
# ========================================
print("\n" + "=" * 100)
print("10. VALIDATOR TRUST LEVEL DISTRIBUTION")
print("=" * 100)

for mode in ['content-limit', 'title-limit']:
    mode_df = df[df['mode'] == mode]
    print(f"\n{mode.upper()}:")

    trust_counts = mode_df['validator_trust_level'].value_counts()
    for level in ['high', 'medium-high', 'medium', 'medium-low', 'low']:
        count = trust_counts.get(level, 0)
        pct = count / len(mode_df) * 100
        print(f"  {level:12s}: {count:3d} ({pct:5.1f}%)")

print("\n" + "=" * 100)
print("ANALYSIS COMPLETE")
print("=" * 100)
