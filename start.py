import os
import subprocess

subprocess.Popen(["python","-m","senpy","-f","."], cwd=os.getcwd()+'/senpy')
os.system('python web.py')
