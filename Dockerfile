FROM python:3

RUN apt-get update && apt-get install -y gettext

ADD requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /usr/src/app

ADD . /usr/src/app

ADD run-cron.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/run-cron.sh

ENTRYPOINT ["run-cron.sh"]

CMD ["cron","100", "isis"]