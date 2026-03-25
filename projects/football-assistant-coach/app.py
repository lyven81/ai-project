import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import plotly.graph_objects as go

load_dotenv()

from players import PLAYERS
from simulation import run_week, check_transfer_risk
from report import select_squad, recommend_formation
from sample_data import SAMPLE_WEEK
from narrative import generate_narratives, apply_narratives
from config import (
    FORMATIONS, DEFAULT_FORMATION,
    THRESHOLD_LINEUP, THRESHOLD_BENCH, THRESHOLD_UNUSED,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Football Assistant Coach",
    page_icon="⚽",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
body { background-color: #f0fdf4; color: #111827; }
.stApp { background-color: #f0fdf4; }

.metric-card {
    background: white;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    border: 1px solid #bbf7d0;
    box-shadow: 0 2px 8px rgba(22,163,74,0.08);
}
.metric-value { font-size: 2rem; font-weight: 700; color: #16a34a; }
.metric-label { font-size: 0.8rem; color: #6b7280; text-transform: uppercase; letter-spacing: 1px; }

.player-card {
    background: white;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    border-left: 4px solid #16a34a;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.player-card.bench  { border-left-color: #f59e0b; }
.player-card.unused { border-left-color: #d1d5db; }
.player-card.risk   { border-left-color: #ef4444; background: #fff7ed; }

.pos-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 8px;
}
.pos-GK  { background: #ede9fe; color: #6d28d9; }
.pos-DEF { background: #dbeafe; color: #1d4ed8; }
.pos-MID { background: #d1fae5; color: #065f46; }
.pos-FWD { background: #fef3c7; color: #92400e; }

.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #15803d;
    padding: 8px 0;
    border-bottom: 2px solid #bbf7d0;
    margin-bottom: 10px;
}
.transfer-badge {
    background: #ef4444;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.7rem;
    margin-left: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚽ Assistant Coach")
    st.markdown("---")
    formation = st.selectbox("Formation", list(FORMATIONS.keys()), index=list(FORMATIONS.keys()).index(DEFAULT_FORMATION))
    mode = st.radio(
        "Data source",
        ["Sample data (instant)", "Live AI simulation"],
        index=0,
        help="Sample data loads instantly. Live simulation calls the AI — takes 15–30 seconds.",
    )
    if mode == "Live AI simulation":
        simulate_weeks = st.radio("Weeks to simulate", ["This week only", "Two weeks (with form)"], index=0)
    st.markdown("---")
    st.markdown("**Score thresholds**")
    st.markdown(f"Starting XI: **{THRESHOLD_LINEUP}+**")
    st.markdown(f"Bench: **{THRESHOLD_BENCH}–{THRESHOLD_LINEUP-1}**")
    st.markdown(f"Unused: **{THRESHOLD_UNUSED}–{THRESHOLD_BENCH-1}**")
    st.markdown(f"Transfer risk: **below {THRESHOLD_UNUSED}** (2 weeks)")
    st.markdown("---")
    run_btn = st.button("Load Results", type="primary", use_container_width=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Football Assistant Coach")
st.markdown("AI-powered player selection based on training performance — team chemistry weighted above individual brilliance.")

# ── Simulation ────────────────────────────────────────────────────────────────
if run_btn:
    st.session_state.pop("results", None)
    st.session_state.pop("selection", None)
    st.session_state.pop("transfer_risk", None)
    st.session_state.pop("week2_scores", None)

    if mode == "Sample data (instant)":
        base_results = SAMPLE_WEEK
        with st.spinner("Generating coaching notes..."):
            narratives = generate_narratives(base_results, PLAYERS)
        results = apply_narratives(base_results, narratives)
        transfer_risk = []
    else:
        last_week_scores = None
        if simulate_weeks == "Two weeks (with form)":
            with st.spinner("Running Week 1 training..."):
                week1 = run_week(PLAYERS)
            last_week_scores = {pid: d["weekly_score"] for pid, d in week1.items()}
            st.session_state["week2_scores"] = last_week_scores

        with st.spinner("Running AI training sessions — evaluating 22 players across 4 sessions..."):
            results = run_week(PLAYERS, last_week_scores=last_week_scores)

        transfer_risk = check_transfer_risk(
            results,
            {pid: s for pid, s in last_week_scores.items()} if last_week_scores else {}
        )

    recommended, fit_scores = recommend_formation(results)

    st.session_state["results"] = results
    st.session_state["transfer_risk"] = transfer_risk
    st.session_state["preferred_formation"] = formation
    st.session_state["recommended_formation"] = recommended
    st.session_state["fit_scores"] = fit_scores
    st.session_state["formation_used"] = formation
    st.session_state["selection"] = select_squad(results, formation, transfer_risk)

# ── Display results ───────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.info("Pick a formation and data source in the sidebar, then click **Load Results**.")
    st.stop()

results            = st.session_state["results"]
transfer_risk      = st.session_state["transfer_risk"]
preferred          = st.session_state.get("preferred_formation", DEFAULT_FORMATION)
recommended        = st.session_state.get("recommended_formation", DEFAULT_FORMATION)
fit_scores         = st.session_state.get("fit_scores", {})
formation_used     = st.session_state.get("formation_used", DEFAULT_FORMATION)

# ── Hybrid advisor panel ───────────────────────────────────────────────────────
if fit_scores:
    mismatch = preferred != recommended
    panel_color = "#fff7ed" if mismatch else "#f0fdf4"
    border_color = "#fb923c" if mismatch else "#86efac"
    icon        = "⚠️" if mismatch else "✅"
    fit_rows = "".join(
        f"<span style='margin-right:18px;'><strong>{f}</strong> — {s:.0f} pts"
        f"{'  ← recommended' if f == recommended else ''}"
        f"{'  ← your choice' if f == preferred and mismatch else ''}</span>"
        for f, s in sorted(fit_scores.items(), key=lambda x: -x[1])
    )
    if mismatch:
        advisory_text = (
            f"Your preferred formation is <strong>{preferred}</strong>, "
            f"but this week's in-form players fit <strong>{recommended}</strong> better "
            f"({fit_scores[recommended]:.0f} pts vs {fit_scores[preferred]:.0f} pts). "
            f"You can keep your formation or switch to the recommended one."
        )
    else:
        advisory_text = (
            f"Your preferred formation <strong>{preferred}</strong> is the best fit "
            f"for this week's in-form players ({fit_scores[preferred]:.0f} pts). No adjustment needed."
        )

    st.markdown(f"""
    <div style="background:{panel_color}; border:2px solid {border_color}; border-radius:10px; padding:16px 20px; margin-bottom:16px;">
      <div style="font-size:1rem; font-weight:700; color:#111827; margin-bottom:8px;">{icon} Formation Advisor</div>
      <div style="font-size:0.9rem; color:#374151; margin-bottom:12px;">{advisory_text}</div>
      <div style="font-size:0.82rem; color:#6b7280;">{fit_rows}</div>
    </div>
    """, unsafe_allow_html=True)

    if mismatch:
        col_keep, col_switch = st.columns(2)
        with col_keep:
            if st.button(f"Keep {preferred} (my choice)", use_container_width=True):
                st.session_state["formation_used"] = preferred
                st.session_state["selection"] = select_squad(results, preferred, transfer_risk)
                st.rerun()
        with col_switch:
            if st.button(f"Switch to {recommended} (recommended)", type="primary", use_container_width=True):
                st.session_state["formation_used"] = recommended
                st.session_state["selection"] = select_squad(results, recommended, transfer_risk)
                st.rerun()

formation_used = st.session_state.get("formation_used", DEFAULT_FORMATION)
selection      = st.session_state["selection"]

# ── Headline metrics ──────────────────────────────────────────────────────────
avg_form  = sum(d["form_score"] for d in results.values()) / len(results)
top_score = max(d["form_score"] for d in results.values())
risk_count = len(transfer_risk)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{formation_used}</div>
        <div class="metric-label">Formation</div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{avg_form:.1f}</div>
        <div class="metric-label">Squad Average Form</div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{top_score:.1f}</div>
        <div class="metric-label">Highest Form Score</div></div>""", unsafe_allow_html=True)
with c4:
    color = "#dc2626" if risk_count > 0 else "#16a34a"
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value" style="color:{color};">{risk_count}</div>
        <div class="metric-label">Transfer Risk</div></div>""", unsafe_allow_html=True)

st.markdown("---")

# ── Squad Selection ───────────────────────────────────────────────────────────
left_col, right_col = st.columns([1.1, 1])

with left_col:
    # Starting XI
    st.markdown('<div class="section-title">Starting XI</div>', unsafe_allow_html=True)
    for p in selection["lineup"]:
        score_color = "#16a34a" if p["form_score"] >= THRESHOLD_LINEUP else "#d97706"
        st.markdown(f"""
        <div class="player-card">
          <span class="pos-badge pos-{p['position']}">{p['position']}</span>
          <strong style="color:#111827;">{p['name']}</strong>
          <span style="float:right; font-weight:700; color:{score_color};">{p['form_score']}</span>
          <br><small style="color:#6b7280;">{p['highlight']}</small>
        </div>""", unsafe_allow_html=True)

    st.markdown('<br><div class="section-title">Bench (5)</div>', unsafe_allow_html=True)
    for p in selection["bench"]:
        score_color = "#d97706" if p["form_score"] >= THRESHOLD_BENCH else "#ea580c"
        st.markdown(f"""
        <div class="player-card bench">
          <span class="pos-badge pos-{p['position']}">{p['position']}</span>
          <strong style="color:#111827;">{p['name']}</strong>
          <span style="float:right; font-weight:700; color:{score_color};">{p['form_score']}</span>
          <br><small style="color:#6b7280;">{p['highlight']}</small>
        </div>""", unsafe_allow_html=True)

    st.markdown('<br><div class="section-title">Unused Squad</div>', unsafe_allow_html=True)
    for p in selection["unused"]:
        is_risk = p["id"] in transfer_risk
        card_cls = "risk" if is_risk else "unused"
        risk_badge = '<span class="transfer-badge">Transfer Risk</span>' if is_risk else ""
        st.markdown(f"""
        <div class="player-card {card_cls}">
          <span class="pos-badge pos-{p['position']}">{p['position']}</span>
          <strong style="color:#111827;">{p['name']}</strong>{risk_badge}
          <span style="float:right; font-weight:700; color:#9ca3af;">{p['form_score']}</span>
          <br><small style="color:#6b7280;">{p['concern']}</small>
        </div>""", unsafe_allow_html=True)

with right_col:
    # Radar / bar chart: all 22 players ranked
    st.markdown('<div class="section-title">Squad Form Rankings</div>', unsafe_allow_html=True)

    chart_data = sorted(
        [{"name": d["name"], "pos": d["position"], "form": d["form_score"],
          "ind": d["sessions"]["Friday"]["individual_score"],
          "chem": d["sessions"]["Friday"]["chemistry_score"],
          "uni": d["sessions"]["Friday"]["universal_score"]}
         for d in results.values()],
        key=lambda x: x["form"], reverse=True
    )
    names  = [f"{p['name']} ({p['pos']})" for p in chart_data]
    forms  = [p["form"] for p in chart_data]
    colors = [
        "#16a34a" if f >= THRESHOLD_LINEUP
        else "#f59e0b" if f >= THRESHOLD_BENCH
        else "#f97316" if f >= THRESHOLD_UNUSED
        else "#ef4444"
        for f in forms
    ]

    fig = go.Figure(go.Bar(
        x=forms,
        y=names,
        orientation="h",
        marker_color=colors,
        text=[f"{f:.1f}" for f in forms],
        textposition="outside",
        textfont=dict(color="#111827"),
    ))
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f9fafb",
        font=dict(color="#374151", size=11),
        xaxis=dict(range=[0, 105], gridcolor="#e5e7eb", color="#6b7280"),
        yaxis=dict(categoryorder="array", categoryarray=names[::-1], tickfont=dict(size=10), color="#374151"),
        height=620,
        margin=dict(l=10, r=50, t=20, b=20),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Session breakdown table (Friday scrimmage)
    st.markdown('<div class="section-title">Friday Scrimmage Breakdown</div>', unsafe_allow_html=True)
    table_rows = []
    for pid, d in sorted(results.items(), key=lambda x: x[1]["form_score"], reverse=True):
        fri = d["sessions"]["Friday"]
        table_rows.append({
            "Player": d["name"],
            "Pos": d["position"],
            "Individual": fri["individual_score"],
            "Team Chemistry": fri["chemistry_score"],
            "Universal": fri["universal_score"],
            "Session Total": fri["total_score"],
            "Form Score": d["form_score"],
        })
    df = pd.DataFrame(table_rows)

    def color_form(val):
        if val >= THRESHOLD_LINEUP:  return "color: #16a34a; font-weight: bold"
        if val >= THRESHOLD_BENCH:   return "color: #d97706; font-weight: bold"
        if val >= THRESHOLD_UNUSED:  return "color: #ea580c; font-weight: bold"
        return "color: #dc2626; font-weight: bold"

    styled = df.style.applymap(color_form, subset=["Form Score"])
    st.dataframe(styled, use_container_width=True, height=400)

# ── Coach notes ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Coach Notes")
expander_cols = st.columns(3)
with expander_cols[0]:
    with st.expander("Starting XI — individual highlights"):
        for p in selection["lineup"]:
            st.markdown(f"**{p['name']}** — {p['highlight']}")
with expander_cols[1]:
    with st.expander("Bench — areas to watch"):
        for p in selection["bench"]:
            st.markdown(f"**{p['name']}** — {p['concern']}")
with expander_cols[2]:
    with st.expander("Unused — development notes"):
        for p in selection["unused"]:
            st.markdown(f"**{p['name']}** — {p['concern']}")

# ── Transfer shortlist ────────────────────────────────────────────────────────
if selection["transfer_shortlist"]:
    st.markdown("---")
    st.error(f"**Transfer Shortlist** — {len(selection['transfer_shortlist'])} player(s) flagged for two consecutive weeks below form threshold.")
    for p in selection["transfer_shortlist"]:
        st.markdown(f"- **{p['name']}** ({p['position']}) — Form: {p['form_score']:.1f}")
