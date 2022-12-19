FROM python:3.10-alpine

# Python Buffer settings ensure errors are sent to the terminal container
ENV PYTHONUNBUFFERED=1

# Dependencies to get postgres & make working on alpine
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev make

WORKDIR /repo_automator

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
