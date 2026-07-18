import streamlit as st
from database import init_db, get_connection
from datetime import date
from streak_logic import update_streak_on_completion, get_streak

st.set_page_config(page_title="Deadline Tracker", layout="wide")
init_db()

page = st.sidebar.radio("Navigate", ["Today", "Goals", "Add New"])

if page == "Today":
    st.title("Today's Tasks")
    current, longest = get_streak()
    st.metric("Current Streak 🔥", f"{current} days", help=f"Longest streak: {longest} days")
    conn = get_connection()
    tasks = conn.execute(
        "SELECT id, title, deadline FROM tasks WHERE status='pending' AND deadline <= ?",
        (date.today(),)
    ).fetchall()

    if not tasks:
        st.info("No tasks due today. Add some in 'Add New'!")

    for task_id, title, deadline in tasks:
        if st.checkbox(f"{title} (due {deadline})", key=f"task_{task_id}"):
            conn.execute(
                "UPDATE tasks SET status='done', completed_at=? WHERE id=?",
                (date.today(), task_id)
            )
            conn.commit()
            update_streak_on_completion()
            st.rerun()
    conn.close()

elif page == "Goals":
    st.title("Your Goals")
    conn = get_connection()
    goals = conn.execute("SELECT id, title, deadline FROM goals").fetchall()

    if not goals:
        st.info("No goals yet. Add one in 'Add New'!")

    for goal_id, title, deadline in goals:
        total = conn.execute("SELECT COUNT(*) FROM tasks WHERE goal_id=?", (goal_id,)).fetchone()[0]
        done = conn.execute("SELECT COUNT(*) FROM tasks WHERE goal_id=? AND status='done'", (goal_id,)).fetchone()[0]
        pct = (done / total * 100) if total > 0 else 0
        st.subheader(f"{title} (due {deadline})")
        st.progress(pct / 100)
        st.caption(f"{done}/{total} tasks complete")
    conn.close()

elif page == "Add New":
    st.title("Add Goal or Task")
    tab1, tab2 = st.tabs(["Add Goal", "Add Task"])

    with tab1:
        with st.form("goal_form"):
            title = st.text_input("Goal title")
            deadline = st.date_input("Deadline")
            if st.form_submit_button("Add Goal"):
                conn = get_connection()
                conn.execute("INSERT INTO goals (title, deadline) VALUES (?, ?)", (title, deadline))
                conn.commit()
                conn.close()
                st.success("Goal added!")
                st.rerun()

    with tab2:
        conn = get_connection()
        goals = conn.execute("SELECT id, title FROM goals").fetchall()
        conn.close()
        goal_options = {g[1]: g[0] for g in goals}

        with st.form("task_form"):
            task_title = st.text_input("Task title")
            task_deadline = st.date_input("Task deadline")
            goal_choice = st.selectbox(
                "Under which goal?",
                options=list(goal_options.keys()) if goal_options else ["No goals yet"]
            )
            if st.form_submit_button("Add Task"):
                conn = get_connection()
                conn.execute(
                    "INSERT INTO tasks (goal_id, title, deadline) VALUES (?, ?, ?)",
                    (goal_options.get(goal_choice), task_title, task_deadline)
                )
                conn.commit()
                conn.close()
                st.success("Task added!")
                st.rerun()