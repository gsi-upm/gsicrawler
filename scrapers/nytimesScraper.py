import requests
import json
from newspaper import Article


def retrieveNytimesNews(search, num, filepath):
	r = requests.get("https://query.nytimes.com/svc/add/v1/sitesearch.json?q=" + search + "&spotlight=true&facet=true")

	response = r.json()["response"]["docs"]

	news = []
	with open(filepath, 'a') as outfile:
		for newsitem in response:
			if newsitem["source"] != "Internet Video Archive":
				aux = dict()
				aux["@type"] = "schema:NewsArticle"
				aux["@id"] = newsitem["web_url"]
				aux["_id"] = newsitem["web_url"]
				aux["schema:datePublished"] = newsitem["pub_date"]
				aux["schema:dateModified"] = newsitem["updated"]
				aux["schema:articleBody"] = "articletext"
				aux["schema:about"] = [key["value"] for key in newsitem["keywords"]]
				aux["schema:author"] = newsitem["source"]
				aux["schema:headline"] = newsitem["headline"]["main"]
				aux["schema:search"] = search
				aux["schema:thumbnailUrl"] = "https://www.nytimes.com/" + newsitem["multimedia"][0]["url"]
				news.append(aux)

		for newsitem in news:
			a = Article(newsitem["@id"])
			a.download()
			a.parse()
			newsitem["schema:articleBody"] = a.text
			json.dump(newsitem, outfile)
			outfile.write('\n')



