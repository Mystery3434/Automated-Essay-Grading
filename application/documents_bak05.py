from application.conversion.parser import main as parser
from application.database import get_db
from flask import Blueprint, request, current_app, jsonify, json, g, make_response
from flask_cors import CORS, cross_origin

import ast
import os
import redis
from rq import Queue, Connection
import hashlib
import time
import json
import logging
from datetime import datetime
from application.redis_worker import get_worker_pipeline
from application.redis_connection import get_redis_connection

documents = Blueprint('documents', __name__,
                        template_folder='templates')

def genHash(content):
    # Generate Hash
    # m = hashlib.sha256()
    m = hashlib.md5()
    m.update(content.encode('utf-8'))
    return m.hexdigest()

def queue_convert_doc(res, processedContent, submission_id, hashId, user_id, filename="", filepath="", prompt ="", facts=""):
    cursor = None
    cur = None
    job_id = ""
    insertID = ""

    # 1. New entry in table `document`, record the status of a) conversion file or b) process_analysis

    if filename == "" and filepath == "":
        # Text
        pass
    else:
        # File
        pass

    with current_app.app_context():
        try:
            # MySQL
            db = get_db()
            conn = db.connect()
            cursor = conn.cursor()
            if filename == "" and filepath == "":
                # Text
                cursor.execute("INSERT INTO document (body, submission_id, uuid, prompt, facts) VALUES (%s, %s, %s, %s, %s);", (processedContent, submission_id, hashId, prompt, facts))
            else:
                # File
                cursor.execute("INSERT INTO document (body, submission_id, uuid, filename, filepath, prompt, facts) VALUES (%s, %s, %s, %s, %s, %s, %s);", ("", submission_id, hashId, filename, filepath, prompt, facts))
            # Submission by User
            cursor.execute("INSERT INTO user_tasks (user_id, submission_id, uuid) VALUES (%s, %s, %s);", (user_id, submission_id, hashId))
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
                q = Queue(current_app.config['QUEUES'][1], connection=redis_connection)
                job = {}
                if filename == "" and filepath == "":
                    # Text
                    job = q.enqueue(process_analysis, str(insertID), hashId, submission_id)
                else:
                    # File
                    job = q.enqueue(process_convert, str(insertID), hashId, submission_id, filename, filepath)
                job_id = job.get_id()
                logging.warn("text processing queued with job ID: " + str(job_id))
                logging.warn(f"Curr {current_app.config['QUEUES'][1]} Queue: " + str(len(q)))
            except:
                logging.warn("queue failed, process text in local thread")
                # process_success = process_convert(insertID)
                # if(not process_success["status"]):
                #     res["success"] = False
        finally:
            # MySQL
            if cursor is not None:
                cursor.close()

        # Default return
        return make_response(jsonify({
            'status': 'OK',
            'msg': 'Record inserted.',
            'uuid': hashId,
            'id': insertID,
            "task_id": job_id,
            'submission_id': submission_id,
        }))

# tika
# parser
def process_convert(id, uuid, submission_id, filename="", filepath=""):
    cur = None
    db = None
    with current_app.app_context():
        try:
            logging.warn("processing document {}.".format(id))

            # MySQL
            db = get_db()
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT process_status, body FROM document WHERE uuid = %s;", (uuid))
            result = cursor.fetchall()
            body = result[0][1]

            if True or len(body) > 0:

                if False and body["process_status"] == "FINISHED":
                    logging.warn("document {} already processed.".format(uuid))
                    success = True
                else:
                    # MySQL
                    cursor.execute("UPDATE document SET process_status = 'PROCESSING' WHERE uuid = %s;", (uuid))
                    cursor.execute("UPDATE user_tasks SET process_status = 'PROCESSING' WHERE uuid = %s;", (uuid))
                    conn.commit()

                    result = ""
                    # Import parser
                    try:
                        result = parser(
                            filename=filename,
                            filepath=filepath,
                            newname=filename+"_converted",
                        )
                    except Exception as e:
                        with open("/home/flask/app/output_files/{}-{}.txt".format(id, uuid), mode="a", encoding="utf8") as f:
                            f.write("Error in main: {}".format(e))

                    # MySQL
                    cursor.execute("UPDATE document SET process_status = 'CONVERRTED', processed_body = %s WHERE uuid = %s;", (json.dumps(result), uuid))
                    cursor.execute("UPDATE user_tasks SET process_status = 'CONVERRTED' WHERE uuid = %s;", (uuid))
                    conn.commit()
                    success = True

                    insertID = id
                    try:
                        redis_connection = get_redis_connection()
                        q = Queue(current_app.config['QUEUES'][0], connection=redis_connection)
                        job = q.enqueue(process_analysis, str(insertID), uuid, submission_id)
                        job_id = job.get_id()
                        logging.warn("text processing queued with job ID: " + str(job_id))
                        logging.warn(f"Curr {current_app.config['QUEUES'][0]} Queue: " + str(len(q)))
                    except Exception as e:
                        logging.warn(f"queue failed, process text in local thread\n{e}")
                        # process_success = process_analysis(insertID)
                        # if(not process_success["status"]):
                        #     res["success"] = False

            else:
                print("unable to get document {} .".format(id))
                success = False
        except Exception as e:
            pass
            with open("/home/flask/app/output_files/{}-{}.txt".format(id, uuid), mode="a", encoding="utf8") as f:
                f.write("\n")
                f.write(str(e))
            success = False
        finally:
            pass
        return success

