FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        cuda-command-line-tools-11-2 \
        libcudnn8=8.1.1.33-1+cuda11.2 \
        libcudnn8-dev=8.1.1.33-1+cuda11.2 \
        libnvinfer7=7.2.1-1+cuda11.2 \
        libnvinfer-dev=7.2.1-1+cuda11.2 \
        libnvparsers7=7.2.1-1+cuda11.2 \
        libnvparsers-dev=7.2.1-1+cuda11.2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./app /app

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
