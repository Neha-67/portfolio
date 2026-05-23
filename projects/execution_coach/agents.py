import json
import random
from datetime import datetime

# ── AGENT 1: Goal Intake ──────────────────────────────────────────
def goal_intake(goals: list[str], hours: float) -> dict:
    """
    Takes raw goals + available hours.
    Returns structured task list with priorities and time estimates.
    """
    total_tasks = len(goals)
    time_per_task = round(hours / total_tasks, 1) if total_tasks > 0 else 1.0

    normalized = []
    for i, goal in enumerate(goals):
        normalized.append({
            "task": goal.strip(),
            "priority": i + 1,
            "estimated_hours": time_per_task,
            "status": "pending"
        })

    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_hours_available": hours,
        "normalized_tasks": normalized
    }


# ── AGENT 2: Planner ─────────────────────────────────────────────
def planner_agent(task_data: dict) -> str:
    """
    Takes structured task list.
    Returns a human-readable day plan with time blocks.
    """
    tasks = task_data["normalized_tasks"]
    top_3 = tasks[:3]  # Focus on top 3 only

    start_hour = 9  # Assume 9 AM start
    plan_lines = [f"📅 DAY PLAN — {task_data['date']}\n"]

    for task in top_3:
        end_hour = start_hour + task["estimated_hours"]
        plan_lines.append(
            f"  ⏰ {start_hour:.0f}:00 → {end_hour:.0f}:00 | "
            f"[Priority {task['priority']}] {task['task']}"
        )
        start_hour = end_hour

    plan_lines.append(f"\n  ✅ Focus on these 3. Remaining tasks are stretch goals.")
    return "\n".join(plan_lines)


# ── AGENT 3: Evaluator ────────────────────────────────────────────
def evaluator_agent(goals: list[str], completed: list[str]) -> dict:
    """
    Compares planned goals vs completed tasks.
    Returns score, reflection, and improvement tip.
    """
    total = len(goals)
    done = len(completed)
    score = round((done / total) * 10, 1) if total > 0 else 0

    tips = [
        "Break tasks into 25-min focused blocks tomorrow.",
        "Identify your top 1 blocker and remove it first.",
        "Start with the hardest task when energy is highest.",
        "Time-box each task strictly — set a timer.",
        "Reduce the goal count. 3 is better than 10."
    ]

    missed = [g for g in goals if g not in completed]

    return {
        "score": f"{score}/10",
        "completed": completed,
        "missed": missed,
        "reflection": f"You finished {done}/{total} tasks today.",
        "blocker": "Unknown — add tracking tomorrow to find patterns.",
        "tip_for_tomorrow": random.choice(tips)
    }