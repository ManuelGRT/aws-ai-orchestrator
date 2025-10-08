FROM tiangolo/uvicorn-gunicorn:python3.10

ARG API_NAME=inpainting-ai
ARG ML_MODEL_RELEASE=master
ARG WORK_DIR=/opt/apis
ARG REQUIREMENTS_FILE=requirements.txt

ENV PYTHONPATH=${WORK_DIR}/${API_NAME}
ENV API_NAME_DIR=${WORK_DIR}/${API_NAME}

WORKDIR ${WORK_DIR}

# Install system dependencies first
RUN apt-get update && \
    apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh && \
    ssh-keyscan bitbucket.org > /root/.ssh/known_hosts

RUN mkdir ./${API_NAME}

# Copy requirements first to leverage Docker cache
COPY ${REQUIREMENTS_FILE} ./${API_NAME}/

# Install Python dependencies in a single layer
RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir huggingface-hub==0.12.1 \
 && pip install --no-cache-dir diffusers==0.16.1 --no-deps \
 && pip install --no-cache-dir lama-cleaner==1.2.5 --no-deps


RUN pip install --no-cache-dir -r ./${API_NAME}/${REQUIREMENTS_FILE}

# Copy application code after installing dependencies
COPY api/ ./${API_NAME}/api/

EXPOSE 80

CMD uvicorn --app-dir $API_NAME_DIR/api app:app --host 0.0.0.0 --port 80 --backlog 4096 --no-access-log --workers 2 --no-server-header