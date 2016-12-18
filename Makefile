.PHONY: test

clean:
	find . -name \*.pyc -exec rm {\} \;

run: 
	python main.py

