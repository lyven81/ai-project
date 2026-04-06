"""Good Company — Prompt library for stock research."""

PLAIN_LANGUAGE = """
Write in plain language that a smart business owner can understand. Short sentences.
If you use a financial term, explain it in parentheses the first time.
Plain language does not mean shallow thinking — be thorough and professional."""

# Phase 1: Is this a good company?
PHASE_1 = {
    "cheat_sheet": {
        "name": "Company Overview",
        "step": 1,
        "visual_type": "metrics",
        "instruction": """Turn this quarter report into an investor cheat sheet.
Include:
- What the company actually does (one paragraph)
- How it makes money
- Biggest growth drivers
- Biggest risks
- Key numbers: revenue, net profit, EPS (earnings per share), profit margin
- Segment breakdown if available
- Management tone — are they confident, cautious, or dodging questions?
- What to watch next quarter
""" + PLAIN_LANGUAGE + """

At the very end of your response, include this data block with numbers from the report.
Use the exact format — the app reads this to display visual cards:

VISUAL_DATA_START
{"metrics": [
  {"label": "Revenue", "value": "(amount with currency)", "change": "(YoY % change or 'N/A')"},
  {"label": "Net Profit", "value": "(amount)", "change": "(YoY % change or 'N/A')"},
  {"label": "EPS", "value": "(amount)", "change": "(YoY % change or 'N/A')"},
  {"label": "Profit Margin", "value": "(percentage)", "change": "(change in pp or 'N/A')"}
]}
VISUAL_DATA_END

QUARTER REPORT:
{report_text}"""
    },

    "forensic_check": {
        "name": "Forensic Check",
        "step": 2,
        "visual_type": "scorecard",
        "instruction": """Check this quarter report like an accountant looking for problems.
Review the financials and management commentary for:

- Revenue quality — is revenue growing from real demand, or from one-off items?
- Earnings quality — are profits from actual operations, or from accounting tricks?
- Cash flow strength — does the cash coming in match the profit reported?
- Debt risk — is borrowing increasing? Can the company pay it back?
- Dilution risk — is the company issuing more shares (which reduces your ownership)?
- Accounting signals — any signs of aggressive accounting? (recognizing revenue too early, hiding costs as "investments")
- Narrative vs numbers — does what management says match what the numbers show?

If you find red flags, explain each one clearly.
If no red flags are found, say so directly.
""" + PLAIN_LANGUAGE + """

At the very end, include this data block. Rate each area: "green" (clean), "yellow" (minor concern), or "red" (serious flag):

VISUAL_DATA_START
{"checks": [
  {"area": "Revenue Quality", "rating": "(green/yellow/red)", "note": "(one line)"},
  {"area": "Earnings Quality", "rating": "(green/yellow/red)", "note": "(one line)"},
  {"area": "Cash Flow", "rating": "(green/yellow/red)", "note": "(one line)"},
  {"area": "Debt Risk", "rating": "(green/yellow/red)", "note": "(one line)"},
  {"area": "Dilution Risk", "rating": "(green/yellow/red)", "note": "(one line)"},
  {"area": "Accounting Signals", "rating": "(green/yellow/red)", "note": "(one line)"}
]}
VISUAL_DATA_END

QUARTER REPORT:
{report_text}"""
    },

    "business_vs_stock": {
        "name": "Verdict",
        "step": 3,
        "visual_type": "verdict",
        "instruction": """Based on this quarter report, answer two separate questions:
1. Is this a GOOD BUSINESS? (strong product, reliable profits, good management)
2. Is this a GOOD STOCK? (priced fairly or cheaply relative to its quality)

A good business is not always a good stock. A weak business can sometimes be a good buy if it's cheap enough.

Score each dimension on a scale of 1 to 10:
- Business quality — does it have a lasting advantage?
- Management quality — honest, competent, aligned with shareholders?
- Financial strength — solid balance sheet, healthy cash flow?
- Valuation — does the stock price seem fair based on the numbers?
- Upside probability — is the stock more likely to go up or down from here?

Then classify it as ONE of these four:
1. Great business, bad stock — good company but overpriced right now
2. Bad business, good stock trade — weak company but cheap enough to be interesting
3. Great business, great stock — good company at a fair or cheap price
4. Avoid for now — weak company and not cheap enough to justify the risk

Explain your reasoning in plain terms.
""" + PLAIN_LANGUAGE + """

At the very end, include this data block:

VISUAL_DATA_START
{"verdict": "(1, 2, 3, or 4)",
 "verdict_label": "(the classification text, e.g. Great business, great stock)",
 "scores": [
  {"dimension": "Business Quality", "score": 0},
  {"dimension": "Management", "score": 0},
  {"dimension": "Financial Strength", "score": 0},
  {"dimension": "Valuation", "score": 0},
  {"dimension": "Upside Probability", "score": 0}
]}
VISUAL_DATA_END

QUARTER REPORT:
{report_text}"""
    },
}

