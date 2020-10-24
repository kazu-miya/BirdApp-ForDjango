FROM python:3.7

ENV PYTHONUNBUFFERED 1

RUN apt update && apt upgrade -y

RUN apt install git -y
RUN apt install vim -y
RUN apt install wget -y

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
