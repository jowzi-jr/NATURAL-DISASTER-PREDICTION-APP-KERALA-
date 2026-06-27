import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="DisasterAI — Emergency Response",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0b0f1a;
    color: #d4dbe8;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #0e1420 !important;
    border-right: 1px solid #1a2235 !important;
}

/* ── Logo ── */
.logo-wrap {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0 1rem 1.4rem 1rem;
    border-bottom: 1px solid #1a2235;
    margin-bottom: 1.4rem;
}
.logo-dot {
    width: 36px; height: 36px;
    background: #f59e0b;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    animation: pulse-dot 2.5s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%, 100% { box-shadow: 0 0 0 0 rgba(245,158,11,0.4); }
    50%       { box-shadow: 0 0 0 8px rgba(245,158,11,0); }
}
.logo-title {
    font-size: 1rem;
    font-weight: 600;
    color: #f0f4ff;
    letter-spacing: -0.01em;
}
.logo-sub {
    font-size: 0.7rem;
    color: #4a5a72;
    font-weight: 400;
}

/* ── Sidebar labels ── */
.sidebar-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #3a4a60;
    padding: 0 1rem;
    margin-bottom: 6px;
}

/* ── Sidebar buttons ── */
.stButton > button {
    background: transparent !important;
    color: #7a8fa8 !important;
    border: 1px solid #1a2235 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    padding: 8px 14px !important;
    text-align: left !important;
    width: 100% !important;
    transition: all 0.18s ease !important;
}
.stButton > button:hover {
    background: #131d2e !important;
    border-color: #f59e0b !important;
    color: #f59e0b !important;
}

/* ── Status pill ── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: #0d1f12;
    border: 1px solid #1a3826;
    color: #34d399;
    font-size: 0.72rem;
    font-weight: 500;
    padding: 5px 12px;
    border-radius: 20px;
    margin-bottom: 1.8rem;
    letter-spacing: 0.01em;
}
.status-dot-live {
    width: 7px; height: 7px;
    background: #34d399;
    border-radius: 50%;
    animation: blink 1.8s ease-in-out infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}

/* ── Page header ── */
.page-header {
    margin-bottom: 0.4rem;
}
.page-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: #f0f4ff;
    letter-spacing: -0.02em;
}
.page-sub {
    font-size: 0.83rem;
    color: #4a5a72;
    margin-top: 3px;
    margin-bottom: 1.4rem;
    font-weight: 400;
}

/* ── Divider ── */
.divider {
    border: none;
    border-top: 1px solid #1a2235;
    margin: 1.2rem 0;
}

/* ── Chat bubbles ── */
.bubble-user {
    display: flex;
    justify-content: flex-end;
    margin: 10px 0;
    animation: slide-in-right 0.22s ease;
}
@keyframes slide-in-right {
    from { opacity: 0; transform: translateX(12px); }
    to   { opacity: 1; transform: translateX(0); }
}
.bubble-user-inner {
    background: #1e3a5f;
    color: #d4dbe8;
    padding: 11px 16px;
    border-radius: 16px 16px 4px 16px;
    font-size: 0.9rem;
    line-height: 1.6;
    max-width: 78%;
    font-weight: 400;
    border: 1px solid #1e3a6e;
}

.bubble-ai {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin: 10px 0;
    animation: slide-in-left 0.22s ease;
}
@keyframes slide-in-left {
    from { opacity: 0; transform: translateX(-12px); }
    to   { opacity: 1; transform: translateX(0); }
}
.ai-avatar {
    width: 30px; height: 30px; min-width: 30px;
    background: #f59e0b;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px;
    margin-top: 2px;
}
.bubble-ai-inner {
    background: #0f1922;
    border: 1px solid #1a2d3d;
    padding: 13px 16px;
    border-radius: 4px 16px 16px 16px;
    font-size: 0.9rem;
    line-height: 1.75;
    color: #c8d3e0;
    max-width: 84%;
    font-weight: 400;
}

