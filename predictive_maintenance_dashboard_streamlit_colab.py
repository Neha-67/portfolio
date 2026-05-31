"""
Predictive Maintenance BI Dashboard (Power BI / Tableau style) - Google Colab + Streamlit

How to run in Google Colab:
1) !pip install -q streamlit plotly openpyxl pyngrok
2) Save this script, then run:
   !streamlit run predictive_maintenance_dashboard_streamlit_colab.py &>/content/streamlit.log &
3) Expose with ngrok:
   from pyngrok import ngrok
   public_url = ngrok.connect(8501)
   print(public_url)
4) Open the printed URL.

Dataset expected:
    /content/cleaned_predictive_maintenance.xlsx
"""

import os
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st


# =========================
# App Configuration + Theme
# =========================
st.set_page_config(
    page_title="Predictive Maintenance BI Dashboard",
    page_icon="📊",
    layout="wide",
)

PRIMARY = "#0B3C6D"      # Dark Blue
SECONDARY = "#5DADE2"    # Light Blue
GREEN = "#27AE60"
ORANGE = "#F39C12"
RED = "#E74C3C"
BG_LIGHT = "#F5F7FA"
CARD_BG = "#FFFFFF"

st.markdown(
    f"""
    <style>
      .stApp {{background-color: {BG_LIGHT};}}
      .kpi-card {{
          background: {CARD_BG};
          border-radius: 14px;
          padding: 16px 18px;
          box-shadow: 0 2px 10px rgba(11,60,109,0.1);
          border-left: 6px solid {PRIMARY};
      }}
      .kpi-title {{font-size: 0.9rem; color: #5b6770; margin-bottom: 4px;}}
      .kpi-value {{font-size: 1.8rem; font-weight: 700; color: {PRIMARY};}}
      .block-title {{font-size: 1.15rem; font-weight: 700; color: {PRIMARY}; margin-top: 10px;}}
      .section-gap {{margin-top: 8px; margin-bottom: 8px;}}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Predictive Maintenance Executive Dashboard")
st.caption("Power BI / Tableau-style interactive dashboard for operational monitoring and decision support")


# =========================
# Step 2 — Load Data
# =========================
DATA_PATH = "/content/cleaned_predictive_maintenance.xlsx"

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df_ = pd.read_excel(path)
    if "datetime" in df_.columns:
        df_["datetime"] = pd.to_datetime(df_["datetime"], errors="coerce")
    return df_

if not os.path.exists(DATA_PATH):
    st.error(f"Dataset not found at: {DATA_PATH}")
    st.info("Please upload/copy the Excel file to /content in Colab, then rerun.")
    st.stop()

df = load_data(DATA_PATH)


# =========================
# Step 3 — Calculated Fields
# =========================
if "health_score" not in df.columns:
    st.error("Column 'health_score' is required for this dashboard.")
    st.stop()

if "machineID" not in df.columns:
    st.error("Column 'machineID' is required for this dashboard.")
    st.stop()

if "has_failure" not in df.columns:
    st.error("Column 'has_failure' is required for this dashboard.")
    st.stop()

# Normalize event flags
for flag_col in ["has_failure", "has_maint", "has_error"]:
    if flag_col in df.columns:
        df[flag_col] = pd.to_numeric(df[flag_col], errors="coerce").fillna(0).astype(int)

# Derived / Calculated columns
if "risk_level" not in df.columns:
    if "failure_probability" in df.columns:
        df["risk_level"] = np.select(
            [df["failure_probability"] < 0.4, df["failure_probability"].between(0.4, 0.7, inclusive="both")],
            ["Low", "Medium"],
            default="High",
        )
    else:
        q1 = df["health_score"].quantile(0.33)
        q2 = df["health_score"].quantile(0.66)
        df["risk_level"] = np.select(
            [df["health_score"] <= q1, df["health_score"] <= q2],
            ["High", "Medium"],
            default="Low",
        )

# Machine Status
status_conditions = [
    df["health_score"] > 70,
    (df["health_score"] >= 40) & (df["health_score"] <= 70),
    df["health_score"] < 40,
]
status_choices = ["Healthy", "Warning", "Critical"]
df["machine_status"] = np.select(status_conditions, status_choices, default="Warning")

# Age Group
if "age" in df.columns:
    df["age_group"] = np.select(
        [df["age"] < 5, df["age"].between(5, 10, inclusive="both"), df["age"] > 10],
        ["Young", "Mid", "Old"],
        default="Unknown",
    )
else:
    df["age_group"] = "Unknown"

# month for trends
if "datetime" in df.columns:
    df["month_period"] = df["datetime"].dt.to_period("M").dt.to_timestamp()


# =========================
# Step 5 — Global Filters
# =========================
st.sidebar.header("🔎 Filters")

# Date filter
if "datetime" in df.columns and df["datetime"].notna().any():
    min_date = df["datetime"].min().date()
    max_date = df["datetime"].max().date()
    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date
else:
    start_date, end_date = None, None

# Model filter
models = sorted(df["model"].dropna().astype(str).unique().tolist()) if "model" in df.columns else []
selected_models = st.sidebar.multiselect("Machine model", options=models, default=models)

# Risk filter
risk_levels = sorted(df["risk_level"].dropna().astype(str).unique().tolist())
selected_risk = st.sidebar.multiselect("Risk level", options=risk_levels, default=risk_levels)

# Age group filter
age_groups = sorted(df["age_group"].dropna().astype(str).unique().tolist())
selected_age_groups = st.sidebar.multiselect("Age group", options=age_groups, default=age_groups)

# Filter application
filtered = df.copy()
if start_date is not None and end_date is not None and "datetime" in filtered.columns:
    filtered = filtered[
        (filtered["datetime"].dt.date >= start_date) & (filtered["datetime"].dt.date <= end_date)
    ]

if selected_models and "model" in filtered.columns:
    filtered = filtered[filtered["model"].astype(str).isin(selected_models)]

if selected_risk:
    filtered = filtered[filtered["risk_level"].astype(str).isin(selected_risk)]

if selected_age_groups:
    filtered = filtered[filtered["age_group"].astype(str).isin(selected_age_groups)]

if filtered.empty:
    st.warning("No records match current filters. Adjust filter selections.")
    st.stop()


# =========================
# Measures (DAX-like KPIs)
# =========================
total_machines = int(filtered["machineID"].nunique())
total_failures = int(filtered["has_failure"].sum())
total_records = len(filtered)
failure_rate = (total_failures / total_records) if total_records > 0 else 0
avg_health = float(filtered["health_score"].mean())
high_risk_machines = int(filtered.loc[filtered["risk_level"] == "High", "machineID"].nunique())
maintenance_events = int(filtered["has_maint"].sum()) if "has_maint" in filtered.columns else 0
error_events = int(filtered["has_error"].sum()) if "has_error" in filtered.columns else 0
failure_probability_avg = float(filtered["failure_probability"].mean()) if "failure_probability" in filtered.columns else np.nan


# =========================
# Section 1 — KPI Cards
# =========================
st.markdown("<div class='block-title'>Section 1 — KPI Overview</div>", unsafe_allow_html=True)

kpi_cols = st.columns(6)
kpi_payload = [
    ("🛠️ Total Machines", f"{total_machines:,}", PRIMARY),
    ("❌ Total Failures", f"{total_failures:,}", RED),
    ("📉 Failure Rate", f"{failure_rate:.2%}", ORANGE),
    ("💚 Avg Health Score", f"{avg_health:.2f}", GREEN),
    ("⚠️ High Risk Machines", f"{high_risk_machines:,}", RED),
    ("🔧 Maintenance Events", f"{maintenance_events:,}", SECONDARY),
]

for c, (title, value, border_color) in zip(kpi_cols, kpi_payload):
    c.markdown(
        f"""
        <div class='kpi-card' style='border-left: 6px solid {border_color};'>
            <div class='kpi-title'>{title}</div>
            <div class='kpi-value'>{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.caption(
    f"Error Events: {error_events:,}"
    + (f" | Avg Failure Probability: {failure_probability_avg:.3f}" if not np.isnan(failure_probability_avg) else "")
)


# =========================
# Chart builders
# =========================
def style_fig(fig, title):
    fig.update_layout(
        title=title,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#1f2933"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=30, r=30, t=60, b=30),
    )
    return fig


# =========================
# Section 2 — Failure & Risk
# =========================
st.markdown("<div class='block-title'>Section 2 — Failure & Risk Analysis</div>", unsafe_allow_html=True)
col21, col22, col23 = st.columns(3)

# 1) Failure trend over time
if "month_period" in filtered.columns:
    trend = filtered.groupby("month_period", as_index=False)["has_failure"].sum().rename(columns={"has_failure": "failures"})
    fig1 = px.line(
        trend,
        x="month_period",
        y="failures",
        markers=True,
        color_discrete_sequence=[PRIMARY],
        hover_data={"failures": True},
    )
    fig1 = style_fig(fig1, "Failure Trend Over Time")
else:
    fig1 = go.Figure()
    fig1.add_annotation(text="datetime not available", showarrow=False)

# 2) Risk level distribution (donut)
risk_dist = filtered["risk_level"].value_counts().reset_index()
risk_dist.columns = ["risk_level", "count"]
fig2 = px.pie(
    risk_dist,
    values="count",
    names="risk_level",
    hole=0.55,
    color="risk_level",
    color_discrete_map={"Low": GREEN, "Medium": ORANGE, "High": RED},
)
fig2 = style_fig(fig2, "Risk Level Distribution")

# 3) Machine status distribution
status_dist = filtered["machine_status"].value_counts().reset_index()
status_dist.columns = ["machine_status", "count"]
fig3 = px.bar(
    status_dist,
    x="machine_status",
    y="count",
    color="machine_status",
    color_discrete_map={"Healthy": GREEN, "Warning": ORANGE, "Critical": RED},
)
fig3 = style_fig(fig3, "Machine Status Distribution")

col21.plotly_chart(fig1, use_container_width=True)
col22.plotly_chart(fig2, use_container_width=True)
col23.plotly_chart(fig3, use_container_width=True)


# =========================
# Section 3 — Sensor Insights
# =========================
st.markdown("<div class='block-title'>Section 3 — Sensor Insights</div>", unsafe_allow_html=True)
col31, col32, col33 = st.columns(3)

fig4 = px.box(
    filtered,
    x="has_failure",
    y="vibration" if "vibration" in filtered.columns else "health_score",
    color="has_failure",
    color_discrete_sequence=[SECONDARY, RED],
    labels={"has_failure": "Failure (0/1)"},
)
fig4 = style_fig(fig4, "Vibration vs Failure")

fig5 = px.box(
    filtered,
    x="has_failure",
    y="pressure" if "pressure" in filtered.columns else "health_score",
    color="has_failure",
    color_discrete_sequence=[SECONDARY, RED],
    labels={"has_failure": "Failure (0/1)"},
)
fig5 = style_fig(fig5, "Pressure vs Failure")

fig6 = px.histogram(
    filtered,
    x="health_score",
    nbins=30,
    color_discrete_sequence=[PRIMARY],
)
fig6 = style_fig(fig6, "Health Score Distribution")

col31.plotly_chart(fig4, use_container_width=True)
col32.plotly_chart(fig5, use_container_width=True)
col33.plotly_chart(fig6, use_container_width=True)


# =========================
# Section 4 — Machine Analytics
# =========================
st.markdown("<div class='block-title'>Section 4 — Machine Analytics</div>", unsafe_allow_html=True)
col41, col42, col43 = st.columns(3)

# 7) Failures by model
if "model" in filtered.columns:
    fail_model = filtered.groupby("model", as_index=False)["has_failure"].sum().sort_values("has_failure", ascending=False)
    fig7 = px.bar(fail_model, x="model", y="has_failure", color="model", color_discrete_sequence=px.colors.sequential.Blues)
    fig7 = style_fig(fig7, "Failures by Machine Model")
else:
    fig7 = go.Figure()

# 8) Failures by age group
fail_age = filtered.groupby("age_group", as_index=False)["has_failure"].sum().sort_values("has_failure", ascending=False)
fig8 = px.bar(
    fail_age,
    x="age_group",
    y="has_failure",
    color="age_group",
    color_discrete_map={"Young": SECONDARY, "Mid": ORANGE, "Old": RED, "Unknown": PRIMARY},
)
fig8 = style_fig(fig8, "Failures by Age Group")

# 9) Top 10 high-risk machines
risk_top = (
    filtered.groupby("machineID", as_index=False)["failure_probability"].max().sort_values("failure_probability", ascending=False).head(10)
    if "failure_probability" in filtered.columns
    else filtered.groupby("machineID", as_index=False)["health_score"].mean().sort_values("health_score", ascending=True).head(10)
)

if "failure_probability" in risk_top.columns:
    fig9 = px.bar(
        risk_top.sort_values("failure_probability", ascending=True),
        x="failure_probability",
        y="machineID",
        orientation="h",
        color="failure_probability",
        color_continuous_scale="Reds",
    )
else:
    fig9 = px.bar(
        risk_top.sort_values("health_score", ascending=False),
        x="health_score",
        y="machineID",
        orientation="h",
        color="health_score",
        color_continuous_scale="Oranges",
    )
fig9 = style_fig(fig9, "Top 10 High-Risk Machines")

col41.plotly_chart(fig7, use_container_width=True)
col42.plotly_chart(fig8, use_container_width=True)
col43.plotly_chart(fig9, use_container_width=True)


# =========================
# Section 5 — Correlation
# =========================
st.markdown("<div class='block-title'>Section 5 — Correlation & Drivers</div>", unsafe_allow_html=True)

corr_cols = [c for c in ["volt", "rotate", "pressure", "vibration", "age", "health_score", "has_error", "has_maint", "has_failure", "failure_probability"] if c in filtered.columns]
if len(corr_cols) >= 2:
    corr_df = filtered[corr_cols].corr(numeric_only=True)
    fig10 = px.imshow(
        corr_df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
    )
    fig10 = style_fig(fig10, "Correlation Heatmap")
    st.plotly_chart(fig10, use_container_width=True)
else:
    st.info("Not enough numeric columns available for correlation heatmap.")


# =========================
# Section 6 — Operational Table
# =========================
st.markdown("<div class='block-title'>Section 6 — Operational Monitoring Table</div>", unsafe_allow_html=True)

table_cols = [
    c for c in ["machineID", "model", "health_score", "risk_level", "has_failure", "failure_probability", "machine_status", "age_group"]
    if c in filtered.columns
]

st.dataframe(
    filtered[table_cols].sort_values("health_score", ascending=True),
    use_container_width=True,
    height=400,
)


# =========================
# Step 8 — Export options
# =========================
st.markdown("<div class='block-title'>Export & Usage Instructions</div>", unsafe_allow_html=True)
st.markdown(
    """
- **Run in Colab**: install dependencies, run Streamlit app, expose with `pyngrok`.
- **Export screenshots**: use browser screenshot tools (or OS capture) once dashboard URL is open.
- **Save as HTML**: use the button below to export key visuals into a single HTML file.
"""
)

if st.button("💾 Save dashboard visuals as HTML"):
    export_figures = [fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9]
    if "fig10" in locals():
        export_figures.append(fig10)

    html_parts = [
        "<html><head><title>Predictive Maintenance Dashboard Export</title></head><body>",
        f"<h1>Predictive Maintenance Dashboard Export</h1><p>Generated: {datetime.now()}</p>",
    ]
    for i, fig in enumerate(export_figures, start=1):
        html_parts.append(f"<h2>Chart {i}</h2>")
        html_parts.append(pio.to_html(fig, include_plotlyjs='cdn', full_html=False))
    html_parts.append("</body></html>")

    out_path = "/content/predictive_maintenance_dashboard_export.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))

    st.success(f"Saved HTML export to: {out_path}")

st.caption("Dashboard theme: Dark Blue + Light Blue with Green/Orange/Red risk accents. Designed for executive-ready BI storytelling.")
