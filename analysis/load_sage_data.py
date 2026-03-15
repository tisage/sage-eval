"""
SAGE Final Dataset Loader
=========================

Loads evaluation data from SAGE_FINAL_DATASET JSON files into a pandas DataFrame.
Replaces the old CSV-based loading used by analyze_layer4.py and analyze_layer5.py.

The SAGE_FINAL_DATASET JSON files are the authoritative post-repair data source.
Old CSV files in phase4_layer{4,5}_full_50v50/ contain pre-repair data with
zero-score failed evaluations and should not be used for analysis.

Usage:
    from load_sage_data import load_layer_data, load_category_map

    df = load_layer_data(layer=4)
"""

import json
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import yaml


BASE_DIR = Path(__file__).parent.parent
DATASET_DIR = BASE_DIR / "results" / "SAGE_FINAL_DATASET"
CATALOG_PATH = BASE_DIR / "config" / "story_catalog.yaml"

LAYER_DIRS = {
    4: "layer4_cultural",
    5: "layer5_emotional",
    6: "layer6_existential",
}

LAYER_DIMENSIONS = {
    4: {
        "intersectional_power_dynamics": "IPD",
        "cultural_voice_perspective": "CVP",
        "cultural_specificity": "CSP",
        "cultural_pattern_complexity": "CPC",
    },
    5: {
        "affective_complexity": "AC",
        "psychological_interiority": "PI",
        "emotional_granularity": "EG",
        "emotional_narrative_coherence": "ENC",
    },
    6: {
        "life_philosophy": "LP",
        "moral_reflection": "MR",
        "human_condition": "HC",
        "meaning_exploration": "ME",
    },
}


def load_category_map(catalog_path: Path = CATALOG_PATH) -> Dict[str, str]:
    """Build story_id -> category mapping from story catalog YAML."""
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = yaml.safe_load(f)

    category_map = {}
    for story in catalog.get("canonical_stories", []):
        category_map[story["id"]] = "canonical"
    for story in catalog.get("pulp_stories", []):
        category_map[story["id"]] = "pulp"
    for story in catalog.get("llm_generated_stories", []):
        category_map[story["id"]] = "llm_generated"

    return category_map


def load_layer_data(
    layer: int,
    dataset_dir: Path = DATASET_DIR,
    catalog_path: Path = CATALOG_PATH,
) -> pd.DataFrame:
    """Load all JSON evaluation results for a given layer into a DataFrame.

    Returns a DataFrame with columns matching the old CSV format:
        story_id, mode, category,
        iterative_overall_score, validator_overall_score, overall_score_diff,
        iterative_{DIM}_score, validator_{DIM}_score, {DIM}_score_diff,
        {DIM}_convergence_r4_r5, num_stable_dimensions,
        iterative_overall_confidence, convergence_overall_confidence,
        iterative_{DIM}_confidence,
        validator_trust_level
    """
    if layer not in LAYER_DIRS:
        raise ValueError(f"Layer must be one of {list(LAYER_DIRS.keys())}, got {layer}")

    layer_dir = dataset_dir / LAYER_DIRS[layer]
    dim_map = LAYER_DIMENSIONS[layer]
    category_map = load_category_map(catalog_path)

    rows = []
    for json_path in sorted(layer_dir.glob("*.json")):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        story_id = data["story_id"]
        mode = data["mode"]
        category = category_map.get(story_id, "unknown")

        primary = data["primary_result"]
        peer = data.get("peer_result", {})

        # Primary (iterative) scores
        iterative_overall_score = primary.get("score", 0.0) or 0.0
        iterative_overall_confidence = primary.get("overall_confidence", 0.0) or 0.0

        # Validator scores
        validator_overall_score = peer.get("validator_overall_score", 0.0) or 0.0

        # Overall score diff
        overall_score_diff = abs(iterative_overall_score - validator_overall_score)

        # Validator trust level
        validator_trust_level = peer.get("trust_level", "unknown")

        row = {
            "story_id": story_id,
            "mode": mode,
            "category": category,
            "iterative_overall_score": iterative_overall_score,
            "validator_overall_score": validator_overall_score,
            "overall_score_diff": overall_score_diff,
            "iterative_overall_confidence": iterative_overall_confidence,
            "validator_trust_level": validator_trust_level,
        }

        # Dimension-level scores
        primary_dims = primary.get("dimensions", {})
        validator_indep = peer.get("independent_scores", {})
        score_trajectory = primary.get("score_trajectory", {})

        num_stable = 0
        for full_name, abbrev in dim_map.items():
            # Iterative dimension score and confidence
            dim_data = primary_dims.get(full_name, {})
            iter_score = dim_data.get("score", 0.0) or 0.0
            iter_conf = dim_data.get("confidence", 0.0) or 0.0
            row[f"iterative_{abbrev}_score"] = iter_score
            row[f"iterative_{abbrev}_confidence"] = iter_conf

            # Validator dimension score
            val_dim = validator_indep.get(full_name, {})
            val_score = val_dim.get("score", 0.0) or 0.0
            row[f"validator_{abbrev}_score"] = val_score

            # Score diff
            row[f"{abbrev}_score_diff"] = abs(iter_score - val_score)

            # Convergence R4->R5 from score trajectory
            trajectory = score_trajectory.get(full_name, [])
            if len(trajectory) >= 5:
                r4_score = trajectory[3]  # Round 4 (0-indexed)
                r5_score = trajectory[4]  # Round 5
                convergence = abs(r5_score - r4_score)
            else:
                convergence = 0.0
            row[f"{abbrev}_convergence_r4_r5"] = convergence

            if convergence < 0.3:
                num_stable += 1

        row["num_stable_dimensions"] = num_stable

        # Convergence overall confidence (from final round)
        conf_trajectory = primary.get("confidence_trajectory", {})
        # Use mean of final round confidences as convergence overall confidence
        final_confs = []
        for full_name in dim_map:
            traj = conf_trajectory.get(full_name, [])
            if traj:
                final_confs.append(traj[-1])
        row["convergence_overall_confidence"] = (
            sum(final_confs) / len(final_confs) if final_confs else 0.0
        )

        rows.append(row)

    df = pd.DataFrame(rows)

    # Sort for consistency
    df = df.sort_values(["story_id", "mode"]).reset_index(drop=True)

    return df


if __name__ == "__main__":
    # Quick self-test
    for layer in [4, 5, 6]:
        df = load_layer_data(layer)
        dims = list(LAYER_DIMENSIONS[layer].values())
        print(f"\nLayer {layer}: {len(df)} rows, {df['story_id'].nunique()} stories")
        print(f"  Categories: {dict(df[df['mode']=='content-limit']['category'].value_counts())}")
        print(f"  Modes: {list(df['mode'].unique())}")
        print(f"  Mean iterative_overall_score: {df['iterative_overall_score'].mean():.3f}")
        print(f"  Zero scores: {(df['iterative_overall_score'] == 0).sum()}")
        for dim in dims:
            print(f"  {dim} mean: {df[f'iterative_{dim}_score'].mean():.3f}")
