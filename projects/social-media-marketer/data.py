import csv
import random
from datetime import datetime


def load_campaigns(filepath="campaigns.csv"):
    campaigns = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            start = datetime.strptime(row["start_date"], "%Y-%m-%d")
            end = datetime.strptime(row["end_date"], "%Y-%m-%d")
            duration = (end - start).days
            campaigns.append({
                "id": int(row["campaign_id"]),
                "channel": row["channel"],
                "objective": row["objective"],
                "segment": row["target_segment"],
                "uplift": float(row["expected_uplift"]),
                "duration": duration,
            })
    return campaigns


def get_options(campaigns, channel, n=3):
    pool = [c for c in campaigns if c["channel"] == channel]
    return random.sample(pool, min(n, len(pool)))


def channel_stats(campaigns):
    stats = {}
    for c in campaigns:
        ch = c["channel"]
        if ch not in stats:
            stats[ch] = []
        stats[ch].append(c["uplift"])
    return {
        ch: {
            "count": len(uplifts),
            "avg": round(sum(uplifts) / len(uplifts), 4),
            "best": round(max(uplifts), 4),
            "worst": round(min(uplifts), 4),
        }
        for ch, uplifts in stats.items()
    }
