class ScrapyTask(luigi.Task):
    """
    Generates a local file containing 5 elements of data in JSON format.
    """ 
    url = luigi.Parameter()

    id = luigi.Parameter()

    analysisType = luigi.Parameter()

    def run(self):
        """
        Writes data in JSON format into the task's output target.
        The data objects have the following attributes:
        * _id is the default Elasticsearch id field,
        * text: the text,
        * date: the day when the data was created.
        """
        filePath = '/tmp/_scrapy-%s.json' % self.id
        retrieveCnnNews(self.url, 10, filePath)
        retrieveNytimesNews(self.url, 10, filePath)

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on the local filesystem.
        :return: the target output for this task.
        :rtype: object (🇵🇾class:luigi.target.Target)
        """
        return luigi.LocalTarget(path='/tmp/_scrapy-%s.json' % self.id)



