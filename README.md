# 🌱 EcoMentor

**EcoMentor** is a gamified educational platform that helps people become more sustainable, one small step at a time.  
It combines **environmental education**, **daily challenges**, and **artificial intelligence** to create an interactive and motivating experience.

## Goal

EcoMentor turns sustainability into a game.  
Users learn to reduce their environmental impact through **personalized challenges**, **micro-lessons**, and a **progress dashboard**. Its aim is to raise awareness among people about leading an environmentally friendly life, always remembering that:

*“A small step for man, a giant leap for mankind.”* - **Every small sustainable action counts.**


## ⚙️ Main Features (MVP)

| Feature | Description |
|---------|-------------|
|  **User Profile** | Create a profile with username and password (data is stored locally in `users.csv`). |
| **Challenges** | One *daily challenge* and a never-ending series of *extra challenge* are generated based on the user's level. |
| **Educational Chat** | EcoMentor AI answers questions only about green topics (ecology, energy, recycling, climate, etc.) using a free LLM's API. |
| **Personal Dashboard** | Graphs and metrics show level, XP, completed challenges, and CO₂ saved. |
| **Custom Goals** | Users can set a CO₂ reduction goal and track their progress. |
| **Gamification** | XP, levels and badges such as “EcoNovice”, “EcoSupporter”, “Green Hero”, and “EcoMaster”. |

## Project Structure

```yaml
EcoMentor/
│
├── app.py # Main Streamlit app
│
├── data/
│ ├── users.csv # User data
│ └── challenges.csv # Challenge data with impact and difficulty
│
├── modules/
│ ├── utils.py # Data management and helper functions
│ ├── profile.py # Login, registration, profile management
│ ├── challenges.py # Challenge logic and user progress
│ ├── dashboard.py # CO₂ dashboard and statistics
│ ├── home.py # Home page
│ └── chatbot.py # Educational chat with free LLM
│
├── LICENSE
├── README.md
└── requirements.txt

```
## Technologies Used
| Category | Tools                                              |
| -------- | -------------------------------------------------- |
| Frontend | Streamlit                                       |
| Backend  | Python (pandas, json, hashlib)                  |
| Database | Local CSV files                                 |
| AI Chat  | Free LLM API                                    |
| Charts   | Streamlit built-in charts                       |

## License
 MIT License 