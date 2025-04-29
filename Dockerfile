FROM python:3.11.6-alpine3.18
LABEL maintainer="viktor66462@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

# Встановлення залежностей та PostgreSQL клієнта
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .


RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user


USER my_user
