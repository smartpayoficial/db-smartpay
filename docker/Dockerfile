FROM python:3.8-slim-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip install pipenv
COPY Pipfile* ./

# Regenerate the lock file to ensure it's up-to-date before installing
RUN pipenv lock
RUN pipenv install --dev --system
RUN pip install email-validator

COPY . .
EXPOSE 80
