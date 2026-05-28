from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="AI Automation Command Center",
    page_icon="⚙️",
    layout="wide"
)

DATA_PATH = Path("data/automation_use_cases.csv")


@st.cache_data
def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH)
    data["priority_score"] = (
        (data["impact_score"] * 2.0)
        + (data["confidence_score"] * 1.5)
        + (data["estimated_hours_saved_month"] / 6)
        - data["effort_score"]
    ).round(1)
    return data


df = load_data()

st.title("AI Automation Command Center")
st.caption(
    "A practical dashboard for collecting, scoring, and tracking automation ideas across internal teams."
)

with st.sidebar:
    st.header("View options")
    departments = st.multiselect(
        "Department",
        sorted(df["department"].unique()),
        default=sorted(df["department"].unique())
    )

    statuses = st.multiselect(
        "Status",
        sorted(df["status"].unique()),
        default=sorted(df["status"].unique())
    )

filtered = df[df["department"].isin(departments) & df["status"].isin(statuses)]

total_ideas = len(filtered)
ready_for_pilot = filtered[filtered["status"].str.contains("Ready", case=False, na=False)].shape[0]
hours_saved = int(filtered["estimated_hours_saved_month"].sum())
avg_priority = round(filtered["priority_score"].mean(), 1) if total_ideas else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Automation ideas", total_ideas)
kpi2.metric("Ready for pilot", ready_for_pilot)
kpi3.metric("Estimated hours saved / month", hours_saved)
kpi4.metric("Average priority score", avg_priority)

st.divider()

left, right = st.columns([1.25, 1])

with left:
    st.subheader("Roadmap view")
    roadmap = filtered.sort_values("priority_score", ascending=False)
    st.dataframe(
        roadmap[
            [
                "department",
                "process_name",
                "current_pain_point",
                "automation_idea",
                "status",
                "priority_score",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

with right:
    st.subheader("Priority ranking")
    chart_data = filtered.sort_values("priority_score", ascending=True)
    fig = px.bar(
        chart_data,
        x="priority_score",
        y="process_name",
        orientation="h",
        hover_data=[
            "department",
            "primary_user",
            "impact_score",
            "effort_score",
            "confidence_score",
        ],
    )
    fig.update_layout(xaxis_title="Priority score", yaxis_title="")
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
        hover_data=["status", "primary_user"],
    )
    hours_chart.update_layout(
        xaxis_title="",
        yaxis_title="Estimated hours saved per month",
        xaxis_tickangle=-35,
    )
    st.plotly_chart(hours_chart, use_container_width=True)

with chart2:
    st.subheader("Roadmap status")
    status_counts = filtered["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    status_chart = px.pie(status_counts, names="status", values="count")
    st.plotly_chart(status_chart, use_container_width=True)

st.divider()

st.subheader("Idea scoring demo")
st.write(
    "This small form is included to show how a team could submit an automation idea and receive a basic first-pass score."
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
        process = st.text_input("Process name", "Manual weekly report preparation")
        pain_point = st.text_area(
            "Current pain point",
            "Describe the repetitive step, delay, or manual coordination problem.",
        )

    with col2:
        idea = st.text_area(
            "Automation idea",
            "Describe what could be automated or improved.",
        )
        impact = st.slider("Impact", 1, 10, 7)
        effort = st.slider("Effort", 1, 10, 5)
        confidence = st.slider("Confidence", 1, 10, 7)

    submitted = st.form_submit_button("Score idea")

if submitted:
    score = round((impact * 2.0) + (confidence * 1.5) + 5 - effort, 1)
    st.success(f"First-pass priority score: {score}")
    st.write(
        "Suggested next step: confirm data availability, check integration options, and decide whether this is a quick win, pilot, or backlog item."
    )

st.divider()

st.subheader("Project scope")
st.markdown(
    """
This project is intentionally simple. It focuses on the thinking behind internal automation:

- collecting practical use cases from teams
- comparing ideas by value and effort
- keeping a visible roadmap
- connecting automation work with operational reporting
- showing leadership where time and quality improvements may come from
"""
)