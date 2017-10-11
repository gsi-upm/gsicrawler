import datetime
import json
import random
import imp
import re
import requests
import os
import time
from rdflib import Graph, plugin
from rdflib.serializer import Serializer

import luigi
from luigi.contrib.esindex import CopyToIndex
import subprocess
from scrapers.tutorial2 import retrieveCnnNews
from scrapers.tutorial3 import retrieveCnnNews as retrieveCnnNewsT3


ES_ENDPOINT = os.environ.get('ES_ENDPOINT')
ES_PORT = os.environ.get('ES_PORT')
FUSEKI_PORT = os.environ.get('FUSEKI_PORT')
FUSEKI_ENDPOINT = os.environ.get('FUSEKI_ENDPOINT')

class CrawlerTask(luigi.Task):
    """
    Generates a local file containing 5 elements of data in JSON format.
    """

    #: the date parameter.

    #date = luigi.DateParameter(default=datetime.date.today())
    #field = str(random.randint(0,10000)) + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    
    url = luigi.Parameter()

    id = luigi.Parameter()

    def run(self):
        """
        Writes data in JSON format into the task's output target.
        The data objects have the following attributes:
        * `_id` is the default Elasticsearch id field,
        * `text`: the text,
        * `date`: the day when the data was created.
        """
        #today = datetime.date.today()
        filePath = '/tmp/_scrapy-%s.json' % self.id
        #scraperImported = imp.load_source(self.website, 'scrapers/%s.py' % (self.website))
        #scraperImported.startScraping(self.url, filePath)
        print(self.url, filePath)
        retrieveCnnNews(self.url, 10, filePath)
        #retrieve_tweets(self.url, filePath, 10)

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on the local filesystem.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return luigi.LocalTarget(path='/tmp/_scrapy-%s.json' % self.id)

class CrawlerTaskT3(luigi.Task):
    """
    Generates a local file containing 5 elements of data in JSON format.
    """

    #: the date parameter.

    #date = luigi.DateParameter(default=datetime.date.today())
    #field = str(random.randint(0,10000)) + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    
    url = luigi.Parameter()

    id = luigi.Parameter()

    def run(self):
        """
        Writes data in JSON format into the task's output target.
        The data objects have the following attributes:
        * `_id` is the default Elasticsearch id field,
        * `text`: the text,
        * `date`: the day when the data was created.
        """
        #today = datetime.date.today()
        filePath = '/tmp/_scrapy-%s.json' % self.id
        #scraperImported = imp.load_source(self.website, 'scrapers/%s.py' % (self.website))
        #scraperImported.startScraping(self.url, filePath)
        print(self.url, filePath)
        retrieveCnnNewsT3(self.url, 10, filePath)
        #retrieve_tweets(self.url, filePath, 10)

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on the local filesystem.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return luigi.LocalTarget(path='/tmp/_scrapy-%s.json' % self.id)

class FusekiTask(luigi.Task):
    """
    This task loads JSON data contained in a :py:class:`luigi.target.Target` and insert into Fuseki platform as a semantic 
    """
     #: date task parameter (default = today)
    url = luigi.Parameter()

    id = luigi.Parameter()

    #file = str(random.randint(0,10000)) + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.SenpyTask` 
        :return: object (:py:class:`luigi.task.Task`)
        """
        return CrawlerTaskT3(self.url, self.id)

    def run(self):
        """
        Receive data from Senpy and is indexed in Fuseki
        """

        f = []

        with self.input().open('r') as infile:
            with self.output().open('w') as outfile:
                for i, line in enumerate(infile):
                    self.set_status_message("Lines read: %d" % i)
                    w = json.loads(line)
                    f.append(w)
                f = json.dumps(f)
                self.set_status_message("JSON created")
                #print(f)
                #g = Graph().parse(data=f, format='json-ld')
                r = requests.put('http://{fusekiend}:{fusekiport}/tutorial/data'.format(fusekiend=FUSEKI_ENDPOINT,fusekiport=FUSEKI_PORT),
                    headers={'Content-Type':'application/ld+json'},
                    data=f)
                self.set_status_message("Data sent to fuseki")
                outfile.write(f)

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on the local filesystem.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return luigi.LocalTarget(path='/tmp/_n3-%s.json' % self.id)



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

    #: the name of the index in ElasticSearch to be updated.
    index = luigi.Parameter()
    #: the name of the document type.
    doc_type = luigi.Parameter()
    #: the host running the ElasticSearch service.
    host = ES_ENDPOINT
    #: the port used by the ElasticSearch service.
    port = ES_PORT
  
    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.SenpyTask`
        :return: object (:py:class:`luigi.task.Task`)
        """
        return CrawlerTaskT3(self.url, self.id)


class PipelineTask(luigi.Task):
  
    #: date task parameter (default = today)
    url = luigi.Parameter()

    id = luigi.Parameter()

    #: the name of the index in ElasticSearch to be updated.
    index = luigi.Parameter()
    #: the name of the document type.
    doc_type = luigi.Parameter()
    #: the host running the ElasticSearch service.
    host = ES_ENDPOINT
    #: the port used by the ElasticSearch service.
    port = ES_PORT
   
    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.SenpyTask`
        :return: object (:py:class:`luigi.task.Task`)
        """

        yield FusekiTask(self.url, self.id)
        
        index=self.index
        doc_type=self.doc_type

        yield Elasticsearch(self.url, self.id, index, doc_type)

if __name__ == "__main__":
    #luigi.run(['--task', 'Elasticsearch'])
    luigi.run(    )
