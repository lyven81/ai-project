import json
import os
from datetime import datetime


class StateManager:
    def __init__(self, state_file="state.json"):
        self.state_file = state_file
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.state_file):
            self._save({
                "products": [],
                "twitter_log": [],
                "last_builder_run": None,
                "last_reporter_run": None,
                "week_number": 0
            })

    def _load(self):
        with open(self.state_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_products(self):
        return self._load().get("products", [])

    def add_product(self, product):
        data = self._load()
        data["products"].append(product)
        data["last_builder_run"] = datetime.now().isoformat()
        self._save(data)

    def update_product(self, gumroad_id, updates):
        data = self._load()
        for p in data["products"]:
            if p["id"] == gumroad_id:
                p.update(updates)
                break
        self._save(data)

    def remove_product(self, gumroad_id):
        data = self._load()
        data["products"] = [p for p in data["products"] if p["id"] != gumroad_id]
        self._save(data)

    def log_tweet(self, product_slug, tweet_text, tweet_id):
        data = self._load()
        data["twitter_log"].append({
            "date": datetime.now().isoformat(),
            "product_slug": product_slug,
            "tweet_text": tweet_text,
            "tweet_id": tweet_id
        })
        self._save(data)

    def get_twitter_log(self):
        return self._load().get("twitter_log", [])

    def get_last_promoted(self):
        log = self.get_twitter_log()
        if not log:
            return None
        return log[-1].get("product_slug")

    def increment_week(self):
        data = self._load()
        data["week_number"] = data.get("week_number", 0) + 1
        data["last_reporter_run"] = datetime.now().isoformat()
        for p in data["products"]:
            p["weeks_live"] = p.get("weeks_live", 0) + 1
        self._save(data)
        return data["week_number"]

    def get_week_number(self):
        return self._load().get("week_number", 0)
