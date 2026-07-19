import streamlit as st
from database import init_db, get_connection
from datetime import date
from streak_logic import update_streak_on_completion, get_streak
from ai_planner import generate_task_breakdown

st.set_page_config(page_title="Deadline Tracker", page_icon="🎯", layout="wide")
init_db()
conn = get_connection()
profile = conn.execute("SELECT onboarded FROM user_profile WHERE id=1").fetchone()
conn.close()

if profile[0] == 0:
    st.title("👋 Welcome! Let's set things up.")
    st.caption("This only takes a few seconds and helps personalize your experience.")

    with st.form("onboarding_form"):
        profession = st.selectbox(
            "What best describes you?",
            ["Student", "Working Professional", "Competitive Exam Aspirant", "Other"]
        )
        target_exam = st.text_input(
            "What are you preparing for? (e.g. GATE, project deadline, interview)"
        )
        hours_per_day = st.slider(
            "How many hours per day can you realistically dedicate?",
            min_value=0.5, max_value=12.0, value=2.0, step=0.5
        )
        submitted = st.form_submit_button("Get Started")

        if submitted:
            conn = get_connection()
            conn.execute(
                "UPDATE user_profile SET profession=?, target_exam=?, hours_per_day=?, onboarded=1 WHERE id=1",
                (profession, target_exam, hours_per_day)
            )
            conn.commit()
            conn.close()
            st.success("You're all set!")
            st.rerun()

    st.stop()

st.sidebar.title("🎯 Deadline Tracker")
page = st.sidebar.radio("Navigate", ["Today", "Goals", "Add New", "Profile"])
st.sidebar.divider()
st.sidebar.caption("Stay consistent. One task at a time.")

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
        st.success("🎉 Nothing due today — you're all caught up!")
        st.caption("Add a new task anytime from the 'Add New' tab.")

    for task_id, title, deadline in tasks:
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.checkbox(f"{title} (due {deadline})", key=f"task_{task_id}"):
                conn.execute(
                    "UPDATE tasks SET status='done', completed_at=? WHERE id=?",
                    (date.today(), task_id)
                )
                conn.commit()
                update_streak_on_completion()
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_task_{task_id}"):
                conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
                conn.commit()
                st.rerun()
    conn.close()

elif page == "Goals":
    st.title("Your Goals")
    conn = get_connection()
    goals = conn.execute("SELECT id, title, deadline FROM goals").fetchall()

    if not goals:
        st.info("📌 No goals yet — start by adding one in 'Add New'.")
        st.caption("A goal could be an exam, a project, or anything with a deadline.")

    for goal_id, title, deadline in goals:
        total = conn.execute("SELECT COUNT(*) FROM tasks WHERE goal_id=?", (goal_id,)).fetchone()[0]
        done = conn.execute("SELECT COUNT(*) FROM tasks WHERE goal_id=? AND status='done'", (goal_id,)).fetchone()[0]
        pct = (done / total * 100) if total > 0 else 0

        celebrated_key = f"celebrated_{goal_id}"
        if total > 0 and pct == 100:
            if not st.session_state.get(celebrated_key):
                st.balloons()
                st.session_state[celebrated_key] = True
        else:
            st.session_state[celebrated_key] = False

        col1, col2 = st.columns([5, 1])
        with col1:
            st.subheader(f"{title} (due {deadline})")
            st.progress(pct / 100)
            st.caption(f"{done}/{total} tasks complete")

            if total > 0:
                from datetime import datetime
                goal_created = conn.execute("SELECT created_at FROM goals WHERE id=?", (goal_id,)).fetchone()[0]
                start_date = datetime.strptime(goal_created, "%Y-%m-%d").date()
                end_date = datetime.strptime(str(deadline), "%Y-%m-%d").date() if isinstance(deadline, str) else deadline
                today_date = date.today()

                total_days = (end_date - start_date).days
                elapsed_days = (today_date - start_date).days

                if total_days > 0:
                    expected_pct = min(100, max(0, (elapsed_days / total_days) * 100))
                else:
                    expected_pct = 100

                diff = pct - expected_pct
                if diff >= 5:
                    status_msg = f"🟢 Ahead of schedule — you're {diff:.0f}% ahead of pace."
                elif diff <= -10:
                    status_msg = f"🔴 Behind schedule — you're {abs(diff):.0f}% behind pace."
                else:
                    status_msg = "🟡 Right on pace — keep it up."

                st.caption(f"Expected progress by today: {expected_pct:.0f}% | {status_msg}")
                with st.expander(f"📋 View all {total} tasks"):
                    goal_tasks = conn.execute(
                        "SELECT title, deadline, status FROM tasks WHERE goal_id=? ORDER BY deadline",
                        (goal_id,)
                    ).fetchall()
                    for t_title, t_deadline, t_status in goal_tasks:
                        icon = "✅" if t_status == "done" else "⬜"
                        st.write(f"{icon} **{t_title}** — due {t_deadline}")
        with col2:
            st.write("")
            if st.button("🗑️ Delete", key=f"delete_goal_{goal_id}"):
                st.session_state[f"confirm_delete_{goal_id}"] = True

        if st.session_state.get(f"confirm_delete_{goal_id}"):
            st.warning(f"Delete '{title}' and all {total} of its tasks? This cannot be undone.")
            confirm_col1, confirm_col2 = st.columns(2)
            with confirm_col1:
                if st.button("Yes, delete it", key=f"confirm_yes_{goal_id}"):
                    conn.execute("DELETE FROM tasks WHERE goal_id=?", (goal_id,))
                    conn.execute("DELETE FROM goals WHERE id=?", (goal_id,))
                    conn.commit()
                    del st.session_state[f"confirm_delete_{goal_id}"]
                    st.rerun()
            with confirm_col2:
                if st.button("Cancel", key=f"confirm_no_{goal_id}"):
                    del st.session_state[f"confirm_delete_{goal_id}"]
                    st.rerun()

        st.divider()
    conn.close()

