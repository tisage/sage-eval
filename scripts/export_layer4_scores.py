#!/usr/bin/env python3
"""
Export Layer 4 Primary and Peer Judge Scores to CSV

Generates a CSV table with final round (Round 5) scores for all stories,
including both pure_text and prior_knowledge modes.
"""

import json
import csv
import sys
from pathlib import Path
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def load_layer4_scores(layer4_dir: Path) -> List[Dict]:
    """
    Load Layer 4 primary and peer scores from JSON files.

    Returns:
        List of dicts with story scores:
        [
            {
                "story_id": "chekhov_lady_with_dog",
                "category": "Canonical",
                "mode": "pure_text",
                "primary_IPD": 4.0,
                "primary_CVP": 3.5,
                "primary_CSP": 4.6,
                "primary_CPC": 4.0,
                "primary_overall": 4.0,
                "peer_IPD": 4.0,
                "peer_CVP": 3.8,
                ...
            },
            ...
        ]
    """
    # Define canonical and pulp stories
    CANONICAL_STORIES = {
        "chekhov_lady_with_dog",
        "gogol_overcoat",
        "maupassant_necklace",
        "hawthorne_young_goodman_brown",
        "poe_fall_house_usher",
        "joyce_the_dead",
        "kafka_metamorphosis",
        "oconnor_good_country_people",
        "akutagawa_in_a_grove",
        "borges_library_of_babel"
    }

    PULP_STORIES = {
        "brand_the_untamed",
        "burroughs_tarzan_of_apes",
        "carter_nick_carter_stories",
        "cummings_girl_in_golden_atom",
        "grey_riders_of_purple_sage",
        "leinster_mad_planet",
        "lovecraft_dunwich_horror",
        "mcculley_curse_of_capistrano",
        "oppenheim_double_four",
        "rohmer_dr_fu_manchu"
    }

    scores_data = []

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
            story_id = item.get("story_id", "")
            mode = item.get("mode", "")

            if not story_id or not mode:
                continue

            # Determine category
            if story_id in CANONICAL_STORIES:
                category = "Canonical"
            elif story_id in PULP_STORIES:
                category = "Pulp"
            else:
                category = "Unknown"

            # Initialize row
            row = {
                "story_id": story_id,
                "category": category,
                "mode": mode
            }

            # Extract PRIMARY JUDGE scores from primary_result
            primary_result = item.get("primary_result", {})
            primary_dimensions = primary_result.get("dimensions", {})

            row["primary_overall"] = primary_result.get("score", 0.0)

            for full_name, abbrev in dim_mapping.items():
                if full_name in primary_dimensions:
                    row[f"primary_{abbrev}"] = primary_dimensions[full_name].get("score", 0.0)
                else:
                    row[f"primary_{abbrev}"] = None

            # Extract PEER JUDGE scores from peer_result
            peer_result = item.get("peer_result", {})

            # Peer scores are in 'independent_scores', not 'dimensions'
            peer_independent_scores = peer_result.get("independent_scores", {})

            # Calculate peer overall score (average of dimensions)
            peer_dim_scores = []
            for full_name, abbrev in dim_mapping.items():
                if full_name in peer_independent_scores:
                    score = peer_independent_scores[full_name].get("score", 0.0)
                    row[f"peer_{abbrev}"] = score
                    peer_dim_scores.append(score)
                else:
                    row[f"peer_{abbrev}"] = None

            # Calculate peer overall as average
            if peer_dim_scores:
                row["peer_overall"] = round(sum(peer_dim_scores) / len(peer_dim_scores), 2)
            else:
                row["peer_overall"] = None

            # Only add if we have complete data
            if all(row.get(f"primary_{dim}") is not None for dim in ["IPD", "CVP", "CSP", "CPC"]):
                scores_data.append(row)

        except Exception as e:
            print(f"Error loading {json_file}: {e}", file=sys.stderr)
            continue

    # Sort by story_id and mode
    scores_data.sort(key=lambda x: (x["story_id"], x["mode"]))

    return scores_data


def export_to_csv(scores_data: List[Dict], output_file: Path):
    """Export scores to CSV file."""

    if not scores_data:
        print("No data to export!", file=sys.stderr)
        return

    # Define column order
    columns = [
        "story_id",
        "category",
        "mode",
        "primary_overall",
        "primary_IPD",
        "primary_CVP",
        "primary_CSP",
        "primary_CPC",
        "peer_overall",
        "peer_IPD",
        "peer_CVP",
        "peer_CSP",
        "peer_CPC"
    ]

    # Write CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

        for row in scores_data:
            # Only write columns we defined
            filtered_row = {col: row.get(col, "") for col in columns}
            writer.writerow(filtered_row)

    print(f"\n✅ Exported {len(scores_data)} rows to: {output_file}")

    # Print summary
    unique_stories = len(set(row["story_id"] for row in scores_data))
    modes = set(row["mode"] for row in scores_data)

    print(f"\nSummary:")
    print(f"  - Unique stories: {unique_stories}")
    print(f"  - Modes: {', '.join(sorted(modes))}")
    print(f"  - Total rows: {len(scores_data)}")


def main():
    """Main execution function."""

    # Paths
    project_root = Path(__file__).parent.parent
    layer4_dir = project_root / "results" / "new_layer4_20251221_140852"
    output_file = project_root / "results" / "layer4_scores.csv"

    # Verify directory exists
    if not layer4_dir.exists():
        print(f"Error: Layer 4 directory not found: {layer4_dir}", file=sys.stderr)
        sys.exit(1)

    print("Loading Layer 4 scores...")
    scores_data = load_layer4_scores(layer4_dir)
    print(f"Loaded {len(scores_data)} evaluations")

    print("\nExporting to CSV...")
    export_to_csv(scores_data, output_file)

    print(f"\n📊 CSV file ready for analysis: {output_file}")


if __name__ == "__main__":
    main()
