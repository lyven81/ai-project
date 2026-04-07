"""
Consultancy Mentor — Backend Server
Flask app serving the UI, lesson picker, and chat endpoint.
Chat is grounded in the wiki + user's real schedule, priorities, and progress.
"""
import os
import re
import random
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory

# ---------- Paths ----------
DOCS = Path(r"C:\Users\Lenovo\Documents")
KLLM = DOCS / "Knowledge LLM"
MENTOR_DIR = KLLM / "Consultancy Mentor"
WIKI_DIR = MENTOR_DIR / "wiki"
WORK_PLAN = DOCS / "Work Plan"
PROGRESS_LOG_DIR = MENTOR_DIR / "progress-log"
CHAT_LOG_DIR = MENTOR_DIR / "chat-log"
CHAT_LOG_DIR.mkdir(exist_ok=True)
CONFIG_FILE = KLLM / "config.txt"

# ---------- Load API key ----------
def load_api_key():
    if not CONFIG_FILE.exists():
        return None
    for line in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("ANTHROPIC_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

API_KEY = load_api_key()

# ---------- Anthropic client ----------
anthropic_client = None
if API_KEY and API_KEY != "paste-your-key-here":
    try:
        from anthropic import Anthropic
        anthropic_client = Anthropic(api_key=API_KEY)
    except ImportError:
        print("WARNING: anthropic package not installed. Run: pip install anthropic")

# ---------- Load wiki chunks for retrieval + lessons ----------
def load_wiki_chunks():
    """Split every wiki .md file into sections by ## headings."""
    chunks = []
    if not WIKI_DIR.exists():
        return chunks
    for md_file in WIKI_DIR.rglob("*.md"):
        topic = md_file.parent.name if md_file.parent != WIKI_DIR else "index"
        text = md_file.read_text(encoding="utf-8")
        sections = re.split(r"\n(?=## )", text)
        for sec in sections:
            sec = sec.strip()
            if len(sec) < 100:
                continue
            title_match = re.match(r"##\s*(.+)", sec)
            title = title_match.group(1).strip() if title_match else topic
            chunks.append({"topic": topic, "title": title, "text": sec})
    return chunks

WIKI_CHUNKS = load_wiki_chunks()
print(f"Loaded {len(WIKI_CHUNKS)} wiki chunks from {WIKI_DIR}")

# ---------- Load always-on context (Layer 1) ----------
def load_layer1_context():
    parts = ["## User Profile", (
        "Solo data analyst and content creator based in Malaysia. "
        "Running Pau Analytics (consultancy for Malaysian SMEs), "
        "data-analyst-portfolio (GitHub Pages with case studies), "
        "ai-project portfolio, and Junior Youth educational content. "
        "Still building brand, portfolio, and client base. "
        "Experienced with Python, SQL, data analysis. Learning AI engineering + Cloud Run deploys. "
        "Not yet fully specialized in a single vertical — positioning is still being refined."
    )]
    def add(label, path):
        if path and path.exists():
            try:
                parts.append(f"\n## {label}\n" + path.read_text(encoding="utf-8").strip())
            except Exception:
                pass
    add("Weekly Schedule", WORK_PLAN / "schedule.md")
    add("Priority Order", WORK_PLAN / "priority-order.md")
    # Latest progress log
    if PROGRESS_LOG_DIR.exists():
        logs = sorted(PROGRESS_LOG_DIR.glob("2026-W*.md"), reverse=True)
        if logs:
            add(f"This Week's Progress ({logs[0].stem})", logs[0])
    return "\n".join(parts)

LAYER1_CONTEXT = load_layer1_context()
print(f"Layer 1 context: {len(LAYER1_CONTEXT)} chars")

# ---------- Simple keyword retrieval ----------
STOPWORDS = set("the a an is are was were be been am i you we they it this that of to in on for with at by from as and or but if then so do does did how what when where why who which my our your".split())

def tokenize(text):
    return [w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOPWORDS and len(w) > 2]

def retrieve(question, k=3):
    q_tokens = set(tokenize(question))
    if not q_tokens:
        return WIKI_CHUNKS[:k]
    scored = []
    for chunk in WIKI_CHUNKS:
        chunk_tokens = set(tokenize(chunk["text"]))
        score = len(q_tokens & chunk_tokens)
        # boost if question keywords in title
        title_tokens = set(tokenize(chunk["title"]))
        score += 2 * len(q_tokens & title_tokens)
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:k]]

