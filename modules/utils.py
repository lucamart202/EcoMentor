import pandas as pd
import os
import json
import hashlib
import secrets

# Base paths for locating data files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))    # Path to project root
DATA_DIR = os.path.join(BASE_DIR, "data")                                 # Path to data directory
USERS_FILE = os.path.join(DATA_DIR, "users.csv")                          # User data file path
CHALLENGES_FILE = os.path.join(DATA_DIR, "challenges.csv")                # Challenges data file path

def hash_password(password: str) -> str:
    # Create salted hash for password (returns "salt:hashed_password")
    salt = secrets.token_hex(16)  # secure random salt (hex)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest() # hash with salt
    return f"{salt}:{password_hash}"  # return salt:hash

def verify_password(password: str, hashed: str) -> bool:
    # Check if plaintext password matches the saved salted hash
    try:
        if not hashed or pd.isna(hashed) or hashed == "": # empty hash or nan
            return False
        salt, stored_hash = hashed.split(':')  # extract salt, hash
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest() # calculate hash
        return password_hash == stored_hash    # compare hashes
    except:
        return False

# Default values for creating a brand new user row
DEFAULT_USER_VALUES = {
    "password": "",
    "last_completions": json.dumps({}),     # Track daily challenge completions
    "badge": "🌱 EcoNovice",                # Initial user title
    "co2_saved": 0,                         # Start with 0 kg CO2 saved
    "co2_goal": 10,                         # Default CO2 goal
    "level": 1,                             # User starting level
    "xp": 0,                                # User starting XP
    "active_challenge_id": "s",             # Default: no active challenge
    "active_challenge_date": "",            # Date of current challenge
    "optional_challenge_id": ""             # Extra challenge
}

def ensure_data_dir():
    # Create data directory if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_users():
    # Load users.csv and ensure required columns; create empty file if missing
    ensure_data_dir()
    if not os.path.exists(USERS_FILE):
        # Create empty DataFrame with correct columns if user file doesn't exist
        df = pd.DataFrame(columns=[
            "name", "password", "last_completions", "badge",
            "co2_saved", "last_update", "co2_goal", "level", "xp",
            "active_challenge_id", "active_challenge_date", "optional_challenge_id",
            "completed_easy", "completed_medium", "completed_hard"
        ])
        df.to_csv(USERS_FILE, index=False)
    else:
        df = pd.read_csv(USERS_FILE)   # Load user data

        # Ensure last_completions column exists and is set to '{}' if missing
        if 'last_completions' not in df.columns:
            df['last_completions'] = df.apply(lambda x: json.dumps({}), axis=1)
        # Fill missing last_update with current date
        df['last_update'] = df['last_update'].fillna(pd.Timestamp.now().date())

        # Ensure co2_saved is numeric before rounding to avoid TypeError
        if 'co2_saved' in df.columns:
            # Convert non-numeric and missing to 0.0 before rounding
            df['co2_saved'] = pd.to_numeric(df['co2_saved'], errors='coerce').fillna(0)
            df['co2_saved'] = df['co2_saved'].round(1)
        else:
            df['co2_saved'] = 0.0

        # Normalize active_challenge_id and optional_challenge_id columns (convert to int or '')
        for col in ['active_challenge_id', 'optional_challenge_id']:
            df[col] = df[col].apply(lambda x: int(x) if pd.notnull(x) and str(x).replace('.0', '').isdigit() else '')
        
        # Default for missing columns (ensures compatibility even with old user csv)
        for col, default in [
            ("co2_goal", 10),
            ("level", 1),
            ("xp", 0),
            ("active_challenge_id", ""),
            ("active_challenge_date", ""),
            ("optional_challenge_id", ""),
            ("password", "")
        ]:
            if col not in df.columns:
                df[col] = default

        # Default values for challenge completion columns if missing
        for col in ["completed_easy", "completed_medium", "completed_hard"]:
            if col not in df.columns:
                df[col] = 0
    
    return df

def save_users(df):
    # Save the users DataFrame to CSV (post-process for types, conversions)
    ensure_data_dir()
    df = df.copy()
    
    # Ensure last_completions column is always valid JSON string
    if 'last_completions' in df.columns:
        df['last_completions'] = df['last_completions'].apply(
            lambda x: json.dumps(json.loads(x) if isinstance(x, str) else x)
        )
    # Ensure co2_saved is rounded to 1 decimal, and of float type
    if 'co2_saved' in df.columns:
        df['co2_saved'] = pd.to_numeric(df['co2_saved'], errors='coerce').fillna(0)
        df['co2_saved'] = df['co2_saved'].round(1)
    # Normalize challenge columns to empty string or int
    for col in ['active_challenge_id', 'optional_challenge_id']:
        df[col] = df[col].apply(lambda x: int(x) if pd.notnull(x) and str(x).replace('.0', '').isdigit() else '')
    # Save to CSV (overwrite)
    df.to_csv(USERS_FILE, index=False)

def get_current_date():
    # Return current date (YYYY-MM-DD as Timestamp)
    return pd.Timestamp.now().date()

def load_challenges():
    # Load the challenges.csv file (create if missing)
    ensure_data_dir()
    if not os.path.exists(CHALLENGES_FILE):
        # Create empty DataFrame with challenge columns if missing
        df = pd.DataFrame(columns=["id", "title", "ecoImpact", "category", "difficulty"])
        df.to_csv(CHALLENGES_FILE, index=False)
    else:
        df = pd.read_csv(CHALLENGES_FILE)
    return df
