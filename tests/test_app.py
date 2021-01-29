"""Tests for `kune` package."""

import pytest

from kune.kune import create_app
from tests.conftest import test_page

def test_config():
    assert not create_app(test_page).testing
    assert create_app(test_page, {'TESTING': True}).testing

def test_non_route(client):
    assert client.get('/hello').status_code == 404
    
def test_index_route(client):
    assert ('http://localhost/following' ==
            client.get('/').headers['Location'])
    # 
    
def test_following_route(client):
    response = client.get('/following').data
    assert (b'Kune Test Page' in response and
            b'function sync_anchor(msg, cb)' in response)
    
# Test that cursor resets