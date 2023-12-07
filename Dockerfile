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

#COPY . .
#COPY api_like_OAI.py /root/api_like_OAI.py
#COPY examples /root/examples
#COPY build /root/build
#COPY app /root/app
COPY app /app

# setting build related env vars
ENV CUDA_DOCKER_ARCH=all
ENV LLAMA_CUBLAS=1

# Install depencencies
RUN python3 -m pip install --upgrade pip pytest cmake scikit-build setuptools fastapi uvicorn sse-starlette pydantic-settings flask requests starlette-context
RUN pip3 install -r /app/requirements.txt

# Install llama-cpp-python (build with cuda)
RUN CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python

# Run the server
#CMD python3 /root/api_like_OAI.py --host 0.0.0.0 --llama-api=http://0.0.0.0:8000 &
#CMD python3 -m llama_cpp.server --model /var/model/ggml-model-f16.gguf --n_gpu_layers 35
#CMD /root/build/server -m /var/model/ggml-model-f16.gguf -t 10 -ngl 40 -c 2048 &
WORKDIR /app
#COPY app/app.py /root/app/main.py
COPY app/app_test.py /app/main.py
COPY app/llmframe.py /app/llmframe.py
