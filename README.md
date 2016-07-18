![Ewe Tasker Logo](./front-end/app/images/logo.png)

This website is useful to the analysis of comments from external aplications like Yelp, Amazon, Twitter, Youtube, Facebook, TripAdvisor an Foursquare. The user will choose
the type of analysis he wants to carry out (Emotions, Sentiments or Fake Analysis)
and he will also supply, for instance, a direct URL to a Yelp’s Business, the
id of a Facebook’s Fan Page or a YouTube’s Video. GSI Crawler will download the
comments belonging to this element and, later, the pertinent analysis will be run
using the <a href="https://github.com/gsi-upm/senpy">Senpy</a> tool. Once the analysis is finished, a summary of the result will be
shown and the possibility of review each comment one by one will be also offered.

*Note: Facebook and Tripadvisor analysis are not currently available.*

#Installation
First of all, clone the git project locally and access to gsicrawler directory.
```
git clone https://github.com/gsi-upm/gsicrawler.git

cd gsicrawler
```
#Run
Create the project docker image from Dockerfile
```
docker build -t "gsicrawler:dockerfile" .

```

Run your docker image locally in port 8888 and run the *start.py* script to initialize the gsicrawler server
```
docker run -p 8888:8888 -t -i gsicrawler:dockerfile python start.py

```

Access from your browser and execute your analysis
```
http://localhost:8888
```

#References
<a href="http://www.gsi.dit.upm.es/index.php/es/investigacion/publicaciones?view=publication&task=show&id=394">[1]</a>*"Development of a Social Media Crawler for Sentiment Analysis"*

<a href="https://github.com/gsi-upm/senpy">[2]</a>*"Senpy Documentation"*
