import streamlit as st
import pandas as pd
from datetime import date
import json
from modules.utils import load_users, load_challenges, save_users

# Check if a challenge is available for proposal again based on its completion recency
def is_challenge_available(challenge_id, last_completions, min_days=7):
    from datetime import datetime  # for date comparison
    
    str_id = str(challenge_id)  # ensure string id
    
    # Challenge is available if not in recent completions
    if str_id not in last_completions:
        return True
        
    # Check how many days since last completion
    last_completion = datetime.strptime(last_completions[str_id], "%Y-%m-%d").date()
    days_passed = (date.today() - last_completion).days
    return days_passed >= min_days

# Update challenge completion history and counters for a user
def update_completion_history(df_users, user_name, challenge_id):
    today = str(date.today())  # today's date as string
    challenge_id_str = str(challenge_id)  # ensure string

    # Add last_completions column if missing (stores challenge completion dates)
    if 'last_completions' not in df_users.columns:
        df_users['last_completions'] = df_users.apply(lambda x: json.dumps({}), axis=1)

    # Find user's row index by username
    row_idx = df_users.index[df_users['name'] == user_name]
    if len(row_idx) == 0:
        return df_users, None
    row_idx = row_idx[0]

    # Load or initialize last completion dates dict
    last_completions = json.loads(df_users.at[row_idx, 'last_completions'] if pd.notnull(df_users.at[row_idx, 'last_completions']) else '{}')
    
    # Keep only 5 most recent challenges, remove oldest if full
    if len(last_completions) >= 5:
        oldest_challenge = min(last_completions.items(), key=lambda x: x[1])[0]
        del last_completions[oldest_challenge]

    # Add current challenge to last_completions
    last_completions[challenge_id_str] = today
    df_users.at[row_idx, 'last_completions'] = json.dumps(last_completions)

    # Update challenge difficulty counters for the user (easy, medium, hard)
    try:
        df_challenges = load_challenges()  # load challenge info
        diff = df_challenges.loc[df_challenges['id'] == int(challenge_id), 'difficulty'].iloc[0]
        col_map = {
            'Easy': 'completed_easy',
            'Medium': 'completed_medium',
            'Hard': 'completed_hard'
        }
        col = col_map.get(diff)
        if col:
            if col not in df_users.columns:
                df_users[col] = 0  # initialize column if missing
            # increment completion count
            df_users.loc[df_users['name'] == user_name, col] = (
                df_users.loc[df_users['name'] == user_name, col].fillna(0).astype(int) + 1
            )
    except Exception:
        # Ignore errors if challenge or columns are missing
        pass

    # Reload user row with updates and save users
    user_series = df_users[df_users['name'] == user_name].iloc[0]
    save_users(df_users)

    return df_users, user_series

# Pick a hard challenge available for today
def get_daily_challenge(df_challenges, last_completions):
    available = df_challenges[
        (df_challenges["difficulty"] == "Hard") &
        (df_challenges["id"].apply(lambda x: is_challenge_available(x, last_completions, min_days=7)))
    ]
    return available.sample(1).iloc[0] if not available.empty else None

# Pick an easy or medium available challenge, excluding today's daily
def get_optional_challenge(df_challenges, last_completions, active_daily_id):
    available = df_challenges[
        (df_challenges["difficulty"].isin(["Easy", "Medium"])) &
        (~df_challenges["id"].isin([active_daily_id])) &
        (df_challenges["id"].apply(lambda x: is_challenge_available(x, last_completions, min_days=3)))
    ]
    return available.sample(1).iloc[0] if not available.empty else None

# Get emoji and color representing challenge difficulty
def get_difficulty_style(difficulty):
    styles = {
        "Easy": ("🟢", "green"),
        "Medium": ("🟡", "orange"),
        "Hard": ("🔴", "red")
    }
    return styles.get(difficulty, ("⚪", "gray"))

