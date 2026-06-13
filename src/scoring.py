"""Transparent scoring logic for automation-opportunity discovery."""


def calculate_priority_score(
    impact: float,
    effort: float,
    confidence: float,
    estimated_hours_saved_month: float,
) -> float:
    """Return the documented first-pass opportunity score."""
    return round(
        (float(impact) * 2.0)
        + (float(confidence) * 1.5)
        + (float(estimated_hours_saved_month) / 6.0)
        - float(effort),
        1,
    )


def classify_score(score: float) -> str:
    """Map a score to the roadmap's human-review recommendation."""
    if score >= 27:
        return "Strong pilot candidate"
    if score >= 22:
        return "Good discovery candidate"
    if score >= 17:
        return "Needs more validation"
    return "Backlog candidate"
