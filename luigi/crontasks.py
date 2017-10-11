import sched, time 
import os
import subprocess
import analysistask

s = sched.scheduler(time.time, time.sleep)

def runevery():
    print("inside .py")

    identifier = time.time()
    website = 'twitter'
    command = 'python -m luigi --module analysistask PipelineTask --index gsicrawler --doc-type "{website}" --website {website} --url "{url}" --id {id} --analysisType "{analysisType}"'.format(url="isis",website=website,id=identifier,analysisType="sentiments,emotions")
    subprocess.call(command.split(), shell= False)
    s.enter(86400, 1, runevery) #Change here your cron time
s.enter(10, 1, runevery)
s.run()