"""The kune flask app for serving synced slides."""

import os
import json
from flask import Flask, render_template, redirect, url_for, session, abort
from flask_socketio import SocketIO, emit
from jinja2 import Template


def update_cursor(cursor_file, cursor_position):
    with open(cursor_file, 'w') as f:
        json.dump({'cursor': cursor_position}, f)


def get_cursor(cursor_file):
    with open(cursor_file, 'r') as f:
        return json.load(f)['cursor']


def create_app(html_file, config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        CURSOR_FILE=os.path.join(app.instance_path, 'cursor.json'),
        LEADER_TOKEN='lead',
        SOCKETIO_ASYNC_MODE=None,
    )
    if config:  # load the config if passed in
        app.config.from_mapping(config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    update_cursor(app.config['CURSOR_FILE'], '')

    def create_template(html_file):
        sync_scripts_block = '{% block sync_scripts %}{% endblock %}'
        with open(html_file) as f:
            html = f.read()
        return Template(html.replace('</head>',
                                     f'{sync_scripts_block}\n</head>'))

    @app.route('/')
    @app.route('/follow')
    def index():
        cursor = get_cursor(app.config['CURSOR_FILE'])[1:]  # no '#' in flask
        return redirect(url_for('following', _anchor=cursor))

    @app.route(f"/{app.config['LEADER_TOKEN']}")
    def lead():
        session['is_leader'] = True
        cursor = get_cursor(app.config['CURSOR_FILE'])[1:]  # no '#' in flask
        return redirect(url_for('leading', _anchor=cursor))

    @app.route('/following')
    def following():
        session['is_leader'] = False
        return render_template('synced.jinja2',
                               templated_html=create_template(html_file),
                               async_mode=app.config['SOCKETIO_ASYNC_MODE'])

    @app.route('/leading')
    def leading():
        if not session['is_leader']:
            abort(403)
        return render_template('synced.jinja2',
                               templated_html=create_template(html_file),
                               async_mode=app.config['SOCKETIO_ASYNC_MODE'])

    return app


def create_socketio(app):
    socketio = SocketIO(app, async_mode=app.config['SOCKETIO_ASYNC_MODE'])

    @socketio.event
    def hash_change(message):
        cursor_file = app.config['CURSOR_FILE']
        if message['data'] != get_cursor(cursor_file):
            update_cursor(cursor_file, message['data'])
            emit('updated_cursor', {'data': message['data']}, broadcast=True)

    return socketio
