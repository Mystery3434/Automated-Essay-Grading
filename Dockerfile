FROM python:3.6.10-buster

# Install "software-properties-common" (for the "add-apt-repository")
RUN apt-get update && apt-get install -y software-properties-common
RUN apt-get -y install curl dirmngr apt-transport-https lsb-release ca-certificates
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list

# Install Nodejs-12 and OpenJDK-8
RUN apt-get install -y nodejs default-jre

# Fix certificate issues
RUN apt-get update && \
    apt-get install -y ca-certificates-java yarn && \
    apt-get clean && \
    update-ca-certificates -f;

# Setup JAVA_HOME -- useful for docker commandline
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
RUN export JAVA_HOME

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

# Build Client
WORKDIR /home/flask/app/application/veriguide_dashboard_client
RUN ls
RUN rm -rf /home/flask/app/application/veriguide_dashboard_client/build/
RUN mkdir -p /home/flask/app/application/veriguide_dashboard_client/build/index

RUN yarn install
RUN yarn build --output-path=build/index

WORKDIR /home/flask/app

USER flask
