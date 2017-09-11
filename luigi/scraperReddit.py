import sys
import requests
import json
import requests.auth
import os
from pprint import pprint as print


## Configuration

reddit_user = os.environ["REDDIT_USER"]
reddit_pass = os.environ["REDDIT_PASS"]
reddit_client = os.environ["REDDIT_CLIENT"]
reddit_token = os.environ["REDDIT_TOKEN"]

client_auth = requests.auth.HTTPBasicAuth(reddit_client, reddit_token)
post_data = {"grant_type": "password", "username": reddit_user, "password": reddit_pass}
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

def getArticles(search = '', limit = 4, filePath = 'articles.json'):
    limit = "&limit="+str(limit)
    sort = '&sort=top'
    URL = "https://oauth.reddit.com/search"

    searchResponse = requests.get(URL+"?"+"q="+search+sort+limit, headers=headers)
    searchResponseJson = searchResponse.json()

    # Save the JSON with the different articles

    with open(filePath, 'w') as outfile:
        for article in searchResponseJson['data']['children']:
            articleData = article['data']
            jsonArticle = {}
            jsonArticle['id'] = articleData['id']
            jsonArticle['subreddit'] = articleData['subreddit']
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

            
            jsonArticle['@context'] = ["http://schema.org","http://latest.senpy.cluster.gsi.dit.upm.es/api/contexts/Context.jsonld"]
            jsonArticle['@type'] = "BlogPost"
            jsonArticle['@id'] = "reddit.com" + articleData['permalink']
            jsonArticle['about'] = [search]
            jsonArticle['text'] = articleData['title']
            jsonArticle['creator'] = articleData['author']
            jsonArticle['datePublished'] = articleData['created_utc']


            
            outfile.write(json.dumps(jsonArticle))
            outfile.write('\n')

# Auxiliar method to save the JSON with the different comments

def moveInsideCommentsTree(comment, article, commentsJSON):
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

        jsonComment['@context'] = ["http://schema.org","http://latest.senpy.cluster.gsi.dit.upm.es/api/contexts/Context.jsonld"]
        jsonComment['@type'] = "Comment"
        jsonComment['parentItem'] = article['@id']
        jsonComment['@id'] = comment['name']
        jsonComment['about'] = article['search']
        jsonComment['text'] = comment['body']
        jsonComment['creator'] = comment['author']
        jsonComment['datePublished'] = comment['created_utc']
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

    with open(articlesJSON) as json_file, open(filePath, 'w') as outfile:
        for line in json_file:
            article = json.loads(line)
            commentsResponse = requests.get("https://oauth.reddit.com"+article['permalink']+"", headers=headers)
            commentsResponseJson = commentsResponse.json()
            for comment in commentsResponseJson:
                moveInsideCommentsTree(comment, article, commentsJSON)
        for comment in commentsJSON:
            outfile.write(json.dumps(comment))
            outfile.write('\n')
