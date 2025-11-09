import streamlit as st
import pandas as pd
from modules.utils import load_users, save_users

def show_dashboard_page():
    st.header("📊 Your Dashboard")

    df_users = load_users()
    user_name = st.session_state.get("user")
    if not user_name:
        st.warning("Log in before using our services.")
        return

    user = df_users[df_users["name"] == user_name].iloc[0]

    st.metric("🏅 Level", int(user["level"]))
    st.metric("🏆 Title", user["badge"])
    try:
        st.metric("🎯 Challenges Completed", int(user["completed_easy"] + user["completed_medium"] + user["completed_hard"]))
    except ValueError:
        st.metric("🎯 Challenges Completed", 0)
    st.metric("⭐ Total XP", int(user["xp"]))
    st.metric("💨 CO₂ Saved", f"{float(user['co2_saved']):.1f} kg")

    st.divider()

    current_goal = user.get("co2_goal", 10)
    st.subheader("🎯 Set your personal CO₂ goal")
    new_goal = st.number_input("Goal (kg)", min_value=1, max_value=1000, value=int(current_goal))
    if st.button("Update goal"):
        df_users.loc[df_users["name"] == user_name, "co2_goal"] = new_goal
        save_users(df_users)
        st.success(f"✅ Goal updated to {new_goal} kg CO₂ saved!")

    # Progress bar
    progress = min(float(user["co2_saved"]) / float(new_goal), 1.0)
    st.progress(progress)
    st.write(f"Progress: **{progress*100:.1f}%** of your goal")
