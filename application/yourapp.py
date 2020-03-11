from yourapp.main import main
from application.database import get_db, connect_db, close_db, EDocuments
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


#backend method to process a single text with the nltk pos tagger given a id
def process_task(id):
    cur = None
    db = None
    with current_app.app_context():
        try:
            logging.warn("processing document {}.".format(id))
            # # MongoDB
            # connect_db()
            # result = EDocuments.objects.with_id(id)
            # body = result.body

            # MySQL
            db = get_db()
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT process_status, body FROM document WHERE id = %s;", (id))
            result = cursor.fetchall()
            body = result[0][1]

            if len(body) > 0:

                if False and body["process_status"] == "FINISHED":
                    logging.warn("document {} already processed.".format(id))
                    success = True
                else:
                    # MongoDB
                    # result.modify(set__process_status = "PROCESSING")

                    # MySQL
                    cursor.execute("UPDATE document SET process_status = 'PROCESSING' WHERE id = %s;", (id))
                    conn.commit()

                    result = ""
                    # Import yourapp
                    from yourapp.main import main
                    try:
                        result = main(
                            uid=id,
                            body=body,
                        )
                    except Exception as e:
                        with open("/home/flask/app/output_files/{}.txt".format(id), mode="a", encoding="utf8") as f:
                            f.write("Error in main: {}".format(e))


                    # MongoDB
                    # result.modify(set__process_status = "FINISHED", set__processed_body = json.dumps(result))

                    # MySQL
                    cursor.execute("UPDATE document SET process_status = 'FINISHED', processed_body = %s WHERE id = %s;", (json.dumps(result), id))
                    conn.commit()
                    success = True
            else:
                print("unable to get document {} .".format(id))
                success = False
        except Exception as e:
            pass
            with open("/home/flask/app/output_files/{}.txt".format(id), mode="a", encoding="utf8") as f:
                f.write("\n")
                f.write(str(e))
            success = False
        finally:
            pass
        return success

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

# Get a document
@yourapp.route('/get', methods = ["POST"])
def get_doc():
    req = request.get_json()
    res = {
        "error": "Some error on /status"
    }

    id = req['id']
    
    # # MongoDB
    # connect_db()
    # result = EDocuments.objects.with_id(id)
    # body = result.body

    # MySQL
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT process_status, body, processed_body FROM document WHERE id = %s;", (id))
    result = cursor.fetchall()

    if len(result) == 0:
        return jsonify({
            "status": "FALED",
            "exist": False,
            "success": False,
            "processed_text": "",
            "body": "",
        })
    else:
        body = result[0]
        return jsonify({
            "status": "OK",
            "exist": True,
            "success": True if result[0][0] == "FINISHED" else False,
            "processed_text": result[0][2],
            "body": result[0][1],
        })

@yourapp.route('/new', methods = ["POST"])
def new_file():
    req = request.get_json()
    res = {}
    res["success"] = False

    inputContent = request.form.get('textline')
    inputContent = inputContent.strip()

    if inputContent == '':
        logging.warn('No text in request')
        
        return make_response(jsonify({
            'status': 'FAILED',
            'msg': 'No text in in request'
        }), 502)
    else:
        # Generate Hash
        processedContent = inputContent
        hashId = genHash(processedContent)

        cursor = None
        cur = None
        job_id = ""
        with current_app.app_context():
            try:
                # # MongoDB
                # connect_db()
                # doc = EDocuments(body = processedContent)
                # doc.save()
                # insertID = doc.id

                # MySQL
                db = get_db()
                conn = db.connect()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO document (body) VALUES (%s);", (processedContent))
                conn.commit()
                insertID = cursor.lastrowid

            except Exception as e:
                # response with failure in case of any exception
                res["success"] = False
                logging.warn("Can't insert DB\n{}".format(e))
            else:
                # after successful insertion, process the text and response with the document ID.
                res["success"] = True
                res["id"] = insertID

                try:
                    redis_connection = get_redis_connection()
                    q = Queue(current_app.config['QUEUES'][0], connection=redis_connection)
                    job = q.enqueue(process_task, str(insertID))
                    job_id = job.get_id()
                    logging.warn("text processing queued with job ID: " + str(job_id))
                    logging.warn("Curr Queue: " + str(len(q)))
                except:
                    logging.warn("queue failed, process text in local thread")
                    process_success = process_task(insertID)
                    if(not process_success["status"]):
                        res["success"] = False

                return make_response(jsonify({
                    'status': 'OK',
                    'msg': 'Record inserted.',
                    'hash': hashId,
                    'id': insertID,
                    "task_id": job_id
                }))
            finally:
                # # MongoDB
                # close_db()

                # MySQL
                if cursor is not None:
                    cursor.close()

        return make_response(jsonify({
            'status': 'FAILED',
            'msg': 'No file attached in request'
        }), 502)

    return make_response(jsonify({
        'status': 'FAILED',
        'msg': 'POST method is preferred.'
    }), 502)
