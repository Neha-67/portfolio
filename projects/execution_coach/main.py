import json
from agents import goal_intake, planner_agent, evaluator_agent

def save_session(data: dict, filename="session_log.json"):
    """Saves today's session to a file (your memory layer)."""
    try:
        with open(filename, "r") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []

    history.append(data)

    with open(filename, "w") as f:
        json.dump(history, f, indent=2)
    print(f"\n💾 Session saved to {filename}")


def morning_session():
    print("\n" + "="*45)
    print("     🌅 EXECUTION COACH — MORNING MODE")
    print("="*45)

    # Collect goals
    print("\nEnter your goals for today (one per line).")
    print("Press ENTER twice when done:\n")
    goals = []
    while True:
        g = input("  Goal: ").strip()
        if g == "":
            break
        goals.append(g)

    if not goals:
        print("No goals entered. Exiting.")
        return None

    # Collect hours
    hours = float(input("\nHow many hours do you have today? "))

    # Run Agents
    print("\n── Running Goal Intake Agent... ──")
    task_data = goal_intake(goals, hours)
    print(json.dumps(task_data, indent=2))

    print("\n── Running Planner Agent... ──")
    plan = planner_agent(task_data)
    print(plan)

    return {"goals": goals, "hours": hours, "task_data": task_data, "plan": plan}


def evening_session(goals: list[str]):
    print("\n" + "="*45)
    print("     🌙 EXECUTION COACH — EVENING REVIEW")
    print("="*45)

    print("\nWhich goals did you complete? (one per line)")
    print("Press ENTER twice when done:\n")
    completed = []
    while True:
        c = input("  Completed: ").strip()
        if c == "":
            break
        completed.append(c)

    print("\n── Running Evaluator Agent... ──")
    result = evaluator_agent(goals, completed)

    print(f"\n  📊 Score:      {result['score']}")
    print(f"  ✅ Done:       {', '.join(result['completed']) or 'None'}")
    print(f"  ❌ Missed:     {', '.join(result['missed']) or 'None'}")
    print(f"  💬 Reflection: {result['reflection']}")
    print(f"  💡 Tomorrow:   {result['tip_for_tomorrow']}")

    return result


# ── MAIN ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nWelcome to your Execution Coach Agent!")
    mode = input("\nType 'morning' or 'evening': ").strip().lower()

    if mode == "morning":
        session = morning_session()
        if session:
            save_session(session)

    elif mode == "evening":
        # Load today's goals from saved session
        try:
            with open("session_log.json", "r") as f:
                history = json.load(f)
            goals = history[-1]["goals"]
            print(f"\nLoaded today's goals: {goals}")
        except (FileNotFoundError, IndexError, KeyError):
            print("No morning session found. Enter goals manually:")
            goals = []
            while True:
                g = input("  Goal: ").strip()
                if g == "": break
                goals.append(g)

        result = evening_session(goals)
        save_session({"evening_review": result})

    else:
        print("Invalid option. Run again and type 'morning' or 'evening'.")