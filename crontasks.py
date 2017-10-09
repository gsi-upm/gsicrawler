import sched, time 
import os
import subprocess
import sys

s = sched.scheduler(time.time, time.sleep)

def runevery():
    if sys.argv[1] == "tutorial2":
        print("Tutorial 2 STARTED!")
        identifier = time.time()
        command = 'python -m luigi --module tutorialtask CrawlerTask  --url "{url}" --id "{id}" --num 10'.format(url="isis",id=identifier)
        subprocess.call(command.split(), shell= False)
    elif sys.argv[1] == "tutorial3":
        print("Tutorial 3 STARTED!")
        identifier = time.time()
        command = 'python -m luigi --module tutorialtask PipelineTask --index tutorial --doc-type news --url "{url}" --id "{id}" --num 10'.format(url="isis",id=identifier)
        subprocess.call(command.split(), shell= False)
    else:
        identifier = time.time()
        command = 'python -m luigi --module analysistask PipelineTask --index gsicrawler --doc-type news --url "{url}" --id "{id}" --analysisType "sentiments,emotions" --num {num}'.format(url="isis",id=identifier, num=int(sys.argv[1]))
        subprocess.call(command.split(), shell= False)
        s.enter(86400, 1, runevery) #Change here your cron time 
s.enter(2, 1, runevery)
s.run()