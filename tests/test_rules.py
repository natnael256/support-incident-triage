import pytest
from src.rules import classify


@pytest.fixture
def rules():
    """Minimal rule set — deliberately not the production file."""
    return [
        {
            "name": "service_outage",
            "severity": "P1",
            "fields": ["title", "body"],
            "any": ["is down", "can't check out"],
        },
        {
            "name": "slow_performance",
            "severity": "P3",
            "fields": ["title", "body"],
            "any": ["slow to load"],
        },
        {
            "name": "typo_report",
            "severity": "P4",
            "fields": ["title", "body"],
            "any": ["typo on"],
        },
    ]


def test_matches_first_rule(rules):
    ticket = {"title": "checkout is down", "body": ""}
    assert classify(ticket, rules) == ("P1", "service_outage")


def test_matches_on_body_not_just_title(rules):
    ticket = {"title": "Help", "body": "the page is slow to load"}
    assert classify(ticket, rules) == ("P3", "slow_performance")


def test_no_match_returns_none(rules):
    ticket = {"title": "How do I change my email?", "body": ""}
    assert classify(ticket, rules) == (None, None)


def test_first_match_wins_not_most_severe(rules):
    """A ticket matching both P1 and P3 gets P1 because it appears first."""
    ticket = {"title": "checkout is down", "body": "also slow to load"}
    assert classify(ticket, rules) == ("P1", "service_outage")


def test_case_insensitive(rules):
    ticket = {"title": "CHECKOUT IS DOWN", "body": ""}
    assert classify(ticket, rules) == ("P1", "service_outage")


def test_curly_apostrophe_matches_straight(rules):
    ticket = {"title": "customers can\u2019t check out", "body": ""}
    assert classify(ticket, rules) == ("P1", "service_outage")


def test_missing_field_does_not_crash(rules):
    ticket = {"title": "checkout is down"}  # no body key
    assert classify(ticket, rules) == ("P1", "service_outage")


def test_service_name_alone_does_not_match(rules):
    """Service names must never trigger a rule — they appear at every severity."""
    ticket = {"title": "question about checkout", "body": ""}
    assert classify(ticket, rules) == (None, None)