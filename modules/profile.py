import streamlit as st
import pandas as pd
from modules.utils import load_users, save_users, DEFAULT_USER_VALUES, get_current_date, hash_password, verify_password

def is_valid_username(name):
    # Validate the username
    if not name or len(name.strip()) == 0:
        return False, "Name cannot be empty"
    if len(name) > 30:
        return False, "Name cannot exceed 30 characters"
    if not name.replace(" ", "").isalnum():
        return False, "Name can only contain letters, numbers and spaces"
    return True, ""

def is_valid_pwd(password: str) -> tuple[bool, str]:
    # Validate the password
    if not password or len(password.strip()) == 0:
        return False, "Password cannot be empty"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if len(password) > 50:
        return False, "Password cannot exceed 50 characters"
    return True, ""

def show_profile_page():
    # Main profile page logic (login/register or manage account)
    st.header("👤 Profile Management")
    
    user_name = st.session_state.get("user")  # Get current user from session
    
    # If logged in, show account settings tabs
    if user_name:
        st.success(f"✅ You are logged in as **{user_name}**")
        st.divider()
        
        # Tabs for password change, delete account, info
        tab1, tab2, tab3 = st.tabs(["🔐 Change Password", "🗑️ Delete Account", "ℹ️ Info"])
        
        with tab1:
            st.subheader("🔐 Change Password")
            current_password = st.text_input("Current password", type="password", key="current_pwd") # Old password
            new_password = st.text_input("New password", type="password", key="new_pwd")             # New password
            confirm_password = st.text_input("Confirm new password", type="password", key="confirm_pwd") # Confirm new
            if st.button("Change password"):
                # Ensure all fields filled
                if not current_password or not new_password or not confirm_password:
                    st.error("Fill in all fields")
                else:
                    df_users = load_users()
                    user = df_users[df_users["name"] == user_name]
                    if user.empty:
                        st.error("User not found")
                    else:
                        stored_hash = user.iloc[0]["password"]  # Get user's old password hash
                        if not verify_password(current_password, stored_hash): # Check old password
                            st.error("❌ Current password incorrect")
                        else:
                            # Validate new password
                            is_valid, error_msg = is_valid_pwd(new_password)
                            if not is_valid:
                                st.error(error_msg)
                            elif new_password != confirm_password:
                                st.error("❌ Passwords do not match")
                            else:
                                # Update new password
                                new_hash = hash_password(new_password)
                                df_users.loc[df_users["name"] == user_name, "password"] = new_hash
                                save_users(df_users)
                                st.success("✅ Password changed successfully!")
        
        with tab2:
            st.subheader("🗑️ Delete Account")
            st.warning("⚠️ **WARNING**: This action is irreversible. All your data will be permanently deleted.")
            
            confirm_name = st.text_input("Type your username to confirm", key="delete_confirm_name") # Username confirmation
            delete_password = st.text_input("Enter your password to confirm", type="password", key="delete_pwd") # Password
            
            if st.button("🗑️ Delete Account Permanently", type="primary"):
                # Both fields must be filled
                if not confirm_name or not delete_password:
                    st.error("Fill in all fields")
                elif confirm_name != user_name:
                    # Username must match current user's
                    st.error("❌ Username does not match")
                else:
                    df_users = load_users()
                    user = df_users[df_users["name"] == user_name]
                    if user.empty:
                        st.error("User not found")
                    else:
                        stored_hash = user.iloc[0]["password"]  # Get user's password hash
                        if not verify_password(delete_password, stored_hash): # Check password
                            st.error("❌ Password incorrect")
                        else:
                            # Actually remove user from DataFrame
                            df_users = df_users[df_users["name"] != user_name]
                            save_users(df_users)
                            # Remove user from session (logout)
                            del st.session_state["user"]
                            st.success("✅ Account deleted successfully")
                            st.info("Reload the page to return to the login screen")
                            st.rerun()
        
        with tab3:
            st.subheader("ℹ️ Account Information")
            df_users = load_users()
            user = df_users[df_users["name"] == user_name].iloc[0] # Get current user row as Series
            # Display some account info fields
            st.write(f"**Username:** {user_name}")
            st.write(f"**Last update date:** {user.get('last_update', 'N/A')}")
            st.write(f"**Level:** {user.get('level', 1)}")
            st.write(f"**XP:** {user.get('xp', 0)}")
            st.write(f"**Badge:** {user.get('badge', 'N/A')}")
    
    else:
        # Show login/registration radio choice section
        choice = st.radio("Do you want to log in or create a new profile?", ["Log in", "Register"])
        
        if choice == "Log in":
            st.subheader("🔐 Log in to your profile")
            name = st.text_input("Username")   # Username input
            password = st.text_input("Password", type="password") # Password input
            
            if st.button("Enter"):
                # Must provide both fields
                if not name or not password:
                    st.error("Enter username and password")
                else:
                    df_users = load_users()
                    user = df_users[df_users["name"] == name.strip()]  # Try to find user
                    if user.empty:
                        st.error("❌ Username or password incorrect")
                    else:
                        stored_hash = user.iloc[0]["password"]    # Get user's password hash
                        if verify_password(password, stored_hash): # Check password
                            st.session_state["user"] = name.strip() # Store user in session state
                            st.success(f"✅ Welcome back, {name.strip()}!")
                            st.rerun()
                        else:
                            st.error("❌ Username or password incorrect")
        
        else:
            st.subheader("📝 Create new profile")
            name = st.text_input("Enter your name")                                             # Name input
            password = st.text_input("Password", type="password", help="Minimum 6 characters")  # Password input
            confirm_password = st.text_input("Confirm password", type="password")               # Confirm password
            if st.button("Create profile"):
                # All fields must be filled
                if not name or not password or not confirm_password:
                    st.error("Fill in all fields")
                else:
                    df_users = load_users()                    # Load all users
                    names = df_users["name"].tolist()          # List of all existing names
                    
                    is_valid, error_msg = is_valid_username(name) # Validate user name
                    if not is_valid:
                        st.error(error_msg)
                    elif name.strip() in names:
                        # No duplicate usernames allowed
                        st.warning("This name already exists.")
                    else:
                        is_valid_pwd_result, error_msg_pwd = is_valid_pwd(password) # Validate pwd
                        if not is_valid_pwd_result:
                            st.error(error_msg_pwd)
                        elif password != confirm_password:
                            # Must confirm password
                            st.error("❌ Passwords do not match")
                        else:
                            # Create new user data using defaults
                            new_user_data = DEFAULT_USER_VALUES.copy()
                            new_user_data["name"] = name.strip()
                            new_user_data["password"] = hash_password(password)
                            new_user_data["last_update"] = get_current_date()
                            # Create DataFrame for new user and persist
                            new_user = pd.DataFrame([new_user_data])
                            df_users = pd.concat([df_users, new_user], ignore_index=True)
                            save_users(df_users)
                            # Log the new user in and reload
                            st.session_state["user"] = name.strip()
                            st.success(f"🎉 Welcome, {name.strip()}!")
                            st.rerun()
