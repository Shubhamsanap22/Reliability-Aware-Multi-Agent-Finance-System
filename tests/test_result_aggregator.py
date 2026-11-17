
from app.aggregation.result_aggregator import ResultAggregator
from app.models.schemas import AgentState, AgentStatus


def test_aggregator_summarizes_successful_results():
    results = [
        AgentState(
            agent_name="Risk Agent",
            status=AgentStatus.COMPLETED,
            output="Risk score: 0.3",
            reliability=0.9,
            allocated_budget=100,
            used_budget=60,
        ),
        AgentState(
            agent_name="Investment Agent",
            status=AgentStatus.COMPLETED,
            output="Review earnings and valuation.",
            reliability=0.8,
            allocated_budget=200,
            used_budget=120,
        ),
    ]

    report = ResultAggregator().aggregate(results)

    assert report.overall_status == "completed"
    assert report.total_agents == 2
    assert report.completed_agents == 2
    assert report.failed_agents == 0
    assert len(report.findings) == 2
    assert report.allocated_budget == 300
    assert report.used_budget == 180
    assert "All 2 selected agent(s) completed" in report.executive_summary


def test_aggregator_reports_partial_failures():
    results = [
        AgentState(
            agent_name="Risk Agent",
            status=AgentStatus.COMPLETED,
            output="Risk review completed.",
        ),
        AgentState(
            agent_name="Fundamental Analysis Agent",
            status=AgentStatus.FAILED,
            failure_reason="No fundamentals data available.",
        ),
    ]

    report = ResultAggregator().aggregate(results)

    assert report.overall_status == "partially_completed"
    assert report.completed_agents == 1
    assert report.failed_agents == 1
    assert any(
        "No fundamentals data available" in item
        for item in report.limitations
    )
    assert "Review the limitations" in report.executive_summary


def test_aggregator_does_not_treat_replaced_as_completed():
    report = ResultAggregator().aggregate([
        AgentState(
            agent_name="Portfolio Agent",
            status=AgentStatus.REPLACED,
            output="",
        )
    ])

    assert report.overall_status == "failed"
    assert report.incomplete_agents == 1
    assert report.completed_agents == 0
    assert report.limitations


def test_aggregator_handles_empty_results():
    report = ResultAggregator().aggregate([])

    assert report.overall_status == "no_results"
    assert report.total_agents == 0
    assert report.findings == ()
    assert "No agents were selected" in report.executive_summary


def test_aggregator_flags_completed_agent_without_output():
    report = ResultAggregator().aggregate([
        AgentState(
            agent_name="Market Research Agent",
            status=AgentStatus.COMPLETED,
            output=None,
        )
    ])

    assert report.overall_status == "completed"
    assert not report.findings
    assert any(
        "returned no output" in item
        for item in report.limitations
    )
