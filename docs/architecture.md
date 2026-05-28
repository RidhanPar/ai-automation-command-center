# Architecture Notes

The current version is intentionally lightweight.

## Current flow

```text
CSV data
   ↓
Streamlit app
   ↓
Priority scoring logic
   ↓
Roadmap table + KPI dashboard + charts
```

## Main components

### 1. Data source

The sample data is stored in:

```text
data/automation_use_cases.csv
```

Each row represents one automation idea.

### 2. Scoring logic

The app calculates a priority score using:

- impact
- effort
- confidence
- estimated monthly hours saved

The formula is simple because this version is meant to show business prioritization logic, not a complex model.

### 3. Dashboard

The dashboard gives four views:

- KPI summary
- roadmap table
- priority ranking
- estimated time-saving chart

### 4. Intake demo

The intake form shows how a team member could submit a new automation idea and receive an initial score.

## Future architecture idea

A more complete version could look like this:

```text
Team idea form
   ↓
n8n webhook
   ↓
Validation and routing
   ↓
PostgreSQL / Google Sheets
   ↓
Dashboard update
   ↓
Email / Teams notification
   ↓
Monthly leadership report
```

This would turn the project from a dashboard into a full workflow automation system.