import streamlit as st
import os
import requests
import json

# -------------
# Page config
# -------------
st.set_page_config(page_title="Groq-SERP Chatbot", layout="wide")
st.title("Groq-SERP-llama-3.3-70b Chatbot")

# -------------
# Load API keys
# -------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
SERPER_API_KEY = st.secrets.get("SERPER_API_KEY") or os.getenv("SERPER_API_KEY")

# Initialize GROQ client if key is available
if GROQ_API_KEY:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None

# ----------------
# Helper functions
# ----------------
def serp_search(query: str) -> dict:
    """Call Serper REST API and return JSON results."""
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY}
    params = {"q": query}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()

def call_llm(prompt: str, max_tokens: int = 4096) -> str:
    """Route prompt to GROQ LLM; raise error if client missing."""
    if not groq_client:
        return "Error: GROQ_API_KEY not provided."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

# -------------------------
# Initialize chat history
# -------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # list of {"role":..., "content":...}

# -------------------------------------------------
# Callback: run when user presses Enter in textbox
# -------------------------------------------------
def on_enter():
    user_msg = st.session_state.user_input.strip()
    if not user_msg:
        return

    # 1. Append user turn
    st.session_state.history.append({"role": "user", "content": user_msg})

    # 2. External SERP search
    with st.spinner("Searching external data..."):
        search_results = serp_search(user_msg)

    # 3. Build prompt for LLM
    prompt = (
        "You are a helpful assistant. Use the following search results to answer the question.\n"
        f"Search results (JSON): {json.dumps(search_results)}\n\n"
        f"Question: {user_msg}\n\n"
        "Please provide a clear, accurate, and fully scoped answer."
    )

    # 4. Call GROQ LLM
    with st.spinner("Generating answer..."):
        try:
            answer = call_llm(prompt)
        except Exception as e:
            answer = f"Error from GROQ: {e}"

    # 5. Append assistant turn
    st.session_state.history.append({"role": "assistant", "content": answer})

    # 6. Clear input box
    st.session_state.user_input = ""

# --------------------------
# User input box (Enter-to-send)
# --------------------------
st.text_input(
    label="You:",
    key="user_input",
    on_change=on_enter,
    placeholder="Type your message and press Enter…"
)

# --------------------------
# Render the chat history
# --------------------------
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Assistant:** {msg['content']}")
