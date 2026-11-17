
# Reliability-Aware Multi-Agent Finance System

<p align="center">
  <strong>A Reliability-Aware Dynamic Multi-Agent System for Financial Decision Support</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Project-M.Tech%20Research-blue" alt="Project: M.Tech Research" />
  <img src="https://img.shields.io/badge/Status-Active%20Development-orange" alt="Status: Active Development" />
  <img src="https://img.shields.io/badge/Python-3.10-blue" alt="Python 3.10" />
  <img src="https://img.shields.io/badge/Testing-Pytest-green" alt="Testing: Pytest" />
</p>

<p align="center">
  <a href="https://github.com/Shubhamsanap22">GitHub Profile</a> |
  <a href="https://github.com/Shubhamsanap22/Reliability-Aware-Multi-Agent-Finance-System">Repository</a>
</p>

---

## Overview

The Reliability-Aware Multi-Agent Finance System is an experimental multi-agent decision-support framework designed to coordinate specialized agents for financial analysis and investment-related tasks.

The system dynamically analyzes user requirements, identifies the capabilities needed to complete a task, selects suitable agents, manages execution budgets, monitors reliability, and combines agent outputs into consolidated results.

Unlike a static multi-agent workflow, the framework incorporates reliability-aware agent selection, execution monitoring, fallback handling, historical tracking, and performance analytics.

This project is being developed as an M.Tech research project in Data Science at COEP Technological University.

## Problem Statement

Financial decision-support tasks often require multiple analytical capabilities, such as investment analysis, risk assessment, and portfolio management.

A fixed execution workflow may select unsuitable agents, consume unnecessary resources, or fail when an individual agent produces an unsuccessful result.

This project explores a dynamic coordination approach in which agent selection and execution are influenced by task requirements, reliability estimates, resource constraints, and observed performance.

## Objectives

- Develop a dynamic multi-agent architecture for financial decision support.
- Analyze user queries and identify the required capabilities.
- Select agents using capability compatibility and weighted scoring.
- Incorporate reliability-aware selection and fallback mechanisms.
- Monitor execution cost, token usage, and execution time.
- Aggregate outputs from multiple agents.
- Maintain execution history for analysis.
- Evaluate system behavior through automated tests and benchmark experiments.

## System Architecture

The system follows a modular architecture with separate components for query analysis, team selection, execution, monitoring, and result aggregation.

```text
                         USER QUERY
                              |
                              v
                       QUERY ANALYZER
                              |
                              v
                     CAPABILITY DETECTION
                              |
                              v
                        TEAM BUILDER
                              |
                              v
                    MULTI-FACTOR SELECTION
                              |
                              v
                       BUDGET MANAGER
                              |
                              v
                          EXECUTOR
                              |
                 +------------+------------+
                 |            |            |
                 v            v            v
             INVESTMENT      RISK       PORTFOLIO
               AGENT         AGENT        AGENT
                 |            |            |
                 +------------+------------+
                              |
                              v
                    RELIABILITY MONITOR
                              |
                              v
                      FAILURE HANDLER
                              |
                              v
                     RESULT AGGREGATOR
                              |
                              v
                    CONSOLIDATED REPORT
                              |
                              v
                         USER OUTPUT
```

## Core Components

| Component             | Responsibility                                       |
| --------------------- | ---------------------------------------------------- |
| Query Analyzer        | Extracts task requirements and required capabilities |
| Capability Registry   | Maps capabilities to available agents                |
| Team Builder          | Constructs a suitable team of agents                 |
| Selection Policy      | Ranks eligible agents using weighted scoring         |
| Budget Manager        | Tracks and manages execution resource constraints    |
| Executor              | Coordinates agent execution                          |
| Reliability Monitor   | Tracks agent reliability observations                |
| Failure Handler       | Handles unsuccessful execution and fallback behavior |
| Result Aggregator     | Combines agent outputs                               |
| History Store         | Persists execution history                           |
| Performance Analytics | Analyzes execution and performance metrics           |
| Consolidated Report   | Prepares structured final results                    |
| API Routes            | Exposes backend functionality through API endpoints  |

