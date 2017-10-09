import os
import json
import urllib
import requests
import time

#base_url = 'http://127.0.0.1:5000/?algo=sentiment140&i=%s'
API_KEY_MEANING_CLOUD = os.environ.get('API_KEY_MEANING_CLOUD')

def sentimentAnalysis(i):
    r = requests.post('http://meaningcloud.senpy.cluster.gsi.dit.upm.es/api/', data={'algo':'sentiment-meaningCloud', 'apiKey':API_KEY_MEANING_CLOUD, 'i':i["schema:articleBody"]}).json()
    time.sleep(1)
    try:
        sentiments_arr = r["entries"][0]["sentiments"]
        for x, sentiment in enumerate(sentiments_arr):
            sentiment["@id"] = i["@id"]+"#Sentiment{num}".format(num=x)
            sentiments_arr[x] = sentiment
        i["sentiments"] = sentiments_arr
        return i

    except:
        return i
