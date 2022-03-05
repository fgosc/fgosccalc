FROM nikolaik/python-nodejs:python3.8-nodejs16-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y \
        libopencv-core-dev \
        libglib2.0-0 \
        libgl1-mesa-glx \
        # for SVM
        libsm6 libxrender1 libxext-dev \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-docker.txt ./
RUN pip install -r requirements-docker.txt

COPY . ./
RUN python3 makeprop.py
RUN npm install && npm run build

CMD ["python", "main.py", "--host", "0.0.0.0"]
