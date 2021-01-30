"""Fixtures and other config for testing `kune`."""

from pkg_resources import resource_filename
import pytest
from click.testing import CliRunner

from kune import kune


# WebApp
@pytest.fixture
def test_page():
    return resource_filename('tests.resources', 'test_page.html')

@pytest.fixture
def app(test_page):
    """Calls the kune app factory and configures for testing"""
    yield kune.create_app(test_page, config={'TESTING': True,})

@pytest.fixture
def client(app):
    return app.test_client()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def take_lead(self):
        return self._client.get('/lead', follow_redirects=True)

    def relinquish_lead(self):
        return self._client.get('/', follow_redirects=True)  # could also be '/follow'
                  
@pytest.fixture
def auth(client):
    return AuthActions(client)

# CLI
@pytest.fixture
def cli_runner():
    return CliRunner()