## Specialized Agents

The framework supports specialized agents for different financial capabilities.

### 1. Investment Agent

Responsible for investment-related analysis and financial task execution.

### 2. Risk Agent

Responsible for risk-oriented analysis and evaluation.

### 3. Portfolio Agent

Responsible for portfolio management and related analytical tasks.

The capability registry maps requested capabilities to eligible agents. The team builder then evaluates the available candidates before constructing the execution team.

## Multi-Factor Agent Selection

The team builder uses capability compatibility as an eligibility requirement and ranks candidates using an explainable weighted score.

### Initial Scoring Weights

The initial configured weights are experimental defaults, not empirically optimized.

| Factor             | Weight |
| ------------------ | -----: |
| Task relevance     |   0.25 |
| Reliability        |   0.25 |
| Analytical quality |   0.20 |
| Cost efficiency    |   0.20 |
| Execution speed    |   0.10 |

Quality and execution-speed factors are omitted until measured values are available. Remaining active weights are renormalized.

Task relevance currently represents capability-level compatibility, not semantic query matching.

Cost efficiency and execution speed are normalized relative to candidates for the same capability.

### Team Selection Policy

By default, the team builder:

- Selects up to two agents per requested capability.
- Considers candidates whose scores are at least 80% of the best candidate's score for that capability.
- Applies a maximum team size of eight agents.

These are configurable experimental parameters, not claimed optimal values.

### Selection Metadata

Each selected agent receives:

- `selection_score`
- `selection_score_breakdown`

Agent quality and latency metadata default to `None` and must be populated only from measured observations.

## Reliability and Failure Handling

The framework incorporates reliability-aware execution to address unsuccessful agent responses.

Key mechanisms include:

- Reliability tracking for agent execution.
- Monitoring of execution outcomes.
- Failure detection and handling.
- Fallback execution support.
- Execution history for later analysis.

The reliability mechanism is designed to support informed agent selection and improve the robustness of multi-agent coordination.

## Budget and Resource Management

The budget management component tracks execution resource consumption and enforces configured constraints.

The system is designed to monitor:

- Estimated execution cost.
- Token requirements.
- Resource allocation.
- Budget consumption.
- Execution outcomes.

These mechanisms help evaluate the relationship between agent selection, resource utilization, and execution performance.

## Result Aggregation and Reporting

Multiple agents may contribute outputs to a single financial task.

The result aggregation component combines available agent results into a consolidated response.

The reporting component prepares structured outputs for presentation and further analysis.

## Execution History and Performance Analytics

The system maintains execution records to support performance evaluation.

Available functionality includes:

- Historical execution tracking.
- Execution outcome recording.
- Performance summaries.
- Agent-level monitoring.
- Analytical metrics for comparing executions.

Execution history is also intended to support future reliability and selection-policy experiments.

## Frontend and API

The project includes a web-based frontend and a Python backend API.

### Frontend

The frontend is implemented using:

- HTML
- CSS
- JavaScript

### Backend

The backend provides API routes for interacting with the multi-agent framework and coordinating execution.

The API entry point is:

```text
api_server.py
```

The frontend files are located in:

```text
frontend/
```

## Technology Stack

| Category               | Technologies          |
| ---------------------- | --------------------- |
| Programming Language   | Python 3.10           |
| Environment Management | uv                    |
| Testing                | Pytest                |
| Backend                | Python API            |
| Frontend               | HTML, CSS, JavaScript |
| Data Processing        | Pandas                |
| Data Storage           | SQLite                |
| Version Control        | Git, GitHub           |

## Project Structure

