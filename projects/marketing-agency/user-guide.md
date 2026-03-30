# Marketing Agency Dashboard — User Guide

## What This Is

A local dashboard that shows everything your marketing agency is doing across Pau Analytics and Pau AI — content produced, leads captured, pipeline status, and weekly performance. One screen, four tabs.

---

## How to Start

Double-click `start.bat` in this folder. The dashboard opens at:

```
http://localhost:8100
```

Bookmark this URL in your browser.

---

## The Four Tabs

### Tab 1: Content

**What it shows:**
- LinkedIn drafts ready to paste (with a red badge showing how many are pending)
- Each draft shows: date, brand (Pau Analytics or Pau AI), post type, preview text, word count, and status (Pending or Posted)
- Recent blog posts published in the last 14 days
- Recent git activity (commits to the pau-analytics-1.0 repo)

**What to check:**
- Pending LinkedIn drafts — these are posts waiting for you to paste to LinkedIn
- Blog posts published — confirm this week's blog went live

**How often:** Every morning (takes 30 seconds to scan)

---

### Tab 2: Pipeline

**What it shows:**
- Next topic in the publish queue (case study selected by content-scheduler)
- Next week's plan (if coordinator has written one)
- Full publish history (every case study that has been turned into a blog)
- Case study stats: how many remain, how many are live
- Pau AI solution categories: which ones have been showcased on LinkedIn, which haven't

**What to check:**
- Is a topic queued for next week? If not, run `/content-scheduler`
- How many case studies remain? (This tells you how many weeks of content you have left)
- Which Pau AI categories haven't been showcased yet? (Rotate to these next)

**How often:** Once a week (Monday morning, before running `/run-content-week`)

---

### Tab 3: Weekly Report

**What it shows:**
- The latest coordinator report (and all past reports)
- What was published, how many leads came in, which content drove leads, and what to do next

**What to check:**
- Action items — the coordinator flags what needs your attention
- Lead-to-content correlation — which blog posts are generating leads
- Next week recommendation — the coordinator suggests what topic to publish next

**How often:** Friday evening (after running `/coordinator`)

---

### Tab 4: Leads

**What it shows:**
- Total leads, leads this week, leads needing follow-up
- Breakdown by channel: CH-A (Google Ads), CH-B (Blog), CH-W (Chat Widget)
- Blog performance — which blog posts are generating the most leads
- Full lead list with name, challenge, source, and status

**What to check:**
- Needs Follow-up count (shown as a red badge on the tab) — these are leads you haven't responded to yet
- Blog performance — see which topics drive real inquiries
- Lead statuses — make sure no lead sits at "New" for more than 24 hours

