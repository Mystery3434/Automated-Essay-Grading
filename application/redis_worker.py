import redis
from rq import Connection, Worker, Queue
import click
from flask import current_app
from flask.cli import with_appcontext
from rq.local import LocalStack
import logging

_pipeline_stack = LocalStack()

@click.command('run-worker')
@with_appcontext
def run_worker_command():
    redis_url = current_app.config['REDIS_URL']
    redis_connection = redis.from_url(redis_url)
    with Connection(redis_connection):
        worker = MyWorker(list(map(Queue, current_app.config['QUEUES'])))
        worker.work()

def init_app(app):
    app.cli.add_command(run_worker_command)

def get_worker_pipeline():
    pipeline = _pipeline_stack.top
    if pipeline:
        return pipeline
    else:
        return None

class MyWorker(Worker):
    def work(self, *args, **kwargs):
        return Worker.work(self, *args, **kwargs)
