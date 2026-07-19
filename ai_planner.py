import os
import json
from datetime import date
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_task_breakdown(goal_title, goal_deadline, profession, hours_per_day):
    """
    Calls Gemini to break a goal into a list of tasks.
    Returns a list of dicts like: [{"title": "...", "deadline": "YYYY-MM-DD"}, ...]
    """
    model = genai.GenerativeModel("gemini-flash-latest")

    prompt = f"""You are a study/project planning assistant. Break down the following goal into a realistic, actionable list of tasks with suggested deadlines.

Goal: {goal_title}
Goal deadline: {goal_deadline}
Today's date: {date.today()}
User's profession/context: {profession}
Hours available per day: {hours_per_day}

Rules:
- Generate between 6 and 15 tasks, spaced out realistically between today and the goal deadline.
- Each task should be specific and actionable (not vague like "study more").
- Respect the hours per day available — don't overload the schedule.
- Deadlines must be between today and the goal deadline, in YYYY-MM-DD format.
- Order tasks chronologically by deadline.

Respond with ONLY a valid JSON array, no markdown formatting, no explanation, no code fences. Example format:
[{{"title": "Task name here", "deadline": "2026-08-01"}}, {{"title": "Another task", "deadline": "2026-08-05"}}]
"""

    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    # Safety: strip accidental markdown code fences if the model adds them anyway
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:].strip()

    try:
        tasks = json.loads(raw_text)
        return tasks
    except json.JSONDecodeError:
        print("⚠️ Could not parse AI response as JSON. Raw response was:")
        print(raw_text)
        return []