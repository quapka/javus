FROM python:3.6

ARG project_dir=/jsec

COPY . $project_dir
WORKDIR $project_dir
ENV JCVM_ANALYSIS_HOME $project_dir

RUN apt-get update && apt-get install --yes \
    swig3.0 \
    swig \
    python3-swiglpk \
    libpcsclite-dev

# for installing project dependencies we need Pipenv
RUN pip install pipenv
# install project dependencies
RUN pipenv install --system --deploy --ignore-pipfile
# install the actual executable
RUN pipenv install .

EXPOSE 5000
ENTRYPOINT ["pipenv", "run", "python", "scripts/jsec"]
