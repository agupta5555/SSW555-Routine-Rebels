"""US-19: View Weekly Summary."""

import json
from datetime import date, datetime

import pytest

import app as app_module
from extensions import db
from models import Habit


@pytest.fixture(autouse=True)
def fixed_today(monkeypatch):
    class FixedDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 11, 18)  # Wednesday

    monkeypatch.setattr(app_module, 'date', FixedDate)


def add_habit(name, completed=(), **fields):
    habit = Habit(
        name=name,
        completed_dates=json.dumps(list(completed)),
        created_at=datetime(2026, 11, 1, 9),
        **fields,
    )
    db.session.add(habit)
    db.session.commit()
    return habit


def test_current_week_summary_shows_completed_count_and_percentage(client):
    """AC: number and percentage of scheduled habits completed are visible."""
    add_habit('Run', ['2026-11-16'], scheduled_days='Mon,Wed,Fri')
    add_habit('Journal', ['2026-11-17'], scheduled_days='Tue,Thu')

    response = client.get('/habit-tracker/weekly-summary')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-testid="weekly-completed">2<' in html
    assert 'of 3' in html
    assert 'data-testid="weekly-percentage">67%</' in html
    assert '(so far)' in html


def test_past_week_uses_all_seven_days_and_ignores_non_scheduled_completions(client):
    add_habit(
        'Run',
        ['2026-11-09', '2026-11-10', '2026-11-11'],
        scheduled_days='Mon,Wed,Fri',
    )

    response = client.get('/habit-tracker/weekly-summary?week_start=2026-11-09')

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'data-testid="weekly-completed">2<' in html
    assert 'of 3' in html
    assert 'data-testid="weekly-percentage">67%</' in html
    assert '(so far)' not in html


def test_summary_does_not_count_days_before_a_habit_was_created(client):
    habit = Habit(
        name='New daily habit',
        created_at=datetime(2026, 11, 18, 8),
        completed_dates=json.dumps(['2026-11-18']),
    )
    db.session.add(habit)
    db.session.commit()

    html = client.get('/habit-tracker/weekly-summary').get_data(as_text=True)

    assert 'data-testid="weekly-completed">1<' in html
    assert 'of 1' in html
    assert 'data-testid="weekly-percentage">100%</' in html


def test_empty_summary_shows_zero_percent_without_dividing_by_zero(client):
    response = client.get('/habit-tracker/weekly-summary')

    assert response.status_code == 200
    assert b'data-testid="weekly-percentage">0%</' in response.data
    assert b'No habits to summarize' in response.data


@pytest.mark.parametrize('week_start', ['not-a-date', '2026-11-17', '2026-11-23'])
def test_invalid_week_start_is_rejected(client, week_start):
    assert client.get(
        '/habit-tracker/weekly-summary', query_string={'week_start': week_start}
    ).status_code == 400


def test_dashboard_links_to_weekly_summary(client):
    page = client.get('/habit-tracker')

    assert b'/habit-tracker/weekly-summary' in page.data
    assert b'Weekly summary' in page.data
