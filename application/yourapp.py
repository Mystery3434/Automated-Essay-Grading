from yourapp.main import main
from application.database import get_db
from flask import Blueprint, request, current_app, jsonify, json, g, make_response

import redis
from rq import Queue, Connection
import hashlib
import time
import json
import logging
from application.redis_worker import get_worker_pipeline
from application.redis_connection import get_redis_connection

yourapp = Blueprint('yourapp', __name__,
                        template_folder='templates')

def genHash(content):
    # Generate Hash
    # m = hashlib.sha256()
    m = hashlib.md5()
    m.update(content.encode('utf-8'))
    return m.hexdigest()

# For testing of the process_task function
@yourapp.route('/', methods = ["GET", "POST"])
def testing():
    req = request.get_json()
    res = main(
        uid="1",
        body="demo",
    )
    return jsonify({"success":json.loads(res)})

# Queue Status
@yourapp.route('/status', methods = ["GET"])
def get_status():
    req = request.get_json()
    res = {
        "error": "Some error on /status"
    }

    with current_app.app_context():
        redis_connection = get_redis_connection()
        q = Queue(current_app.config['QUEUES'][0], connection=redis_connection)
        queued_job_ids = q.job_ids
        res = {
            "queue": queued_job_ids,
            "len": len(q),
        }
    return jsonify({
        "status": "OK",
        "success": res
    })
