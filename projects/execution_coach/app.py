import streamlit as st
import json
from datetime import datetime
from agents import goal_intake, planner_agent, evaluator_agent

st.set_page_config(page_title="Execution Coach", page_icon="⚡", layout="centered")

st.markdown("""
<style>
  .block-container { padding-top: 2rem; }
  .metric-box { background: #f8f9fa; border-radius: 10px; padding: 1rem; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────
st.markdown("## ⚡ Execution Coach")
st.caption(f"Today: {datetime.now().strftime('%A, %B %d %Y')}")
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────
morning_tab, evening_tab, history_tab = st.tabs(["🌅 Morning", "🌙 Evening", "📋 History"])


# ═══════════════════════════════════════════════════════════════════
# MORNING TAB
# ═══════════════════════════════════════════════════════════════════
with morning_tab:
    st.subheader("Set your goals")

    hours = st.slider("Hours available today", min_value=1.0, max_value=12.0,
                      value=4.0, step=0.5)

    goal1 = st.text_input("Goal 1", placeholder="e.g. Build Streamlit UI")
    goal2 = st.text_input("Goal 2", placeholder="e.g. Study LangGraph docs")
    goal3 = st.text_input("Goal 3", placeholder="e.g. Record demo video")

    goals = [g for g in [goal1, goal2, goal3] if g.strip()]

    if st.button("▶ Run Morning Agents", type="primary"):
        if not goals:
            st.warning("Enter at least one goal.")
        else:
            with st.spinner("Goal Intake Agent running..."):
                task_data = goal_intake(goals, hours)
                if isinstance(task_data, str):
                    task_data = json.loads(task_data)

            st.success("✅ Goal Intake Agent done")

            # Show metrics
            col1, col2 = st.columns(2)
            col1.metric("Total Goals", len(goals))
            col2.metric("Hours Available", f"{hours} h")

            # Show tasks
            st.markdown("#### 📋 Task List")
            for t in task_data["normalized_tasks"]:
                st.markdown(
                    f"**P{t['priority']}** — {t['task']} "
                    f"*(~{t['estimated_hours']} h)*"
                )

            # Planner
            with st.spinner("Planner Agent running..."):
                plan = planner_agent(task_data)

            st.markdown("#### 🗓 Day Plan")
            st.code(plan, language=None)

            # Save to session
            session = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "goals": goals,
                "hours": hours,
                "task_data": task_data,
                "plan": plan
            }
            try:
                with open("session_log.json", "r") as f:
                    history = json.load(f)
            except FileNotFoundError:
                history = []
            history.append(session)
            with open("session_log.json", "w") as f:
                json.dump(history, f, indent=2)

            st.success("💾 Session saved!")


# ═══════════════════════════════════════════════════════════════════
# EVENING TAB
# ═══════════════════════════════════════════════════════════════════
with evening_tab:
    st.subheader("End of day review")

    # Load today's goals
    try:
        with open("session_log.json", "r") as f:
            history = json.load(f)
        today_goals = history[-1].get("goals", [])
        st.info(f"Loaded today's goals: {', '.join(today_goals)}")
    except (FileNotFoundError, IndexError):
        today_goals = []
        st.warning("No morning session found. Add goals below.")

    completed = []
    if today_goals:
        st.markdown("**Mark what you completed:**")
        for g in today_goals:
            if st.checkbox(g, key=f"done_{g}"):
                completed.append(g)
    else:
        manual = st.text_area("Enter completed tasks (one per line)")
        completed = [l.strip() for l in manual.split("\n") if l.strip()]

    if st.button("▶ Run Evaluator Agent", type="primary"):
        if not today_goals and not completed:
            st.warning("No goals or completed tasks found.")
        else:
            with st.spinner("Evaluator Agent running..."):
                result = evaluator_agent(today_goals or completed, completed)

            score_num = float(result["score"].split("/")[0])
            color = "green" if score_num >= 7 else "orange" if score_num >= 4 else "red"

            st.markdown(f"### Score: :{color}[{result['score']}]")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Completed**")
                for c in result["completed"] or ["None"]:
                    st.markdown(f"- {c}")
            with col2:
                st.markdown("**❌ Missed**")
                for m in result["missed"] or ["None"]:
                    st.markdown(f"- {m}")

            st.info(f"💬 {result['reflection']}")
            st.success(f"💡 Tomorrow: {result['tip_for_tomorrow']}")


# ═══════════════════════════════════════════════════════════════════
# HISTORY TAB
# ═══════════════════════════════════════════════════════════════════
with history_tab:
    st.subheader("Past sessions")
    try:
        with open("session_log.json", "r") as f:
            history = json.load(f)
        if not history:
            st.info("No sessions yet.")
        else:
            for i, s in enumerate(reversed(history)):
                date = s.get("date", "Unknown date")
                goals = s.get("goals", [])
                if goals:
                    with st.expander(f"📅 {date} — {len(goals)} goals"):
                        for g in goals:
                            st.markdown(f"- {g}")
                        if "plan" in s:
                            st.code(s["plan"], language=None)
    except FileNotFoundError:
        st.info("No history yet. Run a morning session first.")
