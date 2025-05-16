import streamlit as st
import os
import json
import ast
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, Tool, AgentType

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_output_tokens=8192  # ensure long outputs
)

# Initialize the Serper search tool
tools = [
    Tool(
        name="Intermediate Answer",
        func=GoogleSerperAPIWrapper().run,
        description="Useful for when you need external search"
    )
]

# Build the agent with parsing error handling enabled
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.SELF_ASK_WITH_SEARCH,
    handle_parsing_errors=True,  # retry on output parsing failures
    verbose=False
)

# -- STREAMLIT APP UI --
st.set_page_config(page_title="Agent + Gemnini + Search Chatbot", page_icon="🤖")
st.title("LangChain+Gemini+SERP Test Chatbot")

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
            # Agent will automatically retry parsing if needed
            response = agent.invoke(msg)
        except Exception as e:
            response = f"Error: {e}"
    st.session_state.history.append({"role": "assistant", "message": response})
    st.session_state.user_input = ""

# Input box
st.text_input("You:", key="user_input", on_change=handle_submit)

# Display chat history
for chat in st.session_state.history:
    role = chat.get("role")
    message = str(chat.get("message", ""))
    if role == "user":
        st.chat_message("user").write(message)
    else:
        # Try parsing structured responses
        parsed = None
        if message.strip().startswith("{"):
            try:
                parsed = json.loads(message)
            except (json.JSONDecodeError, TypeError):
                try:
                    parsed = ast.literal_eval(message)
                except Exception:
                    parsed = None
        if isinstance(parsed, dict) and 'output' in parsed:
            # Display only the 'output' field
            st.chat_message("assistant").markdown(parsed['output'])
        else:
            # Render full text otherwise
            st.chat_message("assistant").markdown(message)

