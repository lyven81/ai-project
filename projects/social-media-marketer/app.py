import os
import time
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from config import ROUNDS, STARTING_BUDGET, ROI_BENCHMARK
from data import load_campaigns, channel_stats
from agents import MarketingAgent, PERSONAS
from simulation import run_round
from report import build_report, save_markdown

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Social Media Marketer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* General */
[data-testid="stAppViewContainer"] { background-color: #0e1117; }
[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }

/* Header */
.app-header {
    background: linear-gradient(135deg, #0d1b2a 0%, #1a2744 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 24px;
}
.app-title { font-size: 2rem; font-weight: 700; color: #58a6ff; margin: 0; }
.app-subtitle { color: #8b949e; font-size: 0.95rem; margin-top: 4px; }

/* Metric cards */
.metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
}
.metric-label { font-size: 0.78rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-value { font-size: 1.6rem; font-weight: 700; color: #e6edf3; margin-top: 4px; }

/* Agent cards */
.agent-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.agent-name { font-weight: 600; color: #58a6ff; font-size: 1rem; }
.agent-channel { font-size: 0.8rem; color: #8b949e; }
.profit { color: #3fb950; font-weight: 600; }
.loss { color: #f85149; font-weight: 600; }
.reasoning { color: #8b949e; font-size: 0.85rem; font-style: italic; margin-top: 4px; }

/* Recommendation cards */
.rec-scale {
    background: #0d2818;
    border: 1px solid #3fb950;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.rec-hold {
    background: #2b2000;
    border: 1px solid #d29922;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.rec-cut {
    background: #2d1117;
    border: 1px solid #f85149;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.rec-title { font-weight: 700; font-size: 1rem; margin-bottom: 4px; }
.rec-body { font-size: 0.88rem; color: #8b949e; }

/* Section headers */
.section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #e6edf3;
    border-bottom: 1px solid #30363d;
    padding-bottom: 8px;
    margin-bottom: 16px;
    margin-top: 8px;
}

/* Status badge */
.badge-ok { background: #0d2818; color: #3fb950; padding: 2px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600; }
.badge-flagged { background: #2d1117; color: #f85149; padding: 2px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────

if "simulation_done" not in st.session_state:
    st.session_state.simulation_done = False
if "agents" not in st.session_state:
    st.session_state.agents = None
if "round_logs" not in st.session_state:
    st.session_state.round_logs = []
if "report" not in st.session_state:
    st.session_state.report = None


# ── Load data ─────────────────────────────────────────────────────────────────

@st.cache_data
def get_campaigns():
    return load_campaigns()

@st.cache_data
def get_channel_stats():
    return channel_stats(load_campaigns())

try:
    campaigns = get_campaigns()
    stats = get_channel_stats()
except FileNotFoundError:
    st.error("campaigns.csv not found. Make sure it is in the same folder as app.py.")
    st.stop()


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Simulation Settings")
    st.divider()

    rounds = st.slider("Rounds", min_value=2, max_value=8, value=ROUNDS, step=1)
    starting_budget = st.number_input("Starting Budget ($)", min_value=500, max_value=10000,
                                       value=int(STARTING_BUDGET), step=500)
    benchmark_pct = st.slider("ROI Benchmark (%)", min_value=5, max_value=20,
                               value=int(ROI_BENCHMARK * 100), step=1)
    benchmark = benchmark_pct / 100

    st.divider()
    st.markdown("### 📁 Dataset")
    st.markdown(f"**{len(campaigns)} campaigns** across **{len(stats)} channels**")

    st.divider()
    st.markdown("### 🤖 Agents")
    for ch, p in PERSONAS.items():
        st.markdown(f"**{p['name']}** — {ch}")

    st.divider()

    if st.button("🔄 Reset Simulation", use_container_width=True):
        st.session_state.simulation_done = False
        st.session_state.agents = None
        st.session_state.round_logs = []
        st.session_state.report = None
        st.rerun()


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="app-header">
  <div class="app-title">📊 Social Media Marketer</div>
  <div class="app-subtitle">Multi-Agent Marketing Channel Simulation &nbsp;·&nbsp; Powered by Claude AI</div>
</div>
""", unsafe_allow_html=True)


# ── Channel baseline ──────────────────────────────────────────────────────────

st.markdown('<div class="section-header">Channel Baseline</div>', unsafe_allow_html=True)

cols = st.columns(len(stats))
for col, (ch, s) in zip(cols, sorted(stats.items(), key=lambda x: x[1]["avg"], reverse=True)):
    color = "#3fb950" if s["avg"] >= benchmark else "#f85149"
    col.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">{ch}</div>
      <div class="metric-value" style="color:{color}">{s['avg']*100:.1f}%</div>
      <div style="font-size:0.78rem;color:#8b949e;margin-top:4px;">avg uplift &nbsp;·&nbsp; {s['count']} campaigns</div>
    </div>
    """, unsafe_allow_html=True)

st.caption(f"Benchmark: {benchmark_pct}% minimum uplift. Green = above benchmark, Red = below.")
st.divider()


# ── Run button ────────────────────────────────────────────────────────────────

if not st.session_state.simulation_done:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "your-api-key-here":
        st.warning("API key not set. Open the `.env` file and paste your Anthropic API key, then restart the app.")
        st.stop()

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        run_clicked = st.button("▶ Run Simulation", type="primary", use_container_width=True)
    with col_info:
        st.markdown(
            f"<div style='padding-top:8px;color:#8b949e;'>"
            f"5 agents &nbsp;·&nbsp; {rounds} rounds &nbsp;·&nbsp; "
            f"${starting_budget:,} each &nbsp;·&nbsp; {benchmark_pct}% benchmark"
            f"</div>",
            unsafe_allow_html=True,
        )

    if run_clicked:
        # Override config values with sidebar selections
        import config as _cfg
        _cfg.ROUNDS = rounds
        _cfg.STARTING_BUDGET = float(starting_budget)
        _cfg.ROI_BENCHMARK = benchmark

        agents = [MarketingAgent(ch) for ch in PERSONAS]
        round_logs = []

        progress_bar = st.progress(0, text="Starting simulation...")
        status_container = st.container()

        total_steps = len(agents) * rounds

        with status_container:
            for round_num in range(1, rounds + 1):
                st.markdown(f'<div class="section-header">Round {round_num} of {rounds}</div>',
                            unsafe_allow_html=True)
                round_results = []

                for i, agent in enumerate(agents):
                    record = run_round(agent, campaigns, round_num)
                    round_results.append((agent, record))

                    step = (round_num - 1) * len(agents) + (i + 1)
                    pct = int(step / total_steps * 100)
                    progress_bar.progress(pct, text=f"Round {round_num}/{rounds} — {agent.persona['name']} done")

                    outcome_class = "profit" if record["outcome"] == "PROFIT" else "loss"
                    c = record["campaign"]
                    st.markdown(f"""
                    <div class="agent-card">
                      <span class="agent-name">{agent.persona['name']}</span>
                      <span class="agent-channel"> &nbsp;·&nbsp; {agent.channel}</span><br>
                      Picked: <b>{c['objective']}</b> → <b>{c['segment']}</b>
                      &nbsp;|&nbsp; Uplift: <b>{record['uplift']*100:.1f}%</b>
                      &nbsp;|&nbsp; Allocated: <b>${record['allocated']:.0f}</b>
                      &nbsp;|&nbsp; Net: <span class="{outcome_class}">${record['net']:+.0f} {record['outcome']}</span>
                      <div class="reasoning">{record['reasoning']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                round_logs.append(round_results)

        progress_bar.progress(100, text="Simulation complete!")
        time.sleep(0.3)
        progress_bar.empty()

        report = build_report(agents)
        save_markdown(agents, report)

        st.session_state.agents = agents
        st.session_state.round_logs = round_logs
        st.session_state.report = report
        st.session_state.simulation_done = True
        st.rerun()


# ── Results ───────────────────────────────────────────────────────────────────

if st.session_state.simulation_done:
    agents = st.session_state.agents
    report = st.session_state.report

    st.success("Simulation complete. Results below.")

    # Summary KPIs
    st.markdown('<div class="section-header">Summary</div>', unsafe_allow_html=True)
    best = report["ranked"][0]
    worst = report["ranked"][-1]
    flagged_count = sum(1 for a in agents if a.flagged)
    avg_roi = sum(a.total_roi for a in agents) / len(agents)

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f"""<div class="metric-card">
      <div class="metric-label">Best Channel</div>
      <div class="metric-value" style="color:#3fb950;font-size:1.2rem;">{best.channel}</div>
      <div style="font-size:0.78rem;color:#8b949e;">{best.total_roi:+.1f}% ROI</div>
    </div>""", unsafe_allow_html=True)

    k2.markdown(f"""<div class="metric-card">
      <div class="metric-label">Weakest Channel</div>
      <div class="metric-value" style="color:#f85149;font-size:1.2rem;">{worst.channel}</div>
      <div style="font-size:0.78rem;color:#8b949e;">{worst.total_roi:+.1f}% ROI</div>
    </div>""", unsafe_allow_html=True)

    k3.markdown(f"""<div class="metric-card">
      <div class="metric-label">Avg Portfolio ROI</div>
      <div class="metric-value" style="color:{'#3fb950' if avg_roi >= 0 else '#f85149'};">{avg_roi:+.1f}%</div>
    </div>""", unsafe_allow_html=True)

    k4.markdown(f"""<div class="metric-card">
      <div class="metric-label">Channels Flagged</div>
      <div class="metric-value" style="color:{'#f85149' if flagged_count > 0 else '#3fb950'};">{flagged_count}</div>
      <div style="font-size:0.78rem;color:#8b949e;">of {len(agents)} total</div>
    </div>""", unsafe_allow_html=True)

    st.divider()

    # Leaderboard + Chart side by side
    left, right = st.columns([3, 2])

    with left:
        st.markdown('<div class="section-header">Final Leaderboard</div>', unsafe_allow_html=True)

        rows = []
        for i, agent in enumerate(report["ranked"], 1):
            rows.append({
                "Rank": i,
                "Agent": agent.persona["name"],
                "Channel": agent.channel,
                "Final Budget": f"${agent.budget:.0f}",
                "Total ROI": f"{agent.total_roi:+.1f}%",
                "Avg Uplift": f"{agent.avg_uplift * 100:.1f}%",
                "Benchmark Hit": f"{agent.rounds_above_benchmark}/{len(agent.history)}",
                "Status": "FLAGGED" if agent.flagged else "OK",
            })

        df = pd.DataFrame(rows)

        def style_status(val):
            if val == "FLAGGED":
                return "color: #f85149; font-weight: bold;"
            return "color: #3fb950; font-weight: bold;"

        def style_roi(val):
            if val.startswith("+"):
                return "color: #3fb950; font-weight: bold;"
            elif val.startswith("-"):
                return "color: #f85149; font-weight: bold;"
            return ""

        styled = df.style.applymap(style_status, subset=["Status"]).applymap(style_roi, subset=["Total ROI"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

    with right:
        st.markdown('<div class="section-header">ROI by Channel</div>', unsafe_allow_html=True)

        channels_chart = [a.channel for a in report["ranked"]]
        rois = [round(a.total_roi, 1) for a in report["ranked"]]
        colors = ["#3fb950" if r >= 0 else "#f85149" for r in rois]

        fig = go.Figure(go.Bar(
            x=rois,
            y=channels_chart,
            orientation="h",
            marker_color=colors,
            text=[f"{r:+.1f}%" for r in rois],
            textposition="outside",
        ))
        fig.update_layout(
            paper_bgcolor="#161b22",
            plot_bgcolor="#161b22",
            font_color="#e6edf3",
            xaxis=dict(
                gridcolor="#30363d",
                zeroline=True,
                zerolinecolor="#58a6ff",
                zerolinewidth=1.5,
                title="ROI %",
            ),
            yaxis=dict(gridcolor="#30363d"),
            margin=dict(l=10, r=40, t=10, b=10),
            height=280,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Recommendations
    st.markdown('<div class="section-header">CMO Recommendations</div>', unsafe_allow_html=True)

    rec1, rec2, rec3 = st.columns(3)

    with rec1:
        if report["scale"]:
            for ch in report["scale"]:
                st.markdown(f"""<div class="rec-scale">
                  <div class="rec-title" style="color:#3fb950;">⬆ Scale Up — {ch}</div>
                  <div class="rec-body">Consistent above benchmark. Increase budget allocation here.</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="rec-scale"><div class="rec-title" style="color:#3fb950;">⬆ Scale Up</div><div class="rec-body">No channels qualified this run.</div></div>', unsafe_allow_html=True)

    with rec2:
        if report["hold"]:
            for ch in report["hold"]:
                st.markdown(f"""<div class="rec-hold">
                  <div class="rec-title" style="color:#d29922;">⏸ Hold — {ch}</div>
                  <div class="rec-body">Acceptable. Monitor one more cycle before deciding.</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="rec-hold"><div class="rec-title" style="color:#d29922;">⏸ Hold</div><div class="rec-body">No channels in hold status.</div></div>', unsafe_allow_html=True)

    with rec3:
        if report["cut"]:
            for ch in report["cut"]:
                st.markdown(f"""<div class="rec-cut">
                  <div class="rec-title" style="color:#f85149;">⬇ Cut / Review — {ch}</div>
                  <div class="rec-body">Missed benchmark repeatedly. Pause spend and investigate.</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="rec-cut"><div class="rec-title" style="color:#f85149;">⬇ Cut / Review</div><div class="rec-body">No channels flagged for cutting.</div></div>', unsafe_allow_html=True)

    st.divider()

    # Round-by-round detail (collapsed by default)
    with st.expander("Round-by-Round Detail", expanded=False):
        for round_idx, round_results in enumerate(st.session_state.round_logs, 1):
            st.markdown(f"**Round {round_idx}**")
            for agent, record in round_results:
                c = record["campaign"]
                outcome_color = "#3fb950" if record["outcome"] == "PROFIT" else "#f85149"
                st.markdown(
                    f"- **{agent.persona['name']}** [{agent.channel}] — "
                    f"{c['objective']} → {c['segment']} | "
                    f"Uplift: **{record['uplift']*100:.1f}%** | "
                    f"Net: <span style='color:{outcome_color}'>${record['net']:+.0f}</span> | "
                    f"*{record['reasoning']}*",
                    unsafe_allow_html=True,
                )
            st.markdown("")

    # Download report
    st.divider()
    try:
        with open("simulation_report.md", "r", encoding="utf-8") as f:
            report_text = f.read()
        st.download_button(
            label="⬇ Download Report (Markdown)",
            data=report_text,
            file_name="simulation_report.md",
            mime="text/markdown",
            use_container_width=False,
        )
    except FileNotFoundError:
        pass
