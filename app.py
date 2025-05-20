"""
Streamlit Chatbot with GROQ & Serper Search

This app shows how to implement the same multi-step flow,
using GROQ's Python library for LLM inference and Serper's REST API for search.

Requirements (in requirements.txt):
  streamlit
  requests
  groq

Set your secrets on Streamlit Cloud (or export env vars):
  GROQ_API_KEY = "<your-groq-api-key>"
  SERPER_API_KEY = "<your-serper-key>"

Usage:
  streamlit run app.py
"""

import streamlit as st
import os
import requests
import json
import ast

# -------------
# Configuration
# -------------
# Load API keys
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
    # Perform chat completion via GROQ's OpenAI-compatible endpoint
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

# -------------
# Streamlit UI
# -------------

st.set_page_config(page_title="Test Chatbot")
st.title("Test Chatbot")

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
    # 3. Call GROQ LLM
    with st.spinner("Generating answer..."):
        try:
            answer = call_llm(prompt)
        except Exception as e:
            answer = f"Error from GROQ: {e}"
    # 4. Store results
    st.session_state["last_user"] = user_input
    st.session_state["last_response"] = answer

# Display only the latest query and answer
if st.session_state["last_user"]:
    st.subheader("You asked:")
    st.write(st.session_state["last_user"])
    st.subheader("Answer:")
    st.write(st.session_state["last_response"])

