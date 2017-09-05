import sys
import requests
import json
import requests.auth
import os
from pprint import pprint as print


## Configuration

client_auth = requests.auth.HTTPBasicAuth('JYtWboDkSqwhig', 'nv3x_lKNkRTMLDoSX9xg7TJ93A4')
post_data = {"grant_type": "password", "username": "merinom", "password": "GSIGSI"}
headers = {"User-Agent": "GSI-UPM/1 by merinom"}


## Getting the token

tokenResponse = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
jsonTokenResponse = tokenResponse.json()
headers = {"Authorization": "bearer "+jsonTokenResponse['access_token'], "User-Agent": "ChangeMeClient/0.1 by YourUsername"}


## Getting personal information about the user

def getPersonalInfo():
	personalInfoResponse = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
	personalInfoResponseJson = personalInfoResponse.json()
	return personalInfoResponseJson


## Getting the articles

def getArticles(search = 'gsi', limit = 10, filePath = 'articles.json'):
	limit = "&limit="+str(limit)
	sort = '&sort=top'
	URL = "https://oauth.reddit.com/search"

	searchResponse = requests.get(URL+"?"+"q="+search+sort+limit, headers=headers)
	searchResponseJson = searchResponse.json()

	# Save the JSON with the different articles

	articlesJSON = []
	for article in searchResponseJson['data']['children']:
		articleData = article['data']
		jsonArticle = {}
		jsonArticle['id'] = articleData['id']
		jsonArticle['subredditName'] = articleData['subreddit']
		jsonArticle['subreddit_id'] = articleData['subreddit_id']
		jsonArticle['permalink'] = articleData['permalink']
		jsonArticle['title'] = articleData['title']
		jsonArticle['media'] = articleData['url']
		jsonArticle['num_comments'] = articleData['num_comments']
		jsonArticle['author'] = articleData['author']
		jsonArticle['score'] = articleData['score']
		jsonArticle['archived'] = articleData['archived']
		jsonArticle['timestamp'] = articleData['created_utc']
		jsonArticle['ups'] = articleData['ups']
		jsonArticle['downs'] = articleData['downs']
		jsonArticle['search_term'] = [search]
		articlesJSON.append(jsonArticle)

	with open(filePath, 'w') as outfile:
		json.dump(articlesJSON, outfile)


# Auxiliar method to save the JSON with the different comments

def moveInsideCommentsTree(comment, commentsJSON):
	if isinstance(comment, list):
		for element in comment:
			moveInsideCommentsTree(element, commentsJSON)
	if 'body' in comment:
		jsonComment = {}
		jsonComment['body'] = comment['body']
		jsonComment['author'] = comment['author']
		jsonComment['parent_id'] = comment['parent_id']
		jsonComment['timestamp'] = comment['created_utc']
		jsonComment['downs'] = comment['downs']
		jsonComment['likes'] = comment['likes']
		jsonComment['score'] = comment['score']
		jsonComment['subreddit'] = comment['subreddit']
		jsonComment['subreddit_id'] = comment['subreddit_id']
		jsonComment['ups'] = comment['ups']
		jsonComment['id'] = comment['name']
		commentsJSON.append(jsonComment)
	if 'data' in comment:
		moveInsideCommentsTree(comment['data'], commentsJSON)
	if 'children' in comment:
		moveInsideCommentsTree(comment['children'], commentsJSON)
	if 'replies' in comment:
		moveInsideCommentsTree(comment['replies'], commentsJSON)
		
## Getting the comment of each article given as JSON file

def getComments(articlesJSON = 'articles.json', filePath = 'comments.json'):
	commentsJSON = []

	with open(articlesJSON) as json_file:
		articles = json.load(json_file)
		for article in articles:
			commentsResponse = requests.get("https://oauth.reddit.com"+article['permalink']+"", headers=headers)
			commentsResponseJson = commentsResponse.json()
			for comment in commentsResponseJson:
				moveInsideCommentsTree(comment, commentsJSON)

	with open(filePath, 'w') as outfile:
		json.dump(commentsJSON,outfile)