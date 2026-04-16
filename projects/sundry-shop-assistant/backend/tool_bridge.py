"""
Bridge between MCP-style tools (mcp_tools.py) and Gemini Live API function calling.

Each tool in mcp_tools.py is exposed to the Live API as a FunctionDeclaration.
When the model emits a function call mid-conversation, the corresponding
Python function is invoked and the result is sent back in the session.

To switch to a real MCP server:
  - Replace mcp_tools function references with MCP client calls
  - The FunctionDeclaration schemas stay the same
"""
from google.genai import types

from mcp_tools import ALL_TOOLS

# Schemas describing each tool to Gemini.
# All tools take zero parameters for this dataset (they operate on the full
# 150-row March 2024 window). Future tools with date filters would add params.

_FUNCTION_DECLARATIONS = [
    types.FunctionDeclaration(
        name="get_total_sales",
        description=(
            "Get the total sales revenue, total transaction count, and average "
            "basket size over the whole dataset (March 2024). Use this when the "
            "owner asks 'how much did I sell?' or 'what's my total?'."
        ),
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
    types.FunctionDeclaration(
        name="get_top_day",
        description=(
            "Find the single best-selling day in the dataset. Use this for "
            "questions like 'hari paling laku bulan ni?' or 'best day so far?'."
        ),
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
    types.FunctionDeclaration(
        name="get_weekly_summary",
        description=(
            "Get a week-by-week revenue and transaction breakdown across the "
            "dataset. Use this for 'minggu ni macam mana?' or weekly comparisons."
        ),
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
    types.FunctionDeclaration(
        name="get_sales_by_category",
        description=(
            "Rank all product categories by revenue, including transaction count "
            "and average basket per category. Use this for 'kategori paling laku?' "
            "or 'top categories'."
        ),
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
    types.FunctionDeclaration(
        name="get_slowest_category",
        description=(
            "Identify the three slowest-moving product categories by revenue. "
            "Use this for 'apa paling slow?' or reorder decisions."
        ),
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
    types.FunctionDeclaration(
        name="compare_member_vs_visitor",
        description=(
            "Compare Member vs Visitor customers: revenue share, average basket, "
            "and transaction count. Use this for loyalty program questions like "
            "'member atau visitor spend lebih?'."
        ),
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
    types.FunctionDeclaration(
        name="compare_gender",
        description=(
            "Compare spend by Gender (Male vs Female). Excludes rows with missing "
            "gender. Use this for 'laki atau perempuan spend lebih?'."
        ),
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
    types.FunctionDeclaration(
        name="get_payment_mix",
        description=(
            "Show the revenue and transaction share by payment method (Cash, "
            "Credit Card, Mobile Payment). Use this for 'cash atau card?' or "
            "digital adoption questions."
        ),
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
    types.FunctionDeclaration(
        name="get_payment_by_customer_type",
        description=(
            "Show how Members and Visitors differ in payment method preference. "
            "Use this for 'member pakai apa untuk bayar?'."
        ),
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
    types.FunctionDeclaration(
        name="get_basket_stats",
        description=(
            "Average basket, largest single sale, items per transaction, and "
            "average unit price. Use this for 'average transaksi berapa?' or "
            "'basket paling besar?'."
        ),
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
]


def get_tools() -> list[types.Tool]:
    """Return tool list ready for LiveConnectConfig."""
    return [types.Tool(function_declarations=_FUNCTION_DECLARATIONS)]


def get_tool_mapping() -> dict:
    """Return tool name -> callable mapping for tool execution."""
    return ALL_TOOLS