# Read More: Supplementary reports (available after Phase 1)
READ_MORE = {
    "deep_dive": {
        "name": "Deep Dive",
        "visual_type": "none",
        "instruction": """Based on this quarter report, write a thorough company analysis covering:
1. Business model — what does this company sell, and to whom?
2. Revenue drivers — where does the money come from?
3. Cost structure — what are the biggest expenses?
4. Competitive advantages — what stops competitors from taking their customers?
5. Key risks — what could go wrong?
6. Management quality — do they seem competent and honest?
7. Industry position — are they a leader, challenger, or follower?
8. Outlook — what is likely to happen in the next 1-2 years?

Then give:
- 3 reasons to be bullish (optimistic)
- 3 reasons to be bearish (cautious)
- Your balanced conclusion
""" + PLAIN_LANGUAGE + """

QUARTER REPORT:
{report_text}"""
    },

    "earnings_breakdown": {
        "name": "Earnings Breakdown",
        "visual_type": "none",
        "instruction": """Read this quarter report carefully and break it into:
- What improved compared to previous quarters
- What got worse
- What management is confident about
- What management is avoiding or downplaying
- Hidden warning signs (things not said directly but implied by the numbers)
- Important numbers investors should track next quarter

Then summarize the whole report in plain English — imagine you are explaining it to a friend who is smart but knows nothing about finance.

End with: "What actually matters from this report is..."
""" + PLAIN_LANGUAGE + """

QUARTER REPORT:
{report_text}"""
    },

    "stress_test": {
        "name": "Scenario Stress Test",
        "visual_type": "scenarios",
        "instruction": """Based on this quarter report, imagine three futures for this company:

1. BULL SCENARIO — everything goes right
2. BASE SCENARIO — business continues as it is now
3. BEAR SCENARIO — things go wrong

For each scenario, estimate:
- Revenue direction (growing, flat, or shrinking)
- Profit margin direction (expanding, stable, or compressing)
- Market sentiment (investors optimistic, neutral, or worried)
- What would trigger this scenario

Then answer:
- What would have to happen for this stock to massively outperform?
- What would completely break the investment case?
""" + PLAIN_LANGUAGE + """

At the very end, include this data block:

VISUAL_DATA_START
{"scenarios": [
  {"name": "Bull", "revenue": "(direction)", "margin": "(direction)", "trigger": "(one line)", "probability": "(low/medium/high)"},
  {"name": "Base", "revenue": "(direction)", "margin": "(direction)", "trigger": "(one line)", "probability": "(low/medium/high)"},
  {"name": "Bear", "revenue": "(direction)", "margin": "(direction)", "trigger": "(one line)", "probability": "(low/medium/high)"}
]}
VISUAL_DATA_END

QUARTER REPORT:
{report_text}"""
    },

    "company_comparison": {
        "name": "Company Comparison",
        "visual_type": "comparison",
        "instruction": """Compare these two companies as investment options based on their quarter reports.

Score each company from 1 to 10 on these dimensions, and state who wins each:
- Business model strength
- Revenue growth
- Profit margins
- Cash flow health
- Balance sheet strength
- Valuation (which is cheaper?)
- Competitive moat
- Management quality
- Risk level (lower is better)

Then answer:
- If I could buy only one for a 3-year hold, which one and why?
- If I wanted lower risk, which one and why?
""" + PLAIN_LANGUAGE + """

At the very end, include this data block:

VISUAL_DATA_START
{"company_a": "(name)", "company_b": "(name)",
 "dimensions": [
  {"name": "Business Model", "score_a": 0, "score_b": 0, "winner": "(A or B)"},
  {"name": "Revenue Growth", "score_a": 0, "score_b": 0, "winner": "(A or B)"},
  {"name": "Profit Margins", "score_a": 0, "score_b": 0, "winner": "(A or B)"},
  {"name": "Cash Flow", "score_a": 0, "score_b": 0, "winner": "(A or B)"},
  {"name": "Balance Sheet", "score_a": 0, "score_b": 0, "winner": "(A or B)"},
  {"name": "Valuation", "score_a": 0, "score_b": 0, "winner": "(A or B)"},
  {"name": "Moat", "score_a": 0, "score_b": 0, "winner": "(A or B)"},
  {"name": "Management", "score_a": 0, "score_b": 0, "winner": "(A or B)"},
  {"name": "Risk (lower=better)", "score_a": 0, "score_b": 0, "winner": "(A or B)"}
]}
VISUAL_DATA_END

COMPANY A QUARTER REPORT:
{report_text_a}

COMPANY B QUARTER REPORT:
{report_text_b}"""
    },
}

