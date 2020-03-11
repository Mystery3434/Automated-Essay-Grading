import redis
from flask import Blueprint, render_template, request, jsonify, current_app, g
from rq import push_connection, pop_connection, Queue

def get_redis_connection():
    redis_connection = getattr(g, '_redis_connection', None)
    if redis_connection is None:
        redis_url = current_app.config['REDIS_URL']
        redis_connection = g._redis_connection = redis.from_url(redis_url)
    return redis_connection


def push_rq_connection():
    push_connection(get_redis_connection())


def pop_rq_connection(exception=None):
    pop_connection()

def init_app(app):
    app.before_request(push_rq_connection)
    app.teardown_request(pop_rq_connection)
    
