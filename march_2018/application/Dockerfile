FROM python:3.6.4

COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt && \
    rm -rf /tmp/requirements.txt && \
    mkdir -p /project/application

WORKDIR /project/application

ADD . /project/application
