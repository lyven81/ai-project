import json
import anthropic
from config import MODEL, STARTING_BUDGET, ROI_BENCHMARK, KILL_THRESHOLD

PERSONAS = {
    "Email": {
        "name": "Emma",
        "title": "Email Marketing Agent",
        "style": "patient, data-driven, retention-focused",
        "strength": "nurturing existing customers and re-engaging lapsed ones",
    },
    "Social": {
        "name": "Sam",
        "title": "Social Media Agent",
        "style": "creative, trend-aware, engagement-obsessed",
        "strength": "acquiring new customers and building brand awareness",
    },
    "Paid Search": {
        "name": "Parker",
        "title": "Paid Search Agent",
        "style": "analytical, ROI-obsessed, intent-focused",
        "strength": "capturing high-intent buyers ready to convert",
    },
    "Display": {
        "name": "Diana",
        "title": "Display Advertising Agent",
        "style": "visual-first, audience-focused, retargeting expert",
        "strength": "re-engaging lapsed customers at scale through visuals",
    },
    "Affiliate": {
        "name": "Alex",
        "title": "Affiliate Marketing Agent",
        "style": "performance-driven, partner-focused, cost-conscious",
        "strength": "cost-effective acquisition through external partners",
    },
}


class MarketingAgent:
    def __init__(self, channel):
        self.channel = channel
        self.persona = PERSONAS[channel]
        self.name = f"{self.persona['name']} ({self.persona['title']})"
        self.budget = STARTING_BUDGET
        self.history = []
        self._below_count = 0
        self.flagged = False
        self._client = anthropic.Anthropic()

    def decide(self, options, round_num):
        opts_text = ""
        for i, c in enumerate(options, 1):
            opts_text += (
                f"\n  Option {i}: Objective={c['objective']}, "
                f"Segment={c['segment']}, Duration={c['duration']} days"
            )

        prompt = (
            f"You are {self.persona['name']}, a {self.channel} marketing specialist.\n"
            f"Style: {self.persona['style']}\n"
            f"Strength: {self.persona['strength']}\n\n"
            f"Current budget: ${self.budget:.0f}\n"
            f"Round: {round_num}/4\n"
            f"ROI benchmark: {ROI_BENCHMARK * 100:.0f}% minimum uplift\n\n"
            f"Campaign options for your {self.channel} channel:{opts_text}\n\n"
            f"Pick the option most likely to beat the benchmark.\n"
            f"Allocate 15–25% of your budget.\n\n"
            f'Respond ONLY with valid JSON: {{"choice": 1, "budget_pct": 20, "reasoning": "one sentence"}}'
        )

        try:
            response = self._client.messages.create(
                model=MODEL,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            if "{" in text:
                text = text[text.index("{") : text.rindex("}") + 1]
            decision = json.loads(text)
        except Exception as e:
            decision = {"choice": 1, "budget_pct": 20, "reasoning": f"Default (error: {e})"}

        choice = max(0, min(int(decision.get("choice", 1)) - 1, len(options) - 1))
        pct = max(0.15, min(float(decision.get("budget_pct", 20)) / 100, 0.25))
        reasoning = decision.get("reasoning", "No reasoning given")
        return options[choice], pct, reasoning

    def apply_result(self, campaign, allocated, round_num, reasoning):
        uplift = campaign["uplift"]

        if uplift >= ROI_BENCHMARK:
            earnings = allocated * (1 + uplift)
            outcome = "PROFIT"
            self._below_count = 0
        else:
            earnings = allocated * (uplift / ROI_BENCHMARK)
            outcome = "LOSS"
            self._below_count += 1

        if self._below_count >= KILL_THRESHOLD:
            self.flagged = True

        net = earnings - allocated
        self.budget += net

        record = {
            "round": round_num,
            "campaign": campaign,
            "allocated": allocated,
            "uplift": uplift,
            "earnings": earnings,
            "net": net,
            "outcome": outcome,
            "reasoning": reasoning,
        }
        self.history.append(record)
        return record

    @property
    def total_roi(self):
        if not self.history:
            return 0.0
        spent = sum(h["allocated"] for h in self.history)
        earned = sum(h["earnings"] for h in self.history)
        return (earned - spent) / spent * 100

    @property
    def avg_uplift(self):
        if not self.history:
            return 0.0
        return sum(h["uplift"] for h in self.history) / len(self.history)

    @property
    def rounds_above_benchmark(self):
        return sum(1 for h in self.history if h["uplift"] >= ROI_BENCHMARK)
