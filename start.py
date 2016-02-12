import os

os.chdir('senpy')
os.spawnl(os.P_NOWAIT, 'python -m senpy -f .')
os.chdir('..')
os.system('python web.py')