from datetime import date, timedelta
from database import get_connection

def update_streak_on_completion():
    """Call this every time a task is marked done."""
    conn = get_connection()
    today = date.today()

    row = conn.execute(
        "SELECT current_streak, longest_streak, last_completed_date FROM streak WHERE id=1"
    ).fetchone()
    current_streak, longest_streak, last_completed_date = row

    if last_completed_date is not None:
        last_date = date.fromisoformat(last_completed_date)
    else:
        last_date = None

    if last_date == today:
        # Already logged a completion today, streak doesn't change
        pass
    elif last_date == today - timedelta(days=1):
        # Completed yesterday too -> streak continues
        current_streak += 1
    else:
        # Missed a day (or first ever completion) -> streak resets to 1
        current_streak = 1

    longest_streak = max(longest_streak, current_streak)

    conn.execute(
        "UPDATE streak SET current_streak=?, longest_streak=?, last_completed_date=? WHERE id=1",
        (current_streak, longest_streak, today.isoformat())
    )
    conn.commit()
    conn.close()

def get_streak():
    conn = get_connection()
    row = conn.execute(
        "SELECT current_streak, longest_streak FROM streak WHERE id=1"
    ).fetchone()
    conn.close()
    return row  # (current_streak, longest_streak)