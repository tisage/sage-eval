#!/usr/bin/env python3
"""
Cross-Layer Correlation Analysis: Layer 4 (Cultural) vs Layer 5 (Emotional)

This script analyzes correlations between Layer 4 and Layer 5 dimension scores
to verify layer independence (target: r < 0.7).
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from scipy import stats
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def load_layer4_data(layer4_dir: Path) -> Dict[str, Dict[str, float]]:
    """
    Load Layer 4 data from multi_round_test JSON files.

    Returns:
        Dict mapping story_id to dimension scores:
        {
            "chekhov_lady_with_dog_pure_text": {
                "IPD": 4.0,
                "CVP": 3.5,
                "CSP": 4.5,
                "CPC": 4.0
            },
            ...
        }
    """
    layer4_data = {}

    # Find all multi_round_test JSON files
    json_files = sorted(layer4_dir.glob("multi_round_test_*.json"))

    # Mapping from full names to abbreviations
    dim_mapping = {
        "intersectional_power_dynamics": "IPD",
        "cultural_voice_perspective": "CVP",
        "cultural_specificity": "CSP",
        "cultural_pattern_complexity": "CPC"
    }

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Layer 4 data is an array format
            if not isinstance(data, list) or len(data) == 0:
                continue

            # Get first item (should only be one per file)
            item = data[0]

            # Extract story info
            story_id_raw = item.get("story_id", "")
            mode = item.get("mode", "")

            if not story_id_raw or not mode:
                continue

            # Create unique ID
            story_id = f"{story_id_raw}_{mode}"

            # Extract dimension scores from primary_result
            primary_result = item.get("primary_result", {})
            dimensions = primary_result.get("dimensions", {})

            layer4_data[story_id] = {}
            for full_name, abbrev in dim_mapping.items():
                if full_name in dimensions:
                    layer4_data[story_id][abbrev] = dimensions[full_name].get("score", 0.0)

            # Only keep if we have all 4 dimensions
            if len(layer4_data[story_id]) != 4:
                del layer4_data[story_id]

        except Exception as e:
            print(f"Error loading {json_file}: {e}", file=sys.stderr)
            continue

    return layer4_data


def load_layer5_data(layer5_dir: Path) -> Dict[str, Dict[str, float]]:
    """
    Load Layer 5 data from layer5_*_*.json files.

    Returns:
        Dict mapping story_id to dimension scores:
        {
            "chekhov_lady_with_dog_pure_text": {
                "AC": 4.5,
                "PI": 4.0,
                "EG": 3.5,
                "ENC": 4.5
            },
            ...
        }
    """
    layer5_data = {}

    # Find all layer5 JSON files
    json_files = sorted(layer5_dir.glob("layer5_*.json"))

    # Mapping from full names to abbreviations
    dim_mapping = {
        "affective_complexity": "AC",
        "psychological_interiority": "PI",
        "emotional_granularity": "EG",
        "emotional_narrative_coherence": "ENC"
    }

    for json_file in json_files:
        # Skip the batch summary file
        if "batch_summary" in json_file.name:
            continue

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract story info
            story_id_raw = data.get("story_id", "")
            mode = data.get("mode", "")

            if not story_id_raw or not mode:
                continue

            # Create unique ID
            story_id = f"{story_id_raw}_{mode}"

            # Extract dimension scores from primary_result
            primary_result = data.get("primary_result", {})
            dimensions = primary_result.get("dimensions", {})

            layer5_data[story_id] = {}
            for full_name, abbrev in dim_mapping.items():
                if full_name in dimensions:
                    layer5_data[story_id][abbrev] = dimensions[full_name].get("score", 0.0)

            # Only keep if we have all 4 dimensions
            if len(layer5_data[story_id]) != 4:
                del layer5_data[story_id]

        except Exception as e:
            print(f"Error loading {json_file}: {e}", file=sys.stderr)
            continue

    return layer5_data


def calculate_correlations(
    layer4_data: Dict[str, Dict[str, float]],
    layer5_data: Dict[str, Dict[str, float]]
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, float]]]:
    """
    Calculate Pearson and Spearman correlations between all dimension pairs.

    Returns:
        (pearson_matrix, spearman_matrix) where each matrix is:
        {
            "IPD": {"AC": 0.45, "PI": 0.32, "EG": 0.28, "ENC": 0.35},
            "CVP": {...},
            ...
        }
    """
    # Find common stories
    common_stories = set(layer4_data.keys()) & set(layer5_data.keys())

    if not common_stories:
        raise ValueError("No common stories found between Layer 4 and Layer 5 data")

    print(f"Found {len(common_stories)} common stories")

    # Build dimension vectors
    layer4_dims = ["IPD", "CVP", "CSP", "CPC"]
    layer5_dims = ["AC", "PI", "EG", "ENC"]

    pearson_matrix = defaultdict(dict)
    spearman_matrix = defaultdict(dict)
    p_value_matrix = defaultdict(dict)

    for l4_dim in layer4_dims:
        for l5_dim in layer5_dims:
            # Extract paired values
            l4_values = []
            l5_values = []

            for story_id in sorted(common_stories):
                l4_values.append(layer4_data[story_id][l4_dim])
                l5_values.append(layer5_data[story_id][l5_dim])

            # Calculate Pearson correlation
            pearson_r, pearson_p = stats.pearsonr(l4_values, l5_values)
            pearson_matrix[l4_dim][l5_dim] = pearson_r
            p_value_matrix[l4_dim][l5_dim] = pearson_p

            # Calculate Spearman correlation
            spearman_r, _ = stats.spearmanr(l4_values, l5_values)
            spearman_matrix[l4_dim][l5_dim] = spearman_r

    return dict(pearson_matrix), dict(spearman_matrix), dict(p_value_matrix)


def analyze_overall_layer_correlation(
    layer4_data: Dict[str, Dict[str, float]],
    layer5_data: Dict[str, Dict[str, float]]
) -> Tuple[float, float]:
    """
    Calculate overall layer correlation by averaging dimension scores.

    Returns:
        (pearson_r, spearman_r)
    """
    common_stories = set(layer4_data.keys()) & set(layer5_data.keys())

    layer4_overall = []
    layer5_overall = []

    for story_id in sorted(common_stories):
        # Average all dimension scores
        l4_avg = np.mean(list(layer4_data[story_id].values()))
        l5_avg = np.mean(list(layer5_data[story_id].values()))

        layer4_overall.append(l4_avg)
        layer5_overall.append(l5_avg)

    pearson_r, _ = stats.pearsonr(layer4_overall, layer5_overall)
    spearman_r, _ = stats.spearmanr(layer4_overall, layer5_overall)

    return pearson_r, spearman_r


def generate_report(
    layer4_data: Dict[str, Dict[str, float]],
    layer5_data: Dict[str, Dict[str, float]],
    pearson_matrix: Dict[str, Dict[str, float]],
    spearman_matrix: Dict[str, Dict[str, float]],
    p_value_matrix: Dict[str, Dict[str, float]],
    output_file: Path
):
    """Generate comprehensive correlation analysis report."""

    common_stories = sorted(set(layer4_data.keys()) & set(layer5_data.keys()))

    # Calculate overall correlation
    overall_pearson, overall_spearman = analyze_overall_layer_correlation(
        layer4_data, layer5_data
    )

    report = []
    report.append("# Cross-Layer Correlation Analysis: Layer 4 vs Layer 5")
    report.append("")
    report.append(f"**Generated**: {Path(__file__).name}")
    report.append(f"**Stories Analyzed**: {len(common_stories)}")
    report.append("")

    # Overall layer correlation
    report.append("## 1. Overall Layer Correlation")
    report.append("")
    report.append("Correlation between Layer 4 overall scores (average of 4 dimensions) "
                  "and Layer 5 overall scores (average of 4 dimensions):")
    report.append("")
    report.append(f"- **Pearson r**: {overall_pearson:.3f}")
    report.append(f"- **Spearman ρ**: {overall_spearman:.3f}")
    report.append("")

    # Interpretation
    if abs(overall_pearson) < 0.3:
        interpretation = "✅ **Weak correlation** - Layers are largely independent"
    elif abs(overall_pearson) < 0.7:
        interpretation = "⚠️ **Moderate correlation** - Some layer overlap"
    else:
        interpretation = "❌ **Strong correlation** - Layers may not be independent"

    report.append(f"**Interpretation**: {interpretation}")
    report.append("")

    # Dimension-level correlation matrix
    report.append("## 2. Dimension-Level Correlation Matrix")
    report.append("")
    report.append("### Pearson Correlation Coefficients")
    report.append("")

    # Table header
    layer5_dims = ["AC", "PI", "EG", "ENC"]
    header = "| Layer 4 \\ Layer 5 | " + " | ".join(layer5_dims) + " |"
    separator = "|" + "|".join(["-" * 20] + ["-" * 6] * len(layer5_dims)) + "|"
    report.append(header)
    report.append(separator)

    # Table rows
    for l4_dim in ["IPD", "CVP", "CSP", "CPC"]:
        row = f"| **{l4_dim}** |"
        for l5_dim in layer5_dims:
            r = pearson_matrix[l4_dim][l5_dim]
            p = p_value_matrix[l4_dim][l5_dim]

            # Format with significance markers
            if p < 0.001:
                sig = "***"
            elif p < 0.01:
                sig = "**"
            elif p < 0.05:
                sig = "*"
            else:
                sig = ""

            row += f" {r:+.3f}{sig} |"
        report.append(row)

    report.append("")
    report.append("*Note: \\*\\*\\* p<0.001, \\*\\* p<0.01, \\* p<0.05*")
    report.append("")

    # Spearman correlation
    report.append("### Spearman Correlation Coefficients")
    report.append("")
    report.append(header)
    report.append(separator)

    for l4_dim in ["IPD", "CVP", "CSP", "CPC"]:
        row = f"| **{l4_dim}** |"
        for l5_dim in layer5_dims:
            rho = spearman_matrix[l4_dim][l5_dim]
            row += f" {rho:+.3f} |"
        report.append(row)

    report.append("")

    # Find strongest correlations
    report.append("## 3. Strongest Dimension Pairs")
    report.append("")

    # Flatten correlations
    all_correlations = []
    for l4_dim in ["IPD", "CVP", "CSP", "CPC"]:
        for l5_dim in layer5_dims:
            all_correlations.append((
                abs(pearson_matrix[l4_dim][l5_dim]),
                l4_dim,
                l5_dim,
                pearson_matrix[l4_dim][l5_dim],
                p_value_matrix[l4_dim][l5_dim]
            ))

    # Sort by absolute correlation
    all_correlations.sort(reverse=True)

    report.append("Top 5 strongest correlations (by absolute value):")
    report.append("")

    for i, (abs_r, l4_dim, l5_dim, r, p) in enumerate(all_correlations[:5], 1):
        sig_level = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        report.append(f"{i}. **{l4_dim} × {l5_dim}**: r = {r:+.3f} (p = {p:.4f} {sig_level})")

    report.append("")

    # Analysis by category
    report.append("## 4. Analysis by Literary Category")
    report.append("")

    # Separate canonical and pulp stories
    canonical_stories = [s for s in common_stories if any(
        author in s for author in [
            "chekhov", "gogol", "maupassant", "hawthorne", "poe",
            "joyce", "kafka", "oconnor", "akutagawa", "borges"
        ]
    )]

    pulp_stories = [s for s in common_stories if s not in canonical_stories]

    report.append(f"- Canonical stories: {len(canonical_stories)}")
    report.append(f"- Pulp stories: {len(pulp_stories)}")
    report.append("")

    # Calculate within-category correlations
    if len(canonical_stories) >= 3 and len(pulp_stories) >= 3:
        canonical_l4_data = {k: v for k, v in layer4_data.items() if k in canonical_stories}
        canonical_l5_data = {k: v for k, v in layer5_data.items() if k in canonical_stories}

        pulp_l4_data = {k: v for k, v in layer4_data.items() if k in pulp_stories}
        pulp_l5_data = {k: v for k, v in layer5_data.items() if k in pulp_stories}

        canonical_r, _ = analyze_overall_layer_correlation(canonical_l4_data, canonical_l5_data)
        pulp_r, _ = analyze_overall_layer_correlation(pulp_l4_data, pulp_l5_data)

        report.append(f"**Within-canonical correlation**: r = {canonical_r:.3f}")
        report.append(f"**Within-pulp correlation**: r = {pulp_r:.3f}")
        report.append("")

    # Interpretation summary
    report.append("## 5. Summary and Interpretation")
    report.append("")

    # Count high correlations
    high_corr_count = sum(1 for _, _, _, r, _ in all_correlations if abs(r) >= 0.7)
    moderate_corr_count = sum(1 for _, _, _, r, _ in all_correlations if 0.3 <= abs(r) < 0.7)
    low_corr_count = sum(1 for _, _, _, r, _ in all_correlations if abs(r) < 0.3)

    report.append(f"**Distribution of dimension-pair correlations**:")
    report.append(f"- High (|r| ≥ 0.7): {high_corr_count}/16 ({high_corr_count/16*100:.1f}%)")
    report.append(f"- Moderate (0.3 ≤ |r| < 0.7): {moderate_corr_count}/16 ({moderate_corr_count/16*100:.1f}%)")
    report.append(f"- Low (|r| < 0.3): {low_corr_count}/16 ({low_corr_count/16*100:.1f}%)")
    report.append("")

    # Final verdict
    if high_corr_count == 0 and abs(overall_pearson) < 0.5:
        verdict = ("✅ **Layer independence verified**: No dimension pairs show strong correlation "
                   "(r ≥ 0.7), and overall layer correlation is moderate/weak. Layer 4 (Cultural) "
                   "and Layer 5 (Emotional) measure distinct aspects of literary quality.")
    elif high_corr_count <= 2:
        verdict = (f"⚠️ **Mostly independent with minor overlap**: Only {high_corr_count} dimension "
                   f"pair(s) show strong correlation. Layers are largely independent but some "
                   f"theoretical overlap exists.")
    else:
        verdict = (f"❌ **Significant layer overlap**: {high_corr_count} dimension pairs show strong "
                   f"correlation (r ≥ 0.7). Layer boundaries may need refinement.")

    report.append(f"**Overall Verdict**: {verdict}")
    report.append("")

    # Write report
    output_file.write_text("\n".join(report), encoding='utf-8')
    print(f"\nReport written to: {output_file}")


def main():
    """Main execution function."""

    # Paths
    project_root = Path(__file__).parent.parent
    layer4_dir = project_root / "results" / "new_layer4_20251221_140852"
    layer5_dir = project_root / "results" / "layer5_emotional_parallel_20251222_104119"
    output_file = project_root / "results" / "CROSS_LAYER_CORRELATION_ANALYSIS.md"

    # Verify directories exist
    if not layer4_dir.exists():
        print(f"Error: Layer 4 directory not found: {layer4_dir}", file=sys.stderr)
        sys.exit(1)

    if not layer5_dir.exists():
        print(f"Error: Layer 5 directory not found: {layer5_dir}", file=sys.stderr)
        sys.exit(1)

    print("Loading Layer 4 data...")
    layer4_data = load_layer4_data(layer4_dir)
    print(f"Loaded {len(layer4_data)} Layer 4 evaluations")

    print("\nLoading Layer 5 data...")
    layer5_data = load_layer5_data(layer5_dir)
    print(f"Loaded {len(layer5_data)} Layer 5 evaluations")

    print("\nCalculating correlations...")
    pearson_matrix, spearman_matrix, p_value_matrix = calculate_correlations(
        layer4_data, layer5_data
    )

    print("\nGenerating report...")
    generate_report(
        layer4_data,
        layer5_data,
        pearson_matrix,
        spearman_matrix,
        p_value_matrix,
        output_file
    )

    print("\n✅ Cross-layer correlation analysis complete!")


if __name__ == "__main__":
    main()
