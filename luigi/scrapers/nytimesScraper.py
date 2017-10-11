import requests
import json
from newspaper import Article


def retrieveNytimesNews(search, num, filepath):
	r = requests.get("https://query.nytimes.com/svc/add/v1/sitesearch.json?q=" + search + "&spotlight=true&facet=true")

	response = r.json()["response"]["docs"]

	news = []

	for newsitem in response:
		aux = dict()
		aux["type"] = "NewsArticle"
		aux["@id"] = newsitem["web_url"]
		aux["dataPublished"] = newsitem["pub_date"]
		aux["dataModified"] = newsitem["updated"]
		aux["articleBody"] = "articletext"
		aux["about"] = [key["value"] for key in newsitem["keywords"]]
		aux["author"] = newsitem["source"]
		aux["headline"] = newsitem["headline"]["main"]
		aux["search"] = search
		news.append(aux)

	for newsitem in news:
		a = Article(newsitem["@id"])
		a.download()
		a.parse()
		newsitem["articleBody"] = a.text

	print(news[0])

	with open(filepath, 'w') as outfile:
	    json.dump(news, outfile)
