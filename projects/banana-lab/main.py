"""
Banana Lab — Main Scheduler
============================
Runs all agents on their weekly schedule.

Schedule:
  Monday    09:00  Builder  → create PDF + listing copy, prompt manual Gumroad upload
  Monday    09:30  Site     → rebuild website with all registered products
  Sunday    18:00  Reporter → email weekly summary

Usage:
  python main.py                        — start the scheduler (runs indefinitely)
  python main.py --builder              — run Builder once immediately (test)
  python main.py --reporter             — run Reporter once immediately (test)
  python main.py --all                  — run Builder + Site + Reporter once (full test)
  python main.py --register SLUG URL    — register a manually uploaded Gumroad product
"""

import sys
import json
import time
import schedule
from datetime import datetime

from agents.builder_agent import BuilderAgent
from agents.site_agent import SiteAgent
from agents.reporter_agent import ReporterAgent


def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_config(config):
    required = ["claude_api_key", "email_sender", "email_app_password", "email_recipient"]
    missing = [k for k in required if config.get(k, "").startswith("YOUR_")]
    if missing:
        print("ERROR: Please fill in the following values in config.json:")
        for k in missing:
            print(f"  - {k}")
        sys.exit(1)


def run_builder(config):
    print(f"\n[{datetime.now():%Y-%m-%d %H:%M}] Running Builder Agent...")
    BuilderAgent(config).run()

def run_site(config):
    print(f"\n[{datetime.now():%Y-%m-%d %H:%M}] Running Site Agent...")
    SiteAgent(config).run()

def run_reporter(config):
    print(f"\n[{datetime.now():%Y-%m-%d %H:%M}] Running Reporter Agent...")
    ReporterAgent(config).run()

def run_monday_pipeline(config):
    run_builder(config)
    run_site(config)


def main():
    config = load_config()
    validate_config(config)

    args = sys.argv[1:]

    # --- Register a manually uploaded product ---
    if "--register" in args:
        idx = args.index("--register")
        if len(args) < idx + 3:
            print("Usage: python main.py --register SLUG GUMROAD_URL")
            sys.exit(1)
        slug = args[idx + 1]
        url  = args[idx + 2]
        if BuilderAgent(config).register(slug, url):
            run_site(config)
        return

    # --- One-shot test flags ---
    if "--builder" in args:
        run_monday_pipeline(config)
        return
    if "--reporter" in args:
        run_reporter(config)
        return
    if "--all" in args:
        run_monday_pipeline(config)
        run_reporter(config)
        return

    # --- Scheduled mode ---
    print("Banana Lab scheduler started. Press Ctrl+C to stop.\n")

    schedule.every().monday.at("09:00").do(run_monday_pipeline, config=config)
    schedule.every().sunday.at("18:00").do(run_reporter, config=config)

    print("Schedule:")
    print("  Monday    09:00  Builder + Site Agent")
    print("  Sunday    18:00  Reporter Agent")
    print()

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
