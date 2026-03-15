#!/usr/bin/env python3
"""
Export Layer 5 Primary and Peer Judge Scores to CSV

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


def load_layer5_scores(layer5_dir: Path) -> List[Dict]:
    """
    Load Layer 5 primary and peer scores from JSON files.

    Returns:
        List of dicts with story scores:
        [
            {
                "story_id": "chekhov_lady_with_dog",
                "category": "Canonical",
                "mode": "pure_text",
                "primary_AC": 4.5,
                "primary_PI": 4.5,
                "primary_EG": 3.8,
                "primary_ENC": 4.5,
                "primary_overall": 4.3,
                "peer_AC": 4.5,
                "peer_PI": 4.0,
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
            story_id = data.get("story_id", "")
            mode = data.get("mode", "")

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
            primary_result = data.get("primary_result", {})
            primary_dimensions = primary_result.get("dimensions", {})

            row["primary_overall"] = primary_result.get("score", 0.0)

            for full_name, abbrev in dim_mapping.items():
                if full_name in primary_dimensions:
                    row[f"primary_{abbrev}"] = primary_dimensions[full_name].get("score", 0.0)
                else:
                    row[f"primary_{abbrev}"] = None

            # Extract PEER JUDGE scores from peer_result
            peer_result = data.get("peer_result", {})

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
            if all(row.get(f"primary_{dim}") is not None for dim in ["AC", "PI", "EG", "ENC"]):
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
        "primary_AC",
        "primary_PI",
        "primary_EG",
        "primary_ENC",
        "peer_overall",
        "peer_AC",
        "peer_PI",
        "peer_EG",
        "peer_ENC"
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
    layer5_dir = project_root / "results" / "layer5_emotional_parallel_20251222_104119"
    output_file = project_root / "results" / "layer5_scores.csv"

    # Verify directory exists
    if not layer5_dir.exists():
        print(f"Error: Layer 5 directory not found: {layer5_dir}", file=sys.stderr)
        sys.exit(1)

    print("Loading Layer 5 scores...")
    scores_data = load_layer5_scores(layer5_dir)
    print(f"Loaded {len(scores_data)} evaluations")

    print("\nExporting to CSV...")
    export_to_csv(scores_data, output_file)

    print(f"\n📊 CSV file ready for analysis: {output_file}")


if __name__ == "__main__":
    main()
