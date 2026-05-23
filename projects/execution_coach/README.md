# Execution Coach — Agentic AI Project 1

A multi-agent productivity system that plans your day and evaluates execution.

## Agents Built
- **Goal Intake Agent** — Normalizes raw goals into structured task list
- **Planner Agent** — Generates a time-blocked day plan (top 3 priorities)
- **Evaluator Agent** — End-of-day score, reflection, and improvement tip
- **Memory Layer** — JSON-based session log across morning/evening

## Stack
- Python 3.11
- Streamlit (UI)
- Local placeholder logic (no API dependency)

## How to Run
pip install streamlit
cd projects/execution_coach
streamlit run app.py

## What I Learned
- Multi-agent orchestration basics
- Stateful session design
- User-facing agent loop (morning → evening → history)
