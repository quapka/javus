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

# document port for the viewer part of the application
EXPOSE 80/tcp
EXPOSE 27017/tcp

# set locales to silent Pipenv errors 
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN mkdir /javus
RUN mkdir /registry

COPY . /javus
WORKDIR /javus

# using pipenv in Docker takes forever to then build the image
# this is not ideal, as requirements.txt will get update
# FIXME make sure requirements.txt are up to date
RUN pip3 install --requirement requirements.txt
# not using --editable install the package system-wide
# which was cause of troubles, this could be debugged more
RUN pip3 install --editable .

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
