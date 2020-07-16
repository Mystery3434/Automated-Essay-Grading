from flaskext.mysql import MySQL
import click
from flask import current_app, g
from flask.cli import with_appcontext

#open a new database connection if it does not exist, otherwise return the existing connection
def get_db():
    if 'db' not in g:
        # MySQL
        mysql = MySQL()
        mysql.init_app(current_app)
        g.db = mysql

    return g.db

def init_db():
    # MySQL
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    with current_app.open_resource('resources/database/schema.sql') as schema:
        cursor.execute(schema.read().decode('utf8'))

#flask command to initial the database
@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Database Initialised.')

#initialise the database app
def init_app(app):
    # app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)