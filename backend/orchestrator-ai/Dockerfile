FROM tiangolo/uvicorn-gunicorn:python3.10

ARG API_NAME=orchestrator-ai
ARG ML_MODEL_RELEASE=master
ARG WORK_DIR=/opt/apis
ARG REQUIREMENTS_FILE=requirements.txt

ENV PYTHONPATH=${WORK_DIR}/${API_NAME}
ENV API_NAME_DIR=${WORK_DIR}/${API_NAME}

WORKDIR ${WORK_DIR}

# For python slim versions
# RUN apt update && \
#     apt install -y \
#     gcc \
#     openssh-client \
#     gcc \
#     git \
#     && apt clean

RUN env

RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh && \
    ssh-keyscan bitbucket.org > /root/.ssh/known_hosts

RUN mkdir ./${API_NAME}

# Copy project structure
COPY api/ ./${API_NAME}/api/
COPY ${REQUIREMENTS_FILE} ./${API_NAME}/

RUN pip install --no-cache -r ./${API_NAME}/${REQUIREMENTS_FILE}

EXPOSE 80

CMD uvicorn --app-dir $API_NAME_DIR/api app:app --host 0.0.0.0 --port 80 --backlog 4096 --no-access-log --workers 2 --no-server-header
