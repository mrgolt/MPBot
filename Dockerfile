FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN apt-get -y update
RUN apt-get -y install locales
RUN locale-gen ru_RU.UTF-8
RUN apt-get install -y libfontconfig


RUN apt-get install -yqq unzip curl
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN sudo dpkg -i google-chrome-stable_current_amd64.deb
RUN sudo apt -f install
RUN sudo apt install google-chrome-stable



COPY . .

CMD ["python", "-u", "./bot.py"]