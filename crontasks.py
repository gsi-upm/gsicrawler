import sched, time 
import os
import subprocess
import sys

s = sched.scheduler(time.time, time.sleep)

def main(args):
    print("Calling main with: ", args)
    if len(args) > 0 and args[0] == "tutorial2":
        print("Tutorial 2 STARTED!")
        identifier = time.time()
        command = 'python -m luigi --module tutorialtask CrawlerTask  --url "{url}" --id "{id}"'.format(url="isis",id=identifier)
        subprocess.call(command.split(), shell= False)
    elif len(args) > 0 and  args[0] == "tutorial3":
        print("Tutorial 3 STARTED!")
        identifier = time.time()
        command = 'python -m luigi --module tutorialtask PipelineTask --index tutorial --doc-type news --url "{url}" --id "{id}"'.format(url="isis",id=identifier)
        subprocess.call(command.split(), shell= False)
    elif len(args) > 0 and args[0] == "cron":
        print(args[1:])
        s.enter(2, 1, cron, [args[1:]])
        s.run()
    else:
        identifier = time.time()
        command = 'python -m luigi --module analysistask PipelineTask --index gsicrawler --doc-type news --url "{url}" --id "{id}" --analysisType "sentiments,emotions" --num {num}'.format(url=str(args[1]),id=identifier, num=int(args[0]))
        subprocess.call(command.split(), shell= False)


def cron(arg):
    main(arg)
    s.enter(86400, 1, cron, arg) #Change here your cron time

main(sys.argv[1:])

