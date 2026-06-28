"""Route work items to the right team using rule-based conditional logic.

This script reads a CSV of work items (and generates a realistic sample CSV if
one does not yet exist), applies a small set of routing rules to each item, and
writes ``routing_results.csv`` with two extra columns: ``routed_to`` and
``routing_reason``. A summary of how many items landed in each team is printed
to stdout.

Run ``python conditional_router.py --help`` for the available options.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "output"
DEFAULT_INPUT = DEFAULT_OUTPUT_DIR / "work_items.csv"
DEFAULT_RESULTS = DEFAULT_OUTPUT_DIR / "routing_results.csv"

# A small but varied set of items that exercises every routing branch.
SAMPLE_ITEMS = [
    {
        "item_id": "WI-001",
        "title": "Tickets breaching SLA in support queue",
        "category": "SLA Risk",
        "priority_score": 9,
        "estimated_hours_saved": 18,
    },
    {
        "item_id": "WI-002",
        "title": "Low-priority SLA review for archived queue",
        "category": "SLA Risk",
        "priority_score": 6,
        "estimated_hours_saved": 8,
    },
    {
        "item_id": "WI-003",
        "title": "Monthly cloud cost reconciliation",
        "category": "Cost Optimisation",
        "priority_score": 7,
        "estimated_hours_saved": 12,
    },
    {
        "item_id": "WI-004",
        "title": "Vendor licence consolidation",
        "category": "Cost Optimisation",
        "priority_score": 5,
        "estimated_hours_saved": 25,
    },
    {
        "item_id": "WI-005",
        "title": "Cross-team onboarding automation",
        "category": "Process Improvement",
        "priority_score": 7,
        "estimated_hours_saved": 30,
    },
    {
        "item_id": "WI-006",
        "title": "Tidy up internal wiki tags",
        "category": "Housekeeping",
        "priority_score": 3,
        "estimated_hours_saved": 4,
    },
    {
        "item_id": "WI-007",
        "title": "Critical SLA escalation for enterprise accounts",
        "category": "SLA Risk",
        "priority_score": 10,
        "estimated_hours_saved": 22,
    },
]

REQUIRED_COLUMNS = ["category", "priority_score", "estimated_hours_saved"]


def generate_sample_csv(path: Path) -> pd.DataFrame:
    """Write the built-in sample work items to ``path`` and return them as a DataFrame.

    Creates any missing parent directories. Used when the script is run without
    an existing input CSV so the demo is fully self-contained.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(SAMPLE_ITEMS)
    df.to_csv(path, index=False)
    return df


def route_item(category: str, priority_score: float, estimated_hours_saved: float) -> tuple[str, str]:
    """Return the ``(team, reason)`` for a single work item.

    Rules are evaluated in priority order; the first match wins:

    1. ``SLA Risk`` with priority score > 8 -> ``escalation_team``
    2. ``Cost Optimisation`` -> ``finance_team``
    3. estimated hours saved > 20 -> ``strategic_team``
    4. otherwise -> ``backlog``
    """
    if category == "SLA Risk" and priority_score > 8:
        return "escalation_team", "SLA Risk with priority score > 8"
    if category == "Cost Optimisation":
        return "finance_team", "Cost Optimisation category"
    if estimated_hours_saved > 20:
        return "strategic_team", "High estimated hours saved (> 20)"
    return "backlog", "No higher-priority rule matched"


def route_items(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``df`` with ``routed_to`` and ``routing_reason`` columns added.

    Validates that the required columns are present before routing.
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Input is missing required columns: {', '.join(missing)}")

    routed = df.copy()
    decisions = [
        route_item(row["category"], row["priority_score"], row["estimated_hours_saved"])
        for _, row in routed.iterrows()
    ]
    routed["routed_to"] = [team for team, _ in decisions]
    routed["routing_reason"] = [reason for _, reason in decisions]
    return routed


def summarise(routed: pd.DataFrame) -> str:
    """Return a printable summary of how many items were routed to each team."""
    counts = Counter(routed["routed_to"])
    lines = ["Routing summary:"]
    for team in sorted(counts):
        lines.append(f"  {counts[team]:>3} items routed to {team}")
    lines.append(f"  {'-' * 3}")
    lines.append(f"  {len(routed):>3} items total")
    return "\n".join(lines)


def load_or_create_items(input_path: Path) -> pd.DataFrame:
    """Load work items from ``input_path``, generating a sample CSV if it is missing."""
    if input_path.exists():
        print(f"Loaded work items from: {input_path}")
        return pd.read_csv(input_path)
    print(f"No input found at {input_path}; generating a sample CSV.")
    return generate_sample_csv(input_path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the conditional router."""
    parser = argparse.ArgumentParser(
        description="Route work items to teams using rule-based logic."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Path to the work-items CSV (default: {DEFAULT_INPUT}). "
        "A sample is generated here if the file does not exist.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RESULTS,
        help=f"Path for the routing results CSV (default: {DEFAULT_RESULTS}).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point: load items, route them, write results, and print a summary."""
    args = parse_args(argv)

    df = load_or_create_items(args.input)
    routed = route_items(df)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    routed.to_csv(args.output, index=False)

    print(f"Routing results written to: {args.output}\n")
    print(summarise(routed))


if __name__ == "__main__":
    main()
