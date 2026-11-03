"""Main CLI execution coordinator for MultiAgentSecurity prompt injection experiments."""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

# Ensure workspace root is in sys.path when executed directly as a script
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.definitions import (
    COMPACT_SCENARIO_1_DOC_IDS,
    COMPACT_SCENARIO_2_PAIRS,
    COMPACT_SCENARIO_3_BATCHES,
    RESULTS_DIR,
    SCENARIO_2_PAIRS,
    SCENARIO_3_BATCHES,
    ExperimentResult,
    load_dataset_metadata,
)
from experiments.reporting import generate_markdown_summary
from experiments.scenarios import (
    run_scenario_1_worker_isolation,
    run_scenario_2_mixed_context,
    run_scenario_3_stress_test,
    run_scenario_4_worker_all_docs,
)
from src.utils.logger import get_logger
from src.utils.telemetry import shutdown_telemetry

logger = get_logger("mas.experiments")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments for the experiment runner."""
    parser = argparse.ArgumentParser(
        description="Run prompt injection experiments against MultiAgentSecurity dataset."
    )
    parser.add_argument(
        "--suite",
        choices=["compact", "full"],
        default="compact",
        help="Experiment suite size: 'compact' (24 balanced single & multi-doc stress tests covering all 50 docs) or 'full' (71 exhaustive tests).",
    )
    parser.add_argument(
        "--scenario",
        choices=["all", "scenario_1", "scenario_2", "scenario_3", "scenario_4"],
        default="all",
        help="Specify which scenario to execute (default: all).",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default="baseline",
        help="Tool prompt profile from config/tool_prompts.yaml (e.g. baseline, defended, or any custom profile).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of tests executed per scenario for verification.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(RESULTS_DIR),
        help="Custom output directory for results files.",
    )
    return parser.parse_args()


def main() -> None:
    """Main CLI entrypoint executing configured experiment scenarios."""
    args = parse_arguments()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    results_jsonl = output_dir / f"experiment_run_{timestamp_str}.jsonl"
    summary_md = output_dir / f"summary_{timestamp_str}.md"

    logger.info("=" * 60)
    logger.info("MULTIAGENTSECURITY EXPERIMENT RUNNER")
    logger.info("Timestamp: %s", timestamp_str)
    logger.info("Results File: %s", results_jsonl)
    logger.info("Suite Selected: %s", args.suite)
    logger.info("Scenario Selected: %s", args.scenario)
    logger.info("Tool Profile: %s", args.profile)
    logger.info("=" * 60)

    dataset_meta = load_dataset_metadata()
    metadata_docs = dataset_meta.get("documents", [])

    all_results: list[ExperimentResult] = []

    if args.suite == "compact":
        s1_doc_ids = COMPACT_SCENARIO_1_DOC_IDS
        s2_pairs = COMPACT_SCENARIO_2_PAIRS
        s3_batches = COMPACT_SCENARIO_3_BATCHES
        run_s4 = args.scenario == "scenario_4"
    else:
        s1_doc_ids = None
        s2_pairs = SCENARIO_2_PAIRS
        s3_batches = SCENARIO_3_BATCHES
        run_s4 = args.scenario in ("all", "scenario_4")

    try:
        if args.scenario in ("all", "scenario_1"):
            all_results.extend(
                run_scenario_1_worker_isolation(
                    metadata_docs=metadata_docs,
                    results_file=results_jsonl,
                    limit=args.limit,
                    doc_ids=s1_doc_ids,
                    profile=args.profile,
                )
            )

        if args.scenario in ("all", "scenario_2"):
            all_results.extend(
                run_scenario_2_mixed_context(
                    results_file=results_jsonl,
                    limit=args.limit,
                    pairs=s2_pairs,
                    profile=args.profile,
                )
            )

        if args.scenario in ("all", "scenario_3"):
            all_results.extend(
                run_scenario_3_stress_test(
                    results_file=results_jsonl,
                    limit=args.limit,
                    batches=s3_batches,
                    profile=args.profile,
                )
            )

        if run_s4:
            all_results.extend(
                run_scenario_4_worker_all_docs(
                    metadata_docs=metadata_docs,
                    results_file=results_jsonl,
                    limit=args.limit,
                    profile=args.profile,
                )
            )

        if all_results:
            generate_markdown_summary(all_results, summary_md)
            logger.info("Summary markdown written to %s", summary_md)

        logger.info(
            "Experiment run complete. Total results recorded: %d", len(all_results)
        )
    finally:
        shutdown_telemetry()


if __name__ == "__main__":
    main()