# Update user XP, level, badge and CO2 saved after completing a challenge
def update_user_progress(df_users, user_name, user_data, xp_gain, eco_impact, factor, df_challenges):
    current_co2 = user_data.get("co2_saved", 0)
    co2_saved = current_co2 + (eco_impact * factor)  # incremental update

    # Calculate how many challenges user has completed by sum of counters
    completed_count = (
        user_data.get("completed_easy", 0) + 
        user_data.get("completed_medium", 0) + 
        user_data.get("completed_hard", 0)
    )
    # Determine the badge based on progress
    badge = "🦋 EcoMaster" if completed_count >= 15 and co2_saved >= 50 else \
            "🌳 Green Hero" if completed_count >= 10 else \
            "🌿 EcoSupporter" if completed_count >= 5 else \
            "🌱 EcoNovice"

    user_xp = user_data.get("xp", 0) + xp_gain  # add gained XP
    user_level = user_data.get("level", 1)     # current level

    # Level up if XP threshold is reached
    if user_xp >= min(int(10*user_level*user_level), 500):
        user_level += 1
        st.balloons()
        st.success(f"🎉 You reached level {user_level}!")

    # Persist values in dataframe
    df_users.loc[df_users["name"] == user_name, ["xp", "level", "badge", "co2_saved"]] = [
        user_xp, user_level, badge, co2_saved
    ]

    # Update the mutable user_data dict for immediate local reference
    user_data["xp"] = user_xp
    user_data["level"] = user_level
    user_data["badge"] = badge
    user_data["co2_saved"] = co2_saved

    save_users(df_users)  # commit changes

    return user_xp, user_level, badge, co2_saved

