FROM python:3.9-slim-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install pipenv==v2021.5.29 --no-cache-dir
COPY Pipfile* ./
RUN pipenv install --dev --system

COPY . .
EXPOSE 80
