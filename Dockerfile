FROM python:3.8.6-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libopencv-core-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
    # for SVM
    libsm6 libxrender1 libxext-dev 

COPY requirements-docker.txt ./
RUN pip install -r requirements-docker.txt

COPY . ./
RUN python3 makeprop.py

CMD ["python", "main.py", "--host", "0.0.0.0"]