# Phase 2: Should I invest?
PHASE_2 = {
    "valuation": {
        "name": "Valuation Check",
        "step": 4,
        "visual_type": "valuation",
        "instruction": """Based on the numbers in this quarter report, estimate whether this stock is cheap, fairly priced, or expensive.

Use whichever of these methods the data supports:
- P/E ratio (price divided by earnings — how many years of profit you are paying for)
- EV/EBITDA (company value divided by operating cash profit — useful for comparing companies with different debt levels)
- Price/Sales (price divided by revenue — useful when profits are unstable)
- Free cash flow yield (cash the business generates divided by its market price — like an interest rate on your investment)

For each method you use, explain:
- What the number means in plain terms
- Whether it looks cheap, fair, or expensive compared to similar companies

Then give three price scenarios:
- Cheap case — what price would be a bargain
- Fair value — what price reflects the fundamentals
- Expensive case — at what price is the market too optimistic

If exact share price is not in the report, work with the ratios and multiples available.
Show your assumptions clearly.
""" + PLAIN_LANGUAGE + """

At the very end, include this data block:

VISUAL_DATA_START
{"cheap": "(price or ratio)", "fair": "(price or ratio)", "expensive": "(price or ratio)",
 "current_assessment": "(cheap/fair/expensive)",
 "methods_used": ["(list of valuation methods used)"]}
VISUAL_DATA_END

QUARTER REPORT:
{report_text}"""
    },

    "bull_vs_bear": {
        "name": "Bull vs Bear",
        "step": 5,
        "visual_type": "bullbear",
        "instruction": """Based on this quarter report, build the strongest case FOR and AGAINST investing.

BULL CASE (reasons to buy):
- Why revenue can keep growing
- What could make profit margins expand
- Product or brand strength
- Positive industry trends
- Upcoming events that could push the stock up

BEAR CASE (reasons to avoid):
- Why growth might slow down
- What could squeeze profit margins
- Competition threats
- Balance sheet worries
- Events that could push the stock down

After presenting both sides, tell me:
Which side is stronger right now, and why?
""" + PLAIN_LANGUAGE + """

At the very end, include this data block:

VISUAL_DATA_START
{"bull_points": 0, "bear_points": 0,
 "winner": "(bull or bear)",
 "confidence": "(low/medium/high)",
 "one_line": "(one sentence summary of which side wins and why)"}
VISUAL_DATA_END

QUARTER REPORT:
{report_text}"""
    },

    "risk_check": {
        "name": "Personal Risk Check",
        "step": 6,
        "visual_type": "none",
        "instruction": """I am thinking about buying this company's stock.
My intended purchase price: {price}
How long I plan to hold: {horizon}
My risk tolerance: {risk_tolerance}

Based on this quarter report, tell me straight:
- What can go right if I buy
- What can go wrong
- What I might be underestimating (blind spots)
- What type of investor this stock fits best (income, growth, value, speculative)
- What new information would make this a stronger buy
- What new information would make me walk away

Be direct. If this stock does not fit my profile, say so clearly and explain why.
Do not sugarcoat. I would rather hear an uncomfortable truth than a comfortable lie.
""" + PLAIN_LANGUAGE + """

QUARTER REPORT:
{report_text}"""
    },
}

