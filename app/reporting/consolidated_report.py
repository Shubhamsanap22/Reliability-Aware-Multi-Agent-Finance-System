
"""Build a plain-language report and evidence-backed chart specifications."""
from __future__ import annotations

import json
import math
import re
from typing import Any, Iterable

from app.models.schemas import AgentState, AgentStatus, TaskRequirement


class ConsolidatedReportBuilder:
    """Create one user-facing report without inventing financial inputs.

    The local Ollama model is used only to rewrite findings into plain language.
    Chart values are calculated or extracted by deterministic Python code.
    """

    def __init__(
        self,
        model_name: str = "mistral:latest",
        use_local_llm: bool = True,
    ) -> None:
        self.model_name = model_name
        self.use_local_llm = use_local_llm

    def build(
        self,
        query: str,
        requirement: TaskRequirement,
        results: Iterable[AgentState],
        base_report: dict[str, Any],
    ) -> dict[str, Any]:
        states = tuple(results)

        findings = [
            {
                "agent_name": result.agent_name,
                "output": result.output.strip(),
                "reliability": result.reliability,
            }
            for result in states
            if (
                result.status == AgentStatus.COMPLETED
                and isinstance(result.output, str)
                and result.output.strip()
            )
        ]

        charts = self._build_charts(requirement, findings)
        limitations = base_report.get("limitations", [])
        summary = self._summarize(query, findings, limitations)

        return {
            **base_report,
            "summary": summary,
            "key_findings": [
                finding["output"] for finding in findings
            ],
            "risks": list(limitations),
            "recommendations": [],
            "charts": charts,
            "summary_source": "local_mistral_or_deterministic_fallback",
        }

    def _summarize(
        self,
        query: str,
        findings: list[dict[str, Any]],
        limitations: list[str],
    ) -> str:
        if not findings:
            return (
                "The system could not produce a completed analysis. "
                "Try simplifying the question or checking the data source."
            )

        fallback = " ".join(
            f"{item['agent_name']}: {item['output']}"
            for item in findings
        )

        if limitations:
            fallback += " Limitations: " + " ".join(
                str(item) for item in limitations
            )

        if not self.use_local_llm:
            return fallback

        try:
            import ollama

            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are the plain-language reporting layer for "
                            "a financial decision-support system. Summarize "
                            "only the supplied agent findings in simple "
                            "language. Do not add financial facts, prices, "
                            "predictions, allocations, returns, or "
                            "recommendations that are not present in the "
                            "input. State uncertainty and limitations "
                            "clearly. This is not personalized financial "
                            "advice. Return a concise report in 2-5 short "
                            "paragraphs, with no agent-by-agent headings."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "query": query,
                                "findings": findings,
                                "limitations": limitations,
                            },
                            ensure_ascii=False,
                        ),
                    },
                ],
                options={"temperature": 0.1},
            )

            content = response.get("message", {}).get("content", "")
            content = (
                content.strip()
                if isinstance(content, str)
                else ""
            )

            return content or fallback

        except Exception:
            # Keep the API usable if Ollama is stopped or the model
            # is unavailable.
            return fallback

    def _build_charts(
        self,
        requirement: TaskRequirement,
        findings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        charts: list[dict[str, Any]] = []
        text = "\n".join(
            item["output"] for item in findings
        )

        # Build a projection only when the user supplied an explicit
        # annual-return assumption and a valid investment amount/horizon.
        if (
            requirement.initial_amount is not None
            and requirement.initial_amount > 0
            and requirement.years is not None
            and requirement.years > 0
            and requirement.annual_return is not None
            and math.isfinite(requirement.annual_return)
            and -1 < requirement.annual_return <= 1
            and float(requirement.years).is_integer()
        ):
            points = []

            for year in range(int(requirement.years) + 1):
                value = requirement.initial_amount * (
                    (1 + requirement.annual_return) ** year
                )

                if not math.isfinite(value):
                    points = []
                    break

                points.append(
                    {
                        "x": year,
                        "y": round(value, 2),
                    }
                )

            if len(points) >= 2:
                charts.append(
                    {
                        "type": "line",
                        "title": "Illustrative investment projection",
                        "x_label": "Year",
                        "y_label": "Value (currency units)",
                        "data": points,
                        "note": (
                            "Mathematical illustration using the annual "
                            "return you supplied; actual returns are not "
                            "guaranteed."
                        ),
                    }
                )

        # Only chart an allocation when explicit category percentages
        # appear in the agent output and total approximately 100%.
        allocations = self._extract_allocations(text)

        if (
            len(allocations) >= 2
            and 98 <= sum(item["value"] for item in allocations) <= 102
        ):
            charts.append(
                {
                    "type": "doughnut",
                    "title": "Allocation mentioned in the analysis",
                    "data": allocations,
                    "note": (
                        "Parsed from agent output; verify the allocation "
                        "before acting."
                    ),
                }
            )

        # Do not invent chart data. Additional chart types can be added
        # when structured price series, comparable options, or risk/return
        # pairs are available.
        return charts

    @staticmethod
    def _extract_allocations(
        text: str,
    ) -> list[dict[str, Any]]:
        found: dict[str, float] = {}

        # Conservative pattern: a label followed by a percentage,
        # e.g. Equity: 60%.
        pattern = (
            r"(?im)^\s*([A-Za-z][A-Za-z &/-]{1,35})"
            r"\s*[:\-]\s*(\d{1,3}(?:\.\d+)?)\s*%"
        )

        for match in re.finditer(pattern, text):
            label = match.group(1).strip()
            value = float(match.group(2))

            if 0 <= value <= 100:
                found[label] = value

        return [
            {"label": label, "value": value}
            for label, value in found.items()
        ]
