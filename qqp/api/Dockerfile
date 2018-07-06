FROM python:3.6
MAINTAINER Francisco Vaquero <f.vaquero@opianalytics.com>

RUN apt-get update && \
    apt-get install --yes \
    python3-dev \
    python3-pip \
    pkg-config \
    libpq-dev \
    libgraphviz-dev \
    graphviz \
    git

RUN mkdir api

COPY . /api
WORKDIR /api

EXPOSE 8000

RUN pip3 install -r requirements.txt
CMD ["/bin/bash", "start.sh"]