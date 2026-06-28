# Demo Automation Scripts

Three small, self-contained Python automation scripts that demonstrate real,
working automation patterns against this repo's data and a public API. There is
no mock data or placeholder logic — each script reads real input, does real
work, and writes real output to `demo_automation/output/`.

## What each script does

### `report_generator.py`
Reads `data/automation_use_cases.csv`, computes a composite **priority score**
for every use case (a 0–10 blend of impact, confidence, and inverted effort),
and keeps only the opportunities whose score exceeds a threshold. It writes a
formatted, ranked text report — with scores, status, and estimated hours saved —
to `demo_automation/output/report_YYYY-MM-DD.txt`. The core
`generate_report(df, threshold)` function takes a DataFrame and returns a string,
so it is easy to unit-test in isolation.

### `api_monitor.py`
Polls a public API endpoint (the JSONPlaceholder demo API by default) on a fixed
interval and records each call's HTTP status, response time in milliseconds, and
number of records returned. Results are appended to
`demo_automation/output/api_monitor.log` in a structured
`timestamp | status | latency_ms | record_count` format. Connection and timeout
errors are caught and logged as `ERROR` rows rather than crashing the loop, and
the monitor stops cleanly after the configured number of runs.

### `conditional_router.py`
Reads a CSV of work items (and generates a realistic sample CSV automatically if
none exists), then routes each item to a team using rule-based conditional logic.
It writes `demo_automation/output/routing_results.csv` with the original columns
plus `routed_to` and `routing_reason`, and prints a summary of how many items
landed in each team. The routing rules, in priority order, are:

1. `category == "SLA Risk"` **and** `priority_score > 8` → `escalation_team`
2. `category == "Cost Optimisation"` → `finance_team`
3. `estimated_hours_saved > 20` → `strategic_team`
4. otherwise → `backlog`

## How to run

All commands are run from the repository root. The scripts depend on `pandas`
and `requests` (both already listed in the project `requirements.txt`; install
with `pip install pandas requests` if needed).

```bash
# 1. Generate the prioritised opportunity report (default threshold = 7)
python demo_automation/report_generator.py
python demo_automation/report_generator.py --threshold 8

# 2. Monitor the public API (fast demo: 3 polls, 1 second apart)
python demo_automation/api_monitor.py --interval 1 --max-runs 3
python demo_automation/api_monitor.py            # defaults: 30s interval, 5 runs

# 3. Route work items to teams (auto-creates a sample CSV on first run)
python demo_automation/conditional_router.py
```

> On Windows, use `py -3.11` in place of `python` if that is how your Python 3.11
> interpreter is invoked.

Each script also supports `--help` for the full list of options (input/output
paths, thresholds, intervals, and so on).

## Extending these scripts

These demos are deliberately simple so the patterns are easy to lift into
production work:

- **`api_monitor.py` → a real internal API.** Point `--url` at an internal
  service health or data endpoint, add authentication (e.g. a bearer token via a
  `requests.Session` with default headers), and forward the structured log lines
  to a monitoring stack (Prometheus, Datadog, or a log aggregator) instead of a
  flat file. Alerts can be triggered when `status` is non-200 or `latency_ms`
  crosses a threshold.

- **`conditional_router.py` → database-driven rules.** Replace the hard-coded
  `route_item` rules with rules loaded from a database or config table, so
  business owners can change routing without a code deploy. The work items
  themselves can be read from a queue or database query rather than a CSV, and
  results written back to the same store.

- **`report_generator.py` → scheduled execution.** Run the report on a schedule
  with **cron** (Linux/macOS, e.g. `0 8 * * 1` for every Monday at 08:00) or
  **Windows Task Scheduler** so a fresh `report_YYYY-MM-DD.txt` is produced
  automatically. From there the report can be emailed to stakeholders or posted
  to a Slack/Teams channel.
