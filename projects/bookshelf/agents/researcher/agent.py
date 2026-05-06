"""Data Researcher agent — reads the bookshelf sales dataset and computes
per-SKU, per-category, seasonal, and data-quality metrics.
"""

import os

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from data_tool import analyse_sales_data_summary


MODEL = os.environ.get("BOOKSHELF_MODEL", "gemini-2.5-flash")


def get_sales_metrics() -> str:
    """Read the bookshelf sales dataset and return structured metrics as a JSON string.

    Computes meta totals, top + bottom SKUs (with revenue, profit, velocity,
    margin, Pareto rank), per-category aggregates, per-subcategory aggregates,
    monthly seasonal indices, channel breakdown, and data quality flags.
    """
    return analyse_sales_data_summary(top_n=30)


sales_metrics_tool = FunctionTool(func=get_sales_metrics)


researcher = Agent(
    name="researcher",
    model=MODEL,
    description=(
        "Reads the bookshelf sales dataset and produces structured metrics: "
        "per-SKU revenue/margin/velocity, category aggregates, seasonal indices, "
        "channel breakdown, and data quality checks."
    ),
    instruction=(
        "You are the Data Researcher for Bookshelf, a Malaysian book shop owner's "
        "AI business advisor.\n\n"
        "1. Call the `get_sales_metrics` tool to load the latest sales analytics.\n"
        "2. Return the JSON string from the tool VERBATIM as your response.\n\n"
        "Do not summarise, do not reformat. The downstream Judge needs the raw "
        "structured JSON to validate it. If the tool returns an error key, report "
        "the error clearly so the Judge can fail the run."
    ),
    tools=[sales_metrics_tool],
)


root_agent = researcher
