"""
MyPropLex — Malaysian Property Law Research Assistant
=====================================================
An AI-powered research assistant for Malaysian property lawyers
and conveyancing professionals.
"""

import os
import json
import sys
from pathlib import Path
from anthropic import Anthropic
from tavily import TavilyClient
from dotenv import load_dotenv

# ── Load API keys from .env file ──────────────────────────────────────────────
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# ── Load system prompt from file ──────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
SYSTEM_PROMPT_FILE = SCRIPT_DIR / "system-prompt.txt"

def load_system_prompt():
    if SYSTEM_PROMPT_FILE.exists():
        return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
    return "You are a Malaysian property law research assistant."

# ── Tool definition — Web Search ──────────────────────────────────────────────
TOOLS = [
    {
        "name": "search_web",
        "description": (
            "Search the web for Malaysian property law information. "
            "Use this to find legislation, case law, Bar Council updates, "
            "and legal commentary relevant to the user's question."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up"
                }
            },
            "required": ["query"]
        }
    }
]

# ── Tool execution ────────────────────────────────────────────────────────────
def search_web(query: str, tavily: TavilyClient) -> str:
    """Run a web search and return formatted results."""
    try:
        results = tavily.search(
            query=query,
            max_results=5,
            search_depth="advanced"
        )
        output = []
        for r in results.get("results", []):
            output.append(f"Source: {r.get('url', 'Unknown')}")
            output.append(f"Title: {r.get('title', 'No title')}")
            output.append(f"Content: {r.get('content', 'No content')}")
            output.append("---")
        return "\n".join(output) if output else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"

# ── Agent loop ────────────────────────────────────────────────────────────────
def run_agent(user_message: str, conversation_history: list,
              client: Anthropic, tavily: TavilyClient, system_prompt: str) -> str:
    """Send a message and handle tool calls until a final answer is ready."""
    conversation_history.append({"role": "user", "content": user_message})

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=conversation_history
        )

        # Final answer — no more tool calls
        if response.stop_reason == "end_turn":
            text_blocks = [b.text for b in response.content if hasattr(b, "text")]
            answer = "\n".join(text_blocks)
            conversation_history.append({"role": "assistant", "content": response.content})
            return answer

        # Tool use — execute the requested tool
        elif response.stop_reason == "tool_use":
            conversation_history.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if block.name == "search_web":
                        print(f"  [Searching: {block.input.get('query', '')}]")
                        result = search_web(block.input["query"], tavily)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

            conversation_history.append({"role": "user", "content": tool_results})

        else:
            return "Something went wrong. Please try again."

# ── Startup checks ────────────────────────────────────────────────────────────
def check_setup():
    """Check that API keys are configured before starting."""
    missing = []
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")

    if missing:
        print("\n ERROR: Missing API keys in your .env file:\n")
        for key in missing:
            print(f"  - {key}")
        print("\n Please open the .env file in this folder and add your API keys.")
        print(" See user-guide.md for instructions on how to get them.\n")
        input("Press Enter to exit...")
        sys.exit(1)

# ── Preset questions ──────────────────────────────────────────────────────────
PRESET_QUESTIONS = [
    "What are the steps involved in a standard property transfer in Malaysia under the National Land Code?",
    "What are a housing developer's obligations to buyers under the Housing Development Act (HDA)?",
    "What is the current Real Property Gains Tax (RPGT) rate in Malaysia and how is it calculated?",
    "What does the Strata Titles Act say about the rights and responsibilities of strata unit owners?",
    "What is the legal process if a property buyer wants to back out after signing the Sale and Purchase Agreement?",
    "What are the legal remedies available to a buyer if a developer abandons a housing project in Malaysia?",
    "What is the difference between freehold and leasehold land under the National Land Code?",
    "What are the stamp duty rates for property transactions in Malaysia and who is responsible for paying them?",
    "What conditions must be met for a memorandum of transfer (MOT) to be valid in Malaysia?",
    "What are the legal requirements for a valid tenancy agreement in Malaysia?",
]

def show_menu():
    print()
    print("=" * 65)
    print("   MyPropLex — Malaysian Property Law Research Assistant")
    print("=" * 65)
    print()
    print("  Pick a question below or type your own.\n")
    for i, q in enumerate(PRESET_QUESTIONS, 1):
        print(f"  {i:>2}. {q}")
    print()
    print("  Commands:")
    print("    Type a number (1-10) to select a question")
    print("    Type your own question and press Enter")
    print("    Type 'menu' — show this list again")
    print("    Type 'new'  — start a fresh conversation")
    print("    Type 'exit' — close the program")
    print()
    print("-" * 65)

# ── Main program ──────────────────────────────────────────────────────────────
def main():
    check_setup()

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    system_prompt = load_system_prompt()
    conversation_history = []

    show_menu()

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nClosing MyPropLex. Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "bye", "q"]:
            print("\nClosing MyPropLex. Goodbye!")
            break

        if user_input.lower() == "menu":
            show_menu()
            continue

        if user_input.lower() == "new":
            conversation_history = []
            show_menu()
            continue

        # Handle number selection
        if user_input.isdigit():
            index = int(user_input) - 1
            if 0 <= index < len(PRESET_QUESTIONS):
                user_input = PRESET_QUESTIONS[index]
                print(f"\n  >> {user_input}\n")
            else:
                print(f"\n  Please enter a number between 1 and {len(PRESET_QUESTIONS)}.\n")
                continue

        print("\nResearching... please wait.\n")

        try:
            answer = run_agent(
                user_input, conversation_history,
                client, tavily, system_prompt
            )
            print(f"MyPropLex:\n\n{answer}\n")
            print("-" * 65)
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please check your internet connection and try again.\n")

if __name__ == "__main__":
    main()
