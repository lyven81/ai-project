# Sunday Boardroom — User Guide

A simple guide for running your autonomous company. Read this whenever you forget how something works.

---

## What is the Sunday Boardroom?

It's your weekly leadership meeting with 6 AI managers. You are the Founder and chairman. Every Monday, you hold a 30-minute meeting where the managers report, you make decisions, and they execute the work during the week.

Think of it as: **you run the company, the AI does the work.**

---

## ⚡ The Most Important Thing to Know

**The real meeting happens in Claude Code (the terminal), not in the browser.**

- `boardroom.html` is a **visual mockup** — it looks like Zoom, but nothing in it actually runs a meeting. The buttons are decorative. Open it for ambiance if you like.
- The **actual meeting** happens when you type **`run board meeting`** inside a Claude Code session. That's when Ms Yap drafts the agenda, managers report, Cindy observes, you decide, and minutes get written to `what was discussed.md`.

**Two keywords to remember:**
- `run board meeting` → starts the Monday leadership meeting (anytime, any day — Monday is just the recommended rhythm)
- `check approvals` → runs your daily 5-minute approval queue review

That's it. Everything else, describe in plain language.

---

## Your Leadership Team (7 seats)

| Seat | Name | Role | What they do |
|---|---|---|---|
| 1 | **Aiman Razak** | AI Engineer Lead | Builds & ships new AI projects |
| 2 | **Cindy** | Mentor | Strategic advice + private 1:1s |
| 3 | **Daniel Wong** | Chief Researcher | Data analysis, client reports |
| 4 | **Lee Yih Ven** | Founder (you) | Chairs meetings, makes decisions |
| 5 | **Ms Yap** | Coordinator | Runs meetings, tracks follow-ups |
| 6 | **Ryan Goh** | Marketing Director | Sales, marketing, customer support |
| 7 | **Priya Chen** | Editor-in-Chief | Writes & publishes everything |

---

## Where Everything Lives

All files are in: `C:\Users\Lenovo\Documents\Follow up\`

| File | What it's for |
|---|---|
| `boardroom.html` | The Zoom-style meeting UI. Double-click to open. |
| `company-state.md` | Live source of truth — current goals, active projects, KPIs. Managers update this. |
| `what was discussed.md` | Log of every meeting + every Mentor 1:1 session. |
| `pending approval.md` | Daily approval queue. Check this every day. |
| `team.jpg` | Group photo used as fallback profile pictures. |
| `user guide.md` | This file. |

---

## The Weekly Rhythm

### Every Monday (meeting day)
1. Open Claude Code
2. Say **"run board meeting"** or type `/board-meeting`
3. Ms Yap drafts the agenda from last week's state
4. Each manager gives their 1-page report
5. Cindy shares any strategic observations
6. You decide on open items
7. Ms Yap writes minutes and updates the state file
8. Meeting ends (target: under 30 minutes)

### Every day Monday → Sunday (approval day)
1. Open Claude Code
2. Say **"check approvals"** or type `/check-approvals`
3. Review each pending item (preview + risk level)
4. For each one, say: approve / reject / defer
5. Approved items execute immediately
6. Takes about 5 minutes

### Anytime (Mentor 1:1)
1. Open Claude Code
2. Say **"talk to Cindy"** or **"board-mentor"**
3. Ask for private advice on anything
4. Cindy reads your state files so advice is grounded in reality
5. Summary gets logged to `what was discussed.md`

---

## Using the Boardroom UI (boardroom.html)

Double-click `boardroom.html` to open it in your browser.

### What you'll see
- 7 tiles arranged like a Zoom call
- Each tile shows a face, name, and role
- Side panel shows the meeting agenda
- Bottom bar has control buttons

### How to change a profile photo
1. Click the **📷 camera icon** in the top-left corner of any tile
2. Pick any image from your computer
3. It saves automatically and stays there next time you open the file

### How to change a name
1. **Click on the name** in the tile label
2. Type the new name
3. Press **Enter** to save (or click anywhere else)

### How to highlight who's speaking
Click anywhere on a tile (not on the camera or name). It gets a green glowing border.

### How to switch agenda items
Click any agenda item in the side panel to mark it as active.

### Reset all photos and names
Click the **↺ Reset all photos** button in the bottom-right corner.

### ⚠️ Note
The UI buttons (Mute, Stop Video, Chat, End Meeting) are decorative. The real meeting happens when you run `/board-meeting` in Claude Code. The UI is for the *feeling* of a meeting.

---

## How the Approval Queue Works

Some actions are safe (reading data, drafting content). Others are high-stakes (publishing to live websites, sending messages to real leads, spending money on deployments).

**Safe actions** → managers do them automatically.
**High-stakes actions** → managers add them to `pending approval.md` and wait for you.

### What goes in the queue
- Publishing to pauanalytics.com or portfolio sites
- Sending WhatsApp messages to real leads
- Sending proposals or client content
- Deploying to Cloud Run (costs money)
- Anything that can't be undone

### How to approve
1. Open `pending approval.md` or run `/check-approvals`
2. You'll see each pending item with:
   - What it does
   - Who queued it
   - Risk level
   - Preview link
3. Say "approve #001" to accept, "reject #001" to deny
4. Approved items run immediately

---

## The Rules (That Keep It Honest)

These rules exist so the meeting produces real work, not theatre:

1. **A manager can only report what's in the state file.** No made-up progress.
2. **Every action item must name the skill that will execute it.** If no skill can do it, it's not a valid action item.
3. **Hard 30-minute cap on meetings.** If the agenda is too long, defer items.
4. **Every decision needs an owner and a deadline.** Otherwise it doesn't count.
5. **The Founder approves, the managers do.** If you find yourself doing the work, the manager wasn't set up properly.

---

## Common Things You Might Say

| What you want | What to say |
|---|---|
| Start Monday meeting | "run board meeting" |
| Check daily approvals | "check approvals" |
| Private chat with Mentor | "talk to Cindy" or "ask the mentor" |
| Get a research report | "ask Daniel to run an analyst report on [file]" |
| Check lead pipeline | "ask Ryan for the lead pipeline status" |
| Publish something | "ask Priya to publish [draft]" |
| Build a new AI project | "ask Aiman to plan a new AI app for [idea]" |
| Update company state | "Ms Yap, update company-state.md with [info]" |

You don't need to memorize these. Just describe what you want in plain language and Claude will route to the right person.

---

## Quick Troubleshooting

**The face crops look wrong in the UI**
→ Click the 📷 icon on that tile and upload a clean headshot.

**I can't find a file**
→ All files are in `C:\Users\Lenovo\Documents\Follow up\`

**A manager gave a report that didn't match reality**
→ The state file probably wasn't updated. Tell Ms Yap to reconcile `company-state.md` with what actually happened.

**I forgot to run the Monday meeting**
→ It's fine. Run it whenever. The cadence is a guideline, not a cage.

**The company feels like theatre**
→ Check the rules above. Usually means action items don't name the skill, or managers are reporting hallucinated progress. Tighten the rules, not the agents.

**I want to add or remove a manager**
→ Persona files live in `C:\Users\Lenovo\.claude\agents\`. Edit, delete, or add new ones.

---

## What This Is NOT

- Not a chatbot for small talk — the managers work from real data
- Not a replacement for you — you still make every real decision
- Not running 24/7 — meetings only happen when you trigger them
- Not connected to the internet automatically — you approve every outbound action

---

## The One Sentence Version

**You run a weekly meeting, the managers do the work between meetings, and you approve anything risky before it goes live.**

Everything else is details.
