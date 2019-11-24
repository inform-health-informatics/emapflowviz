# List non-file related targets else they will be monitored by make
.PHONY: hello dreload dhello dbuild dbash dbashv dviz clean dkill dprune

# HOSTIP=`ip -4 addr show scope global dev docker0 | grep inet | awk '{print $$2}' | cut -d / -f 1`
# HOSTIP="172.17.0.1"

hello:
	@echo ">>> hello world"
	echo "$(PWD)"
	# check that HOSTIP resolved OK
	# echo "$(HOSTIP)"

start_postgres:
	# pg_ctl does not behave for me unless I start from the server directory
	@echo ">>> run the following commands"
	@echo "cd ~/data/postgres"
	@echo "pg_ctl -D . restart"

dhello:
	@echo ">>> running hello app for debugging"
	@echo ">>> running app with /app as external directory"
	# delete __pycache__ using docker else don't have root privileges
	docker run -v $(PWD)/app:/app mystar rm -rf __pycache__
	# rebuild then run in reload mode
	docker build \
		--build-arg HTTP_PROXY \
		--build-arg HTTPS_PROXY \
		--build-arg http_proxy \
		--build-arg https_proxy \
		-t mystar . 
	# dropping the d flag since I want to see what it's doing
	docker run \
		--network host \
		--name test_mystar \
		-p 5901:5901 -p 80:80 -v $(PWD)/app:/app \
		-e PORT="5901" \
		-e MODULE_NAME="hello" \
		mystar /start-reload.sh 

dreload:
	@echo ">>> running app with /app as external directory"
	docker run -v $(PWD)/app:/app mystar rm -rf __pycache__
	# rebuild then run in reload mode
	docker build \
		--build-arg HTTP_PROXY \
		--build-arg HTTPS_PROXY \
		--build-arg http_proxy \
		--build-arg https_proxy \
		-t mystar . 
	# dropping the d flag since I want to see what it's doing
	docker run \
		-p 5901:80 -v $(PWD)/app:/app mystar /start-reload.sh 

dviz:
	# run viz
	docker run -v $(PWD)/app:/app mystar rm -rf __pycache__
	docker build \
		--build-arg HTTP_PROXY \
		--build-arg HTTPS_PROXY \
		--build-arg http_proxy \
		--build-arg https_proxy \
		-t mystar . 
	docker run -d -p 5901:80  mystar  

dbuild:
	# fresh build
	@echo ">>> rebuilding the docker image, and labelled mystar"
	docker build \
		--build-arg HTTP_PROXY \
		--build-arg HTTPS_PROXY \
		--build-arg http_proxy \
		--build-arg https_proxy \
		-t mystar . 
	docker image ls | grep mystar

dbash:
	@echo ">>> running a bash shell in the docker container"
	docker container run \
		mystar echo "$(DOCKER_HOST)"
	docker run \
		-it mystar bash  

dbashv:
	@echo ">>> running a bash shell in the docker container"
	@echo ">>> but post reload with the app directory mounted"
	docker run \
		-it -v $(PWD)/app:/app mystar bash  

clean:
	# @ symbol stops the command being echoed itself
	@echo ">>> cleaning files from ./tmp"
	rm -rf tmp/* 

dkill:
	# TODO FIXME
	# docker kill $(eval docker ps -q --filter ancestor=mystar)

dprune:
	# prune all containers older than a week that are not currently running
	docker container prune --filter "until=24h"
	# prune all images
	docker image prune -a --filter "until=24h"
