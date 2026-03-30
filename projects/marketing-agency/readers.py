"""
readers.py — Data readers for the Marketing Agency Dashboard
Reads content files, lead data, and reports from local filesystem and API.
"""

import os
import glob
import re
import subprocess
from datetime import datetime, timedelta
from typing import Optional
import httpx

from config import (
    BLOG_DIR, BLOG_DRAFTS_DIR, LINKEDIN_DRAFTS_DIR, CASE_STUDY_DIR,
    PUBLISH_QUEUE, PUBLISH_LOG, NEXT_WEEK_PLAN, WEEKLY_REPORTS_DIR,
    POSTED_LOG, BLOG_INDEX, PAU_AI_TEMPLATE_DIR, PAU_AI_SHOWCASE_LOG,
    CAMPAIGN_PLAN, LEAD_MANAGER_URL, PAU_ANALYTICS_REPO
)


def read_file_safe(path: str) -> str:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# ── Content Tab ──────────────────────────────────────────────────────────────

def get_linkedin_drafts() -> list[dict]:
    drafts = []
    if not os.path.isdir(LINKEDIN_DRAFTS_DIR):
        return drafts
    for f in sorted(glob.glob(os.path.join(LINKEDIN_DRAFTS_DIR, "*.txt")), reverse=True):
        basename = os.path.basename(f)
        if basename == "posted-log.txt":
            continue
        mod_time = datetime.fromtimestamp(os.path.getmtime(f))
        content = read_file_safe(f)
        # Determine post type from prefix
        if basename.startswith("pau-ai-solution-"):
            post_type = "Pau AI — Solution"
            brand = "Pau AI"
        elif basename.startswith("pau-ai-usecase-"):
            post_type = "Pau AI — Use Case"
            brand = "Pau AI"
        elif basename.startswith("insight-"):
            post_type = "Pau Analytics — Insight"
            brand = "Pau Analytics"
        else:
            post_type = "Pau Analytics — Blog Teaser"
            brand = "Pau Analytics"
        drafts.append({
            "filename": basename,
            "post_type": post_type,
            "brand": brand,
            "date": mod_time.strftime("%Y-%m-%d"),
            "preview": content[:200].strip() if content else "(empty)",
            "full_content": content.strip(),
            "word_count": len(content.split()) if content else 0,
        })
    return drafts


def get_posted_log() -> list[str]:
    content = read_file_safe(POSTED_LOG)
    return [line.strip() for line in content.splitlines() if line.strip()]


def get_recent_blog_posts(days: int = 14) -> list[dict]:
    posts = []
    if not os.path.isdir(BLOG_DIR):
        return posts
    cutoff = datetime.now() - timedelta(days=days)
    for f in glob.glob(os.path.join(BLOG_DIR, "*.html")):
        basename = os.path.basename(f)
        if basename in ("index.html", "template.html"):
            continue
        mod_time = datetime.fromtimestamp(os.path.getmtime(f))
        if mod_time >= cutoff:
            posts.append({
                "slug": basename.replace(".html", ""),
                "date": mod_time.strftime("%Y-%m-%d"),
                "url": f"https://www.pauanalytics.com/blog/{basename}",
            })
    return sorted(posts, key=lambda x: x["date"], reverse=True)


def get_blog_drafts() -> list[dict]:
    drafts = []
    if not os.path.isdir(BLOG_DRAFTS_DIR):
        return drafts
    for f in glob.glob(os.path.join(BLOG_DRAFTS_DIR, "*.md")):
        basename = os.path.basename(f)
        mod_time = datetime.fromtimestamp(os.path.getmtime(f))
        drafts.append({
            "filename": basename,
            "date": mod_time.strftime("%Y-%m-%d"),
        })
    return sorted(drafts, key=lambda x: x["date"], reverse=True)


# ── Pipeline Tab ─────────────────────────────────────────────────────────────