/* ── Typing indicator ── */
.typing-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 0 6px 40px;
    animation: fade-in 0.2s ease;
}
@keyframes fade-in {
    from { opacity: 0; } to { opacity: 1; }
}
.typing-label {
    font-size: 0.78rem;
    color: #4a5a72;
    font-weight: 400;
}
.typing-dots {
    display: flex; gap: 4px;
}
.typing-dots span {
    width: 5px; height: 5px;
    background: #f59e0b;
    border-radius: 50%;
    animation: bounce-dot 1.2s ease-in-out infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce-dot {
    0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
    40%           { transform: scale(1);   opacity: 1; }
}

/* ── Progress bar (fake loading) ── */
.progress-wrap {
    height: 2px;
    background: #1a2235;
    border-radius: 2px;
    overflow: hidden;
    margin: 0 0 1.5rem 0;
}
.progress-bar {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #f59e0b, #fbbf24);
    border-radius: 2px;
    animation: load-bar 1.8s ease forwards;
}
@keyframes load-bar {
    0%   { width: 0%; }
    40%  { width: 60%; }
    80%  { width: 85%; }
    100% { width: 100%; }
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 60px 20px;
}
.empty-icon { font-size: 2.8rem; margin-bottom: 14px; opacity: 0.5; }
.empty-title {
    font-size: 1rem;
    font-weight: 500;
    color: #3a4a60;
    margin-bottom: 6px;
}
.empty-sub { font-size: 0.82rem; color: #2a3a50; }

/* ── Chat input ── */
[data-testid="stChatInput"] {
    padding: 10px 0 !important;
}
[data-testid="stChatInput"] > div {
    background: #0e1420 !important;
    border: 1.5px solid #1e3050 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4) !important;
    transition: border-color 0.2s ease, box-shadow 0.3s ease !important;
    padding: 4px 8px !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #f59e0b !important;
    box-shadow: 0 0 0 4px rgba(245,158,11,0.12), 0 4px 24px rgba(0,0,0,0.4) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    color: #d4dbe8 !important;
    padding: 10px 12px !important;
    caret-color: #f59e0b !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #3a4a60 !important;
}
[data-testid="stChatInput"] textarea:focus {
    box-shadow: none !important;
    outline: none !important;
}
[data-testid="stChatInput"] button {
    background: #f59e0b !important;
    border-radius: 10px !important;
    border: none !important;
    margin: 4px !important;
    transition: background 0.18s ease, transform 0.12s ease !important;
}
[data-testid="stChatInput"] button:hover {
    background: #fbbf24 !important;
    transform: scale(1.08) !important;
}
[data-testid="stChatInput"] button svg {
    fill: #0b0f1a !important;
    stroke: #0b0f1a !important;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Gemini client ──────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return genai.Client(api_key=st.secrets.get("GEMINI_API_KEY", ""))

client = get_client()

SYSTEM_PROMPT = """You are DisasterAI, a professional emergency response assistant specialising in natural disasters — earthquakes, floods, cyclones, tsunamis, wildfires, and landslides.

Your role:
- Provide accurate, calm, and actionable guidance during and after natural disasters
- Offer safety protocols, evacuation steps, first-aid instructions, and preparedness checklists
- Explain disaster science clearly (causes, warning signs, risk factors)
- Give region-specific advice when location is provided
- Reference NDMA, FEMA, Red Cross, UN-OCHA standards where relevant

Tone: Professional, calm, clear. Never alarmist. Simple language, no unnecessary jargon.
Format: Use numbered steps for procedures. Bold critical warnings. Keep responses focused."""

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = None

def get_chat():
    if st.session_state.chat is None:
        st.session_state.chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.4,
                max_output_tokens=1024,
            ),
        )
    return st.session_state.chat

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="logo-wrap">
        <div class="logo-dot">🚨</div>
        <div>
            <div class="logo-title">DisasterAI</div>
            <div class="logo-sub">Natural hazard assistant</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Quick topics</div>', unsafe_allow_html=True)
    quick_prompts = {
        "🌊  Flash flood survival":    "What are the immediate survival steps during a flash flood?",
        "🌀  Cyclone prep guide":       "How do I prepare my home and family before a cyclone hits?",
        "🌍  Earthquake first aid":     "What first-aid should I give after an earthquake injury?",
        "🌋  Volcanic eruption safety": "What should I do if a volcanic eruption is announced nearby?",
        "🌧️  Landslide warning signs":  "What are the early warning signs of a landslide?",
        "📦  Emergency kit checklist":  "Give me a complete emergency disaster kit checklist.",
        "🌊  Tsunami evacuation":       "What is the correct evacuation procedure for a tsunami warning?",
        "🔥  Wildfire escape plan":     "How do I create a wildfire evacuation plan for my family?",
    }
    for label, prompt in quick_prompts.items():
        if st.button(label, key=label):
            st.session_state._quick_prompt = prompt

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">Actions</div>', unsafe_allow_html=True)
    if st.button("🗑  Clear chat"):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()

# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-title">DisasterAI</div>
    <div class="page-sub">Natural disaster safety &amp; emergency response</div>
</div>
<div class="status-pill">
    <span class="status-dot-live"></span>
    AI online &nbsp;·&nbsp; Natural disasters
</div>
<div class="progress-wrap"><div class="progress-bar"></div></div>
""", unsafe_allow_html=True)

# Chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="bubble-user">
            <div class="bubble-user-inner">{msg["content"]}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="bubble-ai">
            <div class="ai-avatar">🚨</div>
            <div class="bubble-ai-inner">{msg["content"]}</div>
        </div>""", unsafe_allow_html=True)

# Empty state
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🌐</div>
        <div class="empty-title">Ask me anything about natural disasters</div>
        <div class="empty-sub">Floods · Earthquakes · Cyclones · Tsunamis · Wildfires · Landslides</div>
    </div>""", unsafe_allow_html=True)

# Quick prompt handler
user_input = None
if hasattr(st.session_state, "_quick_prompt") and st.session_state._quick_prompt:
    user_input = st.session_state._quick_prompt
    del st.session_state._quick_prompt

chat_input = st.chat_input("Ask about disaster safety, preparedness, or emergency response…")
if chat_input:
    user_input = chat_input

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f"""
    <div class="bubble-user">
        <div class="bubble-user-inner">{user_input}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="typing-bar">
        <div class="typing-dots">
            <span></span><span></span><span></span>
        </div>
        <div class="typing-label">DisasterAI is thinking…</div>
    </div>""", unsafe_allow_html=True)

    try:
        chat = get_chat()
        response = chat.send_message(user_input)
        reply = response.text
    except Exception as e:
        reply = f"Something went wrong: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()