from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="AI Automation Command Center",
    page_icon="⚙️",
    layout="wide",
)

DATA_PATH = Path("data/automation_use_cases.csv")

REQUIRED_COLUMNS = [
    "department",
    "process_name",
    "current_pain_point",
    "automation_idea",
    "workflow_stage",
    "primary_user",
    "impact_score",
    "effort_score",
    "confidence_score",
    "estimated_hours_saved_month",
    "status",
]


@st.cache_data
def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH)

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    numeric_columns = [
        "impact_score",
        "effort_score",
        "confidence_score",
        "estimated_hours_saved_month",
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)

    data["priority_score"] = (
        (data["impact_score"] * 2.0)
        + (data["confidence_score"] * 1.5)
        + (data["estimated_hours_saved_month"] / 6)
        - data["effort_score"]
    ).round(1)

    return data


def create_roadmap_view(data: pd.DataFrame) -> pd.DataFrame:
    return data[
        [
            "department",
            "process_name",
            "current_pain_point",
            "automation_idea",
            "workflow_stage",
            "primary_user",
            "status",
            "priority_score",
            "estimated_hours_saved_month",
        ]
    ].rename(
        columns={
            "department": "Department",
            "process_name": "Process",
            "current_pain_point": "Current Pain Point",
            "automation_idea": "Automation Idea",
            "workflow_stage": "Workflow Stage",
            "primary_user": "Primary User",
            "status": "Status",
            "priority_score": "Priority Score",
            "estimated_hours_saved_month": "Estimated Hours Saved / Month",
        }
    )


def classify_score(score: float) -> str:
    if score >= 27:
        return "Strong pilot candidate"
    if score >= 22:
        return "Good discovery candidate"
    if score >= 17:
        return "Needs more validation"
    return "Backlog candidate"


try:
    df = load_data()
except FileNotFoundError:
    st.error("Data file not found. Please check that data/automation_use_cases.csv exists.")
    st.stop()
except ValueError as error:
    st.error(str(error))
    st.stop()


st.title("AI Automation Command Center")
st.caption(
    "An operations decision-support dashboard for prioritizing AI and workflow automation opportunities across business teams."
)

with st.sidebar:
    st.header("View options")

    departments = st.multiselect(
        "Department",
        sorted(df["department"].unique()),
        default=sorted(df["department"].unique()),
    )

    statuses = st.multiselect(
        "Status",
        sorted(df["status"].unique()),
        default=sorted(df["status"].unique()),
    )

filtered = df[df["department"].isin(departments) & df["status"].isin(statuses)]

if filtered.empty:
    st.warning(
        "No automation ideas match the selected filters. Please adjust the department or status selection."
    )
    st.stop()


total_ideas = len(filtered)
ready_for_pilot = filtered[
    filtered["status"].str.contains("Ready", case=False, na=False)
].shape[0]
hours_saved = int(filtered["estimated_hours_saved_month"].sum())
avg_priority = round(filtered["priority_score"].mean(), 1)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Automation ideas", total_ideas)
kpi2.metric("Ready for pilot", ready_for_pilot)
kpi3.metric("Estimated hours saved / month", hours_saved)
kpi4.metric("Average priority score", avg_priority)

top_opportunity = filtered.sort_values("priority_score", ascending=False).iloc[0]
ready_hours = int(
    filtered[
        filtered["status"].str.contains("Ready", case=False, na=False)
    ]["estimated_hours_saved_month"].sum()
)

st.info(
    f"Highest priority opportunity: **{top_opportunity['process_name']}** "
    f"for **{top_opportunity['department']}** with a priority score of "
    f"**{top_opportunity['priority_score']}**. Current ready-for-pilot ideas represent "
    f"an estimated **{ready_hours} hours saved per month**."
)

st.divider()


st.subheader("Automation roadmap")

roadmap = filtered.sort_values("priority_score", ascending=False)
roadmap_display = create_roadmap_view(roadmap)

st.dataframe(
    roadmap_display,
    use_container_width=True,
    hide_index=True,
    height=360,
)

csv_export = roadmap_display.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered roadmap as CSV",
    data=csv_export,
    file_name="automation_roadmap_export.csv",
    mime="text/csv",
)

with st.expander("How priority scoring works"):
    st.markdown(
        """
The priority score is a simple first-pass decision model. It is used to compare automation ideas before deeper discovery.

**Formula**

`priority score = impact × 2 + confidence × 1.5 + estimated monthly hours saved / 6 - effort`

**Inputs**

- **Impact:** expected business or operational value
- **Effort:** estimated implementation difficulty
- **Confidence:** how realistic the idea is based on current process understanding
- **Estimated hours saved:** expected monthly reduction in manual work
"""
    )

st.divider()


st.subheader("Priority ranking")

chart_data = filtered.sort_values("priority_score", ascending=True)

fig = px.bar(
    chart_data,
    x="priority_score",
    y="process_name",
    orientation="h",
    hover_data={
        "department": True,
        "primary_user": True,
        "impact_score": True,
        "effort_score": True,
        "confidence_score": True,
        "priority_score": True,
        "process_name": False,
    },
    labels={
        "priority_score": "Priority Score",
        "process_name": "Process",
        "department": "Department",
        "primary_user": "Primary User",
        "impact_score": "Impact",
        "effort_score": "Effort",
        "confidence_score": "Confidence",
    },
)

fig.update_layout(
    xaxis_title="Priority score",
    yaxis_title="",
    height=430,
    margin=dict(l=20, r=20, t=20, b=40),
)

st.plotly_chart(fig, use_container_width=True)

st.divider()


chart1, chart2 = st.columns(2)

with chart1:
    st.subheader("Potential time saving")

    hours_chart = px.bar(
        filtered.sort_values("estimated_hours_saved_month", ascending=False),
        x="process_name",
        y="estimated_hours_saved_month",
        color="department",
        hover_data={
            "status": True,
            "primary_user": True,
            "process_name": False,
        },
        labels={
            "process_name": "Process",
            "estimated_hours_saved_month": "Estimated Hours Saved / Month",
            "department": "Department",
            "status": "Status",
            "primary_user": "Primary User",
        },
    )

    hours_chart.update_layout(
        xaxis_title="",
        yaxis_title="Estimated hours saved per month",
        xaxis_tickangle=-35,
        height=430,
        margin=dict(l=20, r=20, t=20, b=120),
    )

    st.plotly_chart(hours_chart, use_container_width=True)

with chart2:
    st.subheader("Roadmap status")

    status_counts = filtered["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]

    status_chart = px.pie(
        status_counts,
        names="Status",
        values="Count",
        hole=0.35,
    )

    status_chart.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=20, b=40),
    )

    st.plotly_chart(status_chart, use_container_width=True)

st.divider()


st.subheader("Idea scoring demo")
st.write(
    "This form demonstrates how a team could submit an automation idea and receive a first-pass prioritization score."
)

with st.form("automation_idea_form"):
    col1, col2 = st.columns(2)

    with col1:
        department = st.selectbox(
            "Department",
            [
                "Support Operations",
                "Workforce Operations",
                "People Operations",
                "Finance Operations",
                "Engineering Operations",
                "Leadership",
            ],
        )

        process = st.text_input(
            "Process name",
            "Weekly SLA report preparation",
        )

        pain_point = st.text_area(
            "Current pain point",
            "Team leads manually prepare SLA updates every week, which takes time and creates inconsistent reporting.",
        )

    with col2:
        idea = st.text_area(
            "Automation idea",
            "Automatically calculate SLA status, highlight risky queues, and generate a weekly summary for leadership.",
        )

        impact = st.slider("Impact", 1, 10, 7)
        effort = st.slider("Effort", 1, 10, 5)
        confidence = st.slider("Confidence", 1, 10, 7)

    submitted = st.form_submit_button("Score idea")

if submitted:
    score = round((impact * 2.0) + (confidence * 1.5) + 5 - effort, 1)
    classification = classify_score(score)

    st.success(f"First-pass priority score: {score} — {classification}")

    result_summary = pd.DataFrame(
        [
            {
                "Department": department,
                "Process": process,
                "Impact": impact,
                "Effort": effort,
                "Confidence": confidence,
                "Priority Score": score,
                "Recommendation": classification,
            }
        ]
    )

    st.dataframe(
        result_summary,
        use_container_width=True,
        hide_index=True,
    )

    st.write(
        "Suggested next step: confirm data availability, check integration options, validate the process owner, and decide whether this should move into discovery, pilot, or backlog."
    )

st.divider()


st.subheader("Project scope and assumptions")
st.markdown(
    """
This project focuses on the operating model behind internal automation rather than only the technical implementation.

It demonstrates how teams can:

- collect practical automation ideas from different business functions
- compare opportunities using consistent scoring logic
- maintain a visible automation roadmap
- connect automation work with operational reporting
- show leadership where time, speed, and quality improvements may come from
- prepare future integration with workflow tools such as n8n or internal approval systems

The data used in this project is fictional sample data created for public portfolio use.
"""
)