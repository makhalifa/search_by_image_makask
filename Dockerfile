FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Install CUDA and cuDNN for GPU support
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cuda-command-line-tools-11-2 \
        libcudnn8=8.1.1.33-1+cuda11.2 \
        libcudnn8-dev=8.1.1.33-1+cuda11.2 \
        libnvinfer7=7.2.1-1+cuda11.2 \
        libnvinfer-dev=7.2.1-1+cuda11.2 \
        libnvparsers7=7.2.1-1+cuda11.2 \
        libnvparsers-dev=7.2.1-1+cuda11.2 \
    && rm -rf /var/lib/apt/lists/*

# Install any other dependencies you need
COPY requirements.txt /app
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy your app code and model files into the container
COPY . /app

# Set the default command to start the app server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "1"]