```text
financial_multi_agent/
│
├── app/
│   ├── agents/
│   │   └── base_agent.py
│   │
│   ├── aggregation/
│   │   └── result_aggregator.py
│   │
│   ├── analysis/
│   │   └── query_analyzer.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   ├── execution/
│   │   ├── executor.py
│   │   └── history_store.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   ├── monitoring/
│   │   └── performance_analytics.py
│   │
│   ├── orchestration/
│   │   └── orchestrator.py
│   │
│   ├── reporting/
│   │   └── consolidated_report.py
│   │
│   └── team/
│       ├── selection_policy.py
│       └── team_builder.py
│
├── data/
│   └── market_data.csv
│
├── experiments/
│   ├── llm_benchmark.py
│   ├── llm_benchmark_results.json
│   ├── mistral_benchmark.py
│   └── mistral_benchmark_results.json
│
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── style.css
│
├── tests/
│
├── api_server.py
├── main.py
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

## Installation and Setup

### Prerequisites

- Python 3.10
- Git
- uv package manager

### 1. Clone the Repository

```bash
git clone https://github.com/Shubhamsanap22/Reliability-Aware-Multi-Agent-Finance-System.git
```

### 2. Navigate to the Project

```bash
cd Reliability-Aware-Multi-Agent-Finance-System
```

### 3. Create the Virtual Environment

```bash
uv venv
```

### 4. Install Dependencies

```bash
uv sync
```

### 5. Run the Application

The main application entry point is:

```bash
uv run python main.py
```

The API entry point is:

```bash
uv run python api_server.py
```

Refer to the application configuration and API routes for the available execution options.

## Run Tests

Run the complete automated test suite:

```bash
uv run pytest -q
```

Run tests with detailed output:

```bash
uv run pytest -v
```

The project has previously completed a local test run with **349 passing tests**. This is a recorded development result, not a guarantee that every environment or future version will produce the same result.

## Research Evaluation

The project includes experimental benchmark scripts for evaluating query analysis and model behavior.

Current benchmark artifacts include:

- `experiments/llm_benchmark.py`
- `experiments/llm_benchmark_results.json`
- `experiments/mistral_benchmark.py`
- `experiments/mistral_benchmark_results.json`

These experiments provide an initial basis for evaluating query interpretation, capability identification, structured output validity, and model latency.

Benchmark results should be interpreted within their specific experimental scope. Query-analysis accuracy does not directly establish the reliability or accuracy of the complete multi-agent financial decision-support system.

Further evaluation will investigate:

- Agent selection effectiveness.
- Reliability under agent failures.
- Budget utilization.
- Execution latency.
- Fallback effectiveness.
- Result aggregation quality.
- Performance across different financial task types.

## Current Development Status

The project is under active research and development.

Implemented areas include:

- Modular multi-agent architecture.
- Query analysis and capability detection.
- Multi-factor agent selection.
- Budget-aware execution.
- Reliability monitoring and failure handling.
- Result aggregation and reporting.
- Execution history and performance analytics.
- Backend API and web frontend.
- Automated tests and benchmark experiments.

Further experimental validation and refinement are ongoing.

## Future Scope

- Expand financial datasets and supported financial instruments.
- Improve semantic task-to-agent matching.
- Introduce adaptive agent selection based on measured performance.
- Improve dynamic budget allocation.
- Evaluate reliability under different failure scenarios.
- Integrate more specialized financial agents.
- Conduct comparative experiments against baseline selection strategies.
- Develop stronger quantitative evaluation for research publication.

## Disclaimer

This project is an academic research and experimental decision-support system.

It is not a certified financial advisory platform and does not provide guaranteed investment returns. Outputs should not be treated as personalized financial advice or used as the sole basis for investment decisions.

## Author

**Shubham Sanap**

M.Tech Data Science
COEP Technological University

- GitHub: [Shubhamsanap22](https://github.com/Shubhamsanap22)

---

\<p align="center">
&#x20; \<strong>Reliability-Aware Multi-Agent Finance System\</strong>
&#x20; \<br/>
&#x20; Academic Research Project | 2026
\</p>
