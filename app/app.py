import streamlit as st

from src.chatbot import UFix


st.set_page_config(
    page_title="uFix - UiTM IT Helpdesk",
    page_icon="💻",
    layout="centered"
)


@st.cache_resource
def load_chatbot():
    return UFix()


st.title("uFix")
st.caption("Your UiTM IT Helpdesk Assistant")

st.info(
    "Do not enter passwords or sensitive personal information."
)


# Initialise the chatbot
try:
    bot = load_chatbot()
except Exception as e:
    print(f"[uFix] Initialisation failed: {type(e).__name__}")
    st.error(
        "Unable to initialise the chatbot. "
        "Check the API configuration."
    )
    st.stop()


# Initialise conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Store the greeting
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hi! I'm **uFix**. How can I help you today?"
    })


# Sidebar
with st.sidebar:
    st.header("Supported IT Services")

    st.markdown("""
    - Campus Wi-Fi
    - iStudent Portal
    - UFUTURE
    - Google Workspace
    - Password reset
    - VPN access
    - Digital Student ID
    - ICT Helpdesk and Reporting
    - University Software and Licensing
    - Digital Library and Research Tools
    - Basic Computer Troubleshooting
    """)

    st.divider()

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()


# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Accept user input
user_question = st.chat_input("Ask uFix a question...")


if user_question and user_question.strip():

    st.session_state.messages.append({
        "role": "user",
        "content": user_question
    })

    with st.chat_message("user"):
        st.markdown(user_question)

    # Gen chatbot response
    with st.chat_message("assistant"):
        try:
            with st.spinner("uFix is thinking..."):
                reply = bot.chat(user_question)

        except Exception as e:
            print(f"[uFix] Chat failed: {type(e).__name__}")

            reply = (
                "Sorry, something went wrong while processing "
                "your question. Please try again."
            )

        st.markdown(reply)

    # Store chatbot response
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })