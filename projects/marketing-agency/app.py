"""
app.py — Marketing Agency Dashboard
FastAPI application with 4-tab dashboard: Leads, Content, Pipeline, Weekly Report.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import DASHBOARD_PORT
from readers import (
    get_linkedin_drafts, get_posted_log, get_recent_blog_posts,
    get_blog_drafts, get_publish_queue, get_publish_log,
    get_case_study_stats, get_pau_ai_stats, get_next_week_plan,
    get_weekly_reports, get_leads_from_api, get_lead_stats_from_api,
    get_recent_commits,
)

app = FastAPI(title="Marketing Agency Dashboard")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, tab: str = "content"):
    # Content tab data
    linkedin_drafts = get_linkedin_drafts()
    posted_log = get_posted_log()
    recent_blogs = get_recent_blog_posts()
    blog_drafts = get_blog_drafts()

    # Pipeline tab data
    publish_queue = get_publish_queue()
    publish_log = get_publish_log()
    case_study_stats = get_case_study_stats()
    pau_ai_stats = get_pau_ai_stats()
    next_week_plan = get_next_week_plan()

    # Weekly report tab data
    weekly_reports = get_weekly_reports()

    # Leads tab data
    leads = get_leads_from_api()
    lead_stats = get_lead_stats_from_api()

    # Recent git activity
    recent_commits = get_recent_commits()

    # Count pending LinkedIn posts (not yet posted)
    posted_files = set()
    for line in posted_log:
        parts = line.split("|")
        if len(parts) >= 2:
            posted_files.add(parts[1].strip())
    pending_posts = [d for d in linkedin_drafts if d["filename"] not in posted_files]

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "tab": tab,
        # Content
        "linkedin_drafts": linkedin_drafts,
        "pending_posts": pending_posts,
        "posted_count": len(posted_files),
        "recent_blogs": recent_blogs,
        "blog_drafts": blog_drafts,
        # Pipeline
        "publish_queue": publish_queue,
        "publish_log": publish_log,
        "case_study_stats": case_study_stats,
        "pau_ai_stats": pau_ai_stats,
        "next_week_plan": next_week_plan,
        # Weekly report
        "weekly_reports": weekly_reports,
        # Leads
        "leads": leads,
        "lead_stats": lead_stats,
        # Activity
        "recent_commits": recent_commits,
    })


@app.get("/health")
async def health():
    return {"status": "ok", "app": "Marketing Agency Dashboard"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=DASHBOARD_PORT, reload=True)
