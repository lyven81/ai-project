# Project Outline — Malaysian Fashion Seller Research Assistant

## App Name
**TrendMate** — Market Research Assistant for Malaysian Online Fashion Sellers

## Category
E-commerce Intelligence / AI Research Tool

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
User types question (e.g. "What's trending in women's fashion this week?")
        ↓
app.py — sends to Claude with system prompt + tools
        ↓
Claude decides to search → calls search_web() tool
        ↓
Tavily fetches results (Shopee trends, TikTok, fashion news, suppliers)
        ↓
Claude reads results → reasons → writes actionable recommendation
        ↓
Answer printed to terminal
```

## Core Features (Version 1)

1. **Trend Research** — Find what styles are trending in Malaysia right now
2. **Competitor Scan** — Check what top sellers are listing and at what prices
3. **Supplier Research** — Find wholesale options for specific clothing types
4. **Platform Updates** — Track Shopee/Lazada/TikTok Shop policy changes
5. **Seasonal Planner** — Get reminders and prep tips for upcoming sale events
6. **Conversation Memory** — Remembers earlier questions in the same session

## Files in This Project

| File | Purpose |
|---|---|
| `app.py` | Main application — runs the research assistant |
| `system-prompt.txt` | The AI agent's instructions and market focus |
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
- Shopee / Lazada / TikTok Shop fashion sellers
- Solo fashion dropshippers
- Small fashion boutique owners going online
- Anyone sourcing trending clothing to resell

## Monetization (Future)
- RM50–RM150/month subscription
- Free tier (5 queries/day) to drive adoption
- Upsell: automated daily trend digest via WhatsApp or email

## Roadmap

| Phase | What to Build |
|---|---|
| v1 (Now) | CLI chatbot with search + trend recommendations |
| v2 | Web interface (Streamlit) with simple dashboard |
| v3 | Shopee/Lazada API integration for live pricing data |
| v4 | Automated daily trend report (email or WhatsApp) |
| v5 | Multi-seller subscription with saved preferences |
