import os
import streamlit as st
from dotenv import load_dotenv

# Try to load environment variables
load_dotenv()

# Check for API key
API_KEY = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY", None)

# Determine if we should run in demo mode
DEMO_MODE = not API_KEY

if DEMO_MODE:
    # Import and run demo mode
    st.set_page_config(
        page_title="Claude PDF Summarizer - Demo",
        page_icon="📄",
        layout="wide"
    )
    
    # Apply portfolio color scheme
    st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
        color: #222;
    }
    .stButton > button {
        background-color: #f5f5dc;
        color: #333;
        border: 1px solid #daa520;
        border-radius: 4px;
    }
    .stButton > button:hover {
        background-color: #daa520;
        color: white;
    }
    .stSelectbox > div > div {
        background-color: #f9f9f9;
        color: #222;
    }
    .stFileUploader > div {
        background-color: #f9f9f9;
        border: 2px dashed #007BFF;
    }
    .stSidebar {
        background-color: #f9f9f9;
    }
    .stSidebar .stSelectbox > div > div {
        background-color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)
    
    from demo_mode import run_demo_mode
    run_demo_mode()
    
else:
    # Import required libraries for full mode
    import PyPDF2
    from anthropic import Anthropic
    
    try:
        client = Anthropic(api_key=API_KEY)
    except Exception as e:
        st.error(f"❌ Failed to initialize Anthropic client: {str(e)}")
        st.stop()

# --- PDF text extraction ---
def extract_text_from_pdf(file) -> str:
    try:
        if file is None:
            return "Error: No file provided"
        
        reader = PyPDF2.PdfReader(file)
        text = ""
        
        if len(reader.pages) == 0:
            return "Error: PDF has no pages"
            
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
        if not text.strip():
            return "Error: No text could be extracted from PDF"
            
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

# --- Prompt builder: fully localized + "answer only in ..." guard ---
def build_prompt(text: str, style: str, language: str, bullet_points: int = 3) -> str:
    if language == "Bahasa Malaysia":
        if style == "Professional Executive Summary":
            return (
                f"Hanya gunakan Bahasa Malaysia dalam jawapan; jangan campurkan bahasa lain. "
                f"Tolong ringkaskan kandungan berikut kepada {bullet_points} isi penting "
                f"dalam gaya formal dan padat untuk pembuat keputusan perniagaan:\n\n{text}"
            )
        elif style == "Simple Version":
            return (
                f"Hanya gunakan Bahasa Malaysia dalam jawapan; jangan campurkan bahasa lain. "
                f"Tolong ringkaskan kandungan berikut kepada {bullet_points} isi penting "
                f"dengan bahasa yang mudah difahami oleh orang ramai:\n\n{text}"
            )
        else:  # For Kids
            return (
                f"Hanya gunakan Bahasa Malaysia dalam jawapan; jangan campurkan bahasa lain. "
                f"Tolong terangkan kandungan berikut untuk kanak-kanak dalam {bullet_points} "
                f"isi mudah difahami:\n\n{text}"
            )

    if language == "中文（简体）":
        if style == "Professional Executive Summary":
            return (
                f"请只用简体中文回答，不要混用其他语言。"
                f"请将以下内容以正式、简洁的语气总结为 {bullet_points} 个要点，适合商业决策者阅读：\n\n{text}"
            )
        elif style == "Simple Version":
            return (
                f"请只用简体中文回答，不要混用其他语言。"
                f"请用简洁易懂的语言将以下内容总结为 {bullet_points} 个要点：\n\n{text}"
            )
        else:  # For Kids
            return (
                f"请只用简体中文回答，不要混用其他语言。"
                f"请用适合 10 岁儿童理解的方式，将以下内容总结为 {bullet_points} 个简单要点：\n\n{text}"
            )

    # Default to English
    if style == "Professional Executive Summary":
        return (
            f"Answer only in English; do not mix other languages. "
            f"Write in a formal, concise tone for business decision-makers. "
            f"Summarize the following into {bullet_points} bullet points:\n\n{text}"
        )
    elif style == "Simple Version":
        return (
            f"Answer only in English; do not mix other languages. "
            f"Write in simple, everyday language. "
            f"Summarize the following into {bullet_points} bullet points:\n\n{text}"
        )
    else:  # For Kids
        return (
            f"Answer only in English; do not mix other languages. "
            f"Explain in a fun, friendly way for a 10-year-old. "
            f"Summarize the following into {bullet_points} bullet points:\n\n{text}"
        )

