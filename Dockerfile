FROM python

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN apt-get -y update
RUN apt-get -y install locales
RUN locale-gen ru_RU.UTF-8
RUN apt-get install -y libfontconfig


RUN apt-get install -yqq unzip curl wget gdebi

#RUN apt-get install libnss3-1d libxss1 libgconf2-4 libappindicator1 libindicator7


RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt -f install -y
RUN gdebi google-chrome-stable_current_amd64.deb
#RUN dpkg -i google-chrome-stable_current_amd64.deb


COPY . .

CMD ["python", "-u", "./bot.py"]