from ai_planner import generate_task_breakdown

tasks = generate_task_breakdown(
    goal_title="Prepare for GATE AI/DS exam",
    goal_deadline="2027-02-01",
    profession="Student",
    hours_per_day=3
)

print(f"Generated {len(tasks)} tasks:\n")
for t in tasks:
    print(f"- {t['title']} (due {t['deadline']})")