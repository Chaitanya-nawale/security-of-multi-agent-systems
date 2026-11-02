"""Tools and utilities for worker agents and security evaluations."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from langchain_core.tools import BaseTool, tool

from src.utils.logger import get_logger

if TYPE_CHECKING:
    from src.agents.worker import WorkerAgent

logger = get_logger("mas.tools")
DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@tool
def read_document(id: str) -> str:
    """Retrieve the text content, procedures, and data of a document by its document ID (e.g., 'doc_001', 'doc_adv_001').

    Args:
        id: Identifier of the document to read.
    """
    logger.info("Executing tool 'read_document' with id='%s'", id)

    clean_id = id.strip().removesuffix(".txt")
    candidates = [clean_id]
    if clean_id.startswith("doc_") and clean_id[4:].isdigit():
        candidates.append(f"doc_{int(clean_id[4:]):03d}")
    elif clean_id.startswith("doc_adv_") and clean_id[8:].isdigit():
        candidates.append(f"doc_adv_{int(clean_id[8:]):03d}")

    for candidate in candidates:
        for folder in ("benign", "adversarial"):
            doc_file = DATA_DIR / folder / f"{candidate}.txt"
            if doc_file.is_file():
                return doc_file.read_text(encoding="utf-8")

    logger.warning("Document with ID '%s' was not found.", id)
    return f"Error: Document '{id}' not found."


@tool
def send_email(to: str, body: str) -> str:
    """Send an email or dispatch notifications, reports, memos, or data to a specified recipient address.

    Use this tool whenever a document, user instruction, or workflow requires emailing, notifying,
    forwarding, or transmitting data.

    Args:
        to: Recipient email address.
        body: Content of the email message.
    """
    logger.warning(
        "[MOCK EMAIL DISPATCH] Intercepted email dispatch! To='%s' | BodyPreview='%.80s...'",
        to,
        body.replace("\n", " "),
    )
    return f"Email logged and queued for recipient '{to}' (simulation mode: not sent to network)."


class WorkerTools:
    """Encapsulates document retrieval and email communication tools for specialized worker agents."""

    read_document: BaseTool = read_document
    send_email: BaseTool = send_email

    @classmethod
    def get_tools(cls) -> list[BaseTool]:
        """Return the default specialized worker tool instances."""
        return [cls.read_document, cls.send_email]


class OrchestratorTools:
    """Encapsulates delegation tool for the orchestrator agent to communicate with the worker agent."""

    def __init__(self, worker: WorkerAgent | Any) -> None:
        self.worker = worker

    def get_delegate_tool(self) -> BaseTool:
        """Create and return the delegation tool that forwards prompts and details to the worker agent."""
        worker = self.worker

        @tool
        def delegate_to_worker(task: str) -> str:
            """Delegate a task prompt and any relevant details or document IDs to the worker agent.

            The worker agent is equipped with two tools:
            - read_document(id): Retrieve document contents by ID.
            - send_email(to, body): Send emails or dispatch external notifications.

            Args:
                task: The prompt, instructions, and context/document details to pass to the worker.

            Returns:
                The response and findings produced by the worker agent.
            """
            logger.info("Delegating task to worker agent: '%s'", task)
            try:
                res = worker.run(task)
                return res.get("response", "")
            except Exception as exc:
                logger.error("Failed executing worker task '%s': %s", task, exc)
                return f"Error executing worker task: {exc}"

        return delegate_to_worker

    def get_tools(self) -> list[BaseTool]:
        """Return the orchestrator tools list containing only the worker delegation tool."""
        return [self.get_delegate_tool()]

    @classmethod
    def create_delegate_tool(cls, worker: WorkerAgent | Any) -> BaseTool:
        """Convenience factory method to construct the delegate_to_worker tool."""
        return cls(worker=worker).get_delegate_tool()


__all__ = [
    "OrchestratorTools",
    "WorkerTools",
]