# ---------- System prompt ----------
SYSTEM_PROMPT = """You are a unified-voice mentor for a solo data analyst building Pau Analytics, a Malaysian SME data consultancy. You also advise on his data-analyst-portfolio, ai-project portfolio, and Junior Youth content work.

CRITICAL RULES:
1. Reply in MAXIMUM 2 paragraphs. Each paragraph MAXIMUM 3 sentences.
2. Use direct, clear, simple language. No jargon. No filler. No motivational fluff.
3. Candid tone — tell the truth even when it's uncomfortable. Be encouraging when real progress has been made, not as a default.
4. Never say "Baker says" or "Weiss recommends" — speak as one trusted advisor using "I".
5. Ground EVERY recommendation in the user's actual context (schedule, priorities, progress, skill level). Never give generic advice.
6. Use the wiki frameworks below as the logic behind your answer, but translate them to the user's real situation.
7. If the wiki doesn't cover the question, say so in one sentence and use general reasoning.
8. End with a specific next action when the question calls for one.
9. Never suggest something the user clearly lacks capacity or skill for without naming that gap first.

The user is still building, not yet established. Encourage real wins. Flag real drift. Don't pretend things are further along than they are."""

# ---------- Flask app ----------
app = Flask(__name__)

@app.route("/")
def root():
    return send_from_directory(str(MENTOR_DIR), "mentor-ui.html")

@app.route("/<path:filename>")
def serve_file(filename):
    # Serve any file under Documents (wiki, work plan, etc.)
    full = DOCS / filename
    if not full.exists() or not full.is_file():
        return "Not found", 404
    return send_from_directory(str(full.parent), full.name)

@app.route("/api/lesson")
def api_lesson():
    if not WIKI_CHUNKS:
        return jsonify({"error": "No wiki chunks loaded"}), 500
    chunk = random.choice(WIKI_CHUNKS)
    return jsonify({
        "topic": chunk["topic"].replace("-", " ").title(),
        "title": chunk["title"],
        "text": chunk["text"]
    })

def append_chat_log(question, answer, sources):
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = CHAT_LOG_DIR / f"{today}.md"
    timestamp = datetime.now().strftime("%H:%M")
    src_line = ", ".join(f"{s['topic']}/{s['title']}" for s in sources) if sources else "—"
    entry = (
        f"\n## {timestamp}\n\n"
        f"**Q:** {question}\n\n"
        f"**A:** {answer}\n\n"
        f"_Sources: {src_line}_\n"
    )
    if not log_file.exists():
        log_file.write_text(f"# Chat Log — {today}\n", encoding="utf-8")
    with log_file.open("a", encoding="utf-8") as f:
        f.write(entry)

@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json(force=True)
    question = (data.get("question") or "").strip()
    history = data.get("history") or []  # [{role: 'user'|'assistant', content: '...'}, ...]
    if not question:
        return jsonify({"error": "Empty question"}), 400
    if anthropic_client is None:
        return jsonify({"error": "API key not configured. Paste your key into config.txt and restart."}), 500

    retrieved = retrieve(question, k=3)
    wiki_context = "\n\n---\n\n".join(
        f"[{c['topic']} — {c['title']}]\n{c['text']}" for c in retrieved
    )
    current_user_message = f"""USER CONTEXT (always-on reality):
{LAYER1_CONTEXT}

---

RELEVANT WIKI FRAMEWORKS:
{wiki_context}

---

QUESTION: {question}"""

    # Build messages list: prior history + current question
    messages = []
    for msg in history[-10:]:  # cap at last 10
        role = msg.get("role")
        content = (msg.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": current_user_message})

    try:
        resp = anthropic_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=messages
        )
        answer = resp.content[0].text
        sources = [{"topic": c["topic"], "title": c["title"]} for c in retrieved]
        try:
            append_chat_log(question, answer, sources)
        except Exception as log_err:
            print(f"Chat log write failed: {log_err}")
        return jsonify({"answer": answer, "sources": sources})
    except Exception as e:
        return jsonify({"error": f"LLM call failed: {e}"}), 500

if __name__ == "__main__":
    port = 8765
    print(f"\nConsultancy Mentor running at http://localhost:{port}")
    print(f"Open: http://localhost:{port}/")
    print("Press Ctrl+C to stop.\n")
    app.run(host="127.0.0.1", port=port, debug=False)
