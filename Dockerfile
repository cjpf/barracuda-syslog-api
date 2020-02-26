FROM python:3.8-alpine

WORKDIR /home/api
# RUN python -m venv venv
COPY requirements.txt requirements.txt
RUN apk --update add python py-pip 
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install gunicorn pymysql \
    && apk del build-dependencies

RUN adduser -D api

COPY app app
COPY migrations migrations
COPY barracuda-syslog-api.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP barracuda-syslog-api.py


RUN chown -R api:api ./
USER api

EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]
