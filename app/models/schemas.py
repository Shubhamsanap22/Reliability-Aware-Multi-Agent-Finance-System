from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Execution status of an individual agent."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REPLACED = "replaced"


class TaskRequirement(BaseModel):
    """Structured requirements extracted from a financial query."""

    query: str = Field(
        description="The original user query."
    )

    required_capabilities: list[str] = Field(
        default_factory=list,
        description=(
            "Requested capabilities: investment_analysis, risk_analysis, "
            "portfolio_management, market_research, fundamental_analysis, "
            "technical_analysis, sentiment_analysis, financial_planning."
        ),
    )

    risk_preference: Optional[str] = Field(
        default=None,
        description=(
            "User-stated risk preference: low, moderate, medium or high. "
            "Do not infer it if the user has not provided it."
        ),
    )

    initial_amount: Optional[float] = Field(
        default=None,
        ge=0,
        description="Initial investment amount explicitly stated by the user.",
    )

    target_amount: Optional[float] = Field(
        default=None,
        gt=0,
        description="Target financial amount explicitly stated by the user.",
    )

    years: Optional[int] = Field(
        default=None,
        gt=0,
        description="Investment or financial planning horizon in years.",
    )

    annual_return: Optional[float] = Field(
        default=None,
        description=(
            "Expected annual return as a decimal fraction; 0.10 means 10%. "
            "Never invent this value if the user has not supplied it."
        ),
    )

    symbols: list[str] = Field(
        default_factory=list,
        description=(
            "Explicitly mentioned stock ticker symbols, such as TCS or INFY. "
            "Do not include ordinary words or risk levels."
        ),
    )


class AgentState(BaseModel):
    """Runtime state and result for one agent."""

    agent_name: str

    reliability: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )

    allocated_budget: int = Field(
        default=0,
        ge=0,
    )

    used_budget: int = Field(
        default=0,
        ge=0,
    )

    status: AgentStatus = AgentStatus.PENDING

    output: Optional[str] = None
    failure_reason: Optional[str] = None

    @property
    def remaining_agent_budget(self) -> int:
        """Return the unused portion of this agent's allocation."""
        return max(
            0,
            self.allocated_budget - self.used_budget,
        )


class BudgetState(BaseModel):
    """Global computational budget state."""

    global_budget: int = Field(gt=0)
    allocated_budget: int = Field(default=0, ge=0)
    used_budget: int = Field(default=0, ge=0)
    reserved_budget: int = Field(default=0, ge=0)

    @property
    def remaining_budget(self) -> int:
        """Return global budget remaining after actual usage."""
        return max(
            0,
            self.global_budget - self.used_budget,
        )

    @property
    def available_budget(self) -> int:
        """Return remaining budget after the protected reserve."""
        return max(
            0,
            self.remaining_budget - self.reserved_budget,
        )