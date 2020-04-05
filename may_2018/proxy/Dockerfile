FROM python:3.6.4

COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt && \
    rm -rf /tmp/requirements.txt

RUN mkdir /application
COPY application /application
WORKDIR /application
