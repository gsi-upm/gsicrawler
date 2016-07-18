FROM ubuntu:16.04

RUN apt-get update && apt-get -y install \
	python \
	python-pip \
	python-scrapy \
	python-sklearn \
	phantomjs

RUN pip install --upgrade pip

# Dependencias GSICrawler
RUN pip install bottle parse selenium pytz twython
RUN pip install --upgrade google-api-python-client

# Dependencias Senpy y plugins 
RUN pip install flask gevent pyld gitpython nltk pattern
RUN python -m nltk.downloader stopwords

ADD gsicrawler.tar.gz /app

WORKDIR /app