# Step 7: Final Scorecard (after Phase 2)
FINAL = {
    "final_scorecard": {
        "name": "Final Scorecard",
        "step": 7,
        "visual_type": "scorecard_final",
        "instruction": """You are scoring this company against a personal investment yardstick.
Based on everything in this quarter report, rate the company on each of these 7 dimensions.

SCORING CRITERIA (rate each 1 to 10):

1. FUNDAMENTALS & PROFITABILITY
   - Is EPS (earnings per share) positive? Ideally above 0.01.
   - Is ROE (return on equity — how efficiently the company uses shareholder money) at least 5%?
   - Are profits real and recurring, not from one-off items?

2. FINANCIAL HEALTH & SOLVENCY
   - Is debt manageable? Can the company pay its obligations?
   - Is the balance sheet getting stronger or weaker over time?
   - Net tangible assets (NTA) — is each share backed by real assets worth at least 0.20?

3. VALUATION
   - Does the P/E ratio (if available) fall between 4 and 15? (fair range for value investors)
   - Price-to-book (PTBV) below 1.5? (means you're not overpaying for assets)
   - Price-to-sales (PSR) below 2? (means the stock price isn't too high vs revenue)

4. BUSINESS MOAT
   - Does the company have a lasting competitive advantage?
   - Can competitors easily copy what they do?
   - Is the brand, product, or market position defensible?

5. CASH FLOW & DIVIDENDS
   - Does the company generate real cash from operations (not just paper profits)?
   - Does it pay dividends? Yield of at least 1% is a positive signal.
   - Is free cash flow growing or shrinking?

6. MANAGEMENT & OUTLOOK
   - Does management seem honest and competent based on their commentary?
   - Are their forward-looking statements realistic or overly optimistic?
   - Is the company investing in the right areas for future growth?

7. LIQUIDITY
   - Is the stock actively traded (enough volume to buy/sell easily)?
   - Is the market cap above RM 50 million (avoids very small, risky companies)?
   - Note: if trading volume or market cap data is not in the report, state "data not available" rather than guessing.

FINAL VERDICT:
After scoring all 7 dimensions, give an overall verdict:
- PASS — majority of dimensions score 7 or above, no dimension below 4
- BORDERLINE — mixed scores, some strong and some weak areas
- FAIL — multiple dimensions below 5, or any critical red flag

List what additional data you would need (live stock price, trading volume, market cap) to complete the assessment fully.
""" + PLAIN_LANGUAGE + """

At the very end, include this data block:

VISUAL_DATA_START
{"dimensions": [
  {"name": "Fundamentals & Profitability", "score": 0, "note": "(one line)"},
  {"name": "Financial Health & Solvency", "score": 0, "note": "(one line)"},
  {"name": "Valuation", "score": 0, "note": "(one line)"},
  {"name": "Business Moat", "score": 0, "note": "(one line)"},
  {"name": "Cash Flow & Dividends", "score": 0, "note": "(one line)"},
  {"name": "Management & Outlook", "score": 0, "note": "(one line)"},
  {"name": "Liquidity", "score": 0, "note": "(one line)"}
],
 "overall": "(PASS/BORDERLINE/FAIL)",
 "avg_score": 0,
 "missing_data": ["(list of data not available in the report)"]}
VISUAL_DATA_END

QUARTER REPORT:
{report_text}"""
    },
}
