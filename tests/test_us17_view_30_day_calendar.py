"""US-17: View 30-Day Habit Calendar."""

import json
from datetime import date

import pytest

import app as app_module
from extensions import db
from models import Habit


@pytest.fixture(autouse=True)
def fixed_today(monkeypatch):
    class FixedDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 11, 17)  # Tuesday

    monkeypatch.setattr(app_module, 'date', FixedDate)


def add_habit(**fields):
    habit = Habit(name='Morning walk', **fields)
    db.session.add(habit)
    db.session.commit()
    return habit


def test_calendar_classifies_completed_missed_and_non_scheduled_days(client):
    """AC: calendar days are visually distinguished by completion and schedule."""
    habit = add_habit(
        scheduled_days='Mon,Wed,Fri',
        completed_dates=json.dumps(['2026-11-13', '2026-11-16']),
    )

    response = client.get(f'/habit-tracker/habits/{habit.id}/calendar')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-date="2026-11-16" data-status="completed"' in html
    assert 'data-date="2026-11-13" data-status="completed"' in html
    assert 'data-date="2026-11-11" data-status="missed"' in html
    assert 'data-date="2026-11-12" data-status="not-scheduled"' in html
    assert 'Completed' in html
    assert 'Missed' in html
    assert 'Not scheduled' in html


def test_calendar_contains_exactly_the_last_30_days(client):
    habit = add_habit()

    response = client.get(f'/habit-tracker/habits/{habit.id}/calendar')
    html = response.get_data(as_text=True)

    assert html.count('data-date=') == 30
    assert 'data-date="2026-10-19"' in html
    assert 'data-date="2026-11-17" data-status="scheduled"' in html
    assert 'data-date="2026-10-18"' not in html


def test_dashboard_links_to_each_habit_calendar(client):
    habit = add_habit()

    page = client.get('/habit-tracker')

    assert f'/habit-tracker/habits/{habit.id}/calendar'.encode() in page.data
    assert b'View 30-day calendar' in page.data


def test_calendar_for_missing_habit_returns_404(client):
    assert client.get('/habit-tracker/habits/999/calendar').status_code == 404


def test_viewing_calendar_does_not_change_completion_history(client):
    stored = json.dumps(['2026-11-13'])
    habit = add_habit(completed_dates=stored)

    client.get(f'/habit-tracker/habits/{habit.id}/calendar')

    assert db.session.get(Habit, habit.id).completed_dates == stored
