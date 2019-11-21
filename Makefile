# List non-file related targets else they will be monitored by make
.PHONY: hello dreload  dbuild dbash dviz clean dkill dprune
hello:
	@echo ">>> hello world"

dreload:
	@echo ">>> running app with /app as external directory"
	# dropping the d flag since I want to see what it's doing
	# docker run -d -p 80:80 -v $(pwd):/app mystar /start-reload.sh
	docker run -p 80:80 -v $(pwd):/app mystar /start-reload.sh

dviz:
	# run viz
	docker build -t mystar . 
	docker run -p 80:80  mystar  

dbuild:
	# fresh build
	@echo ">>> rebuilding the docker image, and labelled mystar"
	docker build -t mystar . 
	docker image ls | grep mystar

dbash:
	@echo ">>> running a bash shell in the docker container"
	docker run -it mystar bash  

clean:
	# @ symbol stops the command being echoed itself
	@echo ">>> cleaning files from ./tmp"
	rm -rf tmp/* 

dkill:
	docker kill $(docker ps -q --filter ancestor=mystar )

dprune:
	# prune all containers older than a week that are not currently running
	docker container prune --filter "until=24h"
	# prune all images
	docker image prune -a --filter "until=24h"