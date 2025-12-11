# app/tests/conftest.py
import os
import sys
import pytest

# Add project root (…/crm-marketing-automation) to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app


@pytest.fixture
def app():
    """Create a Flask app instance for tests."""
    app = create_app()
    app.config.update(
        TESTING=True,
    )
    return app


@pytest.fixture
def client(app):
    """Basic test client (not logged in)."""
    return app.test_client()


@pytest.fixture
def logged_in_client(client):
    """
    Test client with a fake logged-in user.

    We set session keys that login_required probably checks, and that
    your marketing pages read (username/email).
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1          # common pattern for auth checks
        sess["username"] = "testuser"
        sess["email"] = "test@example.com"
    return client
