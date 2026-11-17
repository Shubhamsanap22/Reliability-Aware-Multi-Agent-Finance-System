"""Explainable multi-factor scoring for capability-compatible agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional

from app.agents.base_agent import BaseAgent


@dataclass(frozen=True)
class SelectionScore:
    """A normalized score and its factor-level explanation."""

    total: float
    factors: Dict[str, float]
    weights_used: Dict[str, float]


class MultiFactorSelectionPolicy:
    """Rank eligible agents while omitting metrics that are not measured.

    The configured weights are initial experimental settings, not learned or
    empirically optimal values. Missing optional metrics are omitted and the
    remaining weights are renormalized for each comparison group.
    """

    DEFAULT_WEIGHTS = {
        "task_relevance": 0.25,
        "reliability": 0.25,
        "analytical_quality": 0.20,
        "cost_efficiency": 0.20,
        "execution_speed": 0.10,
    }

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
    ) -> None:

        self.weights = dict(weights or self.DEFAULT_WEIGHTS)

        if not self.weights or any(
            value < 0 for value in self.weights.values()
        ):
            raise ValueError(
                "Selection weights must be non-negative."
            )

        if sum(self.weights.values()) <= 0:
            raise ValueError(
                "At least one selection weight must be positive."
            )

    def score_group(
        self,
        agents: Iterable[BaseAgent],
        capability: str,
    ) -> Dict[str, SelectionScore]:
        """Score candidates for one requested capability.

        Cost and speed are normalized relative to candidates in this group.

        Capability match is a hard eligibility check performed by the caller.
        Task relevance defaults to 1.0 because the registry currently provides
        capability-level, not semantic query-level, relevance.
        """

        candidates = list(agents)

        if not candidates:
            return {}

        positive_costs = [
            max(1, int(agent.estimated_cost))
            for agent in candidates
        ]

        lowest_cost = min(positive_costs)

        measured_times = [
            float(agent.average_execution_time_seconds)
            for agent in candidates
            if (
                agent.average_execution_time_seconds is not None
                and agent.average_execution_time_seconds > 0
            )
        ]

        fastest_time = (
            min(measured_times)
            if measured_times
            else None
        )

        raw: Dict[str, Dict[str, float]] = {}

        for agent in candidates:

            relevance = agent.capability_relevance.get(
                capability,
                1.0,
            )

            factors = {
                "task_relevance": self._unit_interval(
                    relevance
                ),

                "reliability": self._unit_interval(
                    agent.reliability
                ),

                "cost_efficiency": min(
                    1.0,
                    lowest_cost / max(
                        1,
                        agent.estimated_cost,
                    ),
                ),
            }

            if agent.analytical_quality_score is not None:

                factors["analytical_quality"] = (
                    self._unit_interval(
                        agent.analytical_quality_score
                    )
                )

            if (
                fastest_time is not None
                and agent.average_execution_time_seconds
            ):

                factors["execution_speed"] = min(
                    1.0,
                    fastest_time
                    / float(
                        agent.average_execution_time_seconds
                    ),
                )

            raw[agent.name] = factors

        scores: Dict[str, SelectionScore] = {}

        for name, factors in raw.items():

            available_weights = {
                key: self.weights[key]
                for key in factors
                if (
                    key in self.weights
                    and self.weights[key] > 0
                )
            }

            denominator = sum(
                available_weights.values()
            )

            if denominator <= 0:

                scores[name] = SelectionScore(
                    total=0.0,
                    factors=factors,
                    weights_used={},
                )

                continue

            normalized_weights = {
                key: value / denominator
                for key, value in available_weights.items()
            }

            total = sum(
                factors[key] * normalized_weights[key]
                for key in normalized_weights
            )

            scores[name] = SelectionScore(
                total=round(total, 6),
                factors=factors,
                weights_used=normalized_weights,
            )

        return scores

    @staticmethod
    def _unit_interval(value: float) -> float:
        """Clamp a score to the interval [0, 1]."""

        return max(
            0.0,
            min(1.0, float(value)),
        )