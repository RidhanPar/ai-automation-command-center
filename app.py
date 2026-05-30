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


st.markdown(
    """
    <style>
        .main {
            background-color: #f8fafc;
        }

        .hero-card {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #334155 100%);
            padding: 34px;
            border-radius: 22px;
            margin-bottom: 24px;
            color: white;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.18);
        }

        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 8px;
        }

        .hero-subtitle {
            font-size: 1.05rem;
            color: #cbd5e1;
            max-width: 900px;
            line-height: 1.6;
        }

        .hero-tags {
            margin-top: 18px;
        }

        .tag {
            display: inline-block;
            padding: 7px 12px;
            margin-right: 8px;
            margin-bottom: 8px;
            border-radius: 999px;
            background-color: rgba(255, 255, 255, 0.12);
            color: #e2e8f0;
            font-size: 0.85rem;
            border: 1px solid rgba(255, 255, 255, 0.16);
        }

        .kpi-card {
            background-color: white;
            padding: 22px;
            border-radius: 18px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
        }

        .kpi-label {
            color: #64748b;
            font-size: 0.86rem;
            font-weight: 600;
            margin-bottom: 6px;
        }

        .kpi-value {
            color: #0f172a;
            font-size: 1.8rem;
            font-weight: 800;
        }

        .section-card {
            background-color: white;
            padding: 24px;
            border-radius: 18px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
            margin-bottom: 18px;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 6px;
        }

        .section-subtitle {
            color: #64748b;
            font-size: 0.95rem;
            margin-bottom: 16px;
        }

        .insight-card {
            background-color: #eff6ff;
            padding: 18px 20px;
            border-radius: 16px;
            border-left: 5px solid #2563eb;
            color: #1e3a8a;
            margin-bottom: 22px;
        }

        .small-note {
            color: #64748b;
            font-size: 0.92rem;
            line-height: 1.6;
        }

        div[data-testid="stDataFrame"] {
            border-radius: 14px;
            overflow: hidden;
        }

        .stDownloadButton button {
            border-radius: 12px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


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
            "primary_user": "Primary User",
            "status": "Status",
            "priority_score": "Priority Score",
            "estimated_hours_saved_month": "Hours Saved / Month",
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


def show_kpi_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


try:
    df = load_data()
except FileNotFoundError:
    st.error("Data file not found. Please check that data/automation_use_cases.csv exists.")
    st.stop()
except ValueError as error:
    st.error(str(error))
    st.stop()


st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">AI Automation Command Center</div>
        <div class="hero-subtitle">
            Operations decision-support dashboard for identifying, prioritizing, and tracking
            AI and workflow automation opportunities across business teams.
        </div>
        <div class="hero-tags">
            <span class="tag">AI Adoption</span>
            <span class="tag">Workflow Automation</span>
            <span class="tag">Operations Analytics</span>
            <span class="tag">Roadmap Prioritization</span>
            <span class="tag">BI-style Reporting</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.header("Dashboard filters")

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

    st.divider()

    st.caption(
        "Use the filters to review automation ideas by department and roadmap status."
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
with kpi1:
    show_kpi_card("Automation ideas", str(total_ideas))
with kpi2:
    show_kpi_card("Ready for pilot", str(ready_for_pilot))
with kpi3:
    show_kpi_card("Hours saved / month", str(hours_saved))
with kpi4:
    show_kpi_card("Avg. priority score", str(avg_priority))


top_opportunity = filtered.sort_values("priority_score", ascending=False).iloc[0]
ready_hours = int(
    filtered[
        filtered["status"].str.contains("Ready", case=False, na=False)
    ]["estimated_hours_saved_month"].sum()
)

st.markdown(
    f"""
    <div class="insight-card">
        <strong>Executive insight:</strong>
        Highest priority opportunity is <strong>{top_opportunity['process_name']}</strong>
        in <strong>{top_opportunity['department']}</strong>, with a priority score of
        <strong>{top_opportunity['priority_score']}</strong>. Current ready-for-pilot ideas
        represent an estimated <strong>{ready_hours} hours saved per month</strong>.
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="section-card">
        <div class="section-title">Automation roadmap</div>
        <div class="section-subtitle">
            Prioritized view of automation opportunities based on impact, effort, confidence,
            and estimated time-saving value.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

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


st.markdown(
    """
    <div class="section-card">
        <div class="section-title">Priority ranking</div>
        <div class="section-subtitle">
            Higher scores indicate stronger candidates for discovery or pilot execution.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

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


chart1, chart2 = st.columns(2)

with chart1:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Potential time saving</div>
            <div class="section-subtitle">
                Estimated monthly time reduction by automation opportunity.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Roadmap status</div>
            <div class="section-subtitle">
                Distribution of automation ideas by current delivery stage.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    status_counts = filtered["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]

    status_chart = px.pie(
        status_counts,
        names="Status",
        values="Count",
        hole=0.42,
    )

    status_chart.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=20, b=40),
        showlegend=True,
    )

    st.plotly_chart(status_chart, use_container_width=True)


st.markdown(
    """
    <div class="section-card">
        <div class="section-title">Idea scoring demo</div>
        <div class="section-subtitle">
            Simulates how a new automation idea could be submitted and reviewed using a first-pass score.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
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

    st.info(
        "Suggested next step: confirm data availability, check integration options, validate the process owner, and decide whether this should move into discovery, pilot, or backlog."
    )


st.markdown(
    """
    <div class="section-card">
        <div class="section-title">Project scope and assumptions</div>
        <div class="small-note">
            This project focuses on the operating model behind internal automation rather than only the technical implementation.
            It demonstrates how teams can collect automation ideas, compare opportunities using consistent scoring logic,
            maintain a visible roadmap, connect automation work with operational reporting, and prepare future integration
            with workflow tools such as n8n or internal approval systems.
            <br><br>
            The data used in this project is fictional sample data created for public portfolio use.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)