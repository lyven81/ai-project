# User Guide — TrendMate
## Malaysian Fashion Seller Research Assistant

---

## What Is This?

TrendMate is an AI assistant built for Malaysian online fashion sellers.
You type a question about the market, and it searches Shopee, TikTok,
fashion news, and supplier sites to give you a practical, actionable answer.

Use it to spot trends early, check competitor prices, research suppliers,
and plan ahead for seasonal sales.

---

## Before You Start — One-Time Setup

You only need to do this once.

### Step 1 — Get Your Anthropic API Key

This is the key that powers the AI brain.

1. Go to **console.anthropic.com**
2. Sign up or log in
3. Click **API Keys** in the left menu
4. Click **Create Key**
5. Copy the key — it starts with `sk-ant-...`
6. Save it somewhere safe — you will not see it again after closing that page

**Cost:** You pay only for what you use. A typical research session costs less than RM0.10.

---

### Step 2 — Get Your Tavily API Key

This is the key that lets the assistant search the web.

1. Go to **app.tavily.com**
2. Sign up for a free account
3. Your API key is shown on the dashboard — copy it
4. Free plan includes 1,000 searches per month — enough to start

---

### Step 3 — Set Up Your API Keys

1. Open the folder where this program is saved
2. Find the file called `.env.example`
3. Make a copy of it and rename the copy to `.env`
   (The file name must be exactly `.env` — no other words, just `.env`)
4. Open `.env` with Notepad
5. Replace the placeholder text with your real keys:

```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
TAVILY_API_KEY=tvly-your-actual-key-here
```

6. Save and close the file

---

### Step 4 — Install the Required Packages (First Time Only)

The first time you double-click `run.bat`, it will automatically install
the packages needed. This takes about 1–2 minutes. Internet connection required.

After the first run, it will start up immediately every time.

---

## How to Use It

### Starting the Program

Double-click the file called **run.bat**

A black window will open and TrendMate will be ready to help.

---

### Asking Questions

Type your question and press **Enter**.

TrendMate will search the web and reply in about 10–30 seconds
depending on your internet speed.

**Example questions you can ask:**

**Trends**
- What women's fashion is trending in Malaysia this week?
- What colours are popular in Malaysian fashion right now?
- Is oversized clothing still trending or is it fading out?
- What modest fashion styles are popular on TikTok Malaysia?

**Pricing**
- What price should I sell baju kurung moden on Shopee?
- What is the average price for Korean-style women's tops on Lazada?
- What margin do most streetwear sellers keep on TikTok Shop?

**Suppliers**
- Where can I source affordable baju raya in bulk?
- What are good suppliers on 1688 for women's casual wear?
- Are there local Malaysian wholesalers for men's polo shirts?

**Platforms & Strategy**
- What's new on Shopee Malaysia this month?
- How do I prepare for 11.11 as a fashion seller?
- What hashtags should I use for fashion on TikTok Malaysia?

**Seasonal Planning**
- When should I start stocking for Raya?
- What sells best during the school holiday season?
- What fashion items peak during Chinese New Year in Malaysia?

---

### Useful Commands

| Command | What it does |
|---|---|
| Type your question | Get a market research answer |
| Type `new` | Clear the conversation and start fresh |
| Type `exit` | Close the program |

---

### Tips for Better Answers

- **Be specific about the category.** Instead of "what is trending?", ask "what women's casual wear is trending on Shopee Malaysia this week?"
- **Mention the platform** if you are selling on a specific one (Shopee, Lazada, or TikTok Shop)
- **Ask follow-up questions** — TrendMate remembers what you asked earlier in the same session
- **Type `new`** when switching to a completely different topic

---

## Understanding the Output

Every answer should include:

- A direct recommendation or finding
- Where the information comes from (platform, news site, or trend data)
- A price range based on current market data
- A sourcing tip if relevant
- A timing note — when to stock, when to promote

TrendMate also shows you what it is searching while it works, like:
```
[Searching: trending women's fashion Malaysia Shopee 2025]
```

---

## Troubleshooting

**"Missing API keys" error on startup**
- Make sure your `.env` file exists in the same folder as `run.bat`
- Check that the key names are spelled exactly right: `ANTHROPIC_API_KEY` and `TAVILY_API_KEY`
- Make sure there are no spaces around the `=` sign

**"Search error" in the answer**
- Check your internet connection
- Your Tavily free plan may have run out of searches for the month
- Log into app.tavily.com to check your usage

**The window closes immediately after double-clicking**
- Open the `.env` file and make sure your API keys are filled in
- Try right-clicking `run.bat` and selecting "Run as administrator"

**Answers seem vague or not specific to Malaysia**
- Rephrase your question to include "Malaysia" and the specific platform
- Example: instead of "what is trending?", try "what is trending on Shopee Malaysia for women's clothing this week?"

---

## Important Notes

- TrendMate provides **market research** — results depend on what is publicly available on the web
- Prices and trends change quickly — always verify before making large buying decisions
- This tool focuses on the Malaysian market only
- Your conversations are not saved — they end when you close the program

---

## File Overview

| File | What it is |
|---|---|
| `run.bat` | Double-click this to start the program |
| `app.py` | The main program code |
| `system-prompt.txt` | The instructions that define the assistant's behaviour |
| `.env` | Your private API keys (you create this) |
| `.env.example` | Template showing what .env should look like |
| `requirements.txt` | List of packages the program needs |
| `user-guide.md` | This file |
