import pytest

from src.scoring import calculate_priority_score, classify_score


def test_priority_score_matches_documented_formula():
    assert calculate_priority_score(7, 5, 7, 30) == 24.5


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (27, "Strong pilot candidate"),
        (22, "Good discovery candidate"),
        (17, "Needs more validation"),
        (16.9, "Backlog candidate"),
    ],
)
def test_score_classification_boundaries(score, expected):
    assert classify_score(score) == expected
