FROM ubuntu

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN apt-get -y update
RUN apt-get -y install locales
RUN locale-gen ru_RU.UTF-8
RUN apt-get install -y libfontconfig


RUN apt-get install -yqq unzip curl wget


ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get install -y tzdata

RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb
RUN apt -f install -y

COPY . .

CMD ["python", "-u", "./bot.py"]