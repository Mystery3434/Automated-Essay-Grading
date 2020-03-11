FROM python:3.6.10-buster

# Create the group and user to be used in this container
RUN groupadd flaskgroup && useradd -m -g flaskgroup -s /bin/bash flask

# Create the working directory (and set it as the working directory)
RUN mkdir -p /home/flask/app/application
WORKDIR /home/flask/app

# Install the package dependencies (this step is separated
# from copying all the source code to avoid having to
# re-install all python packages defined in requirements.txt
# whenever any source code change is made)
COPY requirements.txt /home/flask/app
RUN pip3 install --no-cache-dir -r requirements.txt


# Copy the supervisor config for starting background workers
COPY ./supervisord.conf /home/flask/app/

# Copy the source code into the container
RUN chown -R flask:flaskgroup /home/flask

COPY ./application /home/flask/app/application
RUN chown -R flask:flaskgroup /home/flask/app/application

COPY ./instance /home/flask/app/instance
RUN chown -R flask:flaskgroup /home/flask/app/instance

COPY ./output_files /home/flask/app/output_files
RUN chown -R flask:flaskgroup /home/flask/app/output_files

# You main app
COPY ./yourapp /home/flask/app/yourapp
RUN chown -R flask:flaskgroup /home/flask/app/yourapp

USER flask
