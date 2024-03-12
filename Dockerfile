FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /tm-app/

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .