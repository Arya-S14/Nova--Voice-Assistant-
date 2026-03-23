"""
NOVA — Siri-like AI Assistant
All bugs fixed: JSON parsing, JS injection, voice auto-submit, auto-open tabs
"""

import streamlit as st
import streamlit.components.v1 as components
import json, re, datetime, requests, time
from groq import Groq
from urllib.parse import quote_plus
import webbrowser

st.set_page_config(page_title="NOVA", page_icon="◈", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
 
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
 
/* ── Animated deep-space background ── */
.stApp {
    background: #04050e;
    color: #f0eeff;
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
}
 
/* Animated aurora background */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(ellipse 110% 70% at 10% -10%, rgba(108,87,255,0.18) 0%, transparent 50%),
        radial-gradient(ellipse 80% 60% at 90% 110%, rgba(6,210,158,0.12) 0%, transparent 50%),
        radial-gradient(ellipse 50% 40% at 50% 50%, rgba(180,100,255,0.05) 0%, transparent 60%);
    animation: auroraShift 12s ease-in-out infinite alternate;
}
@keyframes auroraShift {
    0%   { opacity: 1; transform: scale(1) rotate(0deg); }
    50%  { opacity: 0.7; transform: scale(1.08) rotate(1deg); }
    100% { opacity: 1; transform: scale(1) rotate(0deg); }
}
 
/* Floating particles layer */
.stApp::after {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image:
        radial-gradient(1px 1px at 15% 25%, rgba(124,107,255,0.6) 0%, transparent 100%),
        radial-gradient(1px 1px at 85% 15%, rgba(6,210,158,0.5) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 45% 70%, rgba(180,100,255,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 70% 85%, rgba(124,107,255,0.5) 0%, transparent 100%),
        radial-gradient(1px 1px at 25% 60%, rgba(6,210,158,0.3) 0%, transparent 100%),
        radial-gradient(2px 2px at 60% 35%, rgba(124,107,255,0.35) 0%, transparent 100%),
        radial-gradient(1px 1px at 10% 80%, rgba(255,150,100,0.3) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 90% 60%, rgba(6,210,158,0.4) 0%, transparent 100%);
    animation: floatParticles 20s linear infinite;
}
@keyframes floatParticles {
    0%   { transform: translateY(0px); }
    50%  { transform: translateY(-18px); }
    100% { transform: translateY(0px); }
}
 
/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080918 0%, #05060f 100%) !important;
    border-right: 1px solid rgba(124,107,255,0.12) !important;
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] * { color: #a09ec0 !important; }
[data-testid="stSidebar"] .stButton button {
    background: rgba(124,107,255,0.06) !important;
    border: 1px solid rgba(124,107,255,0.13) !important;
    color: #8a88b0 !important;
    font-size: 12px !important;
    padding: 7px 12px !important;
    border-radius: 10px !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    text-align: left !important;
    box-shadow: none !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stSidebar"] .stButton button::before {
    content: '';
    position: absolute;
    left: -100%;
    top: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(124,107,255,0.1), transparent);
    transition: left 0.4s;
}
[data-testid="stSidebar"] .stButton button:hover::before { left: 100%; }
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(124,107,255,0.14) !important;
    color: #f0eeff !important;
    border-color: rgba(124,107,255,0.32) !important;
    transform: translateX(4px) !important;
    box-shadow: 0 0 12px rgba(124,107,255,0.15) !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #0e0f22 !important;
    border: 1px solid rgba(124,107,255,0.2) !important;
    border-radius: 10px !important;
    color: #f0eeff !important;
}
 
/* ── Chat bubbles ── */
.chat-wrap { max-width: 860px; margin: 0 auto; padding: 8px 0; }
.bubble-row-user { display: flex; justify-content: flex-end; margin: 10px 0; animation: slideInRight 0.35s cubic-bezier(0.4,0,0.2,1); }
.bubble-row-nova  { display: flex; justify-content: flex-start; margin: 10px 0; align-items: flex-start; gap: 10px; animation: slideInLeft 0.35s cubic-bezier(0.4,0,0.2,1); }
 
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(24px) scale(0.96); }
    to   { opacity: 1; transform: translateX(0) scale(1); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-24px) scale(0.96); }
    to   { opacity: 1; transform: translateX(0) scale(1); }
}
 
.av { width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; }
.av-nova {
    background: linear-gradient(135deg, #7c6bff, #4c3bcc);
    color: white;
    box-shadow: 0 0 0 2px rgba(124,107,255,0.25), 0 0 16px rgba(124,107,255,0.4);
    animation: orbGlow 3s ease-in-out infinite;
}
@keyframes orbGlow {
    0%,100% { box-shadow: 0 0 0 2px rgba(124,107,255,0.25), 0 0 16px rgba(124,107,255,0.35); }
    50%      { box-shadow: 0 0 0 3px rgba(124,107,255,0.4),  0 0 28px rgba(124,107,255,0.55); }
}
.av-you { background: rgba(124,107,255,0.15); color: #a78bfa; border: 1px solid rgba(124,107,255,0.25); }
 
.bubble-user {
    background: linear-gradient(135deg, rgba(124,107,255,0.18), rgba(92,79,200,0.1));
    border: 1px solid rgba(124,107,255,0.22);
    border-radius: 20px 4px 20px 20px;
    padding: 13px 18px; max-width: 72%; color: #f0eeff;
    font-size: 14px; line-height: 1.65;
    box-shadow: 0 4px 24px rgba(124,107,255,0.12), inset 0 1px 0 rgba(255,255,255,0.06);
    transition: transform 0.2s, box-shadow 0.2s;
}
.bubble-user:hover { transform: translateY(-1px); box-shadow: 0 6px 32px rgba(124,107,255,0.18), inset 0 1px 0 rgba(255,255,255,0.06); }
 
.bubble-nova {
    background: linear-gradient(135deg, rgba(12,14,32,0.95), rgba(16,18,38,0.85));
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 4px 20px 20px 20px;
    padding: 14px 18px; max-width: 80%; color: #f0eeff;
    font-size: 14px; line-height: 1.75;
    box-shadow: 0 4px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.04);
    transition: transform 0.2s;
}
.bubble-nova:hover { transform: translateY(-1px); }
.bubble-nova a { color: #a78bfa !important; text-decoration: none !important; transition: color 0.2s; }
.bubble-nova a:hover { color: #c4b5fd !important; text-decoration: underline !important; }
.bubble-nova code {
    background: rgba(124,107,255,0.15); padding: 2px 8px; border-radius: 6px;
    font-family: 'JetBrains Mono', monospace; font-size: 12px;
    border: 1px solid rgba(124,107,255,0.2);
}
 
/* ── Action chip ── */
.action-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.22);
    border-radius: 20px; padding: 3px 12px; margin-bottom: 8px;
    font-size: 10px; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase;
    color: #f59e0b; font-family: 'JetBrains Mono', monospace;
    box-shadow: 0 0 8px rgba(245,158,11,0.1);
}
.follow-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(124,107,255,0.1); border: 1px solid rgba(124,107,255,0.22);
    border-radius: 20px; padding: 3px 12px; margin-bottom: 8px;
    font-size: 10px; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase;
    color: #a78bfa; font-family: 'JetBrains Mono', monospace;
}
 
