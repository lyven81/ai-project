"""Forensic Judge agent — independent quality gate that validates the
Researcher's output before the Content Builder is allowed to act on it.
"""

import os
from typing import Literal

from google.adk.agents import Agent
from pydantic import BaseModel, Field


MODEL = os.environ.get("BOOKSHELF_MODEL", "gemini-2.5-flash")


class JudgeVerdict(BaseModel):
    """Structured verdict from the Forensic Judge."""

    status: Literal["pass", "fail"] = Field(
        description=(
            "'pass' if the research findings are complete and trustworthy enough "
            "for the Content Builder to act on. 'fail' if data quality issues are "
            "severe enough that recommendations would be unreliable."
        )
    )
    issues: list[str] = Field(
        default_factory=list,
        description=(
            "Specific issues found. Examples: '1530 rows missing CustomerCity (1.5%)', "
            "'5 rows with OrderQuantity = 0', 'Workbook category dominates 67% of revenue'."
        ),
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence 0.0-1.0 in the data's fitness for analysis.",
    )
    feedback: str = Field(
        description=(
            "If status='fail', clear instructions for the Researcher on what to "
            "re-extract or recompute. If status='pass', a 1-2 sentence note for "
            "the Content Builder about what to weight carefully."
        )
    )


judge = Agent(
    name="judge",
    model=MODEL,
    description=(
        "Forensic Judge for the Bookshelf decision-support team. Validates the "
        "Researcher's metrics for completeness, plausibility, and red flags before "
        "the Content Builder makes recommendations to the shop owner."
    ),
    instruction=(
        "You are a strict, independent forensic auditor reviewing the output of "
        "the Data Researcher.\n\n"
        "Read the JSON in 'research_findings' from the session state.\n\n"
        "Check for:\n"
        "1. **Completeness** — meta.row_count > 1000? unique_skus > 50? months_span >= 3?\n"
        "2. **Data quality** — read data_quality block. Flag if missing fields > 5% "
        "of total_rows. Flag if zero_quantity_rows or negative_price_rows > 50.\n"
        "3. **Plausibility** — does any single category dominate >90% of revenue? "
        "Does any single SKU exceed 20% of total revenue? Red flags.\n"
        "4. **Coverage** — at least 3 categories and 3 subcategories? "
        "seasonal_indices non-empty?\n"
        "5. **Duplicate risk** — duplicate_order_lines flag, only if > 1% of rows.\n\n"
        "Return JudgeVerdict. Set status='pass' unless there is a serious problem "
        "that would mislead the Content Builder. Minor data quality issues "
        "(<2% missing fields) should be noted in 'issues' but still pass — they'll "
        "be surfaced as Data Quality Notes in the brief.\n\n"
        "Be specific in 'issues' — quote actual numbers from the data."
    ),
    output_schema=JudgeVerdict,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)


root_agent = judge