elif page == "Add New":
    st.title("Add Goal or Task")
    tab1, tab2 = st.tabs(["Add Goal", "Add Task"])

    with tab1:
        with st.form("goal_form"):
            title = st.text_input("Goal title")
            deadline = st.date_input("Deadline")
            use_ai = st.checkbox("🤖 Auto-generate tasks with AI", value=True)
            if st.form_submit_button("Add Goal"):
                conn = get_connection()
                cursor = conn.execute("INSERT INTO goals (title, deadline) VALUES (?, ?)", (title, deadline))
                new_goal_id = cursor.lastrowid
                conn.commit()

                if use_ai:
                    profile = conn.execute(
                        "SELECT profession, hours_per_day FROM user_profile WHERE id=1"
                    ).fetchone()
                    profession, hours_per_day = profile

                    with st.spinner("🤖 Generating your task breakdown..."):
                        tasks = generate_task_breakdown(
                            goal_title=title,
                            goal_deadline=str(deadline),
                            profession=profession or "Student",
                            hours_per_day=hours_per_day or 2
                        )

                    for t in tasks:
                        conn.execute(
                            "INSERT INTO tasks (goal_id, title, deadline) VALUES (?, ?, ?)",
                            (new_goal_id, t["title"], t["deadline"])
                        )
                    conn.commit()
                    st.success(f"Goal added with {len(tasks)} AI-generated tasks!")
                else:
                    st.success("Goal added!")

                conn.close()
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
elif page == "Profile":
    st.title("👤 Your Profile")
    conn = get_connection()
    profile = conn.execute(
        "SELECT profession, target_exam, hours_per_day FROM user_profile WHERE id=1"
    ).fetchone()
    conn.close()

    current_profession, current_exam, current_hours = profile

    st.caption("Update your details anytime — this helps personalize your AI-generated plans.")

    with st.form("edit_profile_form"):
        profession = st.selectbox(
            "What best describes you?",
            ["Student", "Working Professional", "Competitive Exam Aspirant", "Other"],
            index=["Student", "Working Professional", "Competitive Exam Aspirant", "Other"].index(current_profession)
            if current_profession in ["Student", "Working Professional", "Competitive Exam Aspirant", "Other"] else 0
        )
        target_exam = st.text_input("What are you preparing for?", value=current_exam or "")
        hours_per_day = st.slider(
            "Hours per day available", min_value=0.5, max_value=12.0,
            value=float(current_hours) if current_hours else 2.0, step=0.5
        )
        if st.form_submit_button("Save Changes"):
            conn = get_connection()
            conn.execute(
                "UPDATE user_profile SET profession=?, target_exam=?, hours_per_day=? WHERE id=1",
                (profession, target_exam, hours_per_day)
            )
            conn.commit()
            conn.close()
            st.success("Profile updated!")
            st.rerun()