/* ── Open button ── */
.open-btn {
    display: inline-flex; align-items: center; gap: 8px; margin-top: 10px;
    background: linear-gradient(135deg, #7c6bff, #5540e0);
    color: white !important; text-decoration: none !important;
    padding: 9px 20px; border-radius: 12px; font-size: 13px; font-weight: 600;
    box-shadow: 0 4px 20px rgba(124,107,255,0.35), inset 0 1px 0 rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.1);
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
    position: relative; overflow: hidden;
}
.open-btn::before {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.1), transparent);
    opacity: 0; transition: opacity 0.25s;
}
.open-btn:hover { box-shadow: 0 8px 32px rgba(124,107,255,0.55), inset 0 1px 0 rgba(255,255,255,0.12) !important; transform: translateY(-2px) !important; color: white !important; }
.open-btn:hover::before { opacity: 1; }
 
/* ── Stat pills ── */
.stat-pill {
    display: inline-flex; flex-direction: column; align-items: center;
    background: rgba(124,107,255,0.07); border: 1px solid rgba(124,107,255,0.12);
    border-radius: 12px; padding: 8px 14px; min-width: 70px;
    transition: all 0.2s;
}
.stat-pill:hover { background: rgba(124,107,255,0.12); border-color: rgba(124,107,255,0.25); transform: translateY(-2px); }
.sp-val { font-family: 'JetBrains Mono', monospace; font-size: 15px; font-weight: 400; color: #a78bfa; }
.sp-lbl { font-size: 9px; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; color: #6e6b8a; margin-top: 2px; }
 
/* ── Skill pills ── */
.skill-p {
    display: inline-block;
    background: rgba(124,107,255,0.07); border: 1px solid rgba(124,107,255,0.14);
    border-radius: 20px; padding: 3px 10px; font-size: 11px; color: #9088c8; margin: 2px;
    transition: all 0.2s; cursor: default;
}
.skill-p:hover { background: rgba(124,107,255,0.18); color: #c4b5fd; border-color: rgba(124,107,255,0.35); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(124,107,255,0.15); }
 
/* ── Text input ── */
.stTextInput input {
    background: rgba(8,9,22,0.92) !important;
    border: 1px solid rgba(124,107,255,0.22) !important;
    border-radius: 14px !important; color: #f0eeff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important; padding: 12px 16px !important;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03) !important;
}
.stTextInput input:focus {
    border-color: rgba(124,107,255,0.6) !important;
    box-shadow: 0 0 0 3px rgba(124,107,255,0.12), inset 0 1px 0 rgba(255,255,255,0.03) !important;
    background: rgba(10,11,26,0.98) !important;
}
.stTextInput input::placeholder { color: #2a2840 !important; }
 
/* ── Send button ── */
.stButton > button {
    background: linear-gradient(135deg, #7c6bff, #5540e0) !important;
    color: white !important; border: none !important; border-radius: 14px !important;
    font-weight: 600 !important; font-size: 14px !important; padding: 12px 22px !important;
    box-shadow: 0 4px 20px rgba(124,107,255,0.35), inset 0 1px 0 rgba(255,255,255,0.12) !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    position: relative !important; overflow: hidden !important;
}
.stButton > button:hover {
    box-shadow: 0 8px 32px rgba(124,107,255,0.55), inset 0 1px 0 rgba(255,255,255,0.12) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:active { transform: translateY(0px) scale(0.98) !important; }
 
hr { border-color: rgba(124,107,255,0.07) !important; }
 
/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(124,107,255,0.3); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(124,107,255,0.5); }
 
/* ── Spinner ── */
.stSpinner > div { border-top-color: #7c6bff !important; }
 
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {
    "messages": [], "cmd_count": 0, "last_action": "—",
    "last_latency": "—", "groq_client": None, "context": {}
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# 🔥 FIX: Intro state
if "introduced" not in st.session_state:
    st.session_state.introduced = False

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are NOVA, an intelligent voice assistant exactly like Siri — warm, natural, helpful, and fully conversational.

CORE BEHAVIOR:
- Understand intent naturally. Never be rigid about phrasing.
- Support multi-turn conversations. If user asks to "set an alarm" without a time, ask for the time.
- Remember context from recent messages to understand follow-ups.
- Be concise but complete. 1-3 sentences for simple things, more detail when needed.
- No markdown formatting. Plain natural speech only.
- Be proactive — if a task needs multiple steps, guide the user through them naturally.

WHEN TO OUTPUT A JSON ACTION:
Output ONLY a valid JSON object on a single line when you need to perform a real action. No other text.

Examples:
{"action":"open_url","url":"https://spotify.com","label":"Spotify","speak":"Opening Spotify for you!"}
{"action":"open_url","url":"https://www.google.com/search?q=lofi+music","label":"Google Search","speak":"Searching for lofi music!"}
{"action":"open_url","url":"https://www.youtube.com/results?search_query=lofi+music","label":"YouTube","speak":"Opening YouTube for lofi music!"}
{"action":"open_url","url":"https://vclock.com/set-alarm-for-7-30-am/","label":"Set Alarm 7:30 AM","speak":"Setting your alarm for 7 30 AM!"}
{"action":"open_url","url":"https://www.google.com/maps/search/coffee+shop+near+me","label":"Maps","speak":"Opening maps for coffee shops near you!"}
{"action":"weather","city":"Mumbai","speak":"Let me check the weather in Mumbai!"}

MULTI-TURN:
User: "Set an alarm" → NOVA: "Sure! What time should I set it for?"
User: "7 AM" → NOVA: {"action":"open_url","url":"https://vclock.com/set-alarm-for-7-00-am/","label":"Set Alarm 7 AM","speak":"Setting alarm for 7 AM!"}

APP SHORTCUTS:
spotify→https://open.spotify.com, youtube→https://youtube.com,
gmail→https://mail.google.com, github→https://github.com,
netflix→https://netflix.com, maps→https://maps.google.com,
whatsapp→https://web.whatsapp.com, instagram→https://instagram.com,
linkedin→https://linkedin.com, twitter→https://x.com,
amazon→https://amazon.in, flipkart→https://flipkart.com,
chatgpt→https://chat.openai.com, notion→https://notion.so,
figma→https://figma.com, zoom→https://zoom.us,
calendar→https://calendar.google.com, drive→https://drive.google.com,
timer→https://www.google.com/search?q=timer,
alarm→https://vclock.com/set-alarm/,
calculator→https://www.google.com/search?q=calculator

IMPORTANT:
- All URLs open in new tab — original tab stays open always.
- For pure questions/conversation, respond naturally — no JSON needed.
- Always complete the user request fully.
"""

# ── Action executor ────────────────────────────────────────────────────────────
def execute_action(data):
    action = data.get("action", "")
    speak = data.get("speak", "Done!")

    if action == "open_url":
        url = data.get("url", "")
        label = data.get("label", "Link")
        # Open in server browser as fallback (local runs)
        try:
            webbrowser.open_new_tab(url)
        except Exception:
            pass
        html = (
            f'<a class="open-btn" href="{url}" target="_blank">🌐 {label} ↗</a>'
            f'<div style="font-size:12px;color:#6e6b8a;margin-top:6px;font-family:monospace">'
            f'Opened in new tab · your NOVA tab stays open</div>'
        )
        return html, speak, url

    if action == "weather":
        city = data.get("city", "London")
        try:
            w = requests.get(
                f"https://wttr.in/{quote_plus(city)}?format=3", timeout=6
            ).text.strip()
            url = f"https://wttr.in/{quote_plus(city)}"
            html = (
                f'<div style="font-size:20px;margin-bottom:6px">🌤️</div>'
                f'<div style="font-size:16px;font-weight:500">{w}</div>'
                f'<br><a class="open-btn" href="{url}" target="_blank">🌤️ Full Forecast ↗</a>'
            )
            return html, w, url
        except Exception:
            url = f"https://wttr.in/{quote_plus(city)}"
            html = f'<a class="open-btn" href="{url}" target="_blank">🌤️ Weather for {city} ↗</a>'
            return html, f"Check weather for {city}", url

    return speak, speak, None


# ── Groq call ──────────────────────────────────────────────────────────────────
def call_groq(client, messages, model):
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages[-12:],
        temperature=0.4,
        max_tokens=512,
    )
    return resp.choices[0].message.content.strip()


# ── Process query — FIX 1: safer JSON parsing ──────────────────────────────────
def process_query(user_input, client, model):
    st.session_state.messages.append({"role": "user", "content": user_input})
    t0 = time.time()

    try:
        history = [
            {"role": m["role"], "content": m.get("raw_content", m["content"])}
            for m in st.session_state.messages
        ]
        reply = call_groq(client, history, model)
    except Exception as e:
        reply = f"I ran into an error: {str(e)}"

    st.session_state.last_latency = f"{int((time.time() - t0) * 1000)}ms"

    # ── FIX 1: Try direct json.loads first, then regex fallback ───────────────
    action_data = None

    # Try 1: full reply is JSON
    try:
        candidate = json.loads(reply.strip())
        if isinstance(candidate, dict) and "action" in candidate:
            action_data = candidate
    except Exception:
        pass

    # Try 2: extract JSON block from reply using regex
    if not action_data:
        match = re.search(r'\{[^{}]*"action"[^{}]*\}', reply, re.DOTALL)
        if match:
            try:
                candidate = json.loads(match.group())
                if "action" in candidate:
                    action_data = candidate
            except Exception:
                pass

    if action_data:
        html_content, speak_text, open_url = execute_action(action_data)
        action_name = action_data.get("action", "")
        tts = action_data.get("speak", speak_text)
        tts = re.sub(r'<[^>]+>', '', tts)

        st.session_state.last_action = action_name
        st.session_state.cmd_count += 1
        st.session_state.messages.append({
            "role": "assistant",
            "content": f'<div>{speak_text}</div><div style="margin-top:8px">{html_content}</div>',
            "raw_content": speak_text,
            "speak": tts,
            "action": action_name,
            "is_action": True,
            "open_url": open_url or "",
            "is_followup": False,
        })
        return

    # Plain conversation reply
    is_followup = reply.rstrip().endswith("?")
    st.session_state.last_action = "follow-up" if is_followup else "conversation"
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "raw_content": reply,
        "speak": reply,
        "is_action": False,
        "open_url": "",
        "is_followup": is_followup,
    })


# ── Fast local responses (no Groq needed) ─────────────────────────────────────
def fast_respond(text):
    t = text.lower().strip()
    now = datetime.datetime.now()
    if re.search(r'\btime\b', t) and not re.search(r'weather|alarm|timer|remind', t):
        return f"It's {now.strftime('%I:%M %p').lstrip('0')} right now."
    if re.search(r'\bdate\b|\btoday\b', t) and not re.search(r'weather|news', t):
        return now.strftime("Today is %A, %B %d, %Y.")
    m = re.search(
        r'([\d.]+)\s*([+\-×x*/÷]|plus|minus|times|divided by|multiplied by)\s*([\d.]+)', t
    )
    if m:
        try:
            a, op, b = float(m.group(1)), m.group(2).strip(), float(m.group(3))
            ops = {
                '+': a + b, 'plus': a + b, '-': a - b, 'minus': a - b,
                '×': a * b, 'x': a * b, '*': a * b, 'times': a * b,
                'multiplied by': a * b, '/': a / b, '÷': a / b, 'divided by': a / b,
            }
            r = ops.get(op)
            if r is not None:
                return f"{m.group(1)} {m.group(2)} {m.group(3)} = {round(r, 6)}"
        except Exception:
            pass
    return None


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:22px 0 14px">
      <div style="position:relative;width:76px;height:76px;margin:0 auto 12px">
        <div style="width:76px;height:76px;border-radius:50%;
          background:radial-gradient(circle at 30% 28%,#c4b5fd,#7c6bff 45%,#3b2fa0);
          display:flex;align-items:center;justify-content:center;font-size:30px;
          box-shadow:0 0 0 2px rgba(124,107,255,0.25),0 0 28px rgba(124,107,255,0.45)">◈</div>
        <div style="position:absolute;inset:-7px;border-radius:50%;
          border:1px solid rgba(124,107,255,0.2);animation:spin 9s linear infinite"></div>
        <div style="position:absolute;inset:-13px;border-radius:50%;
          border:1px dashed rgba(124,107,255,0.1);animation:spin 16s linear infinite reverse"></div>
      </div>
      <style>@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}</style>
      <div style="font-size:21px;font-weight:700;color:#f0eeff;letter-spacing:-.5px">NOVA</div>
      <div style="font-size:9px;color:#6e6b8a;font-family:monospace;margin-top:3px;letter-spacing:1.2px">
        NEURAL VOICE ASSISTANT</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    api_key = st.text_input(
        "🔑 Groq API Key", type="password",
        placeholder="gsk_xxxxxxxxxxxx", help="Free at console.groq.com"
    )
    if api_key:
        try:
            st.session_state.groq_client = Groq(api_key=api_key)
            st.success("✅ Connected")
        except Exception:
            st.session_state.groq_client = None
            st.error("❌ Invalid API key. Please re-enter your API key.")
    else:
        st.caption("Free key → [console.groq.com](https://console.groq.com)")

    model = st.selectbox(
        "🧠 Model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant",
         "meta-llama/llama-4-scout-17b-16e-instruct", "qwen/qwen-3-32b"],
        help="70b = smartest | 8b = fastest"
    )
    st.divider()

    st.markdown(f"""
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
      <div class="stat-pill"><div class="sp-val">{st.session_state.cmd_count}</div><div class="sp-lbl">Actions</div></div>
      <div class="stat-pill"><div class="sp-val" style="font-size:12px">{st.session_state.last_latency}</div><div class="sp-lbl">Speed</div></div>
      <div class="stat-pill"><div class="sp-val" style="font-size:12px;color:#06d6a0">{st.session_state.last_action[:8]}</div><div class="sp-lbl">Last</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("**⚡ What NOVA can do**")
    skills = [
        "🕐 Time & Date", "🌤️ Weather", "🔍 Web Search", "▶️ YouTube",
        "⏰ Alarms & Timers", "🗺️ Maps", "🎵 Open Apps", "📰 News",
        "😄 Jokes", "📖 Dictionary", "💱 Currency", "📏 Units",
        "✨ Motivation", "🧮 Maths", "🌍 Translate", "💬 Chat"
    ]
    st.markdown(
        " ".join([f'<span class="skill-p">{s}</span>' for s in skills]),
        unsafe_allow_html=True
    )
    st.divider()

    st.markdown("**🚀 Try these**")
    quick = [
        "Set an alarm for 7 AM", "What time is it?", "Weather in Mumbai",
        "Open Spotify", "Search YouTube for lofi", "Directions to nearest cafe",
        "Tell me a joke", "100 USD to INR", "Define procrastination",
        "Set a 10 minute timer", "Latest tech news", "Motivational quote",
        "Open Netflix", "30 celsius to fahrenheit", "Open GitHub",
    ]
    for q in quick:
        if st.button(q, key=f"q_{q}", use_container_width=True):
            if st.session_state.groq_client:
                fast = fast_respond(q)
                if fast:
                    st.session_state.messages.append({"role": "user", "content": q})
                    st.session_state.messages.append({
                        "role": "assistant", "content": fast, "speak": fast,
                        "is_action": False, "open_url": "", "is_followup": False
                    })
                else:
                    with st.spinner(""):
                        process_query(q, st.session_state.groq_client, model)
                st.rerun()
            else:
                st.error("Enter Groq API key first!")
    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.cmd_count = 0
        st.session_state.last_action = "—"
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
  padding:14px 20px;background:rgba(120,100,255,0.05);
  border:1px solid rgba(120,100,255,0.1);border-radius:16px;margin-bottom:16px">
  <div style="display:flex;align-items:center;gap:12px">
    <div style="width:40px;height:40px;border-radius:50%;
      background:radial-gradient(circle at 30% 28%,#c4b5fd,#7c6bff 45%,#3b2fa0);
      display:flex;align-items:center;justify-content:center;font-size:18px;
      box-shadow:0 0 18px rgba(124,107,255,0.4)">◈</div>
    <div>
      <div style="font-size:18px;font-weight:700;color:#f0eeff">NOVA</div>
      <div style="font-size:10px;color:#6e6b8a;font-family:monospace">
        {"🟢 Ready · " + model if st.session_state.groq_client else "🔴 Enter Groq API key to start"}</div>
    </div>
  </div>
  <div style="display:flex;gap:16px">
    <div style="text-align:center">
      <div style="font-size:16px;font-weight:600;color:#a78bfa;font-family:monospace">{st.session_state.cmd_count}</div>
      <div style="font-size:9px;color:#6e6b8a;letter-spacing:1px;text-transform:uppercase">Actions</div>
    </div>
    <div style="text-align:center">
      <div style="font-size:16px;font-weight:600;color:#06d6a0;font-family:monospace">{len(st.session_state.messages)}</div>
      <div style="font-size:9px;color:#6e6b8a;letter-spacing:1px;text-transform:uppercase">Messages</div>
    </div>
    <div style="text-align:center">
      <div style="font-size:16px;font-weight:600;color:#f59e0b;font-family:monospace">{st.session_state.last_latency}</div>
      <div style="font-size:9px;color:#6e6b8a;letter-spacing:1px;text-transform:uppercase">Speed</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Get last speak + auto-open URL ────────────────────────────────────────────
auto_open_url = ""
last_speak = ""

# 🔥 FIX: AUTO INTRO LOGIC
if not st.session_state.introduced:
    if st.session_state.groq_client:
        last_speak = "Hi, I am NOVA, your voice assistant. How can I help you?"
        st.session_state.introduced = True
    else:
        last_speak = "Please enter your Groq API key to get started."
else:
    for m in reversed(st.session_state.messages):
        if m["role"] == "assistant":
            if not auto_open_url and m.get("open_url"):
                auto_open_url = m["open_url"]
            raw = m.get("speak", m["content"])
            raw = re.sub(r'<[^>]+>', '', str(raw))
            raw = re.sub(r'[*#]', '', raw).strip()[:280]
            last_speak = raw
            break

# ── FIX 2 & 3: Voice widget — safe JS, no Python/JS mixup ────────────────────
# All JS is inside a proper HTML string — no Python execution of JS code
auto_open_url_js = json.dumps(auto_open_url)   # safe JSON string for JS
last_speak_js = json.dumps(last_speak)          # safe JSON string for JS

auto_open_url_js = json.dumps(auto_open_url)
last_speak_js    = json.dumps(last_speak)
 
bars_html = "".join([
    f'<div class="b" style="animation-delay:{round(i*0.06,2)}s;height:{3+abs(9-i)*2}px"></div>'
    for i in range(22)
])
 
voice_html = f"""<!DOCTYPE html>
<html>
<head>
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: transparent; font-family: 'Space Grotesk', sans-serif; overflow: hidden; }}
 
/* Panel */
.panel {{
    display: flex; align-items: center; gap: 20px;
    background: linear-gradient(135deg, rgba(8,9,22,0.98), rgba(6,7,18,0.96));
    border: 1px solid rgba(124,107,255,0.18);
    border-radius: 22px; padding: 18px 24px;
    box-shadow:
        0 0 0 1px rgba(124,107,255,0.06),
        0 8px 48px rgba(0,0,0,0.6),
        inset 0 1px 0 rgba(255,255,255,0.05),
        inset 0 -1px 0 rgba(0,0,0,0.3);
    position: relative; overflow: hidden;
}}
 
/* Shimmer sweep */
.panel::before {{
    content: '';
    position: absolute; top: 0; left: -100%;
    width: 60%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(124,107,255,0.04), transparent);
    animation: shimmer 6s linear infinite;
}}
@keyframes shimmer {{ from {{ left: -100%; }} to {{ left: 200%; }} }}
 
/* Orb area */
.orb-area {{ position: relative; flex-shrink: 0; width: 72px; height: 72px; }}
 
/* Rotating rings */
.ring {{
    position: absolute; border-radius: 50%;
    border: 1px solid rgba(124,107,255,0.25);
    animation: spin 9s linear infinite;
}}
.ring1 {{ inset: -8px; }}
.ring2 {{ inset: -15px; border-color: rgba(124,107,255,0.12); border-style: dashed; animation: spin 16s linear infinite reverse; }}
.ring3 {{ inset: -22px; border-color: rgba(6,210,158,0.08); animation: spin 24s linear infinite; }}
@keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
 
/* Orb */
.orb {{
    width: 72px; height: 72px; border-radius: 50%;
    background: radial-gradient(circle at 32% 28%, #c4b5fd, #7c6bff 40%, #3b2fa0 75%, #1e1060);
    border: none; cursor: pointer; font-size: 28px;
    display: flex; align-items: center; justify-content: center;
    position: absolute; inset: 0;
    box-shadow:
        0 0 0 2px rgba(124,107,255,0.3),
        0 0 30px rgba(124,107,255,0.5),
        0 0 60px rgba(124,107,255,0.2),
        inset 0 2px 4px rgba(255,255,255,0.15);
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    outline: none;
    animation: idleBreath 4s ease-in-out infinite;
}}
@keyframes idleBreath {{
    0%,100% {{ box-shadow: 0 0 0 2px rgba(124,107,255,0.3), 0 0 30px rgba(124,107,255,0.45), 0 0 60px rgba(124,107,255,0.15), inset 0 2px 4px rgba(255,255,255,0.15); }}
    50%      {{ box-shadow: 0 0 0 3px rgba(124,107,255,0.45), 0 0 44px rgba(124,107,255,0.65), 0 0 80px rgba(124,107,255,0.25), inset 0 2px 4px rgba(255,255,255,0.2); }}
}}
.orb:hover {{ transform: scale(1.08); animation: none;
    box-shadow: 0 0 0 3px rgba(124,107,255,0.5), 0 0 50px rgba(124,107,255,0.7), 0 0 90px rgba(124,107,255,0.3), inset 0 2px 4px rgba(255,255,255,0.2); }}
 
/* Listening state */
.orb.L {{
    background: radial-gradient(circle at 32% 28%, #fca5a5, #ef4444 40%, #991b1b 75%, #4a0a0a);
    box-shadow: 0 0 0 3px rgba(239,68,68,0.4), 0 0 44px rgba(239,68,68,0.65), 0 0 80px rgba(239,68,68,0.25), inset 0 2px 4px rgba(255,255,255,0.15);
    animation: listenPulse 0.75s ease-in-out infinite;
}}
@keyframes listenPulse {{
    0%,100% {{ transform: scale(1); }}
    50%      {{ transform: scale(1.1); box-shadow: 0 0 0 4px rgba(239,68,68,0.5), 0 0 60px rgba(239,68,68,0.8), 0 0 100px rgba(239,68,68,0.35), inset 0 2px 4px rgba(255,255,255,0.2); }}
}}
 
/* Speaking state */
.orb.S {{
    background: radial-gradient(circle at 32% 28%, #6ee7b7, #10b981 40%, #065f46 75%, #022c22);
    box-shadow: 0 0 0 3px rgba(16,185,129,0.4), 0 0 44px rgba(16,185,129,0.65), 0 0 80px rgba(16,185,129,0.25), inset 0 2px 4px rgba(255,255,255,0.15);
    animation: speakPulse 0.5s ease-in-out infinite alternate;
}}
@keyframes speakPulse {{
    from {{ transform: scale(1); }}
    to   {{ transform: scale(1.09); box-shadow: 0 0 0 4px rgba(16,185,129,0.55), 0 0 60px rgba(16,185,129,0.8), 0 0 100px rgba(16,185,129,0.3), inset 0 2px 4px rgba(255,255,255,0.2); }}
}}
 
/* Processing state */
.orb.P {{
    background: radial-gradient(circle at 32% 28%, #fde68a, #f59e0b 40%, #b45309 75%, #5a2a00);
    box-shadow: 0 0 0 3px rgba(245,158,11,0.4), 0 0 44px rgba(245,158,11,0.6), inset 0 2px 4px rgba(255,255,255,0.15);
    animation: processPulse 1.2s ease-in-out infinite;
}}
@keyframes processPulse {{
    0%,100% {{ opacity: 1; transform: scale(1); }}
    50%     {{ opacity: 0.8; transform: scale(0.96); }}
}}
 
/* Middle section */
.mid {{ flex: 1; min-width: 0; }}
 
/* Status text */
.status {{
    font-size: 12px; font-family: 'JetBrains Mono', monospace;
    color: #6e6b8a; margin-bottom: 8px;
    transition: color 0.3s; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis;
    display: flex; align-items: center; gap: 6px;
}}
 
/* Live dot indicator */
.live-dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: #6e6b8a; flex-shrink: 0;
    transition: background 0.3s, box-shadow 0.3s;
}}
.live-dot.active {{
    background: #ef4444;
    box-shadow: 0 0 6px rgba(239,68,68,0.8);
    animation: dotBlink 0.6s ease-in-out infinite;
}}
.live-dot.speaking {{ background: #10b981; box-shadow: 0 0 6px rgba(16,185,129,0.8); animation: dotBlink 0.4s ease-in-out infinite; }}
@keyframes dotBlink {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }} }}
 
/* Waveform */
.waves {{ display: flex; gap: 2px; align-items: flex-end; height: 32px; margin-bottom: 8px; }}
.b {{ width: 3px; border-radius: 2px; background: rgba(124,107,255,0.3); height: 3px; transition: background 0.3s; }}
.b.AL {{
    background: linear-gradient(180deg, #a78bfa, #7c6bff);
    animation: wb 0.5s ease-in-out infinite alternate;
    box-shadow: 0 0 4px rgba(124,107,255,0.4);
}}
.b.AS {{
    background: linear-gradient(180deg, #6ee7b7, #10b981);
    animation: wb 0.35s ease-in-out infinite alternate;
    box-shadow: 0 0 4px rgba(16,185,129,0.4);
}}
@keyframes wb {{ from {{ height: 3px; opacity: 0.3; }} to {{ height: 28px; opacity: 1; }} }}
 
/* Transcript box */
.tbox {{
    background: rgba(124,107,255,0.07);
    border: 1px solid rgba(124,107,255,0.2);
    border-radius: 10px; padding: 8px 12px;
    font-size: 13px; color: #f0eeff;
    font-family: 'JetBrains Mono', monospace;
    display: none; word-break: break-word;
    line-height: 1.5; max-height: 56px; overflow: hidden;
    animation: fadeIn 0.2s ease-out;
}}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(4px); }} to {{ opacity: 1; transform: translateY(0); }} }}
 
.hint {{ font-size: 10px; color: #1a1830; font-family: monospace; margin-top: 5px; }}
 
/* Badges */
.badges {{ display: flex; gap: 6px; margin-top: 4px; flex-wrap: wrap; align-items: center; }}
.badge {{
    display: none; padding: 3px 10px;
    border-radius: 20px; font-size: 10px; font-weight: 700;
    letter-spacing: 0.5px; animation: fadeIn 0.3s ease-out;
}}
.ok  {{ background: rgba(6,214,160,0.12); border: 1px solid rgba(6,214,160,0.25); color: #06d6a0; }}
.cp  {{ background: rgba(245,158,11,0.1);  border: 1px solid rgba(245,158,11,0.22); color: #f59e0b; }}
 
/* Right buttons */
.right {{ display: flex; flex-direction: column; gap: 7px; flex-shrink: 0; }}
.btn {{
    padding: 8px 18px; border-radius: 10px; font-size: 12px; font-weight: 700;
    cursor: pointer; border: none; transition: all 0.2s cubic-bezier(0.4,0,0.2,1);
    white-space: nowrap; font-family: 'Space Grotesk', sans-serif;
    position: relative; overflow: hidden;
}}
.sbtn {{
    background: linear-gradient(135deg, #7c6bff, #5540e0);
    color: white; display: none;
    box-shadow: 0 3px 14px rgba(124,107,255,0.35), inset 0 1px 0 rgba(255,255,255,0.12);
}}
.sbtn:hover {{ box-shadow: 0 5px 22px rgba(124,107,255,0.55), inset 0 1px 0 rgba(255,255,255,0.12); transform: translateY(-1px); }}
.cbtn {{ background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08) !important; color: #6e6b8a; display: none; }}
.cbtn:hover {{ color: #f0eeff; background: rgba(255,255,255,0.08); }}
</style>
</head>
<body>
<div class="panel">
  <div class="orb-area">
    <div class="ring ring1"></div>
    <div class="ring ring2"></div>
    <div class="ring ring3"></div>
    <button class="orb" id="orb" onclick="toggle()" title="Click to speak">◈</button>
  </div>
  <div class="mid">
    <div class="status" id="st">
      <div class="live-dot" id="dot"></div>
      <span id="stText">Click orb to speak — NOVA listens like Siri</span>
    </div>
    <div class="waves" id="waves">{bars_html}</div>
    <div class="tbox" id="tbox"></div>
    <div class="badges">
      <span class="badge ok" id="okB">✅ Sent!</span>
      <span class="badge cp" id="cpB">📋 Paste below ↓</span>
    </div>
    <div class="hint">Chrome / Edge · Microphone permission required</div>
  </div>
  <div class="right">
    <button class="btn sbtn" id="sendBtn" onclick="doSend()">Send ↑</button>
    <button class="btn cbtn" id="cancelBtn" onclick="doCancel()">✕ Cancel</button>
  </div>
</div>
 
<script>
var AU = {auto_open_url_js};
if (AU) {{ setTimeout(function() {{ window.open(AU, '_blank'); }}, 250); }}
 
var SP = {last_speak_js};
var spokenAlready = false;
 
function doSpeak() {{
    if (!SP || spokenAlready || !window.speechSynthesis) return;
    spokenAlready = true;
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(SP);
    u.rate = 1.0; u.pitch = 1.0; u.volume = 1;
    var vs = window.speechSynthesis.getVoices();
    var pick = vs.find(function(v) {{
        return v.lang.startsWith('en') && (
            v.name.includes('Female') || v.name.includes('Samantha') ||
            v.name.includes('Karen') || v.name.includes('Moira') || v.name.includes('Victoria')
        );
    }}) || vs.find(function(v) {{ return v.lang === 'en-US'; }})
       || vs.find(function(v) {{ return v.lang.startsWith('en'); }})
       || vs[0];
    if (pick) u.voice = pick;
    mode('S');
    u.onend = function() {{ mode('');
        // 🔥 FIX: auto start listening after speaking
        setTimeout(function() {{
            if (!listening) {{
                startR();
            }}
        }}, 800);
    }};
    u.onerror = function() {{ mode(''); }};
    window.speechSynthesis.speak(u);
}}
 
if (window.speechSynthesis.getVoices().length > 0) {{
    setTimeout(function() {{
        doSpeak();
        setTimeout(startR, 1000);
    }}, 600);
}} else {{
    window.speechSynthesis.onvoiceschanged = function() {{
        setTimeout(function() {{
            doSpeak();
            setTimeout(startR, 1000);
        }}, 400);
    }};
}}
 
var rec = null, listening = false, txt = '', autoT = null;
 
function mode(m) {{
    var o    = document.getElementById('orb');
    var st   = document.getElementById('stText');
    var dot  = document.getElementById('dot');
    var bs   = document.querySelectorAll('.b');
    o.className = 'orb';
    bs.forEach(function(b) {{ b.className = 'b'; }});
    dot.className = 'live-dot';
 
    if (m === 'L') {{
        o.classList.add('L'); o.textContent = '⏹';
        dot.classList.add('active');
        bs.forEach(function(b, i) {{ b.classList.add('AL'); b.style.animationDelay = (i * 0.06) + 's'; }});
        st.textContent = 'Listening… speak your command';
        document.getElementById('st').style.color = '#a78bfa';
    }} else if (m === 'S') {{
        o.classList.add('S'); o.textContent = '🔊';
        dot.classList.add('speaking');
        bs.forEach(function(b, i) {{ b.classList.add('AS'); b.style.animationDelay = (i * 0.05) + 's'; }});
        st.textContent = 'NOVA is speaking…';
        document.getElementById('st').style.color = '#06d6a0';
    }} else if (m === 'P') {{
        o.classList.add('P'); o.textContent = '⏳';
        st.textContent = 'Processing your request…';
        document.getElementById('st').style.color = '#f59e0b';
    }} else {{
        o.textContent = '◈';
        st.textContent = 'Click orb to speak — NOVA listens like Siri';
        document.getElementById('st').style.color = '#6e6b8a';
    }}
}}
 
function toggle() {{
    if (window.speechSynthesis && window.speechSynthesis.speaking) {{
        window.speechSynthesis.cancel(); mode(''); return;
    }}
    if (listening) {{ stopR(); }} else {{ startR(); }}
}}
 
function startR() {{
    // 🔥 FIX: force mic permission
    navigator.mediaDevices.getUserMedia({{ audio: true }})
    .catch(function() {{
        document.getElementById('stText').textContent = '⚠️ Please allow microphone access';
    }});
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {{
        document.getElementById('stText').textContent = '❌ Use Chrome or Edge for voice input';
        document.getElementById('st').style.color = '#ef4444';
        return;
    }}
    txt = '';
    ['tbox','okB','cpB'].forEach(function(id) {{ document.getElementById(id).style.display = 'none'; }});
    document.getElementById('sendBtn').style.display = 'none';
    document.getElementById('cancelBtn').style.display = 'none';
 
    rec = new SR();
    rec.continuous = false; rec.interimResults = true;
    rec.lang = 'en-US'; rec.maxAlternatives = 3;
 
    rec.onstart = function() {{ listening = true; mode('L'); }};
    rec.onresult = function(e) {{
        var interim = '', final = '';
        for (var i = e.resultIndex; i < e.results.length; i++) {{
            if (e.results[i].isFinal) final += e.results[i][0].transcript;
            else interim += e.results[i][0].transcript;
        }}
        txt = final || interim;
        var tb = document.getElementById('tbox');
        tb.textContent = '"' + txt + '"';
        tb.style.display = 'block';
        document.getElementById('sendBtn').style.display = 'block';
        document.getElementById('cancelBtn').style.display = 'block';
        if (final && final.trim()) {{
            clearTimeout(autoT);
            autoT = setTimeout(function() {{ doSend(); }}, 600);
        }}
    }};
    rec.onerror = function(e) {{
        listening = false; mode('');
        if (e.error !== 'no-speech') {{
            document.getElementById('stText').textContent = '❌ ' + e.error + ' — tap orb to retry';
            document.getElementById('st').style.color = '#ef4444';
        }}
    }};
    rec.onend = function() {{ listening = false; if (!txt.trim()) mode(''); }};
    rec.start();
}}
 
function stopR() {{
    listening = false;
    if (rec) {{ try {{ rec.stop(); }} catch(e) {{}} }}
}}
 
function doSend() {{
    if (!txt.trim()) return;
    clearTimeout(autoT); stopR();
    mode('P');
    document.getElementById('sendBtn').style.display = 'none';
    document.getElementById('cancelBtn').style.display = 'none';
    var t = txt.trim();
 
    try {{
        var pd = window.parent.document;
        var ins = pd.querySelectorAll('input[type="text"]');
        var inp = null;
        ins.forEach(function(i) {{
            if (i.placeholder && i.placeholder.toLowerCase().includes('speak')) inp = i;
        }});
        if (!inp && ins.length > 0) inp = ins[ins.length - 1];
        if (inp) {{
            var nv = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            nv.call(inp, t);
            inp.focus(); inp.value = t;
            inp.dispatchEvent(new Event('input',  {{ bubbles: true }}));
            inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
            setTimeout(function() {{
                if (inp.form) {{ inp.form.requestSubmit(); }}
                var btns = pd.querySelectorAll(
                    'button[kind="primaryFormSubmit"],button[data-testid="baseButton-primaryFormSubmit"]'
                );
                if (btns.length > 0) {{ btns[0].click(); }}
            }}, 180);
        }}
    }} catch(e) {{ console.error('Input injection:', e); }}
 
    navigator.clipboard.writeText(t).catch(function() {{}});
    setTimeout(function() {{
        document.getElementById('okB').style.display = 'inline';
        document.getElementById('cpB').style.display = 'inline';
        document.getElementById('stText').textContent = '✅ "' + t.slice(0,40) + (t.length > 40 ? '…' : '') + '" — paste below if needed';
        document.getElementById('st').style.color = '#06d6a0';
        mode('');
    }}, 800);
}}
 
function doCancel() {{
    txt = ''; clearTimeout(autoT); stopR();
    document.getElementById('tbox').style.display = 'none';
    document.getElementById('sendBtn').style.display = 'none';
    document.getElementById('cancelBtn').style.display = 'none';
    mode('');
}}
</script>
</body>
</html>"""
 
components.html(voice_html, height=180)

# ── Text input ─────────────────────────────────────────────────────────────────
with st.form("chat_form", clear_on_submit=True):
    c1, c2 = st.columns([5, 1])
    with c1:
        user_input = st.text_input(
            "msg",
            placeholder='🎤 Speak using the orb above · or type: "set alarm 7 AM" · "open spotify" · "weather Mumbai"',
            label_visibility="collapsed"
        )
    with c2:
        submitted = st.form_submit_button("Send ↑", use_container_width=True)

if submitted and user_input.strip():
    if not st.session_state.groq_client:
        st.error("⚠️ Enter your Groq API key in the sidebar first!")
    else:
        fast = fast_respond(user_input.strip())
        if fast:
            st.session_state.messages.append({"role": "user", "content": user_input.strip()})
            st.session_state.messages.append({
                "role": "assistant", "content": fast, "speak": fast,
                "is_action": False, "open_url": "", "is_followup": False
            })
        else:
            with st.spinner("NOVA thinking..."):
                process_query(user_input.strip(), st.session_state.groq_client, model)
        st.rerun()

st.divider()

# ── Chat log ───────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:56px 24px">
      <div style="font-size:56px;margin-bottom:16px;opacity:.18">◈</div>
      <div style="font-size:18px;font-weight:600;color:#b8b4d8;margin-bottom:12px">Hi, I'm NOVA</div>
      <div style="font-size:14px;color:#6e6b8a;max-width:420px;margin:0 auto;line-height:1.9">
        I can open apps, set alarms, search the web, give weather,<br>
        convert currencies, tell jokes — anything Siri can do.<br><br>
        <span style="color:#a78bfa;font-weight:500">Click the orb above to speak</span>
        &nbsp;or&nbsp;
        <span style="color:#06d6a0;font-weight:500">type a command below</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="bubble-row-user">
              <div class="bubble-user">{msg["content"]}</div>
              <div class="av av-you" style="margin-left:8px">Y</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            prefix = ""
            if msg.get("is_action"):
                icons = {"open_url": "🌐", "weather": "🌤️"}
                icon = icons.get(msg.get("action", ""), "⚡")
                aname = msg.get("action", "action")
                prefix = f'<div class="action-chip">{icon} {aname.replace("_"," ").upper()}</div><br>'
            elif msg.get("is_followup"):
                prefix = '<div class="follow-chip">💬 FOLLOW-UP</div><br>'

            st.markdown(f"""
            <div class="bubble-row-nova">
              <div class="av av-nova">◈</div>
              <div class="bubble-nova">{prefix}{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.markdown("""
<div style="text-align:center;color:#18162a;font-size:11px;font-family:monospace;padding:4px 0">
NOVA · Streamlit + Groq + LLaMA3 ·
<a href="https://console.groq.com" style="color:#28244a">Free Groq API key</a>
</div>
""", unsafe_allow_html=True)