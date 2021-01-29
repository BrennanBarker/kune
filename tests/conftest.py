"""Tests for `kune` package."""

import pytest
import pkg_resources

test_page = pkg_resources.resource_filename('tests.resources', 'test_page.html')

from kune import kune

@pytest.fixture
def app():
    """Calls the kune app factory and configures for testing"""
    app = kune.create_app(test_page, 
                     config={'TESTING': True,})
    yield app
    

@pytest.fixture
def client(app):
    return app.test_client()