**How often:** Daily (check the badge count — if it says 0, you're done)

**Note:** This tab reads from the Web Chat Lead Manager API. If the Web Chat Lead Manager is not running, this tab will show empty data. Start the Web Chat Lead Manager first if you need live lead data.

---

## Your Daily Routine

| Time | What to Do | Where | Duration |
|---|---|---|---|
| **Morning** | Open dashboard, check Content tab for pending LinkedIn posts | http://localhost:8100 | 30 sec |
| **Morning** | If today is a posting day (Mon/Tue/Thu/Fri), open the draft, copy text, paste to LinkedIn | LinkedIn | 2 min |
| **Morning** | Check Leads tab — any red badge? Review new leads, send WhatsApp follow-ups | Dashboard + WhatsApp | 5 min |

## Your Weekly Routine

| Day | What to Do | Duration |
|---|---|---|
| **Monday morning** | Run `/run-content-week` in Claude Code — produces 1 blog + 4 LinkedIn drafts | 5 min (mostly automated) |
| **Monday** | Paste Monday's Pau Analytics LinkedIn post | 2 min |
| **Tuesday** | Paste Tuesday's Pau AI LinkedIn post | 2 min |
| **Thursday** | Paste Thursday's Pau Analytics LinkedIn post | 2 min |
| **Friday morning** | Run `/coordinator` in Claude Code — generates weekly report | 3 min |
| **Friday** | Paste Friday's Pau AI LinkedIn post | 2 min |
| **Friday evening** | Check Weekly Report tab — read the brief, note any topic preferences for next week | 5 min |

**Total weekly time: ~25 minutes**

---

## Posting Schedule

| Day | Brand | Post Type | What to Look For in the Draft |
|---|---|---|---|
| Monday | Pau Analytics | Blog teaser | Links to a new blog post. Hook + data point + blog URL. |
| Tuesday | Pau AI | Solution showcase | Describes one of 8 solution categories. Demo link included. |
| Thursday | Pau Analytics | Standalone insight | One data finding from a case study. No blog link needed. |
| Friday | Pau AI | Use case spotlight | Zooms into one specific business scenario. Relatable story. |

---

## How to Paste a LinkedIn Post

1. Open the Content tab on the dashboard
2. Find the pending post for today
3. Click to expand (or open the file directly from `pau-analytics-1.0/blog/linkedin-drafts/`)
4. Select all text, copy
5. Open LinkedIn, click "Start a post"
6. Paste the text
7. Add an image if available (optional)
8. Click Post

After posting, update the `posted-log.txt` file:
```
[YYYY-MM-DD] | filename.txt | posted
```

---

## Claude Code Skills

These are the commands you type in Claude Code to run the marketing agency.

### `/run-content-week` — Produce all weekly content

**When:** Monday morning
**What it does:**
1. Picks the next blog topic (reads coordinator's recommendation if available)
2. Writes the blog post
3. Publishes the blog to pauanalytics.com
4. Writes a LinkedIn teaser for the blog (Monday post)
5. Writes a standalone insight post from a different case study (Thursday post)
6. Writes a Pau AI solution showcase post (Tuesday post)
7. Writes a Pau AI use case spotlight post (Friday post)

**What you say:** "run content week" or "produce this week's content"
**Output:** 1 published blog + 4 LinkedIn draft files saved to `linkedin-drafts/`
**Your action after:** Paste Monday's LinkedIn post immediately, paste the rest on their scheduled days.

### `/check-leads` — Review leads and draft follow-ups

**When:** Daily (or whenever you see a Gmail lead alert)
**What it does:**
1. Reads all leads from the Web Chat Lead Manager API
2. Filters leads that need follow-up (status "New" or "Qualifying")
3. Sorts by urgency score (high urgency first)
4. Drafts personalized WhatsApp follow-up messages for each lead

**What you say:** "check leads" or "any new leads"
**Output:** Lead summary + drafted WhatsApp messages ready to copy-paste
**Your action after:** Copy each message, paste into WhatsApp, send. Then update lead status on the dashboard.

**Note:** The Web Chat Lead Manager must be running for this skill to work. Start it first if needed.

### `/coordinator` — Weekly report (existing skill)

**When:** Friday evening
**What you say:** "run the coordinator" or "run the weekly report"
**Output:** Weekly report saved to GitHub + Gmail-ready version

### `/content-scheduler` — Pick next topic (existing skill, runs inside /run-content-week)

You rarely need to run this separately. It runs automatically as part of `/run-content-week`. Only run it directly if you want to queue a topic without producing the full week's content.

---

## How to Follow Up on a Lead

**Option A — Using `/check-leads` (recommended):**
1. Type "check leads" in Claude Code
2. Review the drafted WhatsApp messages
3. Copy each message, paste into WhatsApp, send
4. Update lead status on the Railway dashboard

**Option B — Manual (if Claude Code is not open):**
1. Check the Leads tab on the dashboard — look for leads with status "New"
2. Open your Gmail — the lead alert email contains:
   - Lead name and phone (if provided)
   - Their business challenge
   - AI-suggested WhatsApp opener
3. Copy the suggested opener
4. Open WhatsApp, paste the opener, personalize it
5. Send within 24 hours

---

## What to Review Before Pasting a LinkedIn Post

Quick scan checklist (30 seconds per post):

- **Hook:** Does the first line make you stop? Would you click "see more"?
- **Data point:** Is there a specific number? (not vague — "18% drop" not "significant decline")
- **Accuracy:** Does the data point match the case study?
- **CTA:** Is there a link to the blog (for teasers) or solutions page (for Pau AI)?
- **Length:** Is it 150-250 words? Too short lacks substance, too long loses attention.
- **Hashtags:** 3-5 relevant hashtags at the end?

If something feels off, tell Claude: "Rewrite the hook for [filename]" — it will fix it.

---

## When Things Are Empty

| What's Empty | What It Means | What to Do |
|---|---|---|
| Content tab — no drafts | `/run-content-week` hasn't been run this week | Run `/run-content-week` in Claude Code |
| Pipeline — no topic queued | Content-scheduler hasn't picked a topic | Run `/content-scheduler` in Claude Code |
| Weekly Report — no reports | `/coordinator` hasn't been run yet | Run `/coordinator` in Claude Code |
| Leads — all zeros | Web Chat Lead Manager not running or no leads yet | Start Web Chat Lead Manager (`start.bat` in its folder) |

---

## File Structure

```
Marketing agency/
  app.py                 <- Dashboard server
  config.py              <- All paths and settings
  readers.py             <- Data reading functions
  requirements.txt       <- Python dependencies
  start.bat              <- Double-click to launch
  user-guide.md          <- This file
  static/
    style.css            <- Dashboard styling
  templates/
    dashboard.html       <- Dashboard UI (4 tabs)
  Web Chat Lead Manager/ <- Reference copy of the lead management backend
  ingredients.md         <- All resources for the marketing agency
  marketing-agency-building-plan.md <- Full implementation plan
```

---

## Troubleshooting

| Problem | Check |
|---|---|
| Dashboard won't start | Is Python installed? Run `python --version` in terminal |
| Leads tab shows empty | Is Web Chat Lead Manager running? Check http://localhost:8000/health |
| Content tab shows no drafts | Does `pau-analytics-1.0/blog/linkedin-drafts/` folder exist? |
| Pipeline shows 0 case studies | Does `pau-analytics-1.0/case-study/` folder exist with HTML files? |
| Blog posts not showing | Check `pau-analytics-1.0/blog/` for recent HTML files |
