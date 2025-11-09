import streamlit as st
from modules.profile import show_profile_page
from modules.challenges import show_challenges_page
from modules.dashboard import show_dashboard_page
from modules.chatbot import show_mentor_page
from modules.home import show_home_page
from datetime import date

# Set up main page configuration
st.set_page_config(page_title="EcoMentor", page_icon="🌱", layout="centered")

st.sidebar.title("🌱 EcoMentor AI")

st.sidebar.markdown(f"📅 Today is **{date.today()}**")

# Get username from session state
user_name = st.session_state.get("user")
if user_name:
    st.sidebar.success(f"👋 Hello ***{user_name}***")  # Show logged-in user in sidebar
    # Logout button and logic
    if st.sidebar.button("🚪 Logout"):
        del st.session_state["user"]  # Remove user from session on logout
        st.sidebar.success("Logged out successfully")
        st.rerun()  # Rerun the app to refresh state
    st.sidebar.divider()

# Navigation menu options
options = ["Profile", "Home", "Challenges", "Dashboard", "EcoMentor AI"]

# Sidebar radio for section navigation
menu = st.sidebar.radio("Navigate between sections:", options)

st.sidebar.divider()
st.sidebar.caption("🌱 EcoMentor  —  Build-a-thon 2025")  # Sidebar footer caption

# Navigation logic to show the appropriate page based on menu selection
if menu == "Home":
    show_home_page()
elif menu == "Profile":
    show_profile_page()
elif menu == "Challenges":
    show_challenges_page()
elif menu == "Dashboard":
    show_dashboard_page()
elif menu == "EcoMentor AI":
    show_mentor_page()
