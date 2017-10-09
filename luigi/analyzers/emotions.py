import os
import json
import urllib
import requests

def emotionRecognition(i):
    r = requests.post('http://test.senpy.cluster.gsi.dit.upm.es/api/', data={'algo':'emotion-anew', 'i':i["schema:articleBody"], 'lang':'en'})
    response = r.content.decode('utf-8')
    try:
        response_json = json.loads(response)
        #i["analysis"] = response_json
        emotions_arr = response_json["entries"][0]["emotions"]
        for x, emotion in enumerate(emotions_arr):
            emotion["@id"] = i["@id"]+"#Emotions{num}".format(num=x)
            emotion['onyx:hasEmotion']["@id"] = i["@id"]+"#Emotion{num}".format(num=x)
            emotion['onyx:hasEmotion']['onyx:hasEmotionCategory'] = 'wna:' + emotion['onyx:hasEmotion']['onyx:hasEmotionCategory'].split('ns#')[1]
            emotions_arr[x] = emotion
        i["emotions"] = emotions_arr
        return i
    except json.decoder.JSONDecodeError:
    	return i