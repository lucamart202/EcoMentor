import streamlit as st
import requests
import time

API_URL = "https://apifreellm.com/api/chat"  # LLM API endpoint

def build_chat_context(chat_history):
    """
    Instead of formatting as messages, send previous conversation as a string to the system prompt.
    """
    # Compose the full conversation as text
    context = ""
    for msg in chat_history:
        if msg["role"] == "user":
            context += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            context += f"EcoMentor: {msg['content']}\n"
    return context

def ask_llm(chat_history, question: str) -> str:
    """
    Sends the SYSTEM prompt with context containing all previous messages, plus the latest user question.
    """
    base_prompt = (
        "You are EcoMentor, an educational mentor on the environment. "
        "Answer only questions related to ecology, sustainability, environment, energy, climate, green mobility, sustainable nutrition or energy saving."
        "If the question does not concern these topics, answer exactly: "
        "'Question out of place.'"
        "Answer in beautiful markdown format with proper headings and paragraphs. Do not write any header"
        "Use a positive, educational and concise style.\n\n"
    )
    previous_context = build_chat_context(chat_history)
    # Add the current user question at the end
    full_prompt = (
        base_prompt +
        ("Previous conversation:\n" + previous_context if previous_context else "") +
        f"\nUser: {question}\nEcoMentor:"
    )
    try:
        # Some endpoints expect 'message' as a single string, not chat format
        response = requests.post(
            API_URL, json={"message": full_prompt}, timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "").strip() or \
                     data.get("answer", "").strip()
            if not answer:
                return "Unable to answer the question, please try something else."
            return answer
        else:
            return "Unable to answer the question, please try something else."
    except Exception:
        return "EcoMentor is not available at the moment, please try again later."

def show_mentor_page():
    st.header("💬 EcoMentor AI")

    user_name = st.session_state.get("user")

    if not user_name:
        st.warning("Log in before using our services.")
        return

    st.write(
        "Ask anything about ecology, sustainability, environment, energy, recycling, green mobility, sustainable nutrition, or energy saving."
    )
    st.caption("EcoMentor answers only sustainability-related questions.")

    # Initialize chat history if needed
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Let's start chatting about the environment! 👇"}
        ]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask EcoMentor about the environment, sustainability or energy!"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Query the model and "stream" the response, WITH MEMORY
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            with st.spinner("EcoMentor is thinking... 💬"):
                # Use all past messages as chat history for the LLM
                history = st.session_state.messages[:-1]
                answer = ask_llm(history, prompt)
                # Simulate streaming response, but chunk by line (for better formatting)
                answer_lines = answer.split('\n')
                for line in answer_lines:
                    line_buffer = ""
                    # Stream each line word by word
                    for chunk in line.split():
                        line_buffer += chunk + " "
                        # To force new lines render, use markdown with 'full_response' built so far plus the current line
                        message_placeholder.markdown(full_response + line_buffer + "▌")
                        time.sleep(0.04)
                    full_response += line_buffer.rstrip() + "\n"
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
