"""Poll a public API on a schedule and log status, latency, and record count.

This is a small uptime/health monitor. It repeatedly issues GET requests to a
target endpoint (the JSONPlaceholder demo API by default), measures how long
each call takes, counts the records returned, and appends a structured line to
``demo_automation/output/api_monitor.log``. Connection errors are logged and the
loop continues, so a transient network failure does not crash the monitor.

Run ``python api_monitor.py --help`` for the available options.
"""

from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "output"
DEFAULT_URL = "https://jsonplaceholder.typicode.com/posts"

# Header written once when a fresh log file is created.
LOG_HEADER = "timestamp | status | latency_ms | record_count"


def _utc_timestamp() -> str:
    """Return the current UTC time as an ISO-8601 string (seconds precision)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def poll_once(url: str, timeout: float = 10.0) -> dict:
    """Make a single GET request to ``url`` and return a structured result dict.

    The returned dict always contains ``timestamp``, ``status``, ``latency_ms``,
    and ``record_count`` keys. On a connection/timeout error, ``status`` is set
    to ``"ERROR"``, ``record_count`` to ``0``, and an ``error`` key holds the
    message; the exception is swallowed so the caller can keep polling.
    """
    start = time.perf_counter()
    try:
        response = requests.get(url, timeout=timeout)
        latency_ms = (time.perf_counter() - start) * 1000.0
        record_count = _count_records(response)
        return {
            "timestamp": _utc_timestamp(),
            "status": str(response.status_code),
            "latency_ms": round(latency_ms, 1),
            "record_count": record_count,
        }
    except requests.RequestException as exc:
        latency_ms = (time.perf_counter() - start) * 1000.0
        return {
            "timestamp": _utc_timestamp(),
            "status": "ERROR",
            "latency_ms": round(latency_ms, 1),
            "record_count": 0,
            "error": str(exc),
        }


def _count_records(response: requests.Response) -> int:
    """Return the number of records in a response body.

    Lists report their length, dicts count as a single record, and anything that
    is not valid JSON counts as zero.
    """
    try:
        payload = response.json()
    except ValueError:
        return 0
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        return 1
    return 0


def format_log_line(result: dict) -> str:
    """Format a poll ``result`` dict into a single structured log line."""
    line = (
        f"{result['timestamp']} | "
        f"{result['status']} | "
        f"{result['latency_ms']} | "
        f"{result['record_count']}"
    )
    if "error" in result:
        line += f" | {result['error']}"
    return line


def append_log(line: str, log_path: Path) -> None:
    """Append ``line`` to ``log_path``, creating the file and header if needed."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not log_path.exists()
    with log_path.open("a", encoding="utf-8") as handle:
        if new_file:
            handle.write(LOG_HEADER + "\n")
        handle.write(line + "\n")


def run_monitor(
    url: str,
    interval: float,
    max_runs: int,
    log_path: Path,
) -> list[dict]:
    """Poll ``url`` up to ``max_runs`` times, logging each result.

    Sleeps ``interval`` seconds between polls (but not after the final one) and
    returns the list of result dicts so callers/tests can inspect the run.
    """
    results: list[dict] = []
    for run_number in range(1, max_runs + 1):
        result = poll_once(url)
        results.append(result)

        line = format_log_line(result)
        append_log(line, log_path)
        print(f"[{run_number}/{max_runs}] {line}")

        if run_number < max_runs:
            time.sleep(interval)

    return results


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the API monitor."""
    parser = argparse.ArgumentParser(
        description="Poll a public API on a schedule and log the results."
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=30.0,
        help="Seconds to wait between polls (default: 30).",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=5,
        help="Number of polls before stopping (default: 5).",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_URL,
        help=f"API endpoint to poll (default: {DEFAULT_URL}).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for the log file (default: {DEFAULT_OUTPUT_DIR}).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point: run the monitor loop with the parsed CLI options."""
    args = parse_args(argv)
    log_path = args.output_dir / "api_monitor.log"

    print(f"Polling {args.url} every {args.interval:g}s for {args.max_runs} runs.")
    print(f"Logging to: {log_path}\n")

    run_monitor(args.url, args.interval, args.max_runs, log_path)

    print("\nMonitor finished cleanly.")


if __name__ == "__main__":
    main()
