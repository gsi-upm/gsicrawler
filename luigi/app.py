import flask
import sched, time 
import os
import subprocess
import analysistask
import datetime
import json
from flask import Flask, request, make_response
app = Flask(__name__)

@app.route("/startAnalysis",methods=['POST'])
def startAnalysis():
    
    analysisType=request.args.get('analysisType')
    url=request.args.get('url')
    website = request.args.get('website')
    
    #print(request.data)
    identifier = time.time()

    jsonreponse = {}

    if website == 'reddit':
    	#ES params
        indexPosts= 'reddit'
        indexComments='reddit'
        doc_typePosts='articles'
        doc_typeComments='comments'
        print('reddit website - Run luigi reddit analysis task')
        command = 'python -m luigi --module analysistask ElasticsearchReddit --index-Posts {indexPosts} --index-Comments {indexComments} --doc-type-Posts {doc_typePosts} --doc-type-Comments {doc_typeComments} --website {website} --url {url} --id {id} --analysisType {analysisType}'.format(url=url,website=website,id=identifier,analysisType=analysisType, indexPosts=indexPosts, indexComments=indexComments,doc_typePosts=doc_typePosts,doc_typeComments=doc_typeComments)
        subprocess.call(command.split(), shell= False)
        jsonreponse['index'] = 'reddit'
        jsonreponse['url'] = url
        jsonreponse['website'] = website
        jsonreponse['id'] = identifier
        resp = make_response(json.dumps(jsonreponse))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Content-Type'] = "application/json"
        return resp
    else:
        command = 'python -m luigi --module analysistask Elasticsearch --index gsicrawler --doc-type {website} --website {website} --url {url} --id {id} --analysisType {analysisType}'.format(url=url,website=website,id=identifier,analysisType=analysisType)
        subprocess.call(command.split(), shell= False)
        jsonreponse['index'] = 'gsicrawler'
        jsonreponse['url'] = url
        jsonreponse['website'] = website
        jsonreponse['id'] = identifier
        resp = make_response(json.dumps(jsonreponse))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Content-Type'] = "application/json"
        return resp


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8000)