import urllib.request
import re
from newspaper import Article
import html.parser as htmlparser
import requests
parser = htmlparser.HTMLParser()

def retrieveAlJazeeraNews(search, num, filepath):

	#search = "isis"
	#results = 10

	url = "https://ajnsearch.aljazeera.com/SearchProxy.aspx?m=search&c=english&f=AJE_BS&s=as_q&q=" + search + "&p=0&r=" + str(num) + "&o=any&t=d&cnt=gsaSearch&target=gsaSearch"

	def clean(text):
		text = text.replace(u'\\u0026#39;','\'')
		text = text.replace(u'\\','')
		return(text)

	content = urllib.request.urlopen(url).read()


	tokens = str(content).split()
	urls = []
	headlines = []
	flag = 0
	aux_ = []

	#Headline extraction
	for word in tokens:
		if flag == 1:
			if len(re.findall(r"/a", word)) >0:
				flag = 0
				aux_.append(clean(word.split('u003c')[0][:-2]))
				headlines.append(' '.join(aux_))
				aux_ = []
			else:
				aux_.append(clean(word))
		if 'topics-sec-item-head' in word:
			flag = 1
			aux_.append(clean(word.split('003e')[1]))



	tokens = [word for word in tokens if 'https://www.aljazeera.com/news/' in word]
	tokens = [word.split('https://')[1] for word in tokens ]

	tokens = [word.split('.html')[0] for word in tokens]
	tokens = ['https://' + word + '.html' for word in tokens  ]
	#print(tokens)
	for token in tokens:
		if token not in urls:
			urls.append(token)

	news = []

	cnt = 0
	for url in urls:
		aux = {}
		a = Article(url)
		a.download()
		a.parse()
		aux["@type"] = "schema:NewsArticle"
		aux["@id"] = url
		aux["_id"] = url
		aux["schema:datePublished"] = a.publish_date
		#aux["schema:dateModified"] = a.publish_date
		aux["schema:articleBody"] = a.text
		aux["schema:about"] = a.keywords
		if len(a.authors) > 0:
			aux["schema:author"] =  'Al Jazeera'
		else:
			aux["schema:author"] =  'Al Jazeera'
		aux["schema:headline"] =  headlines[cnt]
		#print(a.text)
		aux["schema:search"] = search
		aux["schema:thumbnailUrl"] = a.top_image
		news.append(aux)
		html = requests.get(url).text
		#file = open(str(headlines[cnt]) + ".html",'w') 
		 
		#file.write(html)
		 
		#file.close() 
		cnt += 1
	#print(len(news))
	#print(news[-1])
	return news





