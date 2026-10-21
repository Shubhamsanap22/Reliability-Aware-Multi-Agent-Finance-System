from app.agents.base_agent import BaseAgent
from app.calculations.financial_planning_metrics import (
    calculate_annual_investment,
    calculate_future_value,
    calculate_planning_score,
    calculate_required_annual_return,
    calculate_risk_adjusted_return,
    classify_planning_suitability,
)
from app.models.schemas import AgentState, AgentStatus


class FinancialPlanningAgent(BaseAgent):
    """Perform goal-based financial planning calculations."""

    def __init__(self) -> None:
        super().__init__(
            name="Financial Planning Agent",
            reliability=0.90,
            estimated_cost=700,
        )

    def execute(
        self,
        query: str,
        budget: int,
        initial_amount: float | None = None,
        target_amount: float | None = None,
        annual_return: float | None = None,
        years: int | None = None,
        risk_level: str = "moderate",
    ) -> AgentState:
        required_budget = 500

        if budget < required_budget:
            return self._failed(budget, "Insufficient budget.")

        (
            initial_amount,
            target_amount,
            annual_return,
            years,
            risk_level,
        ) = self._get_structured_parameters(
            initial_amount=initial_amount,
            target_amount=target_amount,
            annual_return=annual_return,
            years=years,
            risk_level=risk_level,
        )

        if initial_amount is None:
            return self._failed(
                budget,
                "Initial investment amount is required.",
            )

        if target_amount is None:
            return self._failed(
                budget,
                "Target amount is required.",
            )

        if years is None:
            return self._failed(
                budget,
                "Investment time horizon is required.",
            )

        try:
            required_return = calculate_required_annual_return(
                initial_amount=initial_amount,
                target_amount=target_amount,
                years=years,
            )

            expected_return = (
                annual_return
                if annual_return is not None
                else required_return
            )

            planning_score = calculate_planning_score(
                expected_return=expected_return,
                risk_level=risk_level,
                time_horizon=years,
            )

            suitability = classify_planning_suitability(
                planning_score
            )

            required_annual_investment = None

            if annual_return is not None:
                required_annual_investment = calculate_annual_investment(
                    target_amount=target_amount,
                    annual_return=annual_return,
                    years=years,
                    initial_amount=initial_amount,
                )

            risk_adjusted_return = calculate_risk_adjusted_return(
                expected_return=expected_return,
                risk_level=risk_level,
            )

            future_value = None

            if annual_return is not None:
                future_value = calculate_future_value(
                    initial_amount=initial_amount,
                    annual_return=annual_return,
                    years=years,
                )

        except (ValueError, ZeroDivisionError) as error:
            return self._failed(budget, str(error))

        output = self._build_output(
            initial_amount=initial_amount,
            target_amount=target_amount,
            years=years,
            risk_level=risk_level,
            required_return=required_return,
            annual_return=annual_return,
            future_value=future_value,
            required_annual_investment=required_annual_investment,
            risk_adjusted_return=risk_adjusted_return,
            planning_score=planning_score,
            suitability=suitability,
        )

        return AgentState(
            agent_name=self.name,
            reliability=self.reliability,
            allocated_budget=budget,
            used_budget=required_budget,
            status=AgentStatus.COMPLETED,
            output=output,
        )

    def _failed(self, budget: int, reason: str) -> AgentState:
        return AgentState(
            agent_name=self.name,
            reliability=self.reliability,
            allocated_budget=budget,
            used_budget=0,
            status=AgentStatus.FAILED,
            failure_reason=reason,
        )

    def _get_structured_parameters(
        self,
        initial_amount: float | None,
        target_amount: float | None,
        annual_return: float | None,
        years: int | None,
        risk_level: str,
    ):
        """Prefer structured task values over direct-call defaults."""
        if self.task_requirement is not None:
            requirement = self.task_requirement

            if requirement.initial_amount is not None:
                initial_amount = requirement.initial_amount

            if requirement.target_amount is not None:
                target_amount = requirement.target_amount

            if requirement.annual_return is not None:
                annual_return = requirement.annual_return

            if requirement.years is not None:
                years = requirement.years

            if requirement.risk_preference:
                risk_level = requirement.risk_preference

        risk_level = risk_level.strip().lower()

        if risk_level == "medium":
            risk_level = "moderate"

        return (
            initial_amount,
            target_amount,
            annual_return,
            years,
            risk_level,
        )

    @staticmethod
    def _build_output(
        initial_amount: float,
        target_amount: float,
        years: int,
        risk_level: str,
        required_return: float,
        annual_return: float | None,
        future_value: float | None,
        required_annual_investment: float | None,
        risk_adjusted_return: float,
        planning_score: float,
        suitability: str,
    ) -> str:
        output = (
            "Financial Planning Assessment\n\n"
            f"Initial investment: ₹{initial_amount:,.2f}\n"
            f"Target amount: ₹{target_amount:,.2f}\n"
            f"Time horizon: {years} years\n"
            f"Risk level: {risk_level.title()}\n\n"
            "Goal Analysis:\n"
            f"Required annual return if no further contributions are made: "
            f"{required_return * 100:.2f}%\n"
            "Required annual contribution: "
            + (
                f"₹{required_annual_investment:,.2f}\n\n"
                if required_annual_investment is not None
                else "Not calculated. Provide an expected annual return.\n\n"
            )
        )

        if annual_return is not None and future_value is not None:
            output += (
                "Expected Return Scenario:\n"
                f"Expected annual return: {annual_return * 100:.2f}%\n"
                f"Projected future value of initial investment: "
                f"₹{future_value:,.2f}\n"
                f"Risk-adjusted return (project heuristic): "
                f"{risk_adjusted_return * 100:.2f}%\n\n"
            )

        output += (
            "Planning Assessment:\n"
            f"Planning score (project heuristic): {planning_score:.2f}\n"
            f"Suitability category: {suitability}\n\n"
            "This is an illustrative calculation based on the supplied "
            "assumptions. It excludes taxes, fees and inflation unless "
            "explicitly modelled. Returns are not guaranteed and this is "
            "not personalized financial advice."
        )

        return output