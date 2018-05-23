# !/usr/bin/env python3
# Copyright (c) 2018 Jeff Lund
# Capstone Project New Beginnings 2018 - BillShare
# Main application code that runs the website

import os
import flask, flask.views

def create_app():
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', 
        DATABASE=os.path.join(app.instance_path, 'billshare.sqlite')
    )
    app.config.from_pyfile('config.py', silent=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #@app.route('/', methods=('GET', 'POST'))
    #def index():
    #    if flask.g.user:
    #        return home()

     #   return flask.render_template('index.html')

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import user
    app.register_blueprint(user.bp)

    @app.route('/', methods=('GET', 'POST'))
    def index():
        if flask.g.user:
            return user.home()

        return flask.render_template('index.html')


    return app
