"""Fixtures and other config for testing `kune`."""

from pkg_resources import resource_filename, resource_listdir
import pytest
from click.testing import CliRunner

from kune import kune


# WebApp
@pytest.fixture
def page():
    return resource_filename('tests.resources', 'page.html')


@pytest.fixture
def static_dir():
    return resource_filename('tests.resources', 'static')


@pytest.fixture
def app(page):
    """Calls the kune app factory and configures for testing"""
    yield kune.create_app(page, config={'TESTING': True,
                                             'LEADER_TOKEN':'test_token'})


@pytest.fixture
def client(app):
    return app.test_client()


# CLI
@pytest.fixture
def cli_runner():
    return CliRunner()
