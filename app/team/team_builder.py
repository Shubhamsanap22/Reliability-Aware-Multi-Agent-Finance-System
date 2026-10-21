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


class TeamBuilder:
    """Build a deduplicated team and inject dependencies through the registry."""

    def __init__(self, registry=None) -> None:
        self.registry = registry

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

    def build_team(self, requirement: TaskRequirement) -> List[BaseAgent]:
        """Create one agent per requested capability, without duplicates."""
        capabilities = list(
            dict.fromkeys(requirement.required_capabilities)
        )

        # Use the registry whenever one is configured so that agents
        # receive their data providers and other dependencies.
        if self.registry is not None:
            return self.registry.get_agents_for_capabilities(
                capabilities
            )

        # Standalone mode: create agents without injected dependencies.
        team: List[BaseAgent] = []
        seen: set[type[BaseAgent]] = set()

        for capability in capabilities:
            agent_class = self.capability_map.get(capability)

            if agent_class is None or agent_class in seen:
                continue

            team.append(agent_class())
            seen.add(agent_class)

        return team