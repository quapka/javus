# split stages to development and release
FROM ubuntu:18.04 AS ub

ARG project_dir=/jsec

COPY . $project_dir
WORKDIR $project_dir
ENV JCVM_ANALYSIS_HOME $project_dir

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
    openjdk-8-jdk

RUN add-apt-repository ppa:openjdk-r/ppa
# pipenv issues
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN service pcscd start
# RUN service pcscd status

# TODO git init submodule oracle_javacard_sdks
# RUN systemctl enable pcscd.service
# RUN systemctl start pcscd.service 
# RUN systemctl status pcscd.service
# for installing project dependencies we need Pipenv
RUN pip3 install pipenv
# # install project dependencies
RUN pipenv install --system --deploy --ignore-pipfile
# # install the actual executable
RUN pipenv install .
# RUN pipenv run python -c 'from smartcard.System import readers; print(readers())'
# setup GlobalPlatformPro
RUN git clone https://github.com/martinpaljak/GlobalPlatformPro
WORKDIR /
WORKDIR GlobalPlatformPro
RUN ./mvnw package

EXPOSE 5000
# ENTRYPOINT ["pipenv", "run", "python", "scripts/jsec"]
RUN chmod +x "bin/entrypoint-docker-jsec.sh"
ENTRYPOINT ["bin/entrypoint-docker-jsec.sh"]


#############################################

FROM openjdk:8 as jb

ARG project_dir=/jsec

COPY . $project_dir
WORKDIR $project_dir
ENV JCVM_ANALYSIS_HOME $project_dir

RUN apt purge python2. --yes
# TODO add && ? between packages
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
    python3 \
    python3-pip


# RUN add-apt-repository ppa:openjdk-r/ppa


# RUN systemctl enable pcscd.service
# RUN systemctl start pcscd.service 
# RUN systemctl status pcscd.service
# for installing project dependencies we need Pipenv
RUN pip3 install pipenv
# install project dependencies
RUN pipenv --python /usr/bin/python3.6 install --system --deploy --ignore-pipfile
# install the actual executable
RUN pipenv --python /usr/bin/python3.6 install .

EXPOSE 5000
# ENTRYPOINT ["pipenv", "run", "python", "scripts/jsec"]
RUN chmod +x "bin/entrypoint-docker-jsec.sh"
ENTRYPOINT ["bin/entrypoint-docker-jsec.sh"]

#####################

# split stages to development and release
FROM python:3.6 AS pb

ARG project_dir=/jsec

COPY . $project_dir
WORKDIR $project_dir
ENV JCVM_ANALYSIS_HOME $project_dir

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
    software-properties-common

RUN add-apt-repository ppa:openjdk-r/ppa


# RUN systemctl enable pcscd.service
# RUN systemctl start pcscd.service 
# RUN systemctl status pcscd.service
# for installing project dependencies we need Pipenv
RUN pip install pipenv
# install project dependencies
RUN pipenv install --system --deploy --ignore-pipfile
# install the actual executable
RUN pipenv install .

EXPOSE 5000
# ENTRYPOINT ["pipenv", "run", "python", "scripts/jsec"]
RUN chmod +x "bin/entrypoint-docker-jsec.sh"
ENTRYPOINT ["bin/entrypoint-docker-jsec.sh"]


