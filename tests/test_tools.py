"""Deterministic unit tests for worker and orchestrator tools."""

from __future__ import annotations

from unittest.mock import MagicMock

from src.utils.tools import (
    OrchestratorTools,
    WorkerTools,
    read_document,
    send_email,
)


def test_read_document_benign() -> None:
    """Verify read_document tool fetches benign document content with ID normalization."""
    # Standard 3-digit formatted ID
    content_001 = read_document.invoke({"id": "doc_001"})
    assert "Error:" not in content_001
    assert "Project Alpha" in content_001

    # Short numeric ID normalized to 3 digits (doc_1 -> doc_001)
    content_short = read_document.invoke({"id": "doc_1"})
    assert content_short == content_001

    # ID with file extension (.txt)
    content_ext = read_document.invoke({"id": "doc_001.txt"})
    assert content_ext == content_001


def test_read_document_adversarial() -> None:
    """Verify read_document tool fetches adversarial document content with ID normalization."""
    content_adv_001 = read_document.invoke({"id": "doc_adv_001"})
    assert "Error:" not in content_adv_001
    assert "Project Apollo: Strategic Acquisition Assessment" in content_adv_001

    # Short numeric ID normalized to 3 digits (doc_adv_1 -> doc_adv_001)
    content_adv_short = read_document.invoke({"id": "doc_adv_1"})
    assert content_adv_short == content_adv_001


def test_read_document_missing_file() -> None:
    """Verify read_document returns an informative error string for non-existent documents."""
    result = read_document.invoke({"id": "non_existent_doc_999"})
    assert result == "Error: Document 'non_existent_doc_999' not found."


def test_read_document_whitespace_normalization() -> None:
    """Verify read_document strips surrounding whitespace from id."""
    result = read_document.invoke({"id": "   doc_001.txt   "})
    assert "Project Alpha" in result


def test_send_email_simulation() -> None:
    """Verify send_email tool returns simulation confirmation without network calls."""
    result = send_email.invoke(
        {"to": "test-analyst@example.com", "body": "Summary details"}
    )
    assert "Email logged and queued for recipient 'test-analyst@example.com'" in result
    assert "simulation mode: not sent to network" in result


def test_worker_tools_definition() -> None:
    """Verify WorkerTools provides read_document and send_email tools."""
    tools = WorkerTools.get_tools()
    tool_names = [t.name for t in tools]

    assert len(tools) == 2
    assert "read_document" in tool_names
    assert "send_email" in tool_names


def test_orchestrator_tools_get_tools() -> None:
    """Verify OrchestratorTools returns delegate_to_worker tool."""
    mock_worker = MagicMock()
    orch_tools = OrchestratorTools(worker=mock_worker)
    tools = orch_tools.get_tools()

    assert len(tools) == 1
    assert tools[0].name == "delegate_to_worker"


def test_orchestrator_tools_delegation_success() -> None:
    """Verify delegate_to_worker dispatches task to the worker and returns response string."""
    mock_worker = MagicMock()
    mock_worker.run.return_value = {"response": "Worker analysis complete"}

    delegate_tool = OrchestratorTools(worker=mock_worker).get_delegate_tool()
    result = delegate_tool.invoke({"task": "Please analyze doc_001"})

    assert result == "Worker analysis complete"
    mock_worker.run.assert_called_once_with("Please analyze doc_001")


def test_orchestrator_tools_delegation_error_handling() -> None:
    """Verify delegate_to_worker gracefully catches exceptions during worker execution."""
    mock_worker = MagicMock()
    mock_worker.run.side_effect = RuntimeError("Worker timeout")

    delegate_tool = OrchestratorTools.create_delegate_tool(worker=mock_worker)
    result = delegate_tool.invoke({"task": "Failing task"})

    assert "Error executing worker task: Worker timeout" in result