def get_publish_queue() -> Optional[dict]:
    content = read_file_safe(PUBLISH_QUEUE)
    if not content.strip():
        return None
    result = {"raw": content}
    for line in content.splitlines():
        if line.startswith("**Case study slug:**"):
            result["slug"] = line.split(":**", 1)[1].strip()
        elif line.startswith("**Blog language:**"):
            result["language"] = line.split(":**", 1)[1].strip()
        elif line.startswith("**Status:**"):
            result["status"] = line.split(":**", 1)[1].strip()
        elif line.startswith("**Scheduled:**"):
            result["scheduled"] = line.split(":**", 1)[1].strip()
    return result


def get_publish_log() -> list[dict]:
    content = read_file_safe(PUBLISH_LOG)
    entries = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 3:
            entries.append({
                "date": parts[0],
                "slug": parts[1],
                "language": parts[2],
                "status": parts[3] if len(parts) > 3 else "",
            })
    return entries


def get_campaign_phase() -> dict:
    content = read_file_safe(CAMPAIGN_PLAN)
    if not content:
        return {"phase": "Unknown", "description": "Campaign plan not found"}
    today = datetime.now()
    # Simple heuristic: check for phase markers in the campaign plan
    return {
        "raw_available": True,
        "today": today.strftime("%Y-%m-%d"),
    }


def get_case_study_stats() -> dict:
    total = 0
    if os.path.isdir(CASE_STUDY_DIR):
        total = len([f for f in os.listdir(CASE_STUDY_DIR) if f.endswith(".html")])
    published_slugs = set()
    for entry in get_publish_log():
        published_slugs.add(entry["slug"])
    # Count blog posts
    blog_count = 0
    if os.path.isdir(BLOG_DIR):
        blog_count = len([f for f in os.listdir(BLOG_DIR)
                          if f.endswith(".html") and f not in ("index.html", "template.html")])
    return {
        "total_case_studies": total,
        "scheduled": len(published_slugs),
        "remaining": total - len(published_slugs),
        "blog_posts_live": blog_count,
    }


def get_pau_ai_stats() -> dict:
    categories = []
    if os.path.isdir(PAU_AI_TEMPLATE_DIR):
        categories = [d for d in os.listdir(PAU_AI_TEMPLATE_DIR)
                       if os.path.isdir(os.path.join(PAU_AI_TEMPLATE_DIR, d))]
    showcased = []
    content = read_file_safe(PAU_AI_SHOWCASE_LOG)
    if content:
        showcased = [line.strip() for line in content.splitlines() if line.strip()]
    return {
        "total_categories": len(categories),
        "categories": categories,
        "showcased": len(showcased),
        "remaining": len(categories) - len(showcased),
    }


def get_next_week_plan() -> Optional[str]:
    return read_file_safe(NEXT_WEEK_PLAN) or None


# ── Weekly Report Tab ────────────────────────────────────────────────────────

def get_weekly_reports() -> list[dict]:
    reports = []
    if not os.path.isdir(WEEKLY_REPORTS_DIR):
        return reports
    for f in sorted(glob.glob(os.path.join(WEEKLY_REPORTS_DIR, "*.md")), reverse=True):
        basename = os.path.basename(f)
        content = read_file_safe(f)
        reports.append({
            "filename": basename,
            "week": basename.replace(".md", ""),
            "preview": content[:300].strip() if content else "(empty)",
            "full_content": content.strip(),
        })
    return reports


# ── Leads Tab ────────────────────────────────────────────────────────────────

def get_leads_from_api() -> list[dict]:
    try:
        resp = httpx.get(f"{LEAD_MANAGER_URL}/api/leads", timeout=2)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []


def get_lead_stats_from_api() -> dict:
    try:
        resp = httpx.get(f"{LEAD_MANAGER_URL}/api/stats", timeout=2)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {
        "total": 0, "this_week": 0, "needs_followup": 0,
        "ch_a_week": 0, "ch_b_week": 0, "ch_w_week": 0,
        "blog_performance": [],
    }


# ── Git Activity ─────────────────────────────────────────────────────────────

def get_recent_commits(days: int = 7) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", PAU_ANALYTICS_REPO, "log",
             f"--since={days} days ago", "--oneline", "--no-merges"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        pass
    return []
