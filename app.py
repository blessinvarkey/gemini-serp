import streamlit as st
import os
import requests
import json

# -------------
# Page config
# -------------
st.set_page_config(page_title="Groq-SERP Chatbot", layout="wide")
st.title("Groq-llama-3.3-70b Chatbot")

# -------------
# Load API keys
# -------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
SERPER_API_KEY = st.secrets.get("SERPER_API_KEY") or os.getenv("SERPER_API_KEY")

if GROQ_API_KEY:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None

# ----------------
# Helper functions
# ----------------
def serp_search(query: str) -> dict:
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY}
    params = {"q": query}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()

def call_llm(prompt: str, max_tokens: int = 4096) -> str:
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
    st.session_state.history = []  # will hold only assistant responses

# -------------------------------------------------
# Callback: run when user presses Enter in textbox
# -------------------------------------------------
def on_enter():
    user_msg = st.session_state.user_input.strip()
    if not user_msg:
        return

    # 1. External SERP search
    with st.spinner("Searching external data..."):
        search_results = serp_search(user_msg)

    # 2. Build prompt
    prompt = (
        "You are a helpful assistant. Use the following search results to answer the question.\n"
        f"Search results (JSON): {json.dumps(search_results)}\n\n"
        f"Question: {user_msg}\n\n"
        "Please provide a clear, accurate, and fully scoped answer."
    )

    # 3. Call GROQ LLM
    with st.spinner("Generating answer..."):
        try:
            answer = call_llm(prompt)
        except Exception as e:
            answer = f"Error from GROQ: {e}"

    # 4. Store only the assistant's reply
    st.session_state.history.append(answer)

    # 5. Clear input box
    st.session_state.user_input = ""

# --------------------------
# Input box (Enter-to-send)
# --------------------------
st.text_input(
    label="",
    key="user_input",
    on_change=on_enter,
    placeholder="Type your message and press Enter…"
)

# --------------------------
# Render only assistant replies
# --------------------------
for reply in st.session_state.history:
    st.markdown(reply)
