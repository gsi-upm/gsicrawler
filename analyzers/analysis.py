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
    r = requests.get("http://senpy.cluster.gsi.dit.upm.es/api/contexts/Context.jsonld")
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
    i['_id'] = i['@id']
    entities_arr = []
    sentiments_arr = []
    topics_arr = []
    for k in range(0,number_of_requests+1):
        
        if i_len - int(REQUEST_LONG*(k+1)) > 0:
            r = requests.post('http://localhost:5000/api/', data={'algo':'sentiment-vader', 'apiKey':API_KEY_MEANING_CLOUD, 'i':i["http://schema.org/articleBody"][0]["@value"][REQUEST_LONG*k:REQUEST_LONG*k+REQUEST_LONG]})
        else:
            r = requests.post('http://localhost:5000/api/', data={'algo':'sentiment-vader', 'apiKey':API_KEY_MEANING_CLOUD, 'i':i["http://schema.org/articleBody"][0]["@value"][REQUEST_LONG*k:-1]})
        time.sleep(1)
        r = r.json()
        
        if not 'entries' in r:
            continue
        if type(r["entries"][0]["entities"]) is dict:
            r["entries"][0]["entities"] = [r["entries"][0]["entities"]]
        for x, index in enumerate(r["entries"][0]["entities"]):
            index["nif:beginIndex"] = str(int(index["nif:beginIndex"]) + (REQUEST_LONG*k))
            index["nif:endIndex"] = str(int(index["nif:endIndex"]) + (REQUEST_LONG*k))
            if index["@type"].split('#')[-1] == 'ODENTITY_City':
                try:
                    geor = requests.get("https://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query=select+%3Fcoordinates+where+%7B%0D%0A%0D%0Adbr%3A{}+georss%3Apoint+%3Fcoordinates%0D%0A%0D%0A%7D&format=application%2Fsparql-results%2Bjson".format(index.get("marl:describesObject", "").split('/')[-1]))
                    coords = geor.json()['results']['bindings'][0]['coordinates']['value'].split()
                    index['latitude'] = coords[0]
                    index['longitude'] = coords[1]
                except (IndexError, json.decoder.JSONDecodeError):
                    pass
            if index["@type"].split('#')[-1] in ['ODENTITY_Person', 'ODENTITY_FullName']:
                try:
                    peopler = requests.get("https://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query=select+%3Fimage+where+%7B%0D%0A++dbr%3A{}+++dbo%3Athumbnail+%3Fimage%0D%0A%0D%0A%7D+LIMIT+100&format=application%2Fsparql-results%2Bjson&CXML_redir_for_subjs=121&CXML_redir_for_hrefs=&timeout=30000&debug=on&run=+Run+Query+".format(index.get("marl:describesObject", "").split('/')[-1]))
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
            index["rdfs:subClassOf"] = "http://dbpedia.org/resource/Internet"
            topics_arr.append(index)
        

    
    i["sentiments"] = sentiments_arr
    i["entities"] = entities_arr
    i["topics"] = topics_arr
    return i

def expertAnalysis(entry):
    text = entry
    result = {}
    result["text"] = text
    data = {"DOCUMENT":text}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    url_cat = "http://trivalent.expertsystemlab.com/text/rest/categorize"       
    res_cat = requests.post(url_cat, data=json.dumps(data), headers=headers)
    #entry['categorize'] = json.loads(res_cat.text)
    url_info = "http://trivalent.expertsystemlab.com/text/rest/extract-info"
    res_info = json.loads(requests.post(url_info, data=json.dumps(data), headers=headers).text)


    try:
        organization_names = []
        organizations = res_info["RESPONSE"]["ORGANIZATIONS"]
        if isinstance(organizations["ORGANIZATION"],dict):
            organization = organizations["ORGANIZATION"]["BASE"]
            aux = {"@type": "schema:Organization",
                   "schema:name": organization}
            organization_names.append(aux)
        elif len(organizations["ORGANIZATION"]) > 1:
            organizations_ = [x["BASE"] for x in organizations["ORGANIZATION"]]
            organization_names = []
            for organization in organizations_:
                aux = {"@type": "schema:Organization",
                       "schema:name": organization}
                organization_names.append(aux)


    except:
        print("organizations")
        organization_names = []
        


    try:
        people_names = []
        people = res_info["RESPONSE"]["PEOPLE"] 
        if isinstance(people["PERSON"],dict):
            person = people["PERSON"]["BASE"]
            aux = {"@type": "schema:Person",
                   "schema:name": person}
            people_names.append(aux)
        elif len(people["PERSON"]) > 1:
            people_ = [x["BASE"] for x in people["PERSON"]]
            for person in people_:
                aux = {"@type": "schema:Person",
                       "schema:name": person}
                people_names.append(aux)                 
    except:
        people_names = []
        print("people")

    try:
        place_names = []
        places = res_info["RESPONSE"]["PLACES"]
        if isinstance(places["PLACE"], dict):
            place = places["PLACE"]["BASE"]
            aux = {"@type": "schema:Place",
                   "schema:name": place}
            place_names.append(aux)
        elif len(places["PLACE"]) > 1:
            places_ = [x["BASE"] for x in places["PLACE"]]
            for place in places_:
                aux = {"@type": "schema:Place",
                       "schema:name": place}
                place_names.append(aux) 

    except:
        place_names = []
        print("places")

    result['organizations'] = organization_names
    result['people'] = people_names
    result['places'] = place_names 
    #entry['info'] = res_info
    return result

