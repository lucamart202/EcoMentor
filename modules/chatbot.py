import streamlit as st
import time
import requests
import json
import os

# OpenRouter API config
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_ID = "qwen/qwen3-235b-a22b:free"
DAILY_TOKEN_LIMIT = 250_000  # daily limit


def build_chat_context(chat_history):
    # Convert history to plain text
    context = ""
    for msg in chat_history:
        if msg["role"] == "user":
            context += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            context += f"EcoMentor: {msg['content']}\n"
    return context

def ask_llm(chat_history, question: str) -> str:
    # Check and update token tracking
    if "tokens_used_today" not in st.session_state:
        st.session_state.tokens_used_today = 0

    # Estimate used tokens for this request (approximate for LLMs)
    estimated_tokens = len(question) // 4 + 10
    if st.session_state.tokens_used_today + estimated_tokens > DAILY_TOKEN_LIMIT:
        return "Daily limit reached. Try again tomorrow."

    API_KEY = "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"
    if not API_KEY or "<OPENROUTER_API_KEY>" in API_KEY:
        return "EcoMentor is not available at the moment: OpenRouter API key not found in the environment variable."

    # Prepare chat structure for OpenRouter API
    messages = [
        {
            "role": "system",
            "content": (
                "You are EcoMentor, an educational mentor on the environment. "
                "Answer only questions related to ecology, sustainability, environment, energy, climate, green mobility, sustainable nutrition or energy saving. "
                "If the question does not concern these topics, answer exactly: 'Question out of place.' "
                "Answer in beautiful markdown format with proper headings and paragraphs, using a positive, educational, and concise style."
            )
        }
    ]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": question})

    data = {
        "model": MODEL_ID,
        "messages": messages,
    }

    try:
        response = requests.post(
            url=OPENROUTER_API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
            timeout=30
        )
        if response.status_code == 429:
            return "API limit reached, try again later."

        response.raise_for_status()
        result = response.json()
        # Extract the assistant's answer
        answer = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        # Update session tokens used
        usage = result.get("usage", {})
        st.session_state.tokens_used_today += usage.get("total_tokens", estimated_tokens)

        return answer or "Unable to answer the question, please try again."
    except Exception as e:
        return f"EcoMentor is not available at the moment: {e}"

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

    # Display past messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept new user message
    if prompt := st.chat_input("Ask EcoMentor about the environment, sustainability or energy!"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Query the model and stream the response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            with st.spinner("EcoMentor is thinking... 💬"):
                history = st.session_state.messages[:-1]
                answer = ask_llm(history, prompt)
                # Render streamed response (word-by-word, line-by-line)
                for line in answer.split("\n"):
                    line_buffer = ""
                    for chunk in line.split():
                        line_buffer += chunk + " "
                        message_placeholder.markdown(full_response + line_buffer + "▌")
                        time.sleep(0.02)
                    full_response += line_buffer.rstrip() + "\n"
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