# backend method to process a single text with the nltk pos tagger given a id
# yourapp
def process_analysis(id, uuid, submission_id=""):
    cur = None
    db = None
    with open("/home/flask/app/output_files/{}-{}.txt".format(id, uuid), mode="a", encoding="utf8") as f:
        f.write("test in main: {}===>OK 1".format(id))
    with current_app.app_context():
        try:
            logging.warn("processing document {}.".format(id))

            # MySQL
            db = get_db()
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT process_status, processed_body, submission_id, prompt, facts FROM document WHERE uuid = %s;", (uuid))
            result = cursor.fetchall()
            body = result[0][1]
            prompt = result[0][3]
            facts_string = result[0][4]
            facts_list = ast.literal_eval(facts_string)
            facts = [entry["value"] for entry in facts_list]

            success = False

            if True or len(body) > 0:

                if False and body["process_status"] == "FINISHED":
                    logging.warn("document {} already processed.".format(id))
                    success = True
                else:
                    # MySQL
                    cursor.execute("UPDATE document SET process_status = 'PROCESSING' WHERE uuid = %s;", (uuid))
                    cursor.execute("UPDATE user_tasks SET process_status = 'PROCESSING' WHERE uuid = %s;", (uuid))
                    conn.commit()

                    result = {}
                    # Import yourapp
                    from yourapp.main import main
                    try:
                        result = main(
                            id=id,
                            uuid=uuid,
                            body=body,
                            prompt = prompt,
                            facts = facts
                        )
                    except Exception as e:
                        with open("/home/flask/app/output_files/{}-{}.txt".format(id, uuid), mode="a", encoding="utf8") as f:
                            f.write("Error in main: {}".format(e))

                    with open("/home/flask/app/output_files/{}-{}.txt".format(id, uuid), mode="a", encoding="utf8") as f:
                        f.write("\n\ntest in main: {}===>OK 3".format(json.dumps(result)))

                    try:
                        # MySQL
                        cursor.execute("UPDATE document SET process_status = 'FINISHED', processed_body = %s WHERE uuid = %s;", (json.dumps(result), uuid))
                        cursor.execute("UPDATE user_tasks SET process_status = 'FINISHED' WHERE uuid = %s;", (uuid))
                        process_status = "FINISHED"
                        length_by_sentence = 0 # result["processed_body"]["length_by_sentence"]
                        length_by_distinct_token = 0 # result["processed_body"]["length_by_distinct_token"]
                        length_by_word = 0 # result["processed_body"]["length_by_word"]
                        length_by_character = 0 # result["processed_body"]["length_by_character"]
                        lexical_diversity = 0 # result["processed_body"]["lexical_diversity"]
                        data_by_sentence = '{}' # result["processed_body"]["data_by_sentence"]
                        data_by_fdist = '{}' # result["processed_body"]["data_by_fdist"]
                        wordfrequency_all = result["processed_body"]["wordfrequency_all"]
                        wordfrequency_content = result["processed_body"]["wordfrequency_content"]
                        wordfrequency_function = result["processed_body"]["wordfrequency_function"]
                        wordrangescore = result["processed_body"]["wordrangescore"]
                        academicwordscore = result["processed_body"]["academicwordscore"]
                        academic_sublists_score = 0 # result["processed_body"]["academic_sublists_score"]
                        familiarityscore = result["processed_body"]["familiarityscore"]
                        concretenessscore = result["processed_body"]["concretenessscore"]
                        imagabilityscore = result["processed_body"]["imagabilityscore"]
                        meaningfulnesscscore = result["processed_body"]["meaningfulnesscscore"]
                        meaningfulnesspscore = result["processed_body"]["meaningfulnesspscore"]
                        ageofacquisitionscore = result["processed_body"]["ageofacquisitionscore"]
                        grammar_errorrate = 0 # result["processed_body"]["grammar_errorrate"]
                        flesch_reading_ease = result["processed_body"]["flesch_reading_ease"]
                        flesch_kincaid_grade_level = result["processed_body"]["flesch_kincaid_grade_level"]
                        smog = result["processed_body"]["smog"]
                        coleman_liau = result["processed_body"]["coleman_liau"]
                        ari = result["processed_body"]["ari"]
                        semanticoverlap = result["processed_body"]["semanticoverlap"]
                        typetokenratio = 0 # json.dumps(result["processed_body"]["typetokenratio"])
                        holistic_score = result["processed_body"]["holistic_score"]
                        cursor.execute("INSERT INTO tbl_submit_document_stat (submission_id, uuid, process_status, length_by_sentence, length_by_distinct_token, length_by_word, length_by_character, lexical_diversity, data_by_sentence, data_by_fdist, wordfrequency_all, wordfrequency_content, wordfrequency_function, wordrangescore, academicwordscore, academic_sublists_score, familiarityscore, concretenessscore, imagabilityscore, meaningfulnesscscore, meaningfulnesspscore, ageofacquisitionscore, grammar_errorrate, flesch_reading_ease, flesch_kincaid_grade_level, smog, coleman_liau, ari, semanticoverlap, typetokenratio, holistic_score) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (
                            submission_id,
                            uuid,
                            process_status,
                            length_by_sentence,
                            length_by_distinct_token,
                            length_by_word,
                            length_by_character,
                            lexical_diversity,
                            data_by_sentence,
                            data_by_fdist,
                            wordfrequency_all,
                            wordfrequency_content,
                            wordfrequency_function,
                            wordrangescore,
                            academicwordscore,
                            academic_sublists_score,
                            familiarityscore,
                            concretenessscore,
                            imagabilityscore,
                            meaningfulnesscscore,
                            meaningfulnesspscore,
                            ageofacquisitionscore,
                            grammar_errorrate,
                            flesch_reading_ease,
                            flesch_kincaid_grade_level,
                            smog,
                            coleman_liau,
                            ari,
                            semanticoverlap,
                            typetokenratio,
                            holistic_score,
                        ))
                        conn.commit()
                        success = True
                    except Exception as e:
                        with open("/home/flask/app/output_files/{}-{}.txt".format(id, uuid), mode="a", encoding="utf8") as f:
                            f.write("\n\ntest in main: {}===>Error DB".format(e))
            else:
                print("unable to get document {} .".format(id))
                success = False
        except Exception as e:
            with open("/home/flask/app/output_files/{}-{}.txt".format(id, uuid), mode="a", encoding="utf8") as f:
                f.write("\n")
                f.write(str(e))
            success = False
        finally:
            with open("/home/flask/app/output_files/{}-{}.txt".format(id, uuid), mode="a", encoding="utf8") as f:
                f.write("\n\ntest in main: {}===>OK Finally".format(""))
            pass
        return success

