.PHONY: test

clean:
	find . -name \*.pyc -exec rm {\} \;

run: 
	python main.py

dockerize:
	docker rm -f splash
	docker build -t captive-portal .
	docker run --name splash -p 5000:80 -t captive-portal:latest
