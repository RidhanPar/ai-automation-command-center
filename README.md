# AI Automation Command Center

This project is a small operations dashboard for collecting, scoring, and tracking internal automation ideas.

I built it as a portfolio project because many teams do not lack automation ideas. The harder part is usually deciding which ideas are worth doing first, which ones need more discovery, and how to show the value in a simple way to managers or stakeholders.

The app uses sample internal-process scenarios such as SLA risk review, employee request routing, shift swap validation, incident handover summaries, and monthly reporting.

## What the project does

- Lists automation ideas from different business areas
- Scores each idea using impact, effort, confidence, and estimated time saving
- Shows a roadmap view for pilot-ready, discovery, backlog, and validated ideas
- Provides KPI cards for leadership-level visibility
- Includes a simple intake form to test how a new idea could be scored
- Includes a basic n8n-style workflow example for request routing

## Why I built it

In operations and support environments, a lot of improvement opportunities come from small repeated manual steps. Examples include checking queues, routing requests, preparing status updates, validating rules, or creating weekly reports.

This project is my attempt to show how those ideas can be captured in one place, compared fairly, and connected to measurable operational value.

## Tech stack

- Python
- Streamlit
- Pandas
- Plotly
- CSV sample data
- n8n workflow concept

## Folder structure

```text
ai_automation_command_center/
├── app.py
├── requirements.txt
├── data/
│   └── automation_use_cases.csv
├── docs/
│   ├── architecture.md
│   ├── github_setup.md
│   └── interview_notes.md
├── n8n_workflow_demo/
│   ├── employee_request_automation_demo.json
│   └── README.md
└── portfolio_text/
    └── portfolio_copy.md
```

## How to run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## How the score works

The priority score is not meant to be a perfect business formula. It is a simple first-pass score to compare ideas:

```text
priority score =
impact score × 2
+ confidence score × 1.5
+ estimated monthly hours saved / 6
- effort score
```

This gives higher weight to ideas with strong impact and confidence, while reducing the score when effort is high.

## Example use cases included

- SLA risk review
- Shift swap validation
- Employee request routing
- Monthly cost review
- Incident handover summary
- Automation idea intake
- Repeat issue detection

## What I would improve next

- Replace CSV with SQLite or PostgreSQL
- Add login and role-based views
- Add a real approval workflow
- Connect the intake form to a database
- Add n8n webhook integration
- Add Power BI or Tableau reporting layer
- Add audit history for roadmap status changes

## Portfolio description

AI Automation Command Center is a Streamlit dashboard for managing internal automation ideas. It helps teams collect use cases, score them by impact and effort, track roadmap status, and show estimated time-saving value through simple leadership KPIs.

The project demonstrates practical thinking around AI adoption, workflow automation, operational analytics, and data-driven prioritization.