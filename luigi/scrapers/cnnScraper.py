import requests
import json


def retrieveCnnNews(search, num, filepath):
	r = requests.get("https://search.api.cnn.io/content?q=" + search + "&size=" + str(num) + "")

	response = r.json()["result"]

	with open(filepath, 'a') as outfile:
		for newsitem in response:
			if newsitem["source"] != "Internet Video Archive":
				aux = dict()
				aux["@type"] = "schema:NewsArticle"
				aux["@id"] = newsitem["url"]
				aux["_id"] = newsitem["url"]
				aux["schema:datePublished"] = newsitem["firstPublishDate"]
				aux["schema:dateModified"] = newsitem["lastModifiedDate"]
				aux["schema:articleBody"] = newsitem["body"]
				aux["schema:about"] = newsitem["topics"]
				aux["schema:author"] = newsitem["source"]
				aux["schema:headline"] = newsitem["headline"]
				aux["schema:search"] = search
				aux["schema:thumbnailUrl"] = newsitem["thumbnail"]
				json.dump(aux, outfile)
				outfile.write('\n')
