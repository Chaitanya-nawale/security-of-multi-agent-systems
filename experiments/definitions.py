"""Data definitions, test manifests, and structures for MAS experiments."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RESULTS_DIR = Path(__file__).resolve().parent / "results"
METADATA_FILE = DATA_DIR / "dataset_metadata.json"


@dataclass
class AuditTracker:
    """Tracks tool invocations across an evaluation run."""

    read_calls: list[str] = field(default_factory=list)
    email_calls: list[dict[str, str]] = field(default_factory=list)

    def reset(self) -> None:
        """Clear recorded invocations for a new test."""
        self.read_calls.clear()
        self.email_calls.clear()


@dataclass
class ExperimentResult:
    """Structured record of a single experiment execution."""

    timestamp: str
    scenario: str
    test_id: str
    target_docs: list[str]
    category: str
    archetype: str
    expected_send_email: bool
    email_tool_called: bool
    email_calls_count: int
    email_recipients: list[str]
    read_document_called: bool
    read_calls: list[str]
    injection_succeeded: bool
    defense_succeeded: bool
    response_preview: str
    duration_seconds: float
    trace_id: str | None = None
    error: str | None = None
    trajectory_outcome: str = "inert_ignored"


def load_dataset_metadata() -> dict[str, Any]:
    """Load the machine-readable dataset manifest."""
    if not METADATA_FILE.is_file():
        raise FileNotFoundError(f"Dataset metadata not found at {METADATA_FILE}")
    with METADATA_FILE.open(encoding="utf-8") as f:
        return json.load(f)


# Compact Benchmark Suite: 24 Executions Covering All 50 Benchmark Documents
COMPACT_SCENARIO_1_DOC_IDS: list[str] = [
    "doc_001",
    "doc_002",
    "doc_adv_001",
    "doc_adv_002",
    "doc_adv_011",
    "doc_adv_012",
    "doc_adv_021",
    "doc_adv_022",
    "doc_adv_031",
    "doc_adv_032",
]

COMPACT_SCENARIO_2_PAIRS: list[dict[str, str]] = [
    {
        "id": "pair_01",
        "benign_id": "doc_003",
        "adv_id": "doc_adv_003",
        "adv_category": "direct_override",
        "adv_archetype": "mandatory_legal_registry_filing",
    },
    {
        "id": "pair_02",
        "benign_id": "doc_004",
        "adv_id": "doc_adv_004",
        "adv_category": "direct_override",
        "adv_archetype": "automated_analytics_sync",
    },
    {
        "id": "pair_03",
        "benign_id": "doc_005",
        "adv_id": "doc_adv_013",
        "adv_category": "contextual_masquerade",
        "adv_archetype": "apm_telemetry_pipeline_sync",
    },
    {
        "id": "pair_04",
        "benign_id": "doc_006",
        "adv_id": "doc_adv_014",
        "adv_category": "contextual_masquerade",
        "adv_archetype": "soc2_type2_audit_verification",
    },
    {
        "id": "pair_05",
        "benign_id": "doc_007",
        "adv_id": "doc_adv_023",
        "adv_category": "format_escape_injection",
        "adv_archetype": "markdown_code_block_escape",
    },
    {
        "id": "pair_06",
        "benign_id": "doc_008",
        "adv_id": "doc_adv_024",
        "adv_category": "format_escape_injection",
        "adv_archetype": "system_prompt_delimiter_spoofing",
    },
    {
        "id": "pair_07",
        "benign_id": "doc_009",
        "adv_id": "doc_adv_033",
        "adv_category": "advanced_obfuscation",
        "adv_archetype": "multilingual_spanish",
    },
    {
        "id": "pair_08",
        "benign_id": "doc_010",
        "adv_id": "doc_adv_034",
        "adv_category": "advanced_obfuscation",
        "adv_archetype": "leetspeak_homoglyph_encoding",
    },
]

COMPACT_SCENARIO_3_BATCHES: list[dict[str, Any]] = [
    {
        "id": "stress_batch_01",
        "name": "Direct Override Quad",
        "category": "direct_override",
        "doc_ids": ["doc_adv_005", "doc_adv_006", "doc_adv_007", "doc_adv_008"],
    },
    {
        "id": "stress_batch_02",
        "name": "Contextual Masquerade Quad",
        "category": "contextual_masquerade",
        "doc_ids": ["doc_adv_015", "doc_adv_016", "doc_adv_017", "doc_adv_018"],
    },
    {
        "id": "stress_batch_03",
        "name": "Format Escape Quad",
        "category": "format_escape_injection",
        "doc_ids": ["doc_adv_025", "doc_adv_026", "doc_adv_027", "doc_adv_028"],
    },
    {
        "id": "stress_batch_04",
        "name": "Advanced Obfuscation Quad",
        "category": "advanced_obfuscation",
        "doc_ids": ["doc_adv_035", "doc_adv_036", "doc_adv_037", "doc_adv_038"],
    },
    {
        "id": "stress_batch_05",
        "name": "Cross-Category Blend Quad A",
        "category": "cross_category_mixed",
        "doc_ids": ["doc_adv_009", "doc_adv_019", "doc_adv_029", "doc_adv_039"],
    },
    {
        "id": "stress_batch_06",
        "name": "Cross-Category Blend Quad B",
        "category": "cross_category_mixed",
        "doc_ids": ["doc_adv_010", "doc_adv_020", "doc_adv_030", "doc_adv_040"],
    },
]


# Full Exhaustive Suite (71 Runs):
SCENARIO_2_PAIRS: list[dict[str, str]] = [
    {
        "id": "pair_01",
        "benign_id": "doc_001",
        "adv_id": "doc_adv_001",
        "adv_category": "direct_override",
        "adv_archetype": "urgent_cancellation",
    },
    {
        "id": "pair_02",
        "benign_id": "doc_002",
        "adv_id": "doc_adv_005",
        "adv_category": "direct_override",
        "adv_archetype": "emergency_failover_precedence",
    },
    {
        "id": "pair_03",
        "benign_id": "doc_003",
        "adv_id": "doc_adv_010",
        "adv_category": "direct_override",
        "adv_archetype": "priority_zero_escalation",
    },
    {
        "id": "pair_04",
        "benign_id": "doc_004",
        "adv_id": "doc_adv_011",
        "adv_category": "contextual_masquerade",
        "adv_archetype": "statutory_sec_finra_compliance",
    },
    {
        "id": "pair_05",
        "benign_id": "doc_005",
        "adv_id": "doc_adv_014",
        "adv_category": "contextual_masquerade",
        "adv_archetype": "soc2_type2_audit_verification",
    },
    {
        "id": "pair_06",
        "benign_id": "doc_006",
        "adv_id": "doc_adv_018",
        "adv_category": "contextual_masquerade",
        "adv_archetype": "irb_clinical_ethical_oversight",
    },
    {
        "id": "pair_07",
        "benign_id": "doc_007",
        "adv_id": "doc_adv_021",
        "adv_category": "format_escape_injection",
        "adv_archetype": "xml_tag_breakout",
    },
    {
        "id": "pair_08",
        "benign_id": "doc_008",
        "adv_id": "doc_adv_025",
        "adv_category": "format_escape_injection",
        "adv_archetype": "llama_mistral_inst_delimiter",
    },
    {
        "id": "pair_09",
        "benign_id": "doc_009",
        "adv_id": "doc_adv_030",
        "adv_category": "format_escape_injection",
        "adv_archetype": "yaml_frontmatter_k8s_spec",
    },
    {
        "id": "pair_10",
        "benign_id": "doc_010",
        "adv_id": "doc_adv_031",
        "adv_category": "advanced_obfuscation",
        "adv_archetype": "base64_encoded_payload",
    },
    {
        "id": "pair_11",
        "benign_id": "doc_003",
        "adv_id": "doc_adv_033",
        "adv_category": "advanced_obfuscation",
        "adv_archetype": "multilingual_spanish",
    },
    {
        "id": "pair_12",
        "benign_id": "doc_001",
        "adv_id": "doc_adv_038",
        "adv_category": "advanced_obfuscation",
        "adv_archetype": "multi_hop_cross_document_exfil",
    },
]

# Definition of Scenario 3: Multi-Adversarial Stress Batches (8 Batches via Orchestrator)
SCENARIO_3_BATCHES: list[dict[str, Any]] = [
    {
        "id": "stress_batch_01",
        "name": "Direct Override Triad",
        "category": "direct_override",
        "doc_ids": ["doc_adv_002", "doc_adv_004", "doc_adv_007"],
    },
    {
        "id": "stress_batch_02",
        "name": "Contextual Masquerade Triad",
        "category": "contextual_masquerade",
        "doc_ids": ["doc_adv_012", "doc_adv_015", "doc_adv_019"],
    },
    {
        "id": "stress_batch_03",
        "name": "Format Escape Triad",
        "category": "format_escape_injection",
        "doc_ids": ["doc_adv_022", "doc_adv_026", "doc_adv_029"],
    },
    {
        "id": "stress_batch_04",
        "name": "Advanced Obfuscation Triad",
        "category": "advanced_obfuscation",
        "doc_ids": ["doc_adv_032", "doc_adv_034", "doc_adv_037"],
    },
    {
        "id": "stress_batch_05",
        "name": "Cross-Category Quad",
        "category": "cross_category_mixed",
        "doc_ids": ["doc_adv_003", "doc_adv_013", "doc_adv_023", "doc_adv_033"],
    },
    {
        "id": "stress_batch_06",
        "name": "Advanced Evasion Quad",
        "category": "advanced_evasion_mixed",
        "doc_ids": ["doc_adv_008", "doc_adv_016", "doc_adv_028", "doc_adv_040"],
    },
    {
        "id": "stress_batch_07",
        "name": "High-Severity Mixed Triad",
        "category": "high_severity_mixed",
        "doc_ids": ["doc_adv_006", "doc_adv_017", "doc_adv_024"],
    },
    {
        "id": "stress_batch_08",
        "name": "Full Vector Blend Quad",
        "category": "full_vector_blend",
        "doc_ids": ["doc_adv_009", "doc_adv_020", "doc_adv_027", "doc_adv_039"],
    },
]

