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
TODO: then deploy in docker on the GAE

2019-11-22t215252
set up the event loop so that it reads from the postgres database spontaneously (without the need to click)

2019-11-23t105950
now load initial data where time < current time
then recast loop so that it polls every second (but you can speed up to pretend to accelerate time)
and the query pulls all new data
now recast loop so that it simulates


2019-11-24t185423 now works wrt UCLH GAE environment
next task it to make it work with a realistic visit_detail table
then build a realisit simulation
...
or switch from this for now and work with the measurement table and the moving averages

2019-11-25t182637
so I think it will be much easier to get a MWE with the measurements table
though I note this is not working reliably in omop_live so should construct from emap_star
maybe you could just count fact types as they are stored in star?
rather than waste time this evening trying to make the connection via the VPN to check; let's just assume that you can with some SQL magic recreate a stream of measurements with timestamps