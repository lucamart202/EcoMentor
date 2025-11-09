import streamlit as st

# Main function to display the home page
def show_home_page():
    st.title("🌱 EcoMentor AI")

    user_name = st.session_state.get("user")  # Get current user's name from session
    if not user_name:  # Check if user is logged in
        st.warning("Log in before using our services.")
        return

    # Intro text about EcoMentor
    st.markdown(
        """
        Welcome to ***EcoMentor***: the app that helps you transform small daily actions into a big environmental impact.

        The goal is to guide you to reduce your CO₂ impact through simple challenges, tracking your progress and rewarding sustainable behaviors with XP and badges.
        """
    )

    st.success("*“The greatest threat to our planet is the belief that someone else will save it.”*  \n— Robert Swan")

    st.divider()

    # Show available titles (badges) and a brief explanation
    st.subheader("🏆 Titles")
    cols = st.columns(4)  # Create 4 columns to display badges
    badges = [
        # Each badge: name, divider, description, how to get it
        ("🌱 EcoNovice", "---", "You've just started the journey towards a more sustainable lifestyle", "You get this badge by signing up"),
        ("🌿 EcoSupporter", "---", "You've completed some challenges and are saving CO₂", "You get this badge by completing 5 challenges"),
        ("🌳 Green Hero", "---", "You're among the best: many sustainable actions completed", "You get this badge by completing 10 challenges"),
        ("🦋 EcoMaster", "---", "Environmental hero: great impact and consistency over time", "You get this badge by completing 15 challenges and saving 50 kg of CO₂")
    ]
    # Loop through columns and badges to display each badge's info
    for col, b in zip(cols, badges):
        col.markdown(f"**{b[0]}**")
        col.markdown(b[1])
        col.caption(b[2])
        col.caption(b[3])