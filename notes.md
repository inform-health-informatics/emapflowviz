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