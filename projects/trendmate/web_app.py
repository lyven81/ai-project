"""
TrendMate — Web Chat Interface
Malaysian Fashion Seller Research Assistant
Color scheme: Rose Pink + Deep Purple (Fashion / Trendy)
"""

import os
from pathlib import Path
from datetime import datetime

import streamlit as st
from anthropic import Anthropic
from tavily import TavilyClient
from dotenv import load_dotenv

# ── Setup ─────────────────────────────────────────────────────────────────────
load_dotenv()
SCRIPT_DIR = Path(__file__).parent

PRESET_QUESTIONS = [
    "What women's fashion styles are trending in Malaysia this week?",
    "What is the best price range to sell baju kurung moden on Shopee Malaysia?",
    "What men's clothing categories are selling well on TikTok Shop Malaysia right now?",
    "Where can I source affordable women's casual wear in bulk for resale in Malaysia?",
    "What should I prepare as an online fashion seller for the upcoming 11.11 sale?",
    "What fashion hashtags should I use on TikTok Malaysia to get more views?",
    "What are the top trending colours and prints in Malaysian fashion right now?",
    "What is the average profit margin for fashion sellers on Lazada Malaysia?",
    "What modest fashion or hijab styles are popular among Malaysian buyers this season?",
    "How early should I stock up for Hari Raya and what styles sell best that season?",
]

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TrendMate — Fashion Research",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS: Rose Pink + Deep Purple ──────────────────────────────────────────────
st.markdown("""
<style>
    /* Background */
    .stApp { background-color: #FDF5F8; }

    /* Hide Streamlit default chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #2D1B4E !important;
        border-right: 1px solid #3D2560;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div { color: #D8C8EC !important; }
    section[data-testid="stSidebar"] hr { border-color: #3D2560; }

    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: rgba(214,51,132,0.12);
        border: 1px solid rgba(214,51,132,0.35);
        color: #F0D0E4 !important;
        border-radius: 8px;
        text-align: left;
        font-size: 0.8rem;
        line-height: 1.45;
        padding: 8px 12px;
        transition: background 0.2s;
        white-space: normal;
        height: auto;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(214,51,132,0.28);
        border-color: #D63384;
    }

    /* Download button in sidebar */
    section[data-testid="stSidebar"] .stDownloadButton > button {
        background-color: #D63384 !important;
        color: white !important;
        border: none;
        font-weight: 600;
        border-radius: 8px;
    }

    /* Main content */
    .main .block-container { padding-top: 0.5rem; max-width: 860px; }

    /* App header */
    .app-header {
        background: linear-gradient(135deg, #2D1B4E 0%, #6B21A8 100%);
        padding: 18px 24px 14px 24px;
        border-radius: 14px;
        margin-bottom: 16px;
        border-left: 5px solid #D63384;
    }
    .app-header-title {
        color: #F9A8D4;
        font-size: 1.55rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.3px;
    }
    .app-header-sub {
        color: #C4A8D8;
        font-size: 0.82rem;
        margin: 5px 0 0 0;
    }
    .app-header-badge {
        display: inline-block;
        background: rgba(214,51,132,0.2);
        color: #F9A8D4;
        border: 1px solid rgba(214,51,132,0.4);
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.72rem;
        margin-right: 5px;
        margin-top: 8px;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
        margin-bottom: 6px;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageContent"]) {
        background: white;
        border: 1px solid #F0DCE8;
        box-shadow: 0 1px 4px rgba(214,51,132,0.07);
    }

    /* Expander (copy panel) */
    .streamlit-expanderHeader {
        font-size: 0.78rem !important;
        color: #9B6B8A !important;
        background: transparent !important;
    }

    /* Sidebar label */
    .sidebar-label {
        color: #F9A8D4 !important;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }

    /* Welcome message box */
    .welcome-box {
        background: white;
        border: 1px solid #F0DCE8;
        border-left: 4px solid #D63384;
        border-radius: 10px;
        padding: 14px 18px;
        color: #4A2040;
        font-size: 0.88rem;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ── Cached clients ────────────────────────────────────────────────────────────
@st.cache_resource
def init_clients():
    # Read from Streamlit secrets (Cloud) or .env file (local)
    try:
        ak = st.secrets["ANTHROPIC_API_KEY"]
        tk = st.secrets["TAVILY_API_KEY"]
    except (KeyError, FileNotFoundError):
        ak = os.getenv("ANTHROPIC_API_KEY")
        tk = os.getenv("TAVILY_API_KEY")
    if not ak or not tk:
        return None, None
    return Anthropic(api_key=ak), TavilyClient(api_key=tk)

@st.cache_data
def load_system_prompt():
    p = SCRIPT_DIR / "system-prompt.txt"
    return p.read_text(encoding="utf-8") if p.exists() else "You are a market research assistant for Malaysian online fashion sellers."

# ── Tools ─────────────────────────────────────────────────────────────────────
TOOLS = [{
    "name": "search_web",
    "description": "Search the web for Malaysian fashion market info, trending products, competitor pricing, supplier options, and platform updates.",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "The search query"}},
        "required": ["query"]
    }
}]

def search_web(query, tavily):
    try:
        res = tavily.search(query=query, max_results=5, search_depth="advanced")
        lines = []
        for r in res.get("results", []):
            lines.append(f"Source: {r.get('url','')}\nTitle: {r.get('title','')}\nContent: {r.get('content','')}\n---")
        return "\n".join(lines) or "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"

def run_agent(user_message, history, client, tavily, system_prompt):
    history.append({"role": "user", "content": user_message})
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system_prompt,
            tools=TOOLS,
            messages=history
        )
        if response.stop_reason == "end_turn":
            text = "\n".join(b.text for b in response.content if hasattr(b, "text"))
            history.append({"role": "assistant", "content": response.content})
            return text
        elif response.stop_reason == "tool_use":
            history.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use" and block.name == "search_web":
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": search_web(block.input["query"], tavily)
                    })
            history.append({"role": "user", "content": tool_results})
        else:
            return "Something went wrong. Please try again."

# ── Session state ─────────────────────────────────────────────────────────────
if "messages"     not in st.session_state: st.session_state.messages     = []
if "conv_history" not in st.session_state: st.session_state.conv_history = []
if "pending_q"    not in st.session_state: st.session_state.pending_q    = None

# ── Init clients ──────────────────────────────────────────────────────────────
client, tavily = init_clients()
if not client:
    st.error("⚠️ API keys missing. Please check your .env file and restart.")
    st.stop()

system_prompt = load_system_prompt()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 👗 TrendMate")
    st.markdown('<p style="font-size:0.75rem;color:#9B7DB8;">Malaysian Fashion Seller Research</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<p class="sidebar-label">Quick Questions</p>', unsafe_allow_html=True)
    for i, q in enumerate(PRESET_QUESTIONS):
        if st.button(f"{i+1}. {q}", key=f"q{i}", use_container_width=True):
            st.session_state.pending_q = q

    st.markdown("---")

    if st.button("🗑️  Clear Conversation", use_container_width=True):
        st.session_state.messages     = []
        st.session_state.conv_history = []
        st.rerun()

    if st.session_state.messages:
        lines = [f"TrendMate — Research Export\nDate: {datetime.now().strftime('%d %b %Y, %H:%M')}\n{'='*50}\n"]
        for m in st.session_state.messages:
            role = "You" if m["role"] == "user" else "TrendMate"
            lines.append(f"[{role}]\n{m['content']}\n")
        st.download_button(
            "⬇️  Download Conversation",
            data="\n".join(lines),
            file_name=f"trendmate_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <p class="app-header-title">👗 TrendMate</p>
    <p class="app-header-sub">Malaysian Fashion Seller Research Assistant</p>
    <span class="app-header-badge">Shopee</span>
    <span class="app-header-badge">Lazada</span>
    <span class="app-header-badge">TikTok Shop</span>
    <span class="app-header-badge">Suppliers</span>
    <span class="app-header-badge">Seasons</span>
</div>
""", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-box">
        👋 Welcome! Pick a question from the sidebar or type your own below.<br>
        I cover trends, pricing, suppliers, platform updates, and seasonal planning for Malaysian fashion sellers.
    </div>
    """, unsafe_allow_html=True)

# Display chat history
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "👗"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            with st.expander("📋 Copy this answer"):
                st.code(msg["content"], language="")

# ── Process incoming question ─────────────────────────────────────────────────
prompt = None
if st.session_state.pending_q:
    prompt = st.session_state.pending_q
    st.session_state.pending_q = None
elif q := st.chat_input("Type your fashion market question here..."):
    prompt = q

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="👗"):
        with st.spinner("Researching..."):
            try:
                answer = run_agent(prompt, st.session_state.conv_history, client, tavily, system_prompt)
            except Exception as e:
                answer = f"Error: {str(e)}. Please check your internet connection and try again."
        st.markdown(answer)
        with st.expander("📋 Copy this answer"):
            st.code(answer, language="")

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
