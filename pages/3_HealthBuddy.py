# Lab 3: HealthBuddy chatbot page
#
# A friendly AI chatbot built with Pydantic AI and Google Gemini.
# It explains conditions and medical words in simple language.
# It does NOT look anything up in our dataset -- it just talks.
#
# Your Gemini API key goes in .streamlit/secrets.toml as GOOGLE_API_KEY.

import os
import streamlit as st
from pydantic_ai import Agent


st.title("💬 HealthBuddy")
st.write(
    "Ask me to explain a condition, a symptom, or a medical word. "
    "I'm a study buddy, not a doctor!"
)

# Give the Gemini key to Pydantic AI by putting it in the environment.
if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

# If there is no key yet, show a friendly message instead of crashing.
if not os.environ.get("GOOGLE_API_KEY"):
    st.warning(
        "HealthBuddy needs a Gemini API key to work. Paste your free key into "
        ".streamlit/secrets.toml as GOOGLE_API_KEY, then refresh this page."
    )
    st.stop()

# Make the chatbot. The instructions set its personality and keep it on-topic.
# If a model name ever stops working, change the model string below.
agent = Agent(
    "google:gemini-3.5-flash-lite",
    instructions=(
        "You are HealthBuddy, a friendly study helper for medical students. "
        "You explain medical conditions, symptoms, and medical words in a clear, "
        "simple, and encouraging way. Keep your answers short and easy to read. "
        "You are not a doctor, so always remind the user that this is for learning "
        "only and that real symptoms should be checked by a professional. "
        "Do not make up patient data, statistics, or test results."
    ),
)

# We keep two lists in session_state so the chat is remembered between reruns:
#   - messages: what we show on the screen
#   - history:  what Pydantic AI needs to remember the conversation
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []

# Show the conversation we have so far.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["text"])

# The text box at the bottom of the page.
user_text = st.chat_input("Type your question here...")

if user_text:
    # Save and show what the user said.
    st.session_state.messages.append({"role": "user", "text": user_text})
    with st.chat_message("user"):
        st.write(user_text)

    # Ask the AI. The try/except makes sure an error shows a message
    # instead of crashing the whole page.
    try:
        result = agent.run_sync(
            user_text,
            message_history=st.session_state.history,
        )
        answer = result.output
        # Remember the conversation for next time.
        st.session_state.history = result.all_messages()
    except Exception:
        answer = "Sorry, something went wrong. Please try asking again in a moment."

    # Save and show the AI's answer.
    st.session_state.messages.append({"role": "assistant", "text": answer})
    with st.chat_message("assistant"):
        st.write(answer)
