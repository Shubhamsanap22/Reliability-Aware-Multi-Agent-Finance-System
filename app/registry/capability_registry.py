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
from app.data.fallback_provider import FallbackDataProvider


class CapabilityRegistry:
    """Maps capabilities to agent classes and injects dependencies."""

    def __init__(
        self,
        data_provider: FallbackDataProvider | None = None,
        local_file_path: str | None = None,
    ) -> None:
        self.data_provider = data_provider
        self.local_file_path = local_file_path

        self._registry: Dict[str, List[Type[BaseAgent]]] = {
            "investment_analysis": [
                InvestmentAgent,
                PortfolioAgent,
            ],
            "risk_analysis": [RiskAgent],
            "portfolio_management": [PortfolioAgent],
            "market_research": [MarketResearchAgent],
            "fundamental_analysis": [FundamentalAnalysisAgent],
            "technical_analysis": [TechnicalAnalysisAgent],
            "sentiment_analysis": [SentimentAnalysisAgent],
            "financial_planning": [FinancialPlanningAgent],
        }

    def _create_agent(
        self,
        agent_class: Type[BaseAgent],
    ) -> BaseAgent:
        """Create an agent with the dependencies it supports."""

        market_data_agents = {
            RiskAgent,
            MarketResearchAgent,
            InvestmentAgent,
            PortfolioAgent,
            TechnicalAnalysisAgent,
        }

        if agent_class in market_data_agents:
            return agent_class(
                data_provider=self.data_provider,
                local_file_path=self.local_file_path,
            )

        return agent_class()

    def get_agents_for_capability(
        self,
        capability: str,
    ) -> List[BaseAgent]:
        """Return instances registered for one capability."""

        agent_classes = self._registry.get(capability, [])

        return [
            self._create_agent(agent_class)
            for agent_class in agent_classes
        ]

    def get_agents_for_capabilities(
        self,
        capabilities: List[str],
    ) -> List[BaseAgent]:
        """Return unique agent instances for multiple capabilities."""

        agents: List[BaseAgent] = []
        agent_names: set[str] = set()

        for capability in dict.fromkeys(capabilities):
            for agent in self.get_agents_for_capability(capability):
                if agent.name not in agent_names:
                    agents.append(agent)
                    agent_names.add(agent.name)

        return agents