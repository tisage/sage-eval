#!/usr/bin/env python3
"""
Universal Parallel Batch Test for SAGE Framework (Layer 4/5/6)

Single unified script that supports concurrent testing across all evaluation layers.
Replaces individual serial test scripts with parallel execution by default.

Usage:
    # Layer 4 (Cultural)
    python scripts/batch_test_parallel.py --layer 4 --workers 4

    # Layer 5 (Emotional)
    python scripts/batch_test_parallel.py --layer 5 --workers 6

    # Layer 6 (Existential)
    python scripts/batch_test_parallel.py --layer 6 --workers 4

    # Custom story subset
    python scripts/batch_test_parallel.py --layer 5 --workers 4 \
        --stories maupassant_necklace chekhov_lady_with_dog \
        --modes content-limit
"""

import argparse
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from multiprocessing import Pool, Manager, current_process
from functools import partial
import traceback
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from omnisage.core.llm_client import LLMClient


# Layer-specific imports (lazy loaded based on --layer argument)
# UPDATED 2025-12-23: Module and class names updated to new terminology
LAYER_CONFIGS = {
    4: {
        "name": "Cultural",
        "config_file": "config/layer4_cultural_config.yaml",
        "judge_module": "omnisage.evaluation.sage.llm.layer4_cultural_iterative",
        "judge_class": "CulturalIterativeEvaluator",
        "peer_module": "omnisage.evaluation.sage.llm.layer4_cultural_validator",
        "peer_class": "CulturalIndependentValidator",
        "dimensions": [
            "intersectional_power_dynamics",
            "cultural_voice_perspective",
            "cultural_specificity",
            "cultural_pattern_complexity"
        ]
    },
    5: {
        "name": "Emotional",
        "config_file": "config/layer5_emotional_config.yaml",
        "judge_module": "omnisage.evaluation.sage.llm.layer5_emotional_iterative",
        "judge_class": "EmotionalIterativeEvaluator",
        "peer_module": "omnisage.evaluation.sage.llm.layer5_emotional_validator",
        "peer_class": "EmotionalIndependentValidator",
        "dimensions": [
            "affective_complexity",
            "psychological_interiority",
            "emotional_granularity",
            "emotional_narrative_coherence"
        ]
    },
    6: {
        "name": "Existential",
        "config_file": "config/layer6_existential_config.yaml",
        "judge_module": "omnisage.evaluation.sage.llm.layer6_existential_iterative",
        "judge_class": "ExistentialIterativeEvaluator",
        "peer_module": "omnisage.evaluation.sage.llm.layer6_existential_validator",
        "peer_class": "ExistentialIndependentValidator",
        "dimensions": [
            "life_philosophy",
            "moral_reflection",
            "human_condition",
            "meaning_exploration"
        ]
    },
}


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_story_catalog(catalog_path: str) -> dict:
    """Load story catalog from YAML file"""
    with open(catalog_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def select_stories_by_strategy(
    catalog: dict,
    preset: dict
) -> List[dict]:
    """
    Select stories based on experiment preset strategy.

    Strategies:
    - "curated": Use explicitly specified canonical_ids and pulp_ids
    - "first_n": Auto-select first N stories from catalog
    - "all": Select all stories of specified type

    Args:
        catalog: Story catalog dictionary
        preset: Experiment preset configuration

    Returns:
        List of selected story dictionaries
    """
    strategy = preset.get('strategy', 'curated')
    canonical_count = preset.get('canonical_count', 0)
    pulp_count = preset.get('pulp_count', 0)
    llm_count = preset.get('llm_count', 0)

    canonical_stories = catalog['canonical_stories']
    pulp_stories = catalog['pulp_stories']
    llm_stories = catalog.get('llm_generated_stories', [])

    selected = []

    if strategy == "curated":
        # Use explicitly specified IDs
        canonical_ids = preset.get('canonical_ids', [])
        pulp_ids = preset.get('pulp_ids', [])
        llm_ids = preset.get('llm_ids', [])

        for story in canonical_stories:
            if story['id'] in canonical_ids:
                selected.append(story)

        for story in pulp_stories:
            if story['id'] in pulp_ids:
                selected.append(story)

        for story in llm_stories:
            if story['id'] in llm_ids:
                selected.append(story)

    elif strategy == "first_n":
        # Auto-select first N stories
        selected.extend(canonical_stories[:canonical_count])
        selected.extend(pulp_stories[:pulp_count])
        selected.extend(llm_stories[:llm_count])

    elif strategy == "all":
        # Select all stories of specified type
        if canonical_count > 0:
            selected.extend(canonical_stories)
        if pulp_count > 0:
            selected.extend(pulp_stories)
        if llm_count > 0:
            selected.extend(llm_stories)

    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    return selected


def load_story(story_path: str) -> str:
    """Load story text from file"""
    with open(story_path, 'r', encoding='utf-8') as f:
        return f.read()


def import_layer_classes(layer_num: int):
    """Dynamically import layer-specific judge classes"""
    layer_config = LAYER_CONFIGS[layer_num]

    # Import judge class
    judge_module = __import__(layer_config['judge_module'], fromlist=[layer_config['judge_class']])
    judge_class = getattr(judge_module, layer_config['judge_class'])

    # Import peer class
    peer_module = __import__(layer_config['peer_module'], fromlist=[layer_config['peer_class']])
    peer_class = getattr(peer_module, layer_config['peer_class'])

    return judge_class, peer_class


def test_single_task(
    task: dict,
    layer_num: int,
    config: dict,
    llm_models_config: dict,
    output_dir: Path,
    progress_dict: dict,
    judge_class: type,
    peer_class: type
) -> dict:
    """
    Universal test function for a single story×mode combination
    Works for any layer (4/5/6) by using passed judge classes

    Args:
        task: {"story": {...}, "mode": str, "task_id": int, "total_tasks": int}
        layer_num: Layer number (4/5/6)
        config: Full config dict
        llm_models_config: LLM models config
        output_dir: Output directory
        progress_dict: Shared dict for progress tracking
        judge_class: Judge class (e.g., MultiRoundCulturalJudge)
        peer_class: Peer judge class

    Returns:
        {"status": "success"/"failed", "result": {...}, "error": str}
    """
    story = task['story']
    mode = task['mode']
    task_id = task['task_id']
    total_tasks = task['total_tasks']

    story_id = story['id']
    story_path = story['path']
    title = story['title']

    process_name = current_process().name
    layer_name = LAYER_CONFIGS[layer_num]['name']

    try:
        # Create LLM client (each process has its own)
        model_name = config.get('models', {}).get('primary_judge', 'gpt-5-mini')

        # Find model config
        model_config = None
        for model in llm_models_config['production']['models']:
            if model['model_name'] == model_name:
                model_config = model
                break

        if not model_config:
            raise ValueError(f"Model {model_name} not found in llm_models.yaml")

        # Create llm_config
        llm_config = {
            "model_provider": model_config['provider'],
            "model_name": model_config['model_name'],
            "base_url": "https://api.openai.com/v1",
            "key_value": model_config['api_key_env'],
            "model_token_size": model_config.get('max_tokens', 65536)
        }

        if 'reasoning_effort' in model_config:
            llm_config['reasoning_effort'] = model_config['reasoning_effort']
        if 'thinking_budget' in model_config:
            llm_config['thinking_budget'] = model_config['thinking_budget']
        if 'response_format' in model_config:
            llm_config['response_format'] = model_config['response_format']

        llm_client = LLMClient(llm_config)

        # Load story
        text = load_story(story_path)

        print(f"[{process_name}] [{task_id}/{total_tasks}] Layer {layer_num} ({layer_name}): {story_id} ({mode})")

        # Initialize judge (generic - works for any layer)
        num_rounds = config['multi_round'].get('num_rounds', 5)
        # UPDATED 2025-12-24: Use mode parameter directly
        judge = judge_class(
            llm_client=llm_client,
            temperature=1.0,
            num_rounds=num_rounds,
            mode=mode
        )

        # Evaluate
        context = {'title': title} if mode == "title-limit" else {}
        primary_result = judge.evaluate(text, context)

        if primary_result.get('error'):
            raise Exception(f"Iterative evaluation error: {primary_result['error']}")

        # Independent validation (if enabled)
        # UPDATED 2025-12-24: Use validator terminology and mode parameter
        peer_result = None
        if config['multi_round']['independent_validation']['enabled']:
            validator = peer_class(llm_client=llm_client, temperature=1.0)
            validator_context = {
                'iterative_evaluation': primary_result,
                'title': title if mode == "title-limit" else None
            }
            peer_result = validator.evaluate(text, validator_context)

        # Prepare result
        result = {
            "layer": layer_num,
            "story_id": story_id,
            "title": title,
            "mode": mode,
            "primary_result": primary_result,
            "peer_result": peer_result,
            "timestamp": datetime.now().isoformat()
        }

        # Save individual result
        result_file = output_dir / f"layer{layer_num}_{story_id}_{mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        # Update progress
        progress_dict['completed'] += 1
        print(f"[{process_name}] ✅ PASSED: Layer {layer_num} {story_id} ({mode}) - Progress: {progress_dict['completed']}/{total_tasks}")

        return {
            "status": "success",
            "result": result,
            "error": None
        }

    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        progress_dict['failed'] += 1
        print(f"[{process_name}] ❌ FAILED: Layer {layer_num} {story_id} ({mode}) - {str(e)}")

        return {
            "status": "failed",
            "result": {
                "layer": layer_num,
                "story_id": story_id,
                "mode": mode,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            },
            "error": error_msg
        }


def main():
    parser = argparse.ArgumentParser(
        description='Universal Parallel Batch Test for SAGE Framework (Layer 4/5/6)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Smoke test (1 story, quick validation)
  python scripts/batch_test_parallel.py --layer 5 --experiment smoke_test

  # 5v5 pilot test (5 canonical vs 5 pulp)
  python scripts/batch_test_parallel.py --layer 5 --workers 4 --experiment pilot_5v5

  # Full 10v10 validation (10 canonical vs 10 pulp)
  python scripts/batch_test_parallel.py --layer 5 --workers 6 --experiment full_10v10

  # Test all canonical stories only
  python scripts/batch_test_parallel.py --layer 5 --workers 6 --experiment all_canonical

  # Manual story selection (overrides experiment presets)
  python scripts/batch_test_parallel.py --layer 5 --workers 2 \
      --stories maupassant_necklace chekhov_lady_with_dog \
      --modes content-limit

  # Test all stories from config (default)
  python scripts/batch_test_parallel.py --layer 4 --workers 8
        """
    )
    parser.add_argument('--layer', type=int, required=True, choices=[4, 5, 6],
                        help='Layer number (4=Cultural, 5=Emotional, 6=Existential)')
    parser.add_argument('--workers', type=int, default=4,
                        help='Number of parallel workers (default: 4, max recommended: 8)')
    parser.add_argument('--config', default=None,
                        help='Config file path (auto-detected based on layer if not specified)')
    parser.add_argument('--output', default=None,
                        help='Output directory (auto-generated if not specified)')
    parser.add_argument('--experiment', default=None,
                        choices=['smoke_test', 'pilot_5v5', 'pilot_10v10', 'full_10v10', 'full_20v10', 'full_50v50',
                                 'all_canonical', 'all_pulp', 'all_canonical_53', 'full_corpus'],
                        help='Experiment preset to run (default: all stories from catalog)')
    parser.add_argument('--stories', nargs='+', default=None,
                        help='Story IDs to test (overrides --experiment if specified)')
    parser.add_argument('--modes', nargs='+', default=['content-limit', 'title-limit'],
                        choices=['content-limit', 'title-limit'],
                        # UPDATED 2025-12-24: Use new mode names
                        help='Modes to test (default: both)')

    args = parser.parse_args()

    # Validate layer
    if args.layer not in LAYER_CONFIGS:
        print(f"❌ Layer {args.layer} not yet implemented. Available: {list(LAYER_CONFIGS.keys())}")
        sys.exit(1)

    layer_config = LAYER_CONFIGS[args.layer]
    layer_name = layer_config['name']

    # Auto-detect config file
    config_file = args.config if args.config else layer_config['config_file']

    # Auto-generate output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"results/layer{args.layer}_{layer_name.lower()}_parallel_{timestamp}")

    # Load configs
    print(f"Loading Layer {args.layer} ({layer_name}) config from {config_file}...")
    config = load_config(config_file)

    llm_models_config_path = Path(__file__).parent.parent / "config" / "llm_models.yaml"
    llm_models_config = load_config(str(llm_models_config_path))

    # Import layer-specific classes
    print(f"Loading Layer {args.layer} judge classes...")
    judge_class, peer_class = import_layer_classes(args.layer)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load story catalog
    catalog_path_str = config.get('story_catalog', 'config/story_catalog.yaml')
    catalog_path = Path(catalog_path_str)
    if not catalog_path.is_absolute():
        catalog_path = Path(__file__).parent.parent / catalog_path

    if not catalog_path.exists():
        print(f"❌ Error: Story catalog not found: {catalog_path}")
        print("Run: python scripts/sync_story_catalog.py --scan --update")
        sys.exit(1)

    catalog = load_story_catalog(str(catalog_path))
    all_catalog_stories = (
        catalog['canonical_stories'] +
        catalog['pulp_stories'] +
        catalog.get('llm_generated_stories', [])
    )

    # Determine stories to test
    if args.stories:
        # Manual story selection (overrides --experiment)
        test_stories = [s for s in all_catalog_stories if s['id'] in args.stories]
        if len(test_stories) != len(args.stories):
            missing = set(args.stories) - {s['id'] for s in test_stories}
            print(f"⚠️  Warning: Stories not found in catalog: {missing}")
    elif args.experiment:
        # Use experiment preset
        if 'experiment_presets' not in config:
            print(f"❌ Error: Config file {config_file} does not have 'experiment_presets' section")
            print("Please add experiment_presets to your config file.")
            sys.exit(1)

        if args.experiment not in config['experiment_presets']:
            print(f"❌ Error: Experiment preset '{args.experiment}' not found in config")
            print(f"Available presets: {list(config['experiment_presets'].keys())}")
            sys.exit(1)

        preset = config['experiment_presets'][args.experiment]
        test_stories = select_stories_by_strategy(catalog, preset)

        print(f"Using experiment preset: {args.experiment}")
        print(f"Strategy: {preset.get('strategy', 'curated')}")
        print(f"Description: {preset['description']}")
        print(f"Selected: {len(test_stories)} stories")
    else:
        # Default: all stories from catalog
        test_stories = all_catalog_stories
        print(f"Using all stories from catalog: {len(test_stories)} stories")

    # Generate all tasks (story × mode combinations)
    tasks = []
    task_id = 0
    for story in test_stories:
        for mode in args.modes:
            task_id += 1
            tasks.append({
                "story": story,
                "mode": mode,
                "task_id": task_id,
                "total_tasks": len(test_stories) * len(args.modes)
            })

    total_tasks = len(tasks)

    print(f"\n{'='*70}")
    print(f"SAGE PARALLEL BATCH TEST - LAYER {args.layer} ({layer_name.upper()})")
    print(f"{'='*70}")
    print(f"Stories: {len(test_stories)}")
    print(f"Modes: {', '.join(args.modes)}")
    print(f"Total tasks: {total_tasks}")
    print(f"Parallel workers: {args.workers}")
    print(f"Output directory: {output_dir}")
    print(f"Estimated time: {total_tasks / args.workers * 1.5:.1f} minutes (rough estimate)")
    print(f"{'='*70}\n")

    # Confirm if large test
    if total_tasks >= 20 and not args.stories:
        response = input(f"⚠️  You're about to run {total_tasks} tests. Continue? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)

    # Shared progress tracking
    manager = Manager()
    progress_dict = manager.dict()
    progress_dict['completed'] = 0
    progress_dict['failed'] = 0

    # Create partial function with layer-specific classes
    test_func = partial(
        test_single_task,
        layer_num=args.layer,
        config=config,
        llm_models_config=llm_models_config,
        output_dir=output_dir,
        progress_dict=progress_dict,
        judge_class=judge_class,
        peer_class=peer_class
    )

    # Run parallel execution
    print(f"🚀 Starting parallel execution with {args.workers} workers...\n")
    start_time = datetime.now()

    with Pool(processes=args.workers) as pool:
        results = pool.map(test_func, tasks)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Analyze results
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']

    # Save summary
    summary = {
        "layer": args.layer,
        "layer_name": layer_name,
        "total_tasks": total_tasks,
        "successful": len(successful),
        "failed": len(failed),
        "duration_seconds": duration,
        "workers": args.workers,
        "stories": [s['id'] for s in test_stories],
        "modes": args.modes,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    summary_file = output_dir / f"layer{args.layer}_batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n{'='*70}")
    print(f"LAYER {args.layer} ({layer_name.upper()}) BATCH TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Total tasks: {total_tasks}")
    print(f"Successful: {len(successful)} ✅")
    print(f"Failed: {len(failed)} ❌")
    print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"Average time per task: {duration/total_tasks:.1f} seconds")
    print(f"Speedup: ~{total_tasks / args.workers:.1f}x (vs serial)")
    print(f"\nResults saved to: {output_dir}")
    print(f"Summary: {summary_file}")
    print(f"{'='*70}\n")

    if len(failed) > 0:
        print("❌ Failed tasks:")
        for r in failed:
            print(f"  - {r['result']['story_id']} ({r['result']['mode']})")
        print()
        sys.exit(1)
    else:
        print(f"✅ All Layer {args.layer} ({layer_name}) tests completed successfully!\n")
        print("Next steps:")
        print(f"  1. Generate report: python scripts/generate_layer{args.layer}_report.py {output_dir}")
        print(f"  2. Analyze convergence (target: ≥90% dimensions stable)")
        if args.layer == 5:
            print(f"  3. Compare with Layer 4 for cross-layer correlation")
        if args.layer == 6:
            print(f"  3. Compare with Layer 4/5 for cross-layer correlation")


if __name__ == '__main__':
    main()
