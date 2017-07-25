What is GSI Crawler?
----------------

GSI Crawler [#f1]_ is an innovative and useful framework which enables to examine social networks and opinion websites by applying sentiment and emotion analysis techniques. Some of the available platforms are FourSquare and Amazon. The user interacts with the tool through a web interface, selecting the analysis type that wants to carry out and the platform that is going to be examined. Depending on the platform  selected, some aditional resources may be required, such as the URL of the specific content that will be analyzed.

In this documentation we are going to introduce the framework presented above, detailing the global architecture of the project and explaining each module functionalities. Finally we will expose most relevant scenarios inside a case study in order to better understand the system itself. 

Architecture
============

Overview
~~~~~~~~~~~~~~~~~~~~~

GSI Crawler environment is divided in four main modules, each one is focused in one concrete task:

* **Visualisation**, the main function of this module is to represent processed data and display the analysis result, being accessible and interactive. This visualisation is mainly structured in a dashboard, where are represented the results obtained from independent platform queries. The dashboard itself is divided in other components (Polymer Web Components) that globally compound the webpage and redirects the user activity flow.

* **Tasks Server**, is a remote server that handle every user request, processing it using Luigi. Luigi is used as an orchestrator to build sequences of tasks named pipelines through analytic services and elasticSearch, in order to facilitate analysis. Luigi is also used to populate elasticSearch with data. The main server goal is to stack those pipelines inside a queue system, executing them and redirecting the response to the client side in order to be shown.

* **Senpy** [#f2]_ , is a tool originally developed to create sentiment and emotion analysis servers easily. Its goal is to provide a simple way to turn sentiment analysis algorithms into servers, acesing them by making HTTP requests with the text to be analyzed.

* **ElasticSearch** [#f3]_ , represents the persistence layer of the project and stores all the amount of data needed for the visualisation. Once a request is made, the consequent response will be stored in elasticSearch, assigning a valid index so it can be displayed when the task has ended up.


In this figure is a detailed view of the architecture described above:


.. image:: images/arch.png
  :align: center


Modules
~~~~~~~~~~~~~~~~~~~~~

Visualisation - Polymer Web Components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
As we explained in section before, the GSI Crawler framework uses a webpage based on Polymer web components to interact with all the functionalities offered by the tool. These Polymer Web Components are simply independent submodules that can be grouped each other to build the general dashboard interface. In this section we are going to present those components which actively participate in the main application workflow.

The GSI Crawler web interface looks like the image presented below,

.. image:: images/gsicrawler-default-interface.png
  :align: center

Inside this user interface we can notice several interesting components represented in the figure:

.. image:: images/floating-button.png
  :align: left

**Begin to explore** : This is the main input element within the web interface and enables to request a new analysis task for any available platform. It also needs a certain reference about the product or place to be analyzed.

|
.. image:: images/floating-button-platforms.png
  :align: left

**Available platforms** : Due to the high scalability offered by the GSI Crawler framework, it allows to perform analysis tasks inside several third party platforms or websites, such as social networks,online marketplaces, restaurants opinions or any other content. The tool has included by default the *FourSquare* and *Amazon* scrapers, being able to extract the opinions from a given link.

|

**Choose the analysis** : Once the content provider is selected, a card will pop up to select the analysis type and include the URL of the resource that is going to be treated.

.. image:: images/choose-analysis.png
  :align: center

|

**Observe the result** : Finally, the result will be presented in the dashboard showing the result for the requested analysis. 

.. image:: images/amazon-output.png
  :scale: 60%
  :align: center

|

**Profundize inside the result** The inferface also enables to go deeper inside the output obtained, being able to check the sentiment or emotion for each review, tweet or opinion, depending on the platform content. 

.. image:: images/amazon-output-reviews.png
  :align: center



Tasks Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The tasks server is responsible for managing the incoming workflow and set up a valid pipeline to obtain the resources, analyze them and save the result in elasticSearch to be displayed in the client application. Luigi framework is used as an orchestator to build sequence of tasks in order to facilitate the analysis process. 

The main goal of the server is to provide an API REST to add new tasks to the Luigi queue, saving the result in elasticSearch instance and retrieving it asyncronously from the client website. This web service has been implemented using Python Flask library, and contains multiple API calls to queuing tasks depending on the platform selected. 

All the pipelines has the same structure, represented in figure below

.. image:: images/picLuigi.png
  :scale: 100%
  :align: center

As is represented above, pipelines architecture is divided into three main steps, *Fetch*, *Analyze* and *Save*:

* **Fetch** refers to the process of obtain the reviews, tweet, opinion or whatever is desired to be analyzed, from the URL provided. Most of the times, this task involves webpage parsing, recognizing valuable information contained inside html tags and building a new JSON file with only these data. This process is commonly known as *scrapping* a website. In order to facilitate this filtering process exists multiple extensions or library that offers a well-formed structure to carry out this task being less tedious. Inside the Tasks Server, we have imported the Scrapy library in order to agilize the data mining process. Scrapy is an open source and collaborative framework for extracting the data you need from websites, in a fast, simple, yet extensible way. It is based on sub classes named *spiders*, where are contained the required methods to extract the information. The GSI Crawler application has available two spiders, one for each platform Foursquare and Amazon respectively. So to conclude, this task focus on extract the valuable data and generate a JSON which contains all the sentences that will analyze the following task in the pipeline.

* **Analyze** task is responsible of take the input JSON file generated by the previous task, parse it and analyze each text strign using Senpy remote server for it. Senpy service is based on HTTP calls, obtaining an analyzed result for the text attached in the request. Once the task has collected the analysis result, it generates another JSON containing the original sentence and its analysis result.

* **Save** process consists on store the JSON generated previously which contains the analysis result inside elasticSearch instance. ElasticSearch is a distributed, RESTful search and analytics engine capable of solving a growing number of use cases. As the heart of the Elastic Stack, it centrally stores the data so you can discover the expected and uncover the unexpected. To carry put the saving process its necessary to provide two arguments, the **index**, which represents the elastic index where the information will be saved, and the **doc type**, which allows to categorize information that belongs to the same index. It exists a third parameter which is the **id** of the query, but it is automatically generated by default.

To better understand these concepts, we are going to give a clear example that shows how the storing process works internally. Imagine that the user requests a **sentiment** analysis for a certain **Amazon product**. One elasticSearch parameters approach that would fit could be, **amazon** as the elasticSearch *index*, **sentiment** as the *doc type* because there could exist an emotion or even a fake analysis for the same platform, and lastly the *id* that could be the **datetime** when the task request was triggered.

Once the Luigi orchestator has been explained, we will conclude this section detailing how the server behaves when it receives a user request, and what parameters are mandatory to run the operation. The RESTful API workflow is shown in diagram below:

.. image:: images/task-diagram.png
  :align: center


Senpy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Elastic Seach
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. rubric:: References

.. [#f1] José Emilio Carmona. (2016). Development of a Social Media Crawler for Sentiment Analysis.
.. [#f2] J. Fernando Sánchez-Rada, Carlos A. Iglesias, Ignacio Corcuera-Platas & Oscar Araque (2016). Senpy: A Pragmatic Linked Sentiment Analysis Framework. In Proceedings DSAA 2016 Special Track on Emotion and Sentiment in Intelligent Systems and Big Social Data Analysis (SentISData).
.. [#f3] http://elastic.co.

