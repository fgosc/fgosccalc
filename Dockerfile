FROM node:24-slim AS jsbuild

WORKDIR /build

COPY package.json package-lock.json .babelrc ./
RUN npm ci

COPY static/js/src ./static/js/src
RUN npm run build


FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y \
        libglib2.0-0 \
        libgl1 \
        # for SVM
        libsm6 libxrender1 libxext-dev \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-docker.txt ./
RUN pip install -r requirements-docker.txt

COPY . ./
COPY --from=jsbuild /build/static/js/dist ./static/js/dist
RUN python3 makeprop.py

CMD ["python", "main.py", "--host", "0.0.0.0"]
