import requests
import json
import os
import json
import urllib
import requests
import time

#base_url = 'http://127.0.0.1:5000/?algo=sentiment140&i=%s'
API_KEY_MEANING_CLOUD = os.environ.get('API_KEY_MEANING_CLOUD')

def getContext():
    r = requests.get("http://latest.senpy.cluster.gsi.dit.upm.es/api/contexts/Context.jsonld")
    senpy_context = r.json()["@context"]
    senpy_context.update({
        'dbps':'http://www.openlinksw.com/schemas/dbpedia-spotlight#',
        'dbpedia':'http://dbpedia.org/resource/',
        'dbpedia-owl': 'http://dbpedia.org/ontology/',
        'schema':'http://schema.org/',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'marl:hasPolarity': {
            '@type': '@id'
        },
        'rdfs:subClassOf': {
            '@type': '@id'
        },
        'dbps:types': {
            '@type': '@id'
        },
        'dbps:anyURI': {
            '@type': '@id'
        }
    })
    return senpy_context

def semanticAnalysis(i):
    i["@context"] = getContext()
    REQUEST_LONG = 3000
    i_len = len(i["schema:articleBody"])
    number_of_requests = (len(i["schema:articleBody"])//REQUEST_LONG)
    entities_arr = []
    sentiments_arr = []
    topics_arr = []
    for k in range(0,number_of_requests+1):
        
        if i_len - int(REQUEST_LONG*(k+1)) > 0:
            r = requests.post('http://meaningcloud.senpy.cluster.gsi.dit.upm.es/api/', data={'algo':'sentiment-meaningCloud', 'apiKey':API_KEY_MEANING_CLOUD, 'i':i["schema:articleBody"][REQUEST_LONG*k:REQUEST_LONG*k+REQUEST_LONG]})
        else:
            r = requests.post('http://meaningcloud.senpy.cluster.gsi.dit.upm.es/api/', data={'algo':'sentiment-meaningCloud', 'apiKey':API_KEY_MEANING_CLOUD, 'i':i["schema:articleBody"][REQUEST_LONG*k:-1]})
        time.sleep(1)
        r = r.json()
        if type(r["entries"][0]["entities"]) is dict:
            r["entries"][0]["entities"] = [r["entries"][0]["entities"]]
        for x, index in enumerate(r["entries"][0]["entities"]):
            index["nif:beginIndex"] = str(int(index["nif:beginIndex"]) + (REQUEST_LONG*k))
            index["nif:endIndex"] = str(int(index["nif:endIndex"]) + (REQUEST_LONG*k))
            if index["@type"].split('#')[-1] == 'ODENTITY_City':
                try:
                    geor = requests.get("https://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query=select+%3Fcoordinates+where+%7B%0D%0A%0D%0Adbr%3A{}+georss%3Apoint+%3Fcoordinates%0D%0A%0D%0A%7D&format=application%2Fsparql-results%2Bjson".format(index.get("rdfs:subClassOf", "").split('/')[-1]))
                    coords = geor.json()['results']['bindings'][0]['coordinates']['value'].split()
                    index['latitude'] = coords[0]
                    index['longitude'] = coords[1]
                except (IndexError, json.decoder.JSONDecodeError):
                    pass
            if index["@type"].split('#')[-1] in ['ODENTITY_Person', 'ODENTITY_FullName']:
                try:
                    peopler = requests.get("https://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query=select+%3Fimage+where+%7B%0D%0A++dbr%3A{}+++dbo%3Athumbnail+%3Fimage%0D%0A%0D%0A%7D+LIMIT+100&format=application%2Fsparql-results%2Bjson&CXML_redir_for_subjs=121&CXML_redir_for_hrefs=&timeout=30000&debug=on&run=+Run+Query+".format(index.get("rdfs:subClassOf", "").split('/')[-1]))
                    index['dbo:thumbnail'] = peopler.json()['results']['bindings'][0]['image']['value']
                except (IndexError, json.decoder.JSONDecodeError):
                    pass

            entities_arr.append(index)
        if type(r["entries"][0]["sentiments"]) is dict:
            r["entries"][0]["sentiments"] = [r["entries"][0]["sentiments"]]
        for x, index in enumerate(r["entries"][0]["sentiments"]):
            index["@id"] = i["@id"]+"#Sentiment{num}".format(num=x)
            
            if 'nif:beginIndex' in index:
                index["nif:beginIndex"] = str(int(index["nif:beginIndex"]) + (REQUEST_LONG*k))
            if 'nif:endIndex' in index:
                index["nif:endIndex"] = str(int(index["nif:endIndex"]) + (REQUEST_LONG*k))
            sentiments_arr.append(index)
        if type(r["entries"][0]["topics"]) is dict:
            r["entries"][0]["topics"] = [r["entries"][0]["topics"]]
        for x, index in enumerate(r["entries"][0]["topics"]):
            index["@id"] = i["@id"]+"#Topic{num}".format(num=x)
            topics_arr.append(index)
        

    
    i["sentiments"] = sentiments_arr
    i["entities"] = entities_arr
    i["topics"] = topics_arr
    return i
