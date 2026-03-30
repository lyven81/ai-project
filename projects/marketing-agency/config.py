"""
config.py — Marketing Agency Dashboard Configuration
All paths and constants in one place.
"""

import os

# Pau Analytics repo (live site)
PAU_ANALYTICS_REPO = r"C:\Users\Lenovo\pau-analytics-1.0"
BLOG_DIR = os.path.join(PAU_ANALYTICS_REPO, "blog")
BLOG_DRAFTS_DIR = os.path.join(BLOG_DIR, "drafts")
LINKEDIN_DRAFTS_DIR = os.path.join(BLOG_DIR, "linkedin-drafts")
CASE_STUDY_DIR = os.path.join(PAU_ANALYTICS_REPO, "case-study")
PUBLISH_QUEUE = os.path.join(PAU_ANALYTICS_REPO, "publish-queue.md")
PUBLISH_LOG = os.path.join(PAU_ANALYTICS_REPO, "publish-log.txt")
NEXT_WEEK_PLAN = os.path.join(PAU_ANALYTICS_REPO, "next-week-plan.md")
WEEKLY_REPORTS_DIR = os.path.join(PAU_ANALYTICS_REPO, "reports", "weekly")
POSTED_LOG = os.path.join(LINKEDIN_DRAFTS_DIR, "posted-log.txt")
BLOG_INDEX = os.path.join(BLOG_DIR, "index.html")

# Pau AI templates
PAU_AI_TEMPLATE_DIR = r"C:\Users\Lenovo\Documents\Pau AI\template"
PAU_AI_SHOWCASE_LOG = os.path.join(PAU_ANALYTICS_REPO, "pau-ai-showcase-log.txt")

# Campaign plan
CAMPAIGN_PLAN = r"C:\Users\Lenovo\Documents\Pau Analytics\Strategy - How we plan\campaign-plan.md"

# Web Chat Lead Manager API
LEAD_MANAGER_URL = os.getenv("LEAD_MANAGER_URL", "http://localhost:8000")

# Dashboard server
DASHBOARD_PORT = 8100
