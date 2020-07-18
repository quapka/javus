# TODO split stages to development and release
FROM ubuntu:18.04 AS ub

# instal project dependencies
RUN apt-get update && apt-get install --yes \
    # FIXME possibly not needed: swig3.0 \
    swig \
    # FIXME possibly not needed: python3-swiglpk \
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
    openjdk-8-jdk-headless \
    openjdk-8-jre-headless \
    maven \
    mongodb

RUN pip3 install pipenv

# prepare GlobalPlatformPro
# RUN mkdir /dependencies
# WORKDIR /dependencies
# RUN git clone https://github.com/martinpaljak/GlobalPlatformPro
# WORKDIR /dependencies/GlobalPlatformPro
# # NOTE: we are using older version of GlobalPlatformPro, because we
# # depend on the --dump commang line flag
# RUN git checkout git checkout 2d4bb36c145bd8c13606f12aa14e6e29d8ecef78
# RUN ./mvn package
# This command is for the newest version of GlobalPlatformPro
# RUN ./mvnw package

# update the IP address MongoDB listens on to Docker IP
RUN sed --in-place 's/^bind_ip = 127.0.0.1$/bind_ip = 172.17.0.1/' /etc/mongodb.conf
RUN cat /etc/mongodb.conf

# document port for the viewer part of the application
EXPOSE 80/tcp
EXPOSE 27017/tcp

# # start SmartCard daemon
# RUN service pcscd start

# install Python dependencies
# set locales to silent Pipenv errors 
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN mkdir /javus
COPY Pipfile /javus/Pipfile
COPY Pipfile.lock /javus/Pipfile.lock
WORKDIR /javus
# dependencies
RUN pipenv install --system --deploy --ignore-pipfile

COPY . /javus
WORKDIR /javus
RUN pipenv install --dev .

# build the required submodules
RUN git submodule update --init --recursive --jobs 8
WORKDIR /javus/submodules/GlobalPlatformPro
# GlobalPlatformPro is currently fixed to one particular version,
# we need the `--dump` flag
RUN git checkout 2d4bb36c145bd8c13606f12aa14e6e29d8ecef78 && mvn package

WORKDIR /javus/submodules/ant-javacard
RUN ./mvnw package

ENV JCVM_ANALYSIS_HOME /javus
ENV FLASK_APP /javus/viewer.py

WORKDIR /javus
RUN chmod +x "bin/entrypoint-docker-javus.sh"
ENTRYPOINT ["bin/entrypoint-docker-javus.sh"]
