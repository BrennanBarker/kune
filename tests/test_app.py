"""Tests for `kune` flask application."""

from kune import kune
from flask import session, request
from copy import deepcopy

# Switch lead to leader token
# Refactor to auth?

def assert_is_follower(response):
    assert session['is_leader'] == False
    assert b'Kune Test Page' in response.data
    assert b'function sync_anchor' in response.data
    assert b'function notify_server' not in response.data

def assert_is_leader(response):
    assert session['is_leader'] == True
    assert b'Kune Test Page' in response.data
    assert b'function sync_anchor' in response.data
    assert b'function notify_server' in response.data

def test_config(test_page):
    assert not kune.create_app(test_page).testing
    assert kune.create_app(test_page, {'TESTING': True}).testing

def test_bad_route(client):
    assert client.get('/hello').status_code == 404  # Not Found
    
def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/following'
    
def test_following(client):
    with client:
        response = client.get('/following')
        assert_is_follower(response)
    
def test_unauthorized_leading(app, client):
    with client: 
        assert client.get('/following').status_code == 200  # Success
        assert client.get('/leading').status_code == 403  # Forbidden
    
def test_lead_redirect(client):
    response = client.get('/lead')
    assert response.status_code == 302  # Redirect
    assert response.headers['Location'] == 'http://localhost/leading'
        
def test_lead(client):
    with client:
        response = client.get('/lead', follow_redirects=True)
        assert_is_leader(response)
        
def test_leader(client, auth, app):
    with client:
        assert client.get('/', follow_redirects=True).status_code == 200
        response = auth.take_lead()
        assert request.path == '/leading'
        assert_is_leader(response)
        
def test_relinquish_lead(client, auth):
    with client:
        assert client.get('/', follow_redirects=True).status_code == 200
        response = auth.take_lead()
        assert request.path == '/leading'
        assert_is_leader(response)
        response = auth.relinquish_lead()
        assert request.path == '/following'
        assert_is_follower(response)
        
def test_cursor_change_follower(client, app):
    with client:
        response_pre_cursor_change = client.get('/')
        assert response_pre_cursor_change.headers['Location'] == 'http://localhost/following'
        kune.update_cursor(app.config['CURSOR_FILE'], '#2')
        assert kune.get_cursor(app.config['CURSOR_FILE']) == '#2'
        response_post_cursor_change = client.get('/')
        assert response_post_cursor_change.headers['Location'] == 'http://localhost/following#2'
        
def test_cursor_change_leader(client, app):
    with client:
        response_pre_cursor_change = client.get('/lead')
        assert response_pre_cursor_change.headers['Location'] == 'http://localhost/leading'
        kune.update_cursor(app.config['CURSOR_FILE'], '#2')
        assert kune.get_cursor(app.config['CURSOR_FILE']) == '#2'
        response_post_cursor_change = client.get('/lead')
        assert response_post_cursor_change.headers['Location'] == 'http://localhost/leading#2'
        
def test_cursor_reset(client):  # Place after test_cursor_change
    with client:
        response_pre_cursor_change = client.get('/')
        assert response_pre_cursor_change.headers['Location'] == 'http://localhost/following'