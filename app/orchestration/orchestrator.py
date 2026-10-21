from typing import List

from app.analysis.query_analyzer import QueryAnalyzer
from app.execution.executor import Executor
from app.models.schemas import AgentState
from app.monitoring.reliability_monitor import ReliabilityMonitor
from app.team.team_builder import TeamBuilder


class Orchestrator:
    """Coordinate query analysis, agent selection, execution and monitoring."""

    def __init__(
        self,
        analyzer: QueryAnalyzer,
        team_builder: TeamBuilder,
        executor: Executor,
        reliability_monitor: ReliabilityMonitor,
    ) -> None:
        self.analyzer = analyzer
        self.team_builder = team_builder
        self.executor = executor
        self.reliability_monitor = reliability_monitor

    def run(self, query: str) -> List[AgentState]:
        """Run the complete multi-agent workflow."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string.")

        requirement = self.analyzer.analyze(query.strip())

        team = self.team_builder.build_team(requirement)

        if not team:
            return []

        results = self.executor.run_agents_with_fallback(
            agents=team,
            query=requirement.query,
            requirement=requirement,
        )

        agents_by_name = {
            agent.name: agent
            for agent in team
        }

        for result in results:
            agent = agents_by_name.get(result.agent_name)

            if agent is not None:
                self.reliability_monitor.update(
                    agent,
                    result.status,
                )

        return results