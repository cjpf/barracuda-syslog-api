FROM python:3.8-alpine

RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apk del build-dependencies

RUN adduser -D api



WORKDIR /home/api



COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn pymysql


COPY app app
COPY migrations migrations
COPY barracuda-syslog-api.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP barracuda-syslog-api.py


RUN chown -R api:api ./
USER api

EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]
