import streamlit as st
import os
import json
import ast
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, Tool, AgentType

# Initialize the LLM (Gemini) with increased output token limit to avoid truncation
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_output_tokens=8192  
)

# Initialize the Serper search tool
tools = [
    Tool(
        name="Intermediate Answer",
        func=GoogleSerperAPIWrapper().run,
        description="Useful for when you need external search"
    )
]

# Build the agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.SELF_ASK_WITH_SEARCH,
    verbose=False
)

# -- STREAMLIT APP UI --
st.set_page_config(page_title="GenAI Streamlit Chatbot", page_icon="🤖")
st.title("GenAI Streamlit Chatbot")

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Handle user submissions
def handle_submit():
    msg = st.session_state.user_input.strip()
    if not msg:
        return
    st.session_state.history.append({"role": "user", "message": msg})
    with st.spinner("Thinking..."):
        try:
            # Pass through max_tokens to ensure full answer
            response = agent.invoke(msg, stop=None)
        except Exception as e:
            response = f"Error: {e}"
    st.session_state.history.append({"role": "assistant", "message": response})
    st.session_state.user_input = ""

# Input box
st.text_input("You:", key="user_input", on_change=handle_submit)

# Display chat
for chat in st.session_state.history:
    role = chat.get("role")
    message = str(chat.get("message", ""))
    if role == "user":
        st.chat_message("user").write(message)
    else:
        text = message
        # Try parsing as JSON-like dict first
        parsed = None
        if text.strip().startswith("{"):
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                try:
                    parsed = ast.literal_eval(text)
                except Exception:
                    parsed = None
        if isinstance(parsed, dict) and 'output' in parsed:
            # Only display the output field
            st.chat_message("assistant").markdown(parsed['output'])
        else:
            # Fallback: render full text as markdown
            st.chat_message("assistant").markdown(text)

