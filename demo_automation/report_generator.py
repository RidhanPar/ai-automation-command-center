"""Generate a prioritised automation-opportunity report from the use-case CSV.

This script reads ``data/automation_use_cases.csv``, computes a composite
priority score for every use case, keeps the ones above a threshold, and writes
a human-readable text report to ``demo_automation/output/report_YYYY-MM-DD.txt``.

Run ``python report_generator.py --help`` for the available options.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import pandas as pd

# Resolve key paths relative to this file so the script works no matter what the
# current working directory is when it is invoked.
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_CSV = REPO_ROOT / "data" / "automation_use_cases.csv"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "output"


def compute_priority_score(df: pd.DataFrame) -> pd.Series:
    """Return a composite 0-10 priority score for each row of ``df``.

    The score blends three existing columns so that high-impact, high-confidence,
    low-effort opportunities rank highest:

    * ``impact_score``      weighted 50%
    * ``confidence_score``  weighted 30%
    * inverted ``effort_score`` (``10 - effort``) weighted 20%

    The result stays on the same 0-10 scale as the input scores, which keeps the
    default threshold of 7 meaningful.
    """
    impact = df["impact_score"].astype(float)
    confidence = df["confidence_score"].astype(float)
    effort = df["effort_score"].astype(float)
    return (impact * 0.5) + (confidence * 0.3) + ((10 - effort) * 0.2)


def generate_report(df: pd.DataFrame, threshold: float = 7.0) -> str:
    """Build a formatted text report of automation opportunities above ``threshold``.

    Takes a DataFrame with the raw use-case columns, computes the priority score,
    filters for rows whose score strictly exceeds ``threshold``, sorts them from
    highest to lowest priority, and returns the report as a single string. The
    function performs no file or console I/O, which makes it straightforward to
    unit-test.
    """
    scored = df.copy()
    scored["priority_score"] = compute_priority_score(scored)

    top = scored[scored["priority_score"] > threshold].sort_values(
        "priority_score", ascending=False
    )

    lines: list[str] = []
    lines.append("=" * 70)
    lines.append("TOP AUTOMATION OPPORTUNITIES")
    lines.append(f"Generated: {date.today().isoformat()}")
    lines.append(f"Priority score threshold: > {threshold:g}")
    lines.append(f"Opportunities matched: {len(top)} of {len(scored)}")
    lines.append("=" * 70)
    lines.append("")

    if top.empty:
        lines.append("No automation opportunities exceeded the threshold.")
        lines.append("")
        return "\n".join(lines)

    for rank, (_, row) in enumerate(top.iterrows(), start=1):
        lines.append(f"{rank}. {row['process_name']}  ({row['department']})")
        lines.append(f"   Priority score : {row['priority_score']:.2f}")
        lines.append(
            "   Components     : "
            f"impact={row['impact_score']}, "
            f"confidence={row['confidence_score']}, "
            f"effort={row['effort_score']}"
        )
        lines.append(f"   Status         : {row['status']}")
        lines.append(
            f"   Est. hours saved/month : {row['estimated_hours_saved_month']}"
        )
        lines.append(f"   Automation idea : {row['automation_idea']}")
        lines.append("")

    total_hours = top["estimated_hours_saved_month"].astype(float).sum()
    lines.append("-" * 70)
    lines.append(
        f"Combined estimated savings of matched items: {total_hours:.0f} hours/month"
    )
    lines.append("")

    return "\n".join(lines)


def load_use_cases(csv_path: Path) -> pd.DataFrame:
    """Read the automation use-case CSV at ``csv_path`` into a DataFrame.

    Raises ``FileNotFoundError`` with a clear message if the file is missing.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Use-case CSV not found: {csv_path}")
    return pd.read_csv(csv_path)


def write_report(report: str, output_dir: Path) -> Path:
    """Write ``report`` to ``output_dir/report_YYYY-MM-DD.txt`` and return the path.

    Creates ``output_dir`` (and any parents) if it does not already exist.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"report_{date.today().isoformat()}.txt"
    output_path.write_text(report, encoding="utf-8")
    return output_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the report generator."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate a prioritised report of automation opportunities from the "
            "use-case CSV."
        )
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=7.0,
        help="Only include opportunities whose priority score exceeds this value "
        "(default: 7).",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_CSV,
        help=f"Path to the use-case CSV (default: {DEFAULT_CSV}).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to write the report into (default: {DEFAULT_OUTPUT_DIR}).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point: load the CSV, build the report, and save it to disk."""
    args = parse_args(argv)
    df = load_use_cases(args.input)
    report = generate_report(df, args.threshold)
    output_path = write_report(report, args.output_dir)

    print(report)
    print(f"Report written to: {output_path}")


if __name__ == "__main__":
    main()
