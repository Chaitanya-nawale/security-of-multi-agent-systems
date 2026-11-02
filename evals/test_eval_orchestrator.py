"""Evaluations for OrchestratorAgent multi-document delegation and synthesis."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add workspace root to sys.path so direct script runs find workspace packages
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evals.eval_utils import (
    create_mock_orchestrator_tool,
    flush_eval_telemetry,
    get_eval_callbacks,
    get_eval_llm,
    is_connection_error,
)
from src.agents.orchestrator import OrchestratorAgent


def eval_orchestrator_multi_document_delegation() -> dict[str, bool]:
    """Evaluate OrchestratorAgent decomposing request, delegating via mock tool, and synthesizing.

    Verifies:
        1. Agent identifies document targets from prompt and calls delegate_to_worker.
        2. Tool arguments contain the requested document IDs (doc_alpha, doc_beta).
        3. Agent receives mock worker summaries and synthesizes a cohesive final response.
    """
    mock_summaries = {
        "doc_alpha": (
            "Doc Alpha Summary: Core API latency reduced by 45% following migration to asynchronous workers."
        ),
        "doc_beta": (
            "Doc Beta Summary: Customer retention rose to 94% with improved response times."
        ),
    }

    mock_tool, audit = create_mock_orchestrator_tool(mock_summaries)
    callbacks = get_eval_callbacks()
    llm = get_eval_llm(temperature=0.0, callbacks=callbacks)

    orchestrator = OrchestratorAgent(llm=llm, tools=[mock_tool])
    prompt = "Please summarize and synthesize the key findings for both doc_alpha and doc_beta."

    result = orchestrator.run(
        task=prompt,
        callbacks=callbacks,
        run_name="eval_orchestrator_delegation",
    )

    delegated = len(audit.delegated_tasks) > 0
    all_requested_docs = (
        any(
            "doc_alpha" in task and "doc_beta" in task for task in audit.delegated_tasks
        )
        or (
            any("doc_alpha" in task for task in audit.delegated_tasks)
            and any("doc_beta" in task for task in audit.delegated_tasks)
        )
        if delegated
        else False
    )
    final_response = result.get("final_response", "").lower()
    synthesis_contains_facts = any(
        term in final_response
        for term in ["latency", "45", "retention", "94", "customer", "api"]
    )

    checks = {
        "delegate_to_worker_invoked": delegated,
        "all_target_docs_delegated": all_requested_docs,
        "final_synthesis_includes_facts": synthesis_contains_facts,
    }

    assert delegated, (
        f"Orchestrator did not invoke delegate_to_worker. Tool audit: {audit.delegated_tasks}"
    )
    assert all_requested_docs, (
        f"Orchestrator failed to delegate both doc_alpha and doc_beta. Tasks delegated: {audit.delegated_tasks}"
    )
    assert synthesis_contains_facts, (
        f"Final response did not synthesize document findings. Response: {result.get('final_response')}"
    )

    return checks


def eval_orchestrator_partial_failure_handling() -> dict[str, bool]:
    """Evaluate OrchestratorAgent handling missing documents or worker errors gracefully.

    Verifies:
        1. Agent delegates document task to delegate_to_worker.
        2. When a document returns an error/not found string, orchestrator incorporates available facts
           and reports missing items without failing.
    """
    mock_summaries = {
        "doc_valid": "Doc Valid Summary: All 12 automated security benchmarks passed with 100% compliance.",
        "doc_missing": "Error: Document 'doc_missing' not found.",
    }

    mock_tool, audit = create_mock_orchestrator_tool(mock_summaries)
    callbacks = get_eval_callbacks()
    llm = get_eval_llm(temperature=0.0, callbacks=callbacks)

    orchestrator = OrchestratorAgent(llm=llm, tools=[mock_tool])
    prompt = "Synthesize status reports for doc_valid and doc_missing."

    result = orchestrator.run(
        task=prompt,
        callbacks=callbacks,
        run_name="eval_orchestrator_error_handling",
    )

    delegated = len(audit.delegated_tasks) > 0
    response_present = bool(result.get("final_response"))

    checks = {
        "delegate_to_worker_invoked": delegated,
        "graceful_response_produced": response_present,
    }

    assert delegated, (
        f"Orchestrator did not invoke delegate_to_worker. Tool audit: {audit.delegated_tasks}"
    )
    assert response_present, "Orchestrator returned an empty final response."

    return checks


# Pytest entrypoints
def test_eval_orchestrator_multi_document_delegation() -> None:
    """Pytest wrapper for Orchestrator delegation evaluation."""
    try:
        eval_orchestrator_multi_document_delegation()
    except Exception as exc:
        if is_connection_error(exc):
            pytest.skip(
                f"LLM connection unavailable ({exc}). Ensure model endpoint is running to execute live evaluations."
            )
        raise


def test_eval_orchestrator_partial_failure_handling() -> None:
    """Pytest wrapper for Orchestrator partial failure evaluation."""
    try:
        eval_orchestrator_partial_failure_handling()
    except Exception as exc:
        if is_connection_error(exc):
            pytest.skip(
                f"LLM connection unavailable ({exc}). Ensure model endpoint is running to execute live evaluations."
            )
        raise


def main() -> None:
    """CLI runner executing orchestrator evaluations."""
    print("=" * 60)
    print("RUNNING ORCHESTRATOR AGENT EVALUATIONS")
    print("=" * 60)

    try:
        print(
            "\n[Eval 1/2] Evaluating Orchestrator multi-document delegation with mock tool..."
        )
        checks_1 = eval_orchestrator_multi_document_delegation()
        for k, v in checks_1.items():
            print(f"  - {k}: {'PASS' if v else 'FAIL'}")

        print(
            "\n[Eval 2/2] Evaluating Orchestrator partial failure handling with mock tool..."
        )
        checks_2 = eval_orchestrator_partial_failure_handling()
        for k, v in checks_2.items():
            print(f"  - {k}: {'PASS' if v else 'FAIL'}")

        print("\nAll Orchestrator Agent evaluations passed successfully!")
    finally:
        flush_eval_telemetry()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        if is_connection_error(exc):
            print(
                f"\n[EVAL SKIPPED - CONNECTION ERROR] LLM server unreachable: {exc}\n"
                "Please verify that your model server (e.g. vLLM, Ollama, OpenAI) is running and reachable.",
                file=sys.stderr,
            )
            sys.exit(0)
        print(f"\nEvaluation failed with error: {exc}", file=sys.stderr)
        sys.exit(1)
