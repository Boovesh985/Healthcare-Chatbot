# ==========================================
# Streamlit Frontend (streamlit_app.py)
# ==========================================
import os
import streamlit as st
import requests
from dotenv import load_dotenv

# ==========================================================
# Load environment variables
# ==========================================================
load_dotenv()

# ==========================================================
# Streamlit setup
# ==========================================================
st.set_page_config(page_title="🤖 Healthcare Chatbot", page_icon="💬", layout="centered")

# ==========================================================
# Custom CSS for clean layout + visible input bar
# ==========================================================
st.markdown("""
    <style>
        /* General app background */
        .stApp {
            background-color: #a9e7f6;
            color: #000000;
        }

        /* Chat bubbles */
        .chat-bubble {
            padding: 10px 15px;
            border-radius: 15px;
            margin-bottom: 10px;
            line-height: 1.5;
            word-wrap: break-word;
            max-width: 80%;
        }

        .user-bubble {
            background-color: #DCF8C6;
            margin-left: auto;
            text-align: right;
        }

        .bot-bubble {
            background-color: #E8E8E8;
            margin-right: auto;
            text-align: left;
        }

        /* Input container */
        .input-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            position: sticky;
            bottom: 0;
            background: #ffffff;
            padding: 10px 0;
            border-top: 1px solid #ddd;
        }

        /* Input box style */
        div[data-baseweb="input"] > div {
            border-radius: 10px !important;
            height: 40px !important;
        }

        /* Send button */
        .stButton button {
            height: 40px !important;
            background-color: #0078ff !important;
            color: white !important;
            border-radius: 10px !important;
            font-size: 16px !important;
            border: none !important;
        }

        .stButton button:hover {
            background-color: #005fcc !important;
        }

        /* Hide footer + menu */
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================================
# Backend URL
# ==========================================================
FLASK_URL = os.getenv("FLASK_URL", "http://127.0.0.1:8000")
GENERATE_URL = f"{FLASK_URL.rstrip('/')}/api/generate"

# ==========================================================
# Title
# ==========================================================
st.title("🏥 Healthcare Chatbot")
st.markdown("  *Chat with a Mistral-powered assistant about health, symptoms, or wellness tips!*")

# ==========================================================
# Session state
# ==========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# ==========================================================
# Function: Send message to Flask backend
# ==========================================================
def send_message():
    user_input = st.session_state.user_input.strip()
    if not user_input:
        return

    # Add user message
    st.session_state.messages.append(("user", user_input))

    try:
        with st.spinner("🤖 Generating response..."):
            payload = {"prompt": user_input}
            resp = requests.post(GENERATE_URL, json=payload, timeout=60)

        if resp.status_code == 200:
            data = resp.json()
            reply = data.get("response", "⚠️ No response received.")
        else:
            reply = f"❌ Error {resp.status_code}: {resp.text}"
    except Exception as e:
        reply = f"❌ Exception: {e}"

    # Add bot reply
    st.session_state.messages.append(("bot", reply))
    st.session_state.user_input = ""

# ==========================================================
# Display chat history
# ==========================================================
st.markdown("### 💬 Conversation")

for role, text in st.session_state.messages:
    if role == "user":
        st.markdown(f"<div class='chat-bubble user-bubble'>🧑 <b>Me:</b> {text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble bot-bubble'>🤖 <b>Bot:</b> {text}</div>", unsafe_allow_html=True)

# ==========================================================
# Input section — neatly aligned
# ==========================================================
col1, col2 = st.columns([6, 1])

with col1:
    st.text_input(
        "💬 Your message:",
        key="user_input",
        placeholder="Type your message here...",
        label_visibility="collapsed",
        on_change=send_message,
    )

with col2:
    st.button("Send", on_click=send_message)
