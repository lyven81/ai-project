# Project Outline — Malaysian Property Law Research Assistant

## App Name
**MyPropLex** — Malaysian Property Law Research Assistant

## Category
Legal Tech / AI Research Tool

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| AI Model | Claude Sonnet 4.6 (Anthropic) |
| Search Tool | Tavily Search API |
| Interface | Command-line terminal (v1) |
| Config | python-dotenv (.env file) |

## Architecture

```
User types question
        ↓
app.py — sends to Claude with system prompt + tools
        ↓
Claude decides to search → calls search_web() tool
        ↓
Tavily fetches web results (Malaysian legal sites)
        ↓
Claude reads results → reasons → writes cited answer
        ↓
Answer printed to terminal
```

## Core Features (Version 1)

1. **Legal Question Answering** — Ask any Malaysian property law question and get a cited answer
2. **Web Search Integration** — Searches current legislation, case law, and Bar Council updates
3. **Citation Output** — Every answer includes the act name, section number, or case reference
4. **Conversation Memory** — Remembers earlier questions in the same session
5. **Plain Language Mode** — Can translate legal answers into simple client-friendly language

## Files in This Project

| File | Purpose |
|---|---|
| `app.py` | Main application — runs the research assistant |
| `system-prompt.txt` | The AI agent's instructions and legal focus |
| `build-prompt.txt` | Prompt used to build this app with Claude |
| `problem-statement.md` | Why this app exists |
| `project-outline.md` | This file — overall plan |
| `user-guide.md` | How to set up and use the app |
| `requirements.txt` | Python packages needed |
| `.env.example` | Template for API keys |
| `run.bat` | Double-click to launch the app |

## APIs Required

| API | Get it from | Cost |
|---|---|---|
| Anthropic Claude | console.anthropic.com | Pay per use (~$3/1M tokens) |
| Tavily Search | app.tavily.com | Free (1,000 searches/mo), $20/mo after |

## Target Users
- Property lawyers
- Conveyancing clerks
- Legal consultants
- Property developers needing legal clarity

## Monetization (Future)
- RM300–RM800/month per firm subscription
- Per-query pricing for solo practitioners
- White-label version for legal tech companies

## Roadmap

| Phase | What to Build |
|---|---|
| v1 (Now) | CLI chatbot with search + citations |
| v2 | Web interface (Streamlit or Flask) |
| v3 | PDF upload — summarise SPA, loan agreements |
| v4 | Case law database integration (CLJ/MLJ) |
| v5 | Multi-user firm subscription with login |
