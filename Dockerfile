FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN apt-get -y update
RUN apt-get -y install locales
RUN locale-gen ru_RU.UTF-8
RUN apt-get install -y libfontconfig

RUN apt-get install -y google-chrome-stable

RUN apt-get install -yqq unzip curl
RUN sudo apt-get install wget
RUN wget https://dl.google.com/linux/linux_signing_key.pub
RUN sudo apt-get install gnupg
RUN sudo apt-key add linux_signing_key.pub
RUN sudo apt update
RUN sudo apt install google-chrome-stable

COPY . .

CMD ["python", "-u", "./bot.py"]