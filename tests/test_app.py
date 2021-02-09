"""Tests for `kune` flask application."""

from kune import kune
from flask import session, request


def take_lead(app, client, follow_redirects=False):
    return client.get(f"/{app.config['LEADER_TOKEN']}",
                      follow_redirects=follow_redirects)


def relinquish_lead(app, client, follow_redirects=False):
    return client.get('/', follow_redirects=follow_redirects)


def assert_is_follower(response):
    assert session['is_leader'] is False
    assert b'Kune Test Page' in response.data
    assert b'function sync_anchor' in response.data
    assert b'function notify_server' not in response.data


def assert_is_leader(response):
    assert session['is_leader'] is True
    assert b'Kune Test Page' in response.data
    assert b'function sync_anchor' in response.data
    assert b'function notify_server' in response.data


def test_config(page):
    assert not kune.create_app(page).testing
    assert kune.create_app(page, {'TESTING': True}).testing


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


def test_lead_redirect(app, client):
    response = take_lead(app, client)
    assert response.status_code == 302  # Redirect
    assert response.headers['Location'] == 'http://localhost/leading'


def test_lead(app, client):
    with client:
        response = take_lead(app, client, follow_redirects=True)
        assert_is_leader(response)


def test_leader(app, client):
    with client:
        response = take_lead(app, client, follow_redirects=True)
        assert response.status_code == 200
        assert request.path == '/leading'
        assert_is_leader(response)


def test_relinquish_lead(app, client):
    with client:
        response = take_lead(app, client, follow_redirects=True)       
        response = relinquish_lead(app, client, follow_redirects=True)
        assert request.path == '/following'
        assert_is_follower(response)


def test_cursor_change_follower(app, client):
    with client:
        response_pre_cursor_change = client.get('/')
        assert (response_pre_cursor_change.headers['Location'] ==
                'http://localhost/following')
        kune.update_cursor(app.config['CURSOR_FILE'], '#2')
        assert kune.get_cursor(app.config['CURSOR_FILE']) == '#2'
        response_post_cursor_change = client.get('/')
        assert (response_post_cursor_change.headers['Location'] ==
                'http://localhost/following#2')


def test_cursor_change_leader(app, client):
    with client:
        response_pre_cursor_change = take_lead(app, client)
        assert (response_pre_cursor_change.headers['Location'] ==
                'http://localhost/leading')
        kune.update_cursor(app.config['CURSOR_FILE'], '#2')
        assert kune.get_cursor(app.config['CURSOR_FILE']) == '#2'
        response_post_cursor_change = take_lead(app, client)
        assert (response_post_cursor_change.headers['Location'] ==
                'http://localhost/leading#2')


def test_cursor_reset(client):  # Place after test_cursor_change
    with client:
        response_pre_cursor_change = client.get('/')
        assert (response_pre_cursor_change.headers['Location'] ==
                'http://localhost/following')


def test_get_static_file(client):
    assert client.get('/static/style.css').status_code == 200

