FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /SignEasy
RUN apt-get update
WORKDIR /SignEasy
COPY requirement.txt /SignEasy/
RUN pip install -r requirement.txt
COPY . /SignEasy/
