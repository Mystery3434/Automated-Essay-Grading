from flaskext.mysql import MySQL
from mongoengine import *
import click
from flask import current_app, g
from flask.cli import with_appcontext

#open a new database connection if it does not exist, otherwise return the existing connection
def get_db():
    if 'db' not in g:
        # MongoDb
        connect(current_app.config["MONGODB_DB"], host=current_app.config["MONGODB_HOST"], port=current_app.config["MONGODB_PORT"])

        # MySQL
        mysql = MySQL()
        mysql.init_app(current_app)
        g.db = mysql

    return g.db

def connect_db():
    connect(current_app.config["MONGODB_DB"], host=current_app.config["MONGODB_HOST"], port=current_app.config["MONGODB_PORT"])

#close the existing database connection
def close_db(e=None):
    # MongoDb
    disconnect()

def init_db():
    # MongoDb
    EDocuments.dropcollection()

    # MySQL
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    with current_app.open_resource('resources/database/schema.sql') as schema:
        cursor.execute(schema.read().decode('utf8'))

class EDocuments(Document):
    title = StringField(default="Untitled")
    title_doc = BinaryField(required=False)
    body = StringField(required=True)
    text_doc = BinaryField(required=False)
    process_status = StringField(default="NOT PROCESSED")
    tokens = ListField(StringField(), default = [])
    processed_body = StringField(required=False)

#flask command to initial the database
@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Database Initialised.')

#initialise the database app
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)