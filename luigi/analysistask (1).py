import datetime
import json
import random
import imp
import re
import requests
import os
from rdflib import Graph, plugin
from rdflib.serializer import Serializer

import luigi
from luigi.contrib.esindex import CopyToIndex
from scrapy.crawler import CrawlerProcess
from scrapers.foursquare import FourSquareSpider
import subprocess
import scraperReddit

class ScrapyTask(luigi.Task):
    """
    Generates a local file containing 5 elements of data in JSON format.
    """

    #: the date parameter.

    #date = luigi.DateParameter(default=datetime.date.today())
    #field = str(random.randint(0,10000)) + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    
    search = luigi.Parameter()

    id = luigi.Parameter()

    website = luigi.Parameter()

    analysisType = luigi.Parameter()


    def run(self):
        """
        Writes data in JSON format into the task's output target.
        The data objects have the following attributes:
        * `_id` is the default Elasticsearch id field,
        * `text`: the text,
        * `date`: the day when the data was created.
        """
        #today = datetime.date.today()
        print(self.website, self.analysisType)
        filePathA = '/tmp/articles-%s.json' % self.id
        filePathC = '/tmp/comments-%s.json' % self.id
        #scraperImported = imp.load_source(self.website, 'scrapers/%s.py' % (self.website))
        #scraperImported.startScraping(self.url, filePath)
        print(self.url, filePath)
        if self.website == 'reddit':
            #Get the articles
            scraperReddit.getArticles(search = search, limit = 50, filePath = filePathA)
            scraperReddit.getComments(articlesJSON = filePathA, filePath = filePathA)
            #Get the comments

            
        if self.website == 'amazon':
            m = re.search("\/product\/.*\/", self.url)
            try:
                if m:
                    str = m.group(0)
                    amazon_id = str.split('/')[2]
            except:
                pass
            m = re.search("\/dp\/.*\/", self.url)
            try:
                if m:
                    str = m.group(0)
                    amazon_id = str.split('/')[2]
            except:
                pass
            try:
                self.url.index("amazon.com")
                domain = ".com"
            except:
                domain = ".es"
            command = 'scrapy runspider -a domain={domain} -a amazon_id={amazon_id} -a filePath={filePath} scrapers/spiders/{website}.py'.format(domain=domain,amazon_id=amazon_id,filePath=filePath,website=self.website)
        else:    
            command = 'scrapy runspider -a url={url} -a filePath={filePath} --nolog scrapers/spiders/{website}.py'.format(url=self.url,filePath=filePath,website=self.website)
        print(command)
        subprocess.call(command.split(), shell= False)    


    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on the local filesystem.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return [luigi.LocalTarget(path='/tmp/articles-%s.json' % self.id), luigi.LocalTarget(path='/tmp/comments-%s.json' % self.id)]


class AnalysisTaskArticles(luigi.Task):
    """
    Generates a local file containing 5 elements of data in JSON format.
    """

    #: the date parameter.

    #date = luigi.DateParameter(default=datetime.date.today())
    #field = str(random.randint(0,10000)) + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    
    url = luigi.Parameter()

    id = luigi.Parameter()

    website = luigi.Parameter()

    analysisType = luigi.Parameter()

    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.SenpyTask`
        :return: object (:py:class:`luigi.task.Task`)
        """
        return [luigi.LocalTarget(path='/tmp/articles-%s.json' % self.id), luigi.LocalTarget(path='/tmp/comments-%s.json' % self.id)]


    def run(self):
        """
        Writes data in JSON format into the task's output target.
        The data objects have the following attributes:
        * `_id` is the default Elasticsearch id field,
        * `text`: the text,
        * `date`: the day when the data was created.
        """

        #today = datetime.date.today()
        if(self.website == 'reddit'):

            with self.output().open('w') as output:
                with self.input()[0].open('r') as infile:
                    for lineAux in infile:
                        line = json.loads(lineAux)
                        if 'sentiments' in self.analysisType:
                            r = requests.get('http://test.senpy.cluster.gsi.dit.upm.es/api/?algo=sentiment-tass&i=%s' % line['title'])
                            response = r.content.decode('utf-8')
                            response_json = json.loads(response)
                            line["sentiment"] = response_json["entries"][0]["sentiments"][0]["marl:hasPolarity"].split(":")[1]   
                            line["polarity"] = response_json["entries"][0]["sentiments"][0]["marl:polarityValue"]
                            output.write(json.dumps(line))
                            output.write('\n')
                        if 'emotions' in self.analysisType:    
                            r = requests.get('http://test.senpy.cluster.gsi.dit.upm.es/api/?algo=emotion-anew&i=%s' % line['title'])
                            response = r.content.decode('utf-8')
                            response_json = json.loads(response)
                            line["emotion"] = response_json["entries"][0]["emotions"][0]["onyx:hasEmotion"]["onyx:hasEmotionCategory"].split("#")[1]
                            output.write(json.dumps(line))
                            output.write('\n')


    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on the local filesystem.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return luigi.LocalTarget(path='/tmp/articles_analyzed-%s.json' % self.id)

class AnalysisTaskComments(luigi.Task):
    """
    Generates a local file containing 5 elements of data in JSON format.
    """

    #: the date parameter.

    #date = luigi.DateParameter(default=datetime.date.today())
    #field = str(random.randint(0,10000)) + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    
    url = luigi.Parameter()

    id = luigi.Parameter()

    website = luigi.Parameter()

    analysisType = luigi.Parameter()

    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.SenpyTask`
        :return: object (:py:class:`luigi.task.Task`)
        """
        return [luigi.LocalTarget(path='/tmp/articles-%s.json' % self.id), luigi.LocalTarget(path='/tmp/comments-%s.json' % self.id)]


    def run(self):
        """
        Writes data in JSON format into the task's output target.
        The data objects have the following attributes:
        * `_id` is the default Elasticsearch id field,
        * `text`: the text,
        * `date`: the day when the data was created.
        """

        #today = datetime.date.today()
        if(self.website == 'reddit'):
            with self.output().open('w') as output:
                with self.input()[1].open('r') as infile:
                    for lineAux in infile:
                        line = json.loads(lineAux)
                        if 'sentiments' in self.analysisType:
                            r = requests.get('http://test.senpy.cluster.gsi.dit.upm.es/api/?algo=sentiment-tass&i=%s' % line['body'])
                            response = r.content.decode('utf-8')
                            response_json = json.loads(response)
                            line["sentiment"] = response_json["entries"][0]["sentiments"][0]["marl:hasPolarity"].split(":")[1]   
                            line["polarity"] = response_json["entries"][0]["sentiments"][0]["marl:polarityValue"]   
                        if 'emotions' in self.analysisType:    
                            r = requests.get('http://test.senpy.cluster.gsi.dit.upm.es/api/?algo=emotion-anew&i=%s' % line['body'])
                            response = r.content.decode('utf-8')
                            response_json = json.loads(response)
                            line["emotion"] = response_json["entries"][0]["emotions"][0]["onyx:hasEmotion"]["onyx:hasEmotionCategory"].split("#")[1]               


    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on the local filesystem.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return luigi.LocalTarget(path='/tmp/comments_analyzed-%s.json' % self.id)

class Elasticsearch(CopyToIndex):
    """
    This task loads JSON data contained in a :py:class:`luigi.target.Target` into an ElasticSearch index.
    This task's input will the target returned by :py:meth:`~.Senpy.output`.
    This class uses :py:meth:`luigi.contrib.esindex.CopyToIndex.run`.
    After running this task you can run:
    .. code-block:: console
        $ curl "localhost:9200/example_index/_search?pretty"
    to see the indexed documents.
    To see the update log, run
    .. code-block:: console
        $ curl "localhost:9200/update_log/_search?q=target_index:example_index&pretty"
    To cleanup both indexes run:
    .. code-block:: console
        $ curl -XDELETE "localhost:9200/example_index"
        $ curl -XDELETE "localhost:9200/update_log/_query?q=target_index:example_index"
    """
    #: date task parameter (default = today)
    url = luigi.Parameter()

    id = luigi.Parameter()

    analysisType = luigi.Parameter()

    website = luigi.Parameter()

    #: the name of the index in ElasticSearch to be updated.
    index = luigi.Parameter()
    #: the name of the document type.
    doc_type = luigi.Parameter()
    #: the host running the ElasticSearch service.
    host = str(os.environ.get('ES_ENDPOINT'))
    #: the port used by the ElasticSearch service.
    port =  int(os.environ.get('ES_PORT'))

    print(host,port)
    
    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.SenpyTask`
        :return: object (:py:class:`luigi.task.Task`)
        """
        return AnalysisTask(self.url, self.id, self.website, self.analysisType)
  
if __name__ == "__main__":
    #luigi.run(['--task', 'Elasticsearch'])
    luigi.run(  )
