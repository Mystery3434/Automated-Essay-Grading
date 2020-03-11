## Setup
  

To run the server, set up virtual environment with the requirements from requirements.txt.

You may also build a docker image for the server using the provided DOCKERFILE

  

### Redis

The server uses Redis (with RQ) to manage background text processing tasks. To for this to work, install and run the server in localhost with the default port (6379). If no Redis server is running, text processing still works but will be slower.

### Config
Some basic setting can be edited in instance/config.py
```
SECRET_KEY='dev'# secret key used in flask, change this to a randomised value for production usage
REDIS_URL = 'redis://' # url for the Redis Server
QUEUES = ['default'] # list of queue names used by rq workers, only first queue will be used by the app itself.
```
## Running the server

### Basic

You may either use  **run_server.bat** or **run_server.sh** after entering your virtual environment. The server will be hosted on port 5000.

### GUnicorn

You may also use wsgi.py with GUnicorn to start the server using the following command.
The server will be hosted on port 8001.
```

gunicorn -w 8 -b :8001 wsgi:app

```
### Background Workers
To utilize the background workers, make sure that a Redis server is running, by default, the worker will attempt to connect to `redis://redis:6379` if you are hosting the redis server on localhost (or other location), please edit it to `redis://` (or other location) in the **instance/config.py** file

Afterwards, start a worker which will preload the processing pipeline and model, in order to perform the text processing. 

Note that to use a Flask Command, you must set the enviroment variable `FLASK_APP=application` first, for windows: `set FLASK_APP=application`, for linux: `export FLASK_APP=application`
```
flask run-worker

```

you may also run the following command at the base directory to start multiple workers at once. WORKER_COUNT can be modified to change the number of workers to run.
```
export WORKER_COUNT=3  # use "set WORKER_COUNT=3" for windows
supervisord -n
```

If no Redis server is running, text processing still works, but will be slower.
  

### Docker-compose

To directly start the whole server arrangement using docker, you may directly use `docker-compose up` on the base directory. The server will be hosted on port 8001.

the **docker-compose.yaml** file provided are for independent running of the pos tagger web app. To integrate this into the full demo, you may need to copy some of it into the full docker-compose.yaml.  I am unable to test the full setup as of yet.
