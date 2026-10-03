"""
US-01: Create a New Habit
Owner: Aryan Gupta

As a college student trying to build better routines, I want to create a new
habit with a name, category (Health, Work, or Other), and daily goal so that I
can start tracking something specific, like drinking 8 glasses of water or
calling home every day.
"""

import pytest

from models import Habit


def test_us01_create_habit_saves_and_shows_on_dashboard(client):
    """AC: A new habit is saved and appears on the habit tracker page."""
    # Arrange
    habit_data = {"name": "Drink water", "description": "8 glasses a day"}

    # Act
    response = client.post("/habit-tracker", data=habit_data)
    page = client.get("/habit-tracker")

    # Assert
    assert response.status_code == 302
    stored = Habit.query.filter_by(name="Drink water").first()
    assert stored is not None
    assert stored.description == "8 glasses a day"
    assert b"Drink water" in page.data


def test_us01_habit_without_name_is_not_created(client):
    """AC: If I try to save without a name, the habit is not created."""
    # Act
    response = client.post("/habit-tracker", data={"name": "   ", "description": "No name"})

    # Assert
    assert response.status_code == 302
    assert Habit.query.count() == 0


@pytest.mark.xfail(reason="US-01: category and daily goal fields not implemented yet")
def test_us01_create_habit_with_category_and_daily_goal(client):
    """AC: A habit can be created with a category and a daily goal."""
    # Arrange
    habit_data = {"name": "Call home", "category": "Other", "daily_goal": "1"}

    # Act
    client.post("/habit-tracker", data=habit_data)

    # Assert
    stored = Habit.query.filter_by(name="Call home").first()
    assert stored.category == "Other"
    assert stored.daily_goal == 1
