FROM python:3.9-slim-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip && pip install setuptools==57.5.0
RUN pip install pipenv==v2021.5.29 --no-cache-dir
COPY Pipfile* ./

# Regenerate the lock file to ensure it's up-to-date before installing
RUN pipenv lock
RUN pipenv install --dev --system
RUN pip install email-validator

COPY . .
EXPOSE 80
