FROM python:3.6
MAINTAINER Francisco Vaquero <f.vaquero@opianalytics.com>

RUN apt-get update && \
    apt-get install --yes \
    python3-dev \
    python3-pip \
    pkg-config \
    libpq-dev \
    libgraphviz-dev \
    graphviz

RUN mkdir -p etl/output

COPY pipeline.py /etl/pipeline.py
COPY scrapper.py /etl/scrapper.py
COPY run_etl.sh /etl/run_etl.sh
COPY requirements.txt /etl/requirements.txt

WORKDIR /etl

RUN pip3 install -r requirements.txt
CMD ["/bin/bash", "run_etl.sh"]