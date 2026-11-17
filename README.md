## Multi-factor Agent Selection

The team builder uses capability compatibility as an eligibility
requirement and then ranks candidates using an explainable weighted score.

Initial configured weights (experimental defaults, not empirically optimized):

| Factor | Weight |
|---|---:|
| Task relevance | 0.25 |
| Reliability | 0.25 |
| Analytical quality | 0.20 |
| Cost efficiency | 0.20 |
| Execution speed | 0.10 |

Quality and execution-speed factors are omitted until measured values
are available. Remaining active weights are renormalized.

Task relevance currently represents capability-level compatibility,
not semantic query matching.

Cost efficiency and execution speed are normalized relative to
candidates for the same capability.

By default, the team builder selects up to two agents per requested
capability when each candidate's score is at least 80% of the best
candidate's score.

It also applies a maximum team size of eight.

These are configurable experimental parameters, not claimed optimal values.

Each selected agent receives:

- selection_score
- selection_score_breakdown

Agent quality and latency metadata default to None and must be
populated only from measured observations.

## Run Tests

```bash
uv run pytest -q