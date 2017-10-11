# coding: utf-8
import os
import requests



ROOT = os.path.dirname(os.path.realpath(__file__))

ENDPOINT = os.environ.get('ES_ENDPOINT_EXTERNAL', 'localhost:9200')
INDEX = 'gsiCrawler'

eid = 0
with open(os.path.join(ROOT, 'blogPosting.txt'), 'r') as f:
    for line in f:
        url = 'http://{}/{}/{}/{}'.format(ENDPOINT, INDEX, "twitter", eid)
        requests.put(url, data=line, headers={'Content-Type': 'application/json'})
        eid += 1

with open(os.path.join(ROOT, 'comments-ld.txt'), 'r') as f:
    for line in f:
        url = 'http://{}/{}/{}/{}'.format(ENDPOINT, INDEX, "reddit", eid)
        requests.put(url, data=line, headers={'Content-Type': 'application/json'})
        eid += 1
