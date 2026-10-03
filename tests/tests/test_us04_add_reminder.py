"""
US-04: Add a Reminder

As a user, I want to add an optional reminder to a habit so that I do not
forget to complete it.
"""

import pytest

from models import Habit


@pytest.mark.xfail(reason="US-04: habit reminders are not implemented yet")
def test_us04_add_reminder_to_existing_habit(client):
    """AC: A reminder time can be attached to an existing habit."""
    # Arrange
    habit = Habit(name="Go to the gym", description="Workout")
    from extensions import db
    db.session.add(habit)
    db.session.commit()

    # Act
    client.post(
        f"/habit-tracker/{habit.id}/reminder",
        data={"reminder_time": "18:00"},
    )

    # Assert
    stored = Habit.query.get(habit.id)
    assert stored.reminder_time == "18:00"
