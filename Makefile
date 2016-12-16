.PHONY: test

clean:
	find . -name \*.pyc -exec rm {\} \;

include environment.mk

run:	
	python main.py
