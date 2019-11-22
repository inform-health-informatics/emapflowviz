2019-11-20t223007
started with an empty directory
followed notes from https://realpython.com/intro-to-pyenv/#working-with-multiple-environments
set-up an isolated pyenv    

```bash
# I chose 3.7.4 because it was the most up-to-date non-dev version
pyenv install -v 3.7.4 # if not already installed
pyenv virtualenv 3.7.4 emapflowviz
# now set up .python-version which will automatically activate the environment when you cd in 
pyenv local emapflowviz
```

2019-11-20t224729
now switching to learn basics of FastAPI
https://fastapi.tiangolo.com/tutorial/intro/

```bash
pip install fastapi
# this command failed because it couldn't find a clang until I installed pyenv-which-ext
# see https://stackoverflow.com/a/52669973
pip install uvicorn
```

now try the hello world fastapi example
https://fastapi.tiangolo.com/tutorial/first-steps/

now try static files
https://fastapi.tiangolo.com/tutorial/static-files/

2019-11-22t005330
spent ages trying to fix the ws 403 error; failed
now gone back to the super simple gist
https://gist.github.com/akiross/a423c4e8449645f2076c44a54488e973
suggest that I start again with this; of note, this _is_ running in docker

2019-11-22t102703
fixed!
now let's just retest a simple d3 interaction

2019-11-22t155950
now need to see if I can get it to pull from an external postgres db
then deploy in docker on the GAE
