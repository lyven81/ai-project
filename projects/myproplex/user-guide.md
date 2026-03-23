# User Guide — MyPropLex
## Malaysian Property Law Research Assistant

---

## What Is This?

MyPropLex is an AI assistant that helps you research Malaysian property law.
You type a legal question, and it searches the web, reads the results, and
gives you a clear answer with citations.

It covers the National Land Code, HDA, Strata Titles Act, RPGT Act, RERA,
and related Malaysian property legislation.

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

A black window will open and the assistant will be ready.

---

### Asking Questions

Type your question and press **Enter**.

The assistant will search the web and reply in about 10–30 seconds
depending on your internet speed.

**Example questions you can ask:**

- What are the steps in a standard property transfer under the National Land Code?
- What does Section 206 of the NLC say about land dealings?
- What is the RPGT rate for a property sold within 3 years of purchase?
- What are a housing developer's obligations under the HDA?
- Has there been any recent amendment to the Strata Titles Act?
- What happens if a buyer defaults on a Sale and Purchase Agreement?
- Summarise the legal process for a first-time homebuyer in Malaysia
- What is the legal remedy for a developer who abandons a project?

---

### Useful Commands

| Command | What it does |
|---|---|
| Type your question | Get a legal research answer |
| Type `new` | Clear the conversation and start fresh |
| Type `exit` | Close the program |

---

### Tips for Better Answers

- **Be specific.** Instead of "what is property law?", ask "what does Section 76 of the NLC say about restrictions on land use?"
- **Name the act** if you know it — the assistant will search more precisely
- **Ask follow-up questions** — the assistant remembers what you asked earlier in the same session
- **Type `new`** when switching to a different case or topic — this clears the previous context

---

## Understanding the Output

Every answer should include:

- A direct response to your question
- The relevant act name and section number, or case name
- Any important exceptions or caveats
- A note if you should seek formal legal advice for your specific situation

The assistant also shows you what it is searching while it works, like:
```
[Searching: National Land Code Section 340 Malaysia]
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

**Answers seem outdated or incomplete**
- Try rephrasing your question with more specific keywords
- Ask the assistant to search again with different terms

---

## Important Notes

- MyPropLex is a **research tool**, not a substitute for qualified legal advice
- Always verify citations by checking the original legislation or case
- This tool is for Malaysian property law only
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
