import requests
import json


def retrieveCnnNews(search, num, filepath):
 r = requests.get("https://search.api.cnn.io/content?q=" + search + "&size=" + str(num) + "")

 response = r.json()["result"]

 with open(filepath, 'a') as outfile:
    print("CRAWLING RESULT")
    for newsitem in response:
        aux = dict()
        aux["url"] = newsitem["url"]
        aux["headline"] = newsitem["headline"]
        print(aux)
        json.dump(aux, outfile)
        outfile.write('\n')