FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get -y install locales
RUN locale-gen ru_RU.UTF-8
КГТ фзе-пуе штыефдд -н сркщьшгь-икщцыук

COPY . .

