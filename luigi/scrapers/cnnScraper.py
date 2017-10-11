import requests
import json


def retrieveCnnNews(search, num, filepath):
	r = requests.get("https://search.api.cnn.io/content?q=" + search + "&size=" + str(num) + "")

	response = r.json()["result"]

	news = []

	for newsitem in response:
		aux = dict()
		aux["type"] = "NewsArticle"
		aux["@id"] = newsitem["url"]
		aux["dataPublished"] = newsitem["firstPublishDate"]
		aux["dataModified"] = newsitem["lastModifiedDate"]
		aux["articleBody"] = newsitem["body"]
		aux["about"] = newsitem["topics"]
		aux["author"] = newsitem["source"]
		aux["headline"] = newsitem["headline"]
		aux["search"] = search
		news.append(aux)
	print(news[0])

	with open(filepath, 'w') as outfile:
	    json.dump(news, outfile)