# Social Media Marketer — User Guide

## What This App Does

Social Media Marketer runs a simulation where 5 AI agents — one for each marketing channel — compete with the same starting budget over 4 rounds.

Each agent picks campaigns from real data, allocates budget, and gets scored on whether their chosen campaign beats the performance benchmark. At the end, you get a ranked leaderboard and a clear recommendation: which channel to scale up, which to hold, and which to cut.

**The 5 agents:**
| Agent | Channel | Persona |
|-------|---------|---------|
| Emma | Email | Retention-focused, data-driven |
| Sam | Social | Acquisition-focused, creative |
| Parker | Paid Search | ROI-obsessed, conversion-focused |
| Diana | Display | Retargeting expert, visual-first |
| Alex | Affiliate | Performance-driven, cost-conscious |

**What you will learn:**
- Which channel consistently hits the ROI benchmark (9% uplift minimum)
- Which channel loses money and should be cut or reviewed
- Where to reallocate budget for better returns

---

## First-Time Setup

### Step 1 — Get your Anthropic API key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign in or create a free account
3. Click **API Keys** in the left menu
4. Click **Create Key**, give it a name, copy the key

### Step 2 — Add your API key to the app

1. Open the `.env` file in this folder (use Notepad or any text editor)
2. Replace `your-api-key-here` with your actual API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxx
   ```
3. Save and close the file

### Step 3 — Run the app

Double-click `run.bat`.

That's it. The app installs what it needs automatically on first run.

---

## How to Read the Results

### Channel Baseline Table
Shown at the start. This is the raw performance data from your campaigns file — before any simulation. It tells you the average, best, and worst uplift per channel based on historical data.

### Round-by-Round Output
During the simulation you will see each agent's decision every round:
- **Which campaign they picked** (objective + target segment)
- **Uplift achieved** — the actual performance score of that campaign
- **Net result** — profit (green) or loss (red)
- **Their reasoning** — one sentence from the agent explaining the pick

### Final Leaderboard
After 4 rounds, agents are ranked by final budget:
- **Final Budget** — started at $1,000; higher is better
- **Total ROI** — percentage gain or loss over 4 rounds
- **Avg Uplift** — average campaign performance score (benchmark is 9%)
- **Hit Benchmark** — how many of the 4 rounds beat the benchmark
- **Status** — FLAGGED means the agent missed benchmark 2+ consecutive rounds

### CMO Recommendations
Three actions are given:
- **Scale Up** — channels consistently above benchmark; put more budget here
- **Hold** — acceptable performance; watch for one more cycle
- **Cut / Review** — missed benchmark repeatedly; pause spend and investigate

---

## Output File

After every run, a `simulation_report.md` file is saved in this folder. It contains the full leaderboard, recommendations, and round-by-round detail for every agent. Open it in any Markdown viewer or text editor.

---

## Running the Simulation Again

Each run is randomised — agents are given different campaign options from the dataset each time. Running it multiple times and comparing results gives you a more reliable picture of which channels perform consistently.

---

## Adjusting Settings

Open `config.py` in a text editor to change:

| Setting | Default | What it does |
|---------|---------|-------------|
| `STARTING_BUDGET` | 1000 | Starting budget per agent (dollars) |
| `ROI_BENCHMARK` | 0.09 | Minimum uplift to pass (9%) |
| `ROUNDS` | 4 | Number of campaign rounds |
| `KILL_THRESHOLD` | 2 | Consecutive misses before flagging |

---

## Troubleshooting

**"ANTHROPIC_API_KEY is not set"**
Open `.env` and make sure your key is pasted correctly with no extra spaces.

**"campaigns.csv not found"**
The file `campaigns.csv` must be in the same folder as `main.py`. Do not move or rename it.

**"Python is not installed"**
Download Python from python.org. During installation, check the box that says "Add Python to PATH".

**The simulation runs but all results show "Default (error)"**
Your API key may be invalid or have no credits. Check your key at console.anthropic.com.
