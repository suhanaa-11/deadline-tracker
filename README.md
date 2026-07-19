Deadline Tracker

Deadline Tracker is an app designed to make it easier for students and professionals to stay on top of their goals. Whether you're preparing for exams, managing big projects, or building better habits, this tool helps you break down complex objectives into daily, manageable steps. It keeps you motivated with visible progress, streak tracking, and plans to add smart AI-powered features that adapt to your pace.

💡 Why this project?

Most task apps are either too basic, offering just a simple to-do list, or too overwhelming, with endless options but little real guidance. Deadline Tracker is built to solve a specific problem: turning big, intimidating goals—like passing a tough exam or finishing a major project—into small, doable daily tasks. The app keeps you engaged by showing your progress and helping you build momentum through streaks.

✅ Current Features (MVP)

* Goal tracking — create long-term goals with deadlines
* Task management — add tasks under a goal, each with its own deadline
* Today view — see only what’s due today, distraction-free
* Streak tracking — daily completion streaks to build consistency, with longest-streak history
* Progress visualization — per-goal completion percentage via progress bars
* Persistent storage — SQLite database, so data survives across sessions

🛠️ Tech Stack

* Frontend & backend: Streamlit (Python-based UI, no HTML/CSS/JS required)
* Database: SQLite (lightweight, file-based, zero setup)
* Language: Python 3

## 🚀 Getting Started

```bash
git clone https://github.com/suhanaa-11/deadline-tracker.git
cd deadline-tracker

python -m venv venv
venv\Scripts\activate
source venv/bin/activate

pip install -r requirements.txt

streamlit run app.py
```

## 📁 Project Structure

```
deadline-tracker/
├── app.py              # Main Streamlit app (UI + page routing)
├── database.py         # SQLite schema and connection handling
├── streak_logic.py     # Streak calculation logic
├── requirements.txt     # Python dependencies
├── data/
│   └── tracker.db       # SQLite database (auto-created, gitignored)
└── .gitignore
```

## 🗺️ Roadmap

```
[ ] AI-powered goal decomposition — enter a big goal (e.g. “prepare for GATE exam”), AI generates a full task breakdown with yearly/monthly/weekly/daily targets
[ ] Onboarding flow — capture profession, target exam, and available study hours to personalize planning
[ ] Adaptive replanning — automatically adjust future targets when the user falls behind or gets ahead
[ ] Readiness indicator — rule-based progress score (syllabus completion, mock test trend, pace vs. deadline), narrated by AI in plain language — not a false “chance of clearing” prediction
[ ] Contextual motivational messages — AI-generated, based on streak, recent performance, and task type, instead of static strings
[ ] Visual dashboard — pace-vs-target chart, streak heatmap, mock score trend line
[ ] Deployment — live hosted version via Streamlit Community Cloud 
```

📌 Status

This is an active solo learning project, currently at MVP stage. Built to practice full-stack thinking (data modeling, persistence, UI, and eventually AI integration) end-to-end.

