import streamlit as st
import requests

API_URL = "https://apifreellm.com/api/chat"  # LLM API endpoint

def ask_llm(question: str) -> str:
    # Query the EcoMentor LLM API with question and get filtered, focused response

    # System prompt to guide the model response strictly to sustainability topics
    system_prompt = (
        "You are EcoMentor, an educational mentor on the environment. "
        "Answer only questions related to ecology, sustainability, environment, energy, "
        "recycling, climate, green mobility, sustainable nutrition or energy saving. "
        "If the question does not concern these topics, answer exactly: "
        "'Question out of place'. "
        "Use a positive, educational and concise style."
    )

    # Combine system instructions and user's question
    full_prompt = f"{system_prompt}\n\nQuestion: {question}\nAnswer:"

    try:
        # Send request to API with prompt
        response = requests.post(API_URL, json={"message": full_prompt}, timeout=15)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()  # Parse JSON response
            answer = data.get("response", "").strip()  # Get model's answer
            if not answer:
                return "Unable to answer the question, please try something else."
            return answer
        else:
            return "Unable to answer the question, please try something else."

    except Exception:
        # Fallback error message if API/server is unavailable
        return "EcoMentor is not available at the moment, please try again later."

def show_mentor_page():
    # Streamlit UI for the EcoMentor chatbot page
    st.header("💬 EcoMentor AI")

    user_name = st.session_state.get("user")  # Retrieve logged-in user's name
    if not user_name:
        # Prompt login requirement if user not authenticated
        st.warning("Log in before using our services.")
        return

    st.markdown("Ask a question about the environment, sustainability or energy!")

    user_input = st.text_area("Write your question here:", height=100)  # Input box

    if st.button("Ask EcoMentor"):
        # Check if input is not empty
        if not user_input.strip():
            st.warning("Write a question before sending")
            return

        # Show spinner while generating model response
        with st.spinner("EcoMentor is thinking... 💬"):
            answer = ask_llm(user_input)  # Get answer from LLM

        st.subheader("🌍 EcoMentor's Answer:")
        st.success(answer)  # Display the answer to the user