# For testing of the queue_convert_doc function
@documents.route('/', methods = ["GET", "POST"])
def testing():
    req = request.get_json()
    res = main(
        uid="1",
        body="demo",
    )
    return jsonify({"success":json.loads(res)})

# Queue Status
@documents.route('/status', methods = ["GET"])
@cross_origin()
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
@documents.route('/get', methods = ["GET", "POST"])
@cross_origin()
def get_doc():
    id = ""
    uuid = ""
    if request.method == 'GET':
        uuid = request.args.get('uuid')

    req = request.get_json()
    res = {
        "error": "Some error on /status"
    }

    if req:
        id = req['submission_id']
        if 'uuid' in req.keys():
            uuid = req['uuid']

    # MySQL
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT process_status, body, processed_body FROM document WHERE submission_id = %s OR uuid = %s;", (id, uuid))
    result = cursor.fetchall()

    if len(result) == 0:
        return jsonify({
            "status": "FALED",
            "exist": False,
            "success": False,
            "result": "",
        })
    else:
        if result[0][0] != "FINISHED":
            # still waiting
            return jsonify({
                "status": "OK",
                "exist": True,
                "success": True if result[0][0] == "FINISHED" else False,
                "result": result[0][1],
            })
        else:
            #body = result[0]
            cursor = conn.cursor()
            cursor.execute("SELECT process_status, submission_id, length_by_sentence, length_by_distinct_token, length_by_word, length_by_character, lexical_diversity, data_by_sentence, data_by_fdist, wordfrequency_all, wordfrequency_content, wordfrequency_function, wordrangescore, academicwordscore, academic_sublists_score, familiarityscore, concretenessscore, imagabilityscore, meaningfulnesscscore, meaningfulnesspscore, ageofacquisitionscore, grammar_errorrate, flesch_reading_ease, flesch_kincaid_grade_level, smog, coleman_liau, ari, semanticoverlap, typetokenratio, holistic_score FROM tbl_submit_document_stat WHERE submission_id = %s OR uuid = %s;", (id, uuid))
            result2 = cursor.fetchall()

            dict_result = [
                {
                    "process_status": row[0],
                    "submission_id": row[1],
                    "length_by_sentence": row[2],
                    "length_by_distinct_token": row[3],
                    "length_by_word": row[4],
                    "length_by_character": row[5],
                    "lexical_diversity": row[6],
                    "data_by_sentence": row[7],
                    "data_by_fdist": row[8],
                    "wordfrequency_all": row[9],
                    "wordfrequency_content": row[10],
                    "wordfrequency_function": row[11],
                    "wordrangescore": row[12],
                    "academicwordscore": row[13],
                    "academic_sublists_score": row[14],
                    "familiarityscore": row[15],
                    "concretenessscore": row[16],
                    "imagabilityscore": row[17],
                    "meaningfulnesscscore": row[18],
                    "meaningfulnesspscore": row[19],
                    "ageofacquisitionscore": row[20],
                    "grammar_errorrate": row[21],
                    "flesch_reading_ease": row[22],
                    "flesch_kincaid_grade_level": row[23],
                    "smog": row[24],
                    "coleman_liau": row[25],
                    "ari": row[26],
                    "semanticoverlap": row[27],
                    "typetokenratio": row[28],
                    "holistic_score": row[29],
                }
                for row in result2
            ]

            return jsonify({
                "status": "OK",
                "exist": True,
                "success": True,
                "result": dict_result,
            })

            # return jsonify({
            #     "status": "OK",
            #     "exist": True,
            #     "success": True,
            #     "processed_text": json.dumps(result2),
            #     "body": "",
            # })

