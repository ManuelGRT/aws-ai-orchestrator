FROM tiangolo/uvicorn-gunicorn:python3.10

ARG API_NAME=upscaling-ai
ARG WORK_DIR=/opt/apis
ARG REQUIREMENTS_FILE=requirements.txt

ENV PYTHONPATH=${WORK_DIR}/${API_NAME}
ENV API_NAME_DIR=${WORK_DIR}/${API_NAME}

WORKDIR ${WORK_DIR}

# 🔧 System dependencies for NCNN/Vulkan
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    libvulkan1 libomp5 ca-certificates \
    # Add these for OpenCV if headless doesn't resolve everything:
    libgl1 libglib2.0-0 libsm6 libxrender1 libxext6 \
 && rm -rf /var/lib/apt/lists/*

# (Only needed if cloning during build)
RUN mkdir -p /root/.ssh && chmod 0700 /root/.ssh && \
    ssh-keyscan bitbucket.org > /root/.ssh/known_hosts

RUN mkdir -p ${API_NAME}

# 📦 Install OpenCV headless FIRST - CRITICAL STEP
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "opencv-python-headless==4.10.0.84"

# 📦 Copy and install requirements
COPY api/ ./${API_NAME}/api/
COPY ${REQUIREMENTS_FILE} ./${API_NAME}/

RUN apt-get update && apt-get install -y --no-install-recommends \
    libvulkan1 mesa-vulkan-drivers libomp5 ca-certificates \
 && rm -rf /var/lib/apt/lists/*

 RUN pip install --no-cache-dir -r ./${API_NAME}/${REQUIREMENTS_FILE}

EXPOSE 80

# 🧠 1 worker per container; scale replicas in ECS
CMD uvicorn --app-dir $API_NAME_DIR/api app:app --host 0.0.0.0 --port 80 --backlog 4096 --no-access-log --workers 1 --no-server-header