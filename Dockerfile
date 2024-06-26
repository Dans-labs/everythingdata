ARG CUDA_IMAGE="12.1.1-devel-ubuntu22.04"
FROM nvidia/cuda:${CUDA_IMAGE}

# We need to set the host to 0.0.0.0 to allow outside access
ENV HOST 0.0.0.0

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y git build-essential \
    python3 python3-pip gcc wget \
    ocl-icd-opencl-dev opencl-headers clinfo \
    libclblast-dev libopenblas-dev \
    && mkdir -p /etc/OpenCL/vendors && echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd

COPY app /app

# setting build related env vars
ENV CUDA_DOCKER_ARCH=all
ENV LLAMA_CUBLAS=1
EXPOSE 8888

# Install depencencies
RUN python3 -m pip install --upgrade pip pytest cmake scikit-build setuptools fastapi uvicorn sse-starlette pydantic-settings flask requests starlette-context
RUN pip3 install -r /app/requirements.txt

# Install llama-cpp-python (build with cuda)
RUN CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
RUN pip install wikipedia-api langchain jupyter peft nltk git+https://github.com/stanfordnlp/pyreft.git 

WORKDIR /app
COPY app/llmframe.py /app/llmframe.py
#CMD ["sh", "-c", "jupyter notebook --ip=0.0.0.0 --port=8888 --NotebookApp.token=${JUPYTER_PASSWORD} --allow-root --no-browser"]
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--NotebookApp.token=${JUPYTER_PASSWORD}", "--allow-root", "--no-browser"]

