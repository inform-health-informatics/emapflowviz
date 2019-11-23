# List non-file related targets else they will be monitored by make
.PHONY: hello dreload  dbuild dbash dviz clean dkill dprune
hello:
	@echo ">>> hello world"
	echo "$(PWD)"

start_postgres:
	# pg_ctl does not behave for me unless I start from the server directory
	@echo ">>> run the following commands"
	@echo "cd ~/data/postgres"
	@echo "pg_ctl -D . restart"

dreload:
	@echo ">>> running app with /app as external directory"
	# rebuild then run in reload mode
	docker build \
		--build-arg HTTP_PROXY \
		--build-arg HTTPS_PROXY \
		--build-arg http_proxy \
		--build-arg https_proxy \
		-t mystar . 
	# dropping the d flag since I want to see what it's doing
	docker run -p 80:80 -v $(PWD)/app:/app mystar /start-reload.sh 

dviz:
	# run viz
	docker build \
		--build-arg HTTP_PROXY \
		--build-arg HTTPS_PROXY \
		--build-arg http_proxy \
		--build-arg https_proxy \
		-t mystar . 
	docker run -d -p 80:80  mystar  

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