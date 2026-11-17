from typing import Dict, List, Type

from app.agents.base_agent import BaseAgent
from app.agents.financial_planning_agent import FinancialPlanningAgent
from app.agents.fundamental_analysis_agent import FundamentalAnalysisAgent
from app.agents.investment_agent import InvestmentAgent
from app.agents.market_research_agent import MarketResearchAgent
from app.agents.portfolio_agent import PortfolioAgent
from app.agents.risk_agent import RiskAgent
from app.agents.sentiment_analysis_agent import SentimentAnalysisAgent
from app.agents.technical_analysis_agent import TechnicalAnalysisAgent

from app.models.schemas import TaskRequirement
from app.team.selection_policy import MultiFactorSelectionPolicy


class TeamBuilder:
    """Build a deduplicated, budget-aware team using multi-factor ranking."""

    def __init__(
        self,
        registry=None,
        budget_manager=None,
        selection_policy: MultiFactorSelectionPolicy | None = None,
        max_team_size: int = 8,
        max_agents_per_capability: int = 2,
        minimum_relative_score: float = 0.80,
    ) -> None:

        if max_team_size < 1 or max_agents_per_capability < 1:

            raise ValueError(
                "Team-size limits must be positive."
            )

        if not 0 <= minimum_relative_score <= 1:

            raise ValueError(
                "minimum_relative_score must be between 0 and 1."
            )

        self.registry = registry
        self.budget_manager = budget_manager

        self.selection_policy = (
            selection_policy
            or MultiFactorSelectionPolicy()
        )

        self.max_team_size = max_team_size

        self.max_agents_per_capability = (
            max_agents_per_capability
        )

        self.minimum_relative_score = (
            minimum_relative_score
        )

        self.capability_map: Dict[str, Type[BaseAgent]] = {

            "investment_analysis": InvestmentAgent,

            "risk_analysis": RiskAgent,

            "portfolio_management": PortfolioAgent,

            "market_research": MarketResearchAgent,

            "fundamental_analysis": FundamentalAnalysisAgent,

            "technical_analysis": TechnicalAnalysisAgent,

            "sentiment_analysis": SentimentAnalysisAgent,

            "financial_planning": FinancialPlanningAgent,
        }

    def _candidates_for_capability(
        self,
        capability: str,
    ) -> List[BaseAgent]:
        """Get candidate agents for a requested capability."""

        if self.registry is not None:

            return self.registry.get_agents_for_capability(
                capability
            )

        agent_class = self.capability_map.get(
            capability
        )

        return (
            [agent_class()]
            if agent_class is not None
            else []
        )

    def _available_budget(self) -> float:
        """Get the currently available budget."""

        if self.budget_manager is None:

            return float("inf")

        state = getattr(
            self.budget_manager,
            "state",
            None,
        )

        if (
            state is not None
            and hasattr(state, "available_budget")
        ):

            return float(
                state.available_budget
            )

        return float(
            self.budget_manager.remaining_budget
        )

    def build_team(
        self,
        requirement: TaskRequirement,
    ) -> List[BaseAgent]:
        """
        Select complementary agents using multi-factor ranking.

        Multiple agents can be selected for the same capability when
        their scores are sufficiently close to the best candidate.

        Selection is constrained by:

        - Maximum team size
        - Maximum agents per capability
        - Available estimated budget
        - Minimum relative score threshold
        """

        capabilities = list(
            dict.fromkeys(
                requirement.required_capabilities
            )
        )

        selected: List[BaseAgent] = []

        selected_names: set[str] = set()

        spent_estimated_budget = 0

        for capability in capabilities:

            candidates = self._candidates_for_capability(
                capability
            )

            # Remove duplicate and invalid candidates.
            candidates = [
                agent
                for agent in candidates
                if (
                    agent.name not in selected_names
                    and agent.estimated_cost >= 0
                )
            ]

            if not candidates:

                continue

            if len(selected) >= self.max_team_size:

                break

            # Calculate multi-factor scores.
            scores = self.selection_policy.score_group(
                candidates,
                capability,
            )

            # Rank candidates from highest score to lowest.
            ranked = sorted(
                candidates,
                key=lambda agent: scores[agent.name].total,
                reverse=True,
            )

            best_score = scores[
                ranked[0].name
            ].total

            selected_for_capability = 0

            for agent in ranked:

                if len(selected) >= self.max_team_size:

                    break

                score = scores[agent.name]

                # Additional candidates must be sufficiently close
                # to the best candidate's score.
                if (
                    best_score > 0
                    and score.total
                    < best_score * self.minimum_relative_score
                ):

                    continue

                if (
                    selected_for_capability
                    >= self.max_agents_per_capability
                ):

                    break

                # Check whether the agent can be afforded.
                if (
                    spent_estimated_budget + agent.estimated_cost
                    > self._available_budget()
                ):

                    continue

                # Store selection explanation.
                agent.selection_score = score.total

                agent.selection_score_breakdown = dict(
                    score.factors
                )

                selected.append(agent)

                selected_names.add(
                    agent.name
                )

                spent_estimated_budget += (
                    agent.estimated_cost
                )

                selected_for_capability += 1

        return selected