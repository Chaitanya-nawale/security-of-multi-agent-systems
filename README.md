# Multi-Agent Security (MAS)

A minimal two-agent evaluation framework designed to benchmark indirect prompt injection resistance and defense mechanisms in multi-agent systems.

The architecture consists of:

- **Orchestrator Agent**: Receives high-level user tasks (e.g., _"Summarize these documents"_) and delegates task details to the specialized worker agent via the `delegate_to_worker(task: str)` tool before synthesizing the final response.
- **Worker Agent**: Specialized agent equipped with two tools:
  - `read_document(id: str)`: Fetches document content from the corpus by ID.
  - `send_email(to: str, body: str)`: Simulates external communication / exfiltration (mocked to log calls without sending real emails).
- **Benchmark Corpus (`data/`)**: 50 synthetic enterprise documents (`mas-eval-50`) consisting of 10 safe documents and 40 injected documents that try to trick the agent into calling `send_email` (using fake compliance rules, helpfulness traps, injected YAML/JSON configs, and fake system logs).

---

## Prerequisites & Installation

This project requires:
1. **[`uv`](https://astral.sh/uv/)**: Standalone Python package and environment manager (automatically manages Python 3.12 and `.venv`).
2. **`make` (GNU Make)**: Automates development, testing, and evaluation commands.

---

### Step 1: Install Prerequisites by OS

<details open>
<summary><b>macOS</b></summary>

Install `uv` and ensure `make` is installed (via Xcode Command Line Tools or Homebrew):

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or via Homebrew: brew install uv

# Install make / command line tools
xcode-select --install
# Or via Homebrew: brew install make
```
</details>

<details>
<summary><b>Linux (Ubuntu / Debian / Fedora / Arch)</b></summary>

Install `uv` and GNU Make via your package manager:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install make & build essentials
# Ubuntu / Debian:
sudo apt update && sudo apt install -y build-essential make

# Fedora / RHEL:
sudo dnf install -y make

# Arch Linux:
sudo pacman -S --needed make
```
</details>

<details>
<summary><b>Windows (PowerShell / CMD / WSL)</b></summary>

#### 1. Install `uv`
Run in PowerShell (restart terminal after installation):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. Choose how to run `make`:
- **Option A (Install make on Windows)**:
  ```powershell
  winget install GnuWin32.Make   # or: choco install make / scoop install make
  ```
- **Option B (Use WSL)**: Follow the Linux instructions inside your WSL terminal.
- **Option C (Direct `uv run` commands)**: No `make` required; see the [Make & Command Reference](#make--command-reference) below.
</details>

---

### Step 2: Clone & Setup Environment (All Platforms)

```bash
git clone <repo-url>
cd multi-agent-security

# Copy configuration template
cp .env.example .env          # Windows PowerShell: Copy-Item .env.example .env

# Install locked dependencies (uv creates .venv and fetches Python 3.12 if needed)
make install                  # Windows without make: uv sync --frozen
```

---

## Configuration (`.env`)

Open `.env` and set up your LLM backend:

```ini
# OpenAI-compatible LLM endpoint
OPENAI_API_BASE="http://localhost:8000/v1"   # vLLM: :8000/v1, Ollama: :11434/v1, or OpenAI: https://api.openai.com/v1
OPENAI_API_KEY="EMPTY"                     # API key (use "EMPTY" for local instances without auth)
LLM_MODEL="Qwen 3.8 27B"                   # Model name hosted on the endpoint

# (Optional) Langfuse Tracing
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_BASE_URL="https://cloud.langfuse.com"
```

> **Note on Virtual Environments:** `uv run` automatically detects and uses the local `.venv/` virtual environment. You do not need to manually activate the virtual environment (`source .venv/bin/activate` or `.\.venv\Scripts\Activate.ps1`), though you can if desired.

---

## Verifying Setup

1. **Verify LLM Connectivity & Tracing**:
   ```bash
   uv run python sample_inference.py
   ```

2. **Run End-to-End Multi-Agent Demo** (Orchestrator + Worker):
   ```bash
   uv run python sample_agents_run.py
   ```

3. **Run Quality & Offline Test Suite**:
   ```bash
   make check
   ```
   *(Or on Windows without make: `uv run ruff check . && uv run mypy . && uv run pytest`)*

---

## Make & Command Reference

All workflow tasks are defined in [`Makefile`](Makefile). If you have `make` installed, use the short commands. If you are on Windows without `make`, use the direct `uv` equivalents:

| Make Command | Windows / Direct `uv` Equivalent | Action |
| :--- | :--- | :--- |
| `make install` | `uv sync --frozen` | Create `.venv` and install exact pinned dependencies. |
| `make update` | `uv lock --upgrade && uv sync` | Upgrade all dependencies in `uv.lock` and sync. |
| `make check` | `uv run ruff check . && uv run mypy . && uv run pytest` | Run linter (`ruff`), type checker (`mypy`), and offline test suite (`pytest`). |
| `make lint` | `uv run ruff check .` | Run Ruff linter across all source files and tests. |
| `make format` | `uv run ruff format . && uv run ruff check --fix .` | Auto-format codebase and apply safe fixes with Ruff. |
| `make typecheck` | `uv run mypy .` | Run static type analysis using Mypy. |
| `make test` | `uv run pytest` | Run deterministic offline unit tests (`pytest tests/`, no live LLM needed). |
| `make eval` | `uv run pytest evals/` | Run live multi-agent evaluations against mock tools (`pytest evals/`). |
| `make eval-worker` | `uv run python -m evals.test_eval_worker` | Run Worker Agent evaluations directly. |
| `make eval-orchestrator` | `uv run python -m evals.test_eval_orchestrator` | Run Orchestrator Agent evaluations directly. |
| `make experiments` | `uv run python -m experiments.run_experiments` | Run the full prompt injection benchmark across the dataset. |

### Running Experiments with Arguments

By default, `make experiments` runs the **compact, high-pressure stress suite** (24 balanced single- and multi-document tests covering all 50 documents). You can customize runs with CLI arguments:

```bash
# Run default compact suite (24 runs covering all 50 benchmark documents)
uv run python -m experiments.run_experiments

# Run full exhaustive suite (71 runs)
uv run python -m experiments.run_experiments --suite full

# Run only Scenario 1 (Worker direct ingestion boundary)
uv run python -m experiments.run_experiments --scenario scenario_1

# Run with a limit for quick verification
uv run python -m experiments.run_experiments --scenario scenario_1 --limit 5

# Run Scenario 2 (Cross-context contamination pairs)
uv run python -m experiments.run_experiments --scenario scenario_2

# Run Scenario 3 (Multi-adversarial stress quads)
uv run python -m experiments.run_experiments --scenario scenario_3
```

Generated reports and evaluation trajectories are saved directly into [`experiments/results/`](experiments/results/).

---

## Project Structure

```text
├── Makefile                   # Developer automation targets (install, lint, test, eval)
├── pyproject.toml             # Project metadata, dependencies, and tool settings
├── uv.lock                    # Deterministic, cross-platform dependency lockfile
├── sample_inference.py        # Minimal connectivity check for LLM and Langfuse
├── sample_agents_run.py       # End-to-end two-agent execution demonstration
├── src/                       # Core library code
│   ├── agents/                # Orchestrator and Worker agent implementations (LangGraph)
│   │   ├── orchestrator.py    # Two-agent orchestrator with delegation tool
│   │   └── worker.py          # Specialized worker with document and email tools
│   └── utils/                 # Shared utilities
│       ├── tools.py           # read_document, send_email, and OrchestratorTools
│       ├── telemetry.py       # Langfuse tracing probe and lifecycle management
│       └── logger.py          # Standardized logging configuration
├── experiments/               # Benchmark experiment runner and evaluation scenarios
│   ├── run_experiments.py     # CLI experiment runner
│   ├── scenarios.py           # Scenario definitions (Worker isolation, Mixed, Stress)
│   ├── classifier.py          # Trajectory outcome classification
│   ├── reporting.py           # Summary and markdown reporting generator
│   └── CRITERIA.md            # Benchmark criteria and evaluation standards
├── tests/                     # Deterministic offline unit tests (no live LLM required)
├── evals/                     # Live evaluation benchmarks and mock-tool test suites
├── data/                      # 50-document evaluation benchmark (mas-eval-50)
│   ├── README.md              # Dataset threat model & manifest
│   ├── dataset_metadata.json  # Machine-readable ground truth and attack classifications
│   ├── benign/                # Benign corporate documents (doc_001 – doc_010)
│   └── adversarial/           # Injected documents (doc_adv_001 – doc_adv_040)
└── .env.example               # Template environment configuration
```
