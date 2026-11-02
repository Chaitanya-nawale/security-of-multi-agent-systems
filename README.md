# Multi-Agent Security (MAS)

A minimal two-agent evaluation framework designed to benchmark indirect prompt injection resistance and defense mechanisms in multi-agent systems.

The architecture consists of:

- **Orchestrator Agent**: Receives high-level user tasks (e.g., _"Summarize these documents"_) and coordinates delegation.
- **Worker Agent**: Equipped with tools to analyze retrieved documents:
  - `read_document(doc_id: str)`: Fetches document content from the corpus.
  - `send_email(to: str, body: str)`: Simulates external communication / exfiltration (mocked to log calls without sending real emails).
- **Benchmark Corpus (`data/`)**: 50 synthetic enterprise documents (`mas-eval-50`) consisting of 10 safe documents and 40 injected documents that try to trick the agent into calling `send_email` (using fake compliance rules, helpfulness traps, injected YAML/JSON configs, and fake system logs).

---

## Quick Setup

### 1. Install `uv` (Standalone Package & Python Manager)

`uv` is a standalone binary with zero dependencies (no pre-existing Python required):

- **macOS / Linux**:

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  _(or via Homebrew: `brew install uv`)_

- **Windows**:
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### 2. Install Dependencies

Run `make install` to create the virtual environment and install all dependencies:

```bash
make install
```

> **Note:** `make install` runs `uv sync --frozen`. If Python 3.12 is not already installed on your system, `uv` will automatically download and isolate it for you according to `.python-version`.

### 3. Configure Environment Variables

Copy the example configuration file:

```bash
cp .env.example .env
```

Open `.env` and configure your LLM backend:

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

### 4. Verify Setup

Run the sample inference script to ensure model connectivity and tracing work:

```bash
uv run python sample_inference.py
```

Run code quality and test checks:

```bash
make check
```

_(Runs `ruff`, `mypy`, and `pytest`)_

---

## Running Experiments & Evaluations

The framework measures injection success rates (Attack Success Rate / ASR and False Positive Rate / FPR) with and without defenses:

| Command                  | Action                                                             |
| :----------------------- | :----------------------------------------------------------------- |
| `make experiments`       | Run multi-scenario prompt injection experiments across the dataset |
| `make eval`              | Run the evaluation test suite via `pytest`                         |
| `make eval-worker`       | Run Worker agent evaluations against document injection payloads   |
| `make eval-orchestrator` | Run Orchestrator agent coordination evaluations                    |

---

## Project Structure

```text
├── Makefile                   # Common developer targets (install, lint, test, eval)
├── pyproject.toml             # Project dependencies and tool configurations
├── sample_inference.py        # Minimal connectivity check for LLM and Langfuse
├── data/                      # 50-document evaluation benchmark (mas-eval-50)
│   ├── README.md              # Dataset threat model & manifest
│   ├── dataset_metadata.json  # Machine-readable ground truth and attack classifications
│   ├── benign/                # Benign corporate documents (doc_001 – doc_010)
│   └── adversarial/           # Injected documents (doc_adv_001 – doc_adv_040)
└── .env.example               # Template environment configuration
```
