FROM python:3.8-alpine


COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN apk --update add python py-pip gunicorn
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apk del build-dependencies

RUN adduser -D api

WORKDIR /home/api

COPY app app
COPY migrations migrations
COPY barracuda-syslog-api.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP barracuda-syslog-api.py


RUN chown -R api:api ./
USER api

EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]
