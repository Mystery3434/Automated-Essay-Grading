import os

from flask import Flask, render_template

#application factory function
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        MONGODB_DB='yourapp',
        MONGODB_HOST='mongodb',
        MONGODB_PORT=27017,
        MYSQL_DATABASE_USER='root',
        MYSQL_DATABASE_PASSWORD='yourapp_password',
        MYSQL_DATABASE_DB='yourapp',
        MYSQL_DATABASE_HOST='mysql',
        REDIS_URL = 'redis://redis:6379',
        REDIS_HOST = 'redis',
        REDIS_PORT = 6379,
        REDIS_DB = '0',
        QUEUES = ['default'],
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # initialise db module
    import application.database as database
    database.init_app(app)

    # initialise redis connection
    import application.redis_connection as redis_connection
    redis_connection.init_app(app)
    import application.redis_worker as redis_worker
    redis_worker.init_app(app)

    #register blueprints
    from application.yourapp import yourapp
    app.register_blueprint(yourapp, url_prefix='/yourapp')


    # handle the main page
    @app.route('/')
    def index():
        return render_template('index.html') 

    #register error handlers
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, server_error)

    return app

def page_not_found(e):
    return "404 error", 404

def server_error(e):
    return "500 error", 500

app = create_app()