# Main Streamlit UI for showing/handling challenges
def show_challenges_page():
    st.header("🏆 Your Daily Challenges")

    user_name = st.session_state.get("user")  # current user
    if not user_name:
        st.warning("Log in before using our services.")
        return

    df_users = load_users()  # user records
    df_challenges = load_challenges()  # challenge definitions
    today = str(date.today())  # today's date

    user = df_users[df_users["name"] == user_name].iloc[0]  # current user's row
    last_completions = json.loads(user["last_completions"])  # recent completions dict
    factor = 0.1  # kg CO₂ per ecoImpact point

    # --- Show profile stats ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Level", user.get("level", 1))
    with col2:
        st.metric("XP", f"{user.get('xp', 0)}/{min(int(10*user.get('level', 1)*user.get('level', 1)), 500)}")
    with col3:
        st.metric("CO₂ Saved", f"{user.get('co2_saved', 0):.1f} kg")

    # --- Challenge state variables ---
    active_daily_id = user.get("active_challenge_id", "")   # daily challenge id
    active_date = user.get("active_challenge_date", "")     # when daily was loaded
    optional_id = user.get("optional_challenge_id", "")     # extra challenge id
    optional_challenge = None  # stores generated extra challenge, if any

    # --- Select/generate daily challenge for today ---
    if active_daily_id and str(active_date) == today:
        # Already have a daily challenge for today; load it
        daily_challenge = df_challenges[df_challenges["id"] == int(active_daily_id)].iloc[0]
    else:
        # Need to select a new daily challenge
        daily_challenge = get_daily_challenge(df_challenges, last_completions)
        if daily_challenge is None:
            st.info("🎉 No hard challenges available today! Try again tomorrow.")
            return
        
        # Pick an extra challenge for today (easy/medium)
        optional_challenge = get_optional_challenge(df_challenges, last_completions, daily_challenge["id"])
        
        # Track today's active challenges for this user
        optional_id_value = int(optional_challenge["id"]) if optional_challenge is not None else 0
        df_users.loc[df_users["name"] == user_name, [
            "active_challenge_id", 
            "active_challenge_date",
            "optional_challenge_id"
        ]] = [int(daily_challenge["id"]), today, optional_id_value]
        save_users(df_users)
        
        # Update variable for display
        optional_id = optional_id_value

    # --- Display Daily Challenge info ---
    st.subheader("💪 Challenge of the Day")
    diff_emoji, diff_color = get_difficulty_style(daily_challenge['difficulty'])
    st.markdown(f"""
        <div style='padding: 1rem; border-radius: 0.5rem; border: 1px solid {diff_color}; margin-bottom: 1rem;'>
        <h4 style='color: {diff_color}; margin:0;'>{diff_emoji} {daily_challenge['title']}</h4>
        <small>📂 {daily_challenge['category']} • 💫 {daily_challenge['ecoImpact']} impact points</small>
        </div>
    """, unsafe_allow_html=True)

    challenge_id = str(daily_challenge["id"])  # string id of daily challenge
    if challenge_id in last_completions:
        st.info(f"You already completed this challenge on {last_completions[challenge_id]} 🌿")
    elif st.button("✅ Complete the challenge of the day"):
        # User completed the main challenge
        df_users, user = update_completion_history(df_users, user_name, daily_challenge["id"])
        xp_gain = int(daily_challenge["ecoImpact"] * 2)  # hard challenges: double XP
        new_xp, new_level, new_badge, new_co2 = update_user_progress(
            df_users, user_name, user, xp_gain,
            daily_challenge["ecoImpact"], factor, df_challenges
        )
        st.success(f"""
        🌍 Challenge of the day completed! 
        • +{xp_gain} XP (you now have {new_xp} XP)
        • +{daily_challenge['ecoImpact']*factor:.1f} kg CO₂ saved
        • Current level: {new_level}
        • Badge: {new_badge}
        """)

    st.divider()

    # --- Display Extra Challenge info (easy/medium) ---
    st.subheader("🎯 Extra Challenge")
    if optional_id and optional_id != 0:
        # If generated already, use in-memory, otherwise fetch from DB
        if optional_challenge is None:
            optional_challenge = df_challenges[df_challenges["id"] == int(optional_id)].iloc[0]
        
        if optional_challenge is not None:
            diff_emoji, diff_color = get_difficulty_style(optional_challenge['difficulty'])
            st.markdown(f"""
                <div style='padding: 1rem; border-radius: 0.5rem; border: 1px solid {diff_color}; margin-bottom: 1rem;'>
                <h4 style='color: {diff_color}; margin:0;'>{diff_emoji} {optional_challenge['title']}</h4>
                <small>📂 {optional_challenge['category']} • 💫 {optional_challenge['ecoImpact']} impact points</small>
                </div>
            """, unsafe_allow_html=True)

            # Two columns: complete or skip
            col1, col2 = st.columns(2)
            with col1:
                challenge_id = str(optional_challenge["id"])
                if challenge_id in last_completions:
                    st.info(f"You already completed this challenge on {last_completions[challenge_id]} 🌿")
                elif st.button("✅ Complete extra challenge"):
                    # User completes extra challenge
                    df_users, user = update_completion_history(df_users, user_name, optional_challenge["id"])
                    multiplier = {"Easy": 1, "Medium": 1.5}[optional_challenge["difficulty"]]  # XP multiplier by difficulty
                    xp_gain = int(optional_challenge["ecoImpact"] * multiplier)
                    new_xp, new_level, new_badge, new_co2 = update_user_progress(
                        df_users, user_name, user, xp_gain,
                        optional_challenge["ecoImpact"], factor, df_challenges
                    )
                    st.success(f"""
                    🌍 Extra challenge completed! 
                    • +{xp_gain} XP (you now have {new_xp} XP)
                    • +{optional_challenge['ecoImpact']*factor:.1f} kg CO₂ saved
                    • Current level: {new_level}
                    • Badge: {new_badge}
                    """)
            
            with col2:
                if st.button("⏭️ Skip this challenge"):
                    # User requests another optional challenge
                    new_optional = get_optional_challenge(df_challenges, last_completions, active_daily_id)
                    if new_optional is not None:
                        df_users.loc[df_users["name"] == user_name, "optional_challenge_id"] = int(new_optional["id"])
                        save_users(df_users)
                        st.rerun()
                    else:
                        st.info("No other easy/medium challenges available!")
        else:
            st.info("No extra challenges available at the moment.")

    st.divider()
    st.write(f"📅 Challenges valid for today ({today})")
