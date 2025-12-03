FROM python:3.8-slim-bullseye

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip install pipenv
COPY Pipfile* ./

RUN pipenv lock
RUN pipenv requirements > requirements.txt

RUN pip install -r requirements.txt
RUN pip install email-validator

COPY . .
EXPOSE 80