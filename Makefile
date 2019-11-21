# List non-file related targets else they will be monitored by make
.PHONY: hello dbuild dbash dviz clean
hello:
	@echo ">>> hello world"

dviz:
	# run viz
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