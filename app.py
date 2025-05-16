import streamlit as st
import os
import json
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, Tool, AgentType

# Initialize the LLM (Gemini)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0
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
            response = agent.invoke(msg)
        except Exception as e:
            response = f"Error: {e}"
    st.session_state.history.append({"role": "assistant", "message": response})
    st.session_state.user_input = ""

# Input box
st.text_input("You:", key="user_input", on_change=handle_submit)

# Display chat
for chat in st.session_state.history:
    if chat["role"] == "user":
        st.chat_message("user").write(chat["message"])
    else:
        # If the response is valid JSON, show structured JSON; otherwise render markdown
        try:
            parsed = json.loads(chat["message"])
            st.chat_message("assistant").json(parsed)
        except Exception:
            st.chat_message("assistant").markdown(chat["message"])

# Footer
st.caption("Google Gemini + Search")
