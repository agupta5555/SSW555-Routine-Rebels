"""
US-28: Log In

As a registered user, I want to log in to my account so that I can access my
saved habits and progress.
"""

import pytest

from models import User

PASSWORD = 'correct-horse-9'


def register(client, username='neil', password=PASSWORD):
    return client.post('/register', data={
        'username': username,
        'password': password,
        'confirm_password': password,
    })


def login(client, username='neil', password=PASSWORD, **kwargs):
    return client.post('/login', data={'username': username, 'password': password}, **kwargs)


def test_us28_login_page_is_available(client):
    response = client.get('/login')

    assert response.status_code == 200
    assert b'Log in' in response.data


def test_us28_valid_credentials_log_in_and_show_the_dashboard(client):
    """AC: valid credentials log the user in and show their personal dashboard."""
    register(client)

    response = login(client, follow_redirects=True)

    assert response.status_code == 200
    assert b'Logged in as neil.' in response.data
    with client.session_transaction() as flask_session:
        assert flask_session['user_id'] == User.query.filter_by(username='neil').one().id


def test_us28_login_is_case_insensitive_on_username(client):
    register(client, username='Neil')

    response = login(client, username='neil', follow_redirects=True)

    assert response.status_code == 200
    assert b'Logged in as Neil.' in response.data


@pytest.mark.parametrize('username,password', [
    ('neil', 'wrong-password'),
    ('no-such-user', PASSWORD),
    ('', PASSWORD),
    ('neil', ''),
])
def test_us28_invalid_credentials_are_rejected(client, username, password):
    register(client)

    response = login(client, username=username, password=password)

    assert response.status_code == 400
    assert b'Invalid username or password.' in response.data
    with client.session_transaction() as flask_session:
        assert 'user_id' not in flask_session


def test_us28_failed_login_keeps_username_but_not_password(client):
    register(client)

    response = login(client, password='wrong-password')
    page = response.data.decode()

    assert 'value="neil"' in page
    assert PASSWORD not in page


def test_us28_log_in_link_is_in_navigation(client):
    page = client.get('/habit-tracker').data.decode()

    assert 'href="/login"' in page