# Get a user
# PATH: /documents/get_user?user_id=23456
@documents.route('/get_user', methods = ["GET", "POST"])
@cross_origin()
def get_user():

    req = request.get_json()
    res = {
        "error": "Some error on /status"
    }

    id = request.args.get('user_id')

    # MySQL
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()

    # Object of type 'datetime' is not JSON serializable
    if id:
        cursor.execute("SELECT id, submission_id, user_id, uuid, process_status, created FROM user_tasks WHERE user_id = %s;", (id))
    else:
        cursor.execute("SELECT id, submission_id, user_id, uuid, process_status, created FROM user_tasks;")
    result = cursor.fetchall()

    dict_result = [
        {
            "id": row[0],
            "submission_id": row[1],
            "user_id": row[2],
            "uuid": row[3],
            "process_status": row[4],
            "created": str(row[5]),
        }
        for row in result
    ]

    return jsonify(dict_result)

    # return jsonify({
    #     "status": "OK",
    #     "exist": True,
    #     "success": True,
    #     "user_id": id,
    #     "body": json.dumps(result),
    # })

@documents.route('/new', methods = ["POST", "GET"])
@cross_origin()
def new_file():
    req = request.get_json()
    res = {}
    res["success"] = False

    if request.method == 'POST':
        submission_id = request.form.get('submission_id')
        user_id = request.form.get('user_id')
        prompt = request.form.get('prompt')
        facts = request.form.get('facts')

        if 'file' not in request.files:
            print('No file attached in request')
            # Try text:
            inputContent = request.form.get('textline')
            inputContent = inputContent.strip()

            # No text either:
            if inputContent == '' or len(submission_id) == 0:
                print('No text in request')
                return make_response(jsonify({
                    'status': 'FAILED',
                    'msg': 'No text in in request or no submission_id'
                }), 502)

            # Prepare to Queue Conversion
            processedContent = inputContent
            hashId = genHash(processedContent)
            return queue_convert_doc(res, processedContent, submission_id, hashId, user_id, prompt, facts)

        # Trying File:
        file0 = request.files['file']
        if file0.filename == '':
            print('No file selected')
            return make_response(jsonify({
                'status': 'FAILED',
                'msg': 'No file selected'
            }), 502)

        if file0:
            filename = file0.filename
            filepath = ""
            try:
                filepath = os.path.join('/home/flask/app/output_files/', filename)
                file0.save(filepath)
            except Exception as e:
                logging.warn(f'write file error: \n{e}')

            # # File conversion
            # newname = main(os.path.join('./', filename))
            # inputContent = ""
            # with open(newname, 'r', encoding='utf8') as f:
            #     inputContent = f.read().strip()

            # Prepare to Queue Conversion
            # processedContent = inputContent
            # hashId = genHash(processedContent)
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            hashId = genHash(f'{filename}_{timestamp}')
            return queue_convert_doc(res, "", submission_id, hashId, user_id, filename=filename, filepath=filepath, prompt = prompt, facts = facts)

    # Not a POST request
    return make_response(jsonify({
        'status': 'FAILED',
        'msg': 'POST method is preferred.'
    }), 502)
