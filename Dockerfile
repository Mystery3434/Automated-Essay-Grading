FROM nvidia/cuda:10.2-base-ubuntu18.04 

# Install "software-properties-common" (for the "add-apt-repository")
RUN apt update && apt install -y software-properties-common
RUN apt -y install curl dirmngr apt-transport-https lsb-release ca-certificates
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list

# Install Nodejs-12 and OpenJDK-8
RUN apt install -y nodejs openjdk-8-jre build-essential python3.6 python3.6-dev python3-pip python3.6-venv --fix-missing

# Fix certificate issues
RUN apt update && \
    apt install -y ca-certificates-java yarn && \
    apt clean && \
    update-ca-certificates -f;

# Setup JAVA_HOME -- useful for docker commandline
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME
RUN update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java

# Install CUDA
ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64:/usr/local/cuda-10.2/compat"
ENV CUDA_HOME=/usr/local/cuda

WORKDIR /
RUN curl -o /abc.deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-compat-10-2_440.64.00-1_amd64.deb
RUN apt install /abc.deb

COPY cudatoolkit.deb /
RUN dpkg -i /cudatoolkit.deb
RUN apt-key add /var/cuda-repo-10-0-local-10.0.130-410.48/7fa2af80.pub
RUN apt-get update
RUN apt-get -y install cuda

ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/cuda-10.2/targets/x86_64-linux/lib:/usr/lib/x86_64-linux-gnu:/usr/local/cuda-10.2/targets/x86_64-linux/lib/"

COPY ./cuda/include/cudnn.h /usr/local/cuda/include/
COPY ./cuda/lib64/libcudnn* /usr/local/cuda/lib64/
RUN chmod a+r /usr/local/cuda/include/cudnn.h /usr/local/cuda/lib64/libcudnn*

ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/cuda-10.0/targets/x86_64-linux/lib:/usr/lib/x86_64-linux-gnu:/usr/local/cuda-10.0/targets/x86_64-linux/lib/"

# Create the group and user to be used in this container
RUN groupadd flaskgroup && useradd -m -g flaskgroup -s /bin/bash flask

# Create the working directory (and set it as the working directory)
RUN mkdir -p /home/flask/app/application
WORKDIR /home/flask/app

# Install the package dependencies (this step is separated
# from copying all the source code to avoid having to
# re-install all python packages defined in requirements.txt
# whenever any source code change is made)
RUN pip3 install torch torchvision spacy
COPY requirements.txt /home/flask/app
RUN pip3 install --no-cache-dir -r requirements.txt
RUN python3 -m spacy download en_core_web_sm

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