# --- Translate preview snippet to selected language ---
def translate_preview(snippet: str, language: str) -> str:
    """Return preview text in the selected language without extra commentary."""
    if not snippet.strip():
        return ""
    # English needs no translation
    if language == "English":
        return snippet

    if language == "Bahasa Malaysia":
        instruction = (
            "Terjemahkan teks berikut ke dalam Bahasa Malaysia sahaja. "
            "Pulangkan HANYA terjemahan tanpa nota tambahan."
        )
    elif language == "中文（简体）":
        instruction = (
            "请将下列文本翻译成简体中文。只返回翻译内容，不要添加任何说明或括号。"
        )
    else:
        # Fallback
        return snippet

    try:
        resp = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            messages=[{"role": "user", "content": f"{instruction}\n\n{snippet}"}],
        )
        if resp.content and len(resp.content) > 0:
            return resp.content[0].text
        else:
            return snippet
    except Exception as e:
        st.warning(f"Translation failed, showing original text: {str(e)}")
        return snippet

# --- Summarize with Claude ---
def summarize_with_claude(prompt: str) -> str:
    try:
        if not prompt or not prompt.strip():
            return "Error: Empty prompt provided"
        
        if len(prompt) > 100000:  # Reasonable limit to prevent token overflow
            return "Error: Content too long for processing"
        
        resp = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}],
        )
        
        if resp.content and len(resp.content) > 0:
            return resp.content[0].text
        else:
            return "Error: No response received from Claude API"
            
    except Exception as e:
        return f"Error from Claude API: {str(e)}"

# ----------------- Streamlit UI -----------------
st.set_page_config(page_title="Claude PDF Summarizer", layout="centered")

# Apply portfolio color scheme
st.markdown("""
<style>
.stApp {
    background-color: #ffffff;
    color: #222;
}
.stButton > button {
    background-color: #f5f5dc;
    color: #333;
    border: 1px solid #daa520;
    border-radius: 4px;
}
.stButton > button:hover {
    background-color: #daa520;
    color: white;
}
.stSelectbox > div > div {
    background-color: #f9f9f9;
    color: #222;
}
.stFileUploader > div {
    background-color: #f9f9f9;
    border: 2px dashed #007BFF;
}
.stSidebar {
    background-color: #f9f9f9;
}
.stSidebar .stSelectbox > div > div {
    background-color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

st.title("📄 Claude 3 PDF Summarizer")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

summary_style = st.selectbox(
    "Choose summary style",
    ["Professional Executive Summary", "Simple Version", "For Kids"],
)

language = st.selectbox(
    "Choose summary language",
    ["English", "Bahasa Malaysia", "中文（简体）"],
)

bullet_points = st.slider("Number of bullet points", 3, 10, 3)

if uploaded_file:
    with st.spinner("Reading PDF..."):
        full_text = extract_text_from_pdf(uploaded_file)
    
    if full_text.startswith("Error:"):
        st.error(full_text)
        st.stop()

    # Preview: first N chars, translated to selected language
    preview_chars = 1000
    snippet = full_text[:preview_chars]
    with st.spinner("Preparing preview..."):
        preview_text = translate_preview(snippet, language)

    st.subheader("Extracted Content Preview")
    st.text(preview_text + ("" if len(full_text) <= preview_chars else "..."))

    if st.button("Summarize PDF"):
        if len(full_text.strip()) < 50:
            st.error("❌ PDF content too short to summarize effectively.")
            st.stop()
            
        with st.spinner("Summarizing with Claude..."):
            prompt = build_prompt(full_text, summary_style, language, bullet_points)
            summary = summarize_with_claude(prompt)
            
        if summary.startswith("Error:"):
            st.error(summary)
        else:
            st.subheader("📝 Claude Summary")
            st.markdown(summary)
