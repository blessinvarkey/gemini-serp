import streamlit as st
import os
from langchain.utilities import GoogleSerperAPIWrapper
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

# Initialize chat history in session state
if "history" not in st.session_state:
    st.session_state.history = []

# User input form
def handle_submit():
    user_msg = st.session_state.user_input.strip()
    if not user_msg:
        return
    # Append user message
    st.session_state.history.append({"role": "user", "message": user_msg})
    # Get response
    with st.spinner("Thinking..."):
        try:
            bot_response = agent.invoke(user_msg)
        except Exception as e:
            bot_response = f"Error: {e}"
    # Append assistant message
    st.session_state.history.append({"role": "assistant", "message": bot_response})
    # Clear input
    st.session_state.user_input = ""

st.text_input("You:", key="user_input", on_change=handle_submit)

# Display the chat history
for chat in st.session_state.history:
    if chat["role"] == "user":
        st.chat_message("user").write(chat["message"])
    else:
        st.chat_message("assistant").write(chat["message"])

# Footer
st.markdown("---")
st.caption("Gemini + Search ChatBot")
