# TODO split stages to development and release
FROM ubuntu:18.04 AS ub

# instal project dependencies
RUN apt-get update && apt-get install --yes \
    swig3.0 \
    swig \
    python3-swiglpk \
    libpcsclite-dev \
    # smartcard deamon
    pcscd \
    # install pkcs11-tool - only for development
    opensc \
    ant \
    ant-contrib \
    software-properties-common \
    python3-pip \
    git \
    openjdk-8-jdk \
    mongodb

RUN pip3 install pipenv

# prepare GlobalPlatformPro
RUN mkdir /dependencies
WORKDIR /dependencies
RUN git clone https://github.com/martinpaljak/GlobalPlatformPro
WORKDIR /dependencies/GlobalPlatformPro
RUN ./mvnw package

# update the IP address MongoDB listens on to Docker IP
RUN sed --in-place 's/^bind_ip = 127.0.0.1$/bind_ip = 172.17.0.1/' /etc/mongodb.conf
RUN cat /etc/mongodb.conf

# document port for the viewer part of the application
EXPOSE 80/tcp
EXPOSE 27017/tcp

# start SmartCard daemon
RUN service pcscd start

# install Python dependencies
# set locales to silent Pipenv errors 
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN mkdir /jsec
COPY Pipfile /jsec/Pipfile
COPY Pipfile.lock /jsec/Pipfile.lock
WORKDIR /jsec
# dependencies
RUN pipenv install --system --deploy --ignore-pipfile

COPY . /jsec
WORKDIR /jsec
RUN pipenv install .
RUN git submodule update --init --recursive --jobs 8

ENV JCVM_ANALYSIS_HOME /jsec
ENV FLASK_APP /jsec/viewer.py

# set final working directory
# prepare the entry point
RUN chmod +x "bin/entrypoint-docker-jsec.sh"
ENTRYPOINT ["bin/entrypoint-docker-jsec.sh"]


##############################################

#FROM openjdk:8 as jb

#ARG project_dir=/jsec

#COPY . /jsec
#WORKDIR /jsec
#ENV JCVM_ANALYSIS_HOME /jsec

#RUN apt purge python2. --yes
## TODO add && ? between packages
#RUN apt-get update && apt-get install --yes \
#    swig3.0 \
#    swig \
#    python3-swiglpk \
#    libpcsclite-dev \
#    # smartcard deamon
#    pcscd \
#    # install pkcs11-tool - only for development
#    opensc \
#    ant \
#    ant-contrib \
#    software-properties-common \
#    python3 \
#    python3-pip


## RUN add-apt-repository ppa:openjdk-r/ppa


## RUN systemctl enable pcscd.service
## RUN systemctl start pcscd.service 
## RUN systemctl status pcscd.service
## for installing project dependencies we need Pipenv
#RUN pip3 install pipenv
## install project dependencies
#RUN pipenv --python /usr/bin/python3.6 install --system --deploy --ignore-pipfile
## install the actual executable
#RUN pipenv --python /usr/bin/python3.6 install .

#EXPOSE 5000
## ENTRYPOINT ["pipenv", "run", "python", "scripts/jsec"]
#RUN chmod +x "bin/entrypoint-docker-jsec.sh"
#ENTRYPOINT ["bin/entrypoint-docker-jsec.sh"]

######################

## split stages to development and release
#FROM python:3.6 AS pb

#ARG project_dir=/jsec

#COPY . /jsec
#WORKDIR /jsec
#ENV JCVM_ANALYSIS_HOME /jsec

#RUN apt-get update && apt-get install --yes \
#    swig3.0 \
#    swig \
#    python3-swiglpk \
#    libpcsclite-dev \
#    # smartcard deamon
#    pcscd \
#    # install pkcs11-tool - only for development
#    opensc \
#    ant \
#    ant-contrib \
#    software-properties-common

#RUN add-apt-repository ppa:openjdk-r/ppa


## RUN systemctl enable pcscd.service
## RUN systemctl start pcscd.service 
## RUN systemctl status pcscd.service
## for installing project dependencies we need Pipenv
#RUN pip install pipenv
## install project dependencies
#RUN pipenv install --system --deploy --ignore-pipfile
## install the actual executable
#RUN pipenv install .

#EXPOSE 5000
## ENTRYPOINT ["pipenv", "run", "python", "scripts/jsec"]
#RUN chmod +x "bin/entrypoint-docker-jsec.sh"
#ENTRYPOINT ["bin/entrypoint-docker-jsec.sh"]