def myAnalysis(i):
    i["@context"] = getContext()
    REQUEST_LONG = 3000
    i_len = len(i["schema:articleBody"])
    number_of_requests = (len(i["schema:articleBody"])//REQUEST_LONG)
    i['_id'] = i['@id']
    key = "AIzaSyDxZkoTU0IDBZmw6q3-5P6VsZ7cfhiTvcY"
    entities_arr = []
    sentiments_arr = []
    
    for k in range(0,number_of_requests+1):
        
        if i_len - int(REQUEST_LONG*(k+1)) > 0:
            r = requests.post('http://senpy:5000/api/', data={'algo':'sentiment-vader', 'apiKey':API_KEY_MEANING_CLOUD, 'i':i["schema:articleBody"][REQUEST_LONG*k:REQUEST_LONG*k+REQUEST_LONG]})
        else:
            r = requests.post('http://senpy:5000/api/', data={'algo':'sentiment-vader', 'apiKey':API_KEY_MEANING_CLOUD, 'i':i["schema:articleBody"][REQUEST_LONG*k:-1]})
        #time.sleep(1)
        r = r.json()
        
        if not 'entries' in r:
            continue

        if type(r["entries"][0]["sentiments"]) is dict:
            r["entries"][0]["sentiments"] = [r["entries"][0]["sentiments"]]
        for x, index in enumerate(r["entries"][0]["sentiments"]):
            index["@id"] = i["@id"]+"#Sentiment{num}".format(num=x)
            
            if 'nif:beginIndex' in index:
                index["nif:beginIndex"] = str(int(index["nif:beginIndex"]) + (REQUEST_LONG*k))
            if 'nif:endIndex' in index:
                index["nif:endIndex"] = str(int(index["nif:endIndex"]) + (REQUEST_LONG*k))
            sentiments_arr.append(index)



    data = {"DOCUMENT":i["schema:articleBody"]}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    url_cat = "http://trivalent.expertsystemlab.com/text/rest/categorize"       
    res_cat = requests.post(url_cat, data=json.dumps(data), headers=headers)
    #entry['categorize'] = json.loads(res_cat.text)
    url_info = "http://trivalent.expertsystemlab.com/text/rest/extract-info"
    res_info = json.loads(requests.post(url_info, data=json.dumps(data), headers=headers).text)

    try:
        people_names = []
        people = res_info["RESPONSE"]["PEOPLE"] 
        if isinstance(people["PERSON"],dict):
            person = people["PERSON"]["BASE"]
            dbpedia = requests.get('http://model.dbpedia-spotlight.org/en/annotate?text=%s&confidence=0.2&support=20' % person, headers={"Accept":"application/json"}).json()
            resp_arr = dbpedia["Resources"]
            final_person = resp_arr[0]['@URI']
            peopler = requests.get("https://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query=select+%3Fimage+where+%7B%0D%0A++dbr%3A{}+++dbo%3Athumbnail+%3Fimage%0D%0A%0D%0A%7D+LIMIT+100&format=application%2Fsparql-results%2Bjson&CXML_redir_for_subjs=121&CXML_redir_for_hrefs=&timeout=30000&debug=on&run=+Run+Query+".format(final_person.split('/')[-1]))
            thumbnail = peopler.json()['results']['bindings'][0]['image']['value']
            aux = {"@type": "schema:Person",
                   "@id": final_person,
                   "schema:name": person,
                   "schema:image": thumbnail }
            entities_arr.append(aux)
        elif len(people["PERSON"]) > 1:
            people_ = [x["BASE"] for x in people["PERSON"]]
            for person in people_:
                dbpedia = requests.get('http://model.dbpedia-spotlight.org/en/annotate?text=%s&confidence=0.2&support=20' % person, headers={"Accept":"application/json"}).json()
                resp_arr = dbpedia["Resources"]
                final_person = resp_arr[0]['@URI']
                peopler = requests.get("https://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query=select+%3Fimage+where+%7B%0D%0A++dbr%3A{}+++dbo%3Athumbnail+%3Fimage%0D%0A%0D%0A%7D+LIMIT+100&format=application%2Fsparql-results%2Bjson&CXML_redir_for_subjs=121&CXML_redir_for_hrefs=&timeout=30000&debug=on&run=+Run+Query+".format(final_person.split('/')[-1]))
                thumbnail = peopler.json()['results']['bindings'][0]['image']['value']
                aux = {"@type": "schema:Person",
                   "@id": final_person,
                   "schema:name": person,
                   "schema:image": thumbnail }
                entities_arr.append(aux)                
    except:
        pass

    try:
        place_names = []
        places = res_info["RESPONSE"]["PLACES"]
        if isinstance(places["PLACE"], dict):
            place = places["PLACE"]["BASE"]
            dbpedia = requests.get('http://model.dbpedia-spotlight.org/en/annotate?text=%s&confidence=0.2&support=20' % place, headers={"Accept":"application/json"}).json()
            resp_arr = dbpedia["Resources"]
            final_place = resp_arr[0]['@URI']
            place_query = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' + place + '&key=' + key)
            resp_json_payload = place_query.json()
            resp = resp_json_payload['results'][0]['geometry']['location']
            lat = resp['lat']
            lon = resp['lng']
            aux = {"@type": "schema:Place",
                   "@id": final_place,
                   "schema:name": place,
                   "schema:geo": { "@type": "schema:GeoCoordinates", "schema:latitude": lat, "schema:longitude": lon}
                    }
            entities_arr.append(aux) 
        elif len(places["PLACE"]) > 1:
            places_ = [x["BASE"] for x in places["PLACE"]]
            for place in places_:
                dbpedia = requests.get('http://model.dbpedia-spotlight.org/en/annotate?text=%s&confidence=0.2&support=20' % place, headers={"Accept":"application/json"}).json()
                resp_arr = dbpedia["Resources"]
                final_place = resp_arr[0]['@URI']
                place_query = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' + place + '&key=' + key)
                resp_json_payload = place_query.json()
                resp = resp_json_payload['results'][0]['geometry']['location']
                lat = resp['lat']
                lon = resp['lng']
                aux = {"@type": "schema:Place",
                   "@id": final_place,
                   "schema:name": place,
                   "schema:geo": { "@type": "schema:GeoCoordinates", "schema:latitude": lat, "schema:longitude": lon}
                    }
                entities_arr.append(aux)

    except Exception as e:
        print("fail")
        print(e)
        print("/fail")


    try:
        organization_names = []
        organizations = res_info["RESPONSE"]["ORGANIZATIONS"]
        if isinstance(organizations["ORGANIZATION"],dict):
            organization = organizations["ORGANIZATION"]["BASE"]
              
            aux = {"rdfs:subClassOf": "http://dbpedia.org/resource/" + organization,
                   "nif:anchorOf": organization}
            entities_arr.append(aux)
        elif len(organizations["ORGANIZATION"]) > 1:
            organizations_ = [x["BASE"] for x in organizations["ORGANIZATION"]]
            organization_names = []
            for organization in organizations_:
                aux = { "@type": "schema:Organization",
                        "@id": "http://dbpedia.org/resource/" + organization,
                       "schema:name": organization}
                entities_arr.append(aux)


    except:
        print("organizations")
        organization_names = []





        """
        if type(r["entries"][0]["entities"]) is dict:
            r["entries"][0]["entities"] = [r["entries"][0]["entities"]]
        for x, index in enumerate(r["entries"][0]["entities"]):
            index["nif:beginIndex"] = str(int(index["nif:beginIndex"]) + (REQUEST_LONG*k))
            index["nif:endIndex"] = str(int(index["nif:endIndex"]) + (REQUEST_LONG*k))
            if index["@type"].split('#')[-1] == 'ODENTITY_City':
                try:
                    geor = requests.get("https://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query=select+%3Fcoordinates+where+%7B%0D%0A%0D%0Adbr%3A{}+georss%3Apoint+%3Fcoordinates%0D%0A%0D%0A%7D&format=application%2Fsparql-results%2Bjson".format(index.get("marl:describesObject", "").split('/')[-1]))
                    coords = geor.json()['results']['bindings'][0]['coordinates']['value'].split()
                    index['latitude'] = coords[0]
                    index['longitude'] = coords[1]
                except (IndexError, json.decoder.JSONDecodeError):
                    pass
            if index["@type"].split('#')[-1] in ['ODENTITY_Person', 'ODENTITY_FullName']:
                try:
                    peopler = requests.get("https://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query=select+%3Fimage+where+%7B%0D%0A++dbr%3A{}+++dbo%3Athumbnail+%3Fimage%0D%0A%0D%0A%7D+LIMIT+100&format=application%2Fsparql-results%2Bjson&CXML_redir_for_subjs=121&CXML_redir_for_hrefs=&timeout=30000&debug=on&run=+Run+Query+".format(index.get("marl:describesObject", "").split('/')[-1]))
                    index['dbo:thumbnail'] = peopler.json()['results']['bindings'][0]['image']['value']
                except (IndexError, json.decoder.JSONDecodeError):
                    pass

            entities_arr.append(index)
    """
        

    
    i["sentiments"] = sentiments_arr
    i["entities"] = entities_arr

    return i