from app.analysis.query_analyzer import QueryAnalyzer
from app.budget.budget_manager import BudgetManager
from app.data.api_provider import APIDataProvider
from app.data.data_loader import DataLoader
from app.data.data_provider import LocalDataProvider
from app.data.fallback_provider import FallbackDataProvider
from app.execution.executor import Executor
from app.handling.failure_handler import FailureHandler
from app.monitoring.reliability_monitor import ReliabilityMonitor
from app.orchestration.orchestrator import Orchestrator
from app.registry.capability_registry import CapabilityRegistry
from app.team.team_builder import TeamBuilder


def create_application() -> Orchestrator:
    """Construct and connect all application components."""
    data_loader = DataLoader()

    local_provider = LocalDataProvider(
        data_loader=data_loader
    )

    api_provider = APIDataProvider(
        data_loader=data_loader
    )

    fallback_provider = FallbackDataProvider(
        local_provider=local_provider,
        api_provider=api_provider,
    )

    registry = CapabilityRegistry(
        data_provider=fallback_provider,
        local_file_path="data/market_data.csv",
    )

    team_builder = TeamBuilder(
        registry=registry
    )

    analyzer = QueryAnalyzer()

    budget_manager = BudgetManager(
        global_budget=5000
    )

    failure_handler = FailureHandler()

    executor = Executor(
        budget_manager=budget_manager,
        failure_handler=failure_handler,
    )

    reliability_monitor = ReliabilityMonitor()

    return Orchestrator(
        analyzer=analyzer,
        team_builder=team_builder,
        executor=executor,
        reliability_monitor=reliability_monitor,
    )


def main() -> None:
    """Run the financial multi-agent application from the terminal."""
    orchestrator = create_application()

    query = input("Enter your financial query: ").strip()

    if not query:
        print("Please enter a non-empty query.")
        return

    results = orchestrator.run(query)

    print("\n===== RESULTS =====")

    if not results:
        print("No agents were selected for this query.")
        return

    for result in results:
        print(f"\nAgent: {result.agent_name}")
        print(f"Status: {result.status.value}")
        print(f"Budget allocated: {result.allocated_budget}")
        print(f"Budget used: {result.used_budget}")

        if result.output:
            print(f"Output:\n{result.output}")

        if result.failure_reason:
            print(f"Failure: {result.failure_reason}")


if __name__ == "__main__":
    main()