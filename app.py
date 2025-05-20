import streamlit as st
import os
import requests
import json
import google.generativeai as genai

# -------------
# Configuration
# -------------
# Use Streamlit secrets or environment variables
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
SERPER_API_KEY = st.secrets.get("SERPER_API_KEY") or os.getenv("SERPER_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

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


def call_gemini(prompt: str, max_tokens: int = 8192) -> str:
    """Send a prompt to Google Gemini and return the response content."""
    response = genai.chat.completions.create(
        model="gemini-2.0-flash",
        prompt=prompt,
        temperature=0,
        candidate_count=1,
        max_output_tokens=max_tokens
    )
    # Access the message text
    return response.choices[0].message.content

# -------------
# Streamlit UI
# -------------

st.set_page_config(page_title="GenAI Plain Python Chatbot", page_icon="🤖")
st.title("GenAI Plain Python Chatbot")

# Session state to store only the latest interaction
if "last_user" not in st.session_state:
    st.session_state["last_user"] = ""
if "last_response" not in st.session_state:
    st.session_state["last_response"] = ""

# User input
user_input = st.text_input("You:", value="", key="input")
if st.button("Send") and user_input:
    # 1. External search
    with st.spinner("Searching external data..."):
        search_results = serp_search(user_input)
    # 2. Build combined prompt
    search_json = json.dumps(search_results)
    prompt = (
        "You are a helpful assistant. Use the following search results to answer the question.\n"
        f"Search results (JSON): {search_json}\n\n"
        f"Question: {user_input}\n\n"
        "Please provide a clear, accurate, and fully scoped answer."
    )
    # 3. Call Gemini
    with st.spinner("Generating answer..."):
        try:
            answer = call_gemini(prompt)
        except Exception as e:
            answer = f"Error from Gemini: {e}"
    # 4. Store results
    st.session_state["last_user"] = user_input
    st.session_state["last_response"] = answer

# Display only the latest query and answer
if st.session_state["last_user"]:
    st.subheader("You asked:")
    st.write(st.session_state["last_user"])
    st.subheader("Answer:")
    st.write(st.session_state["last_response"])

st.caption("Powered by Google Gemini & Serper Search | Plain Python implementation")
