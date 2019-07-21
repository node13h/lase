.PHONY: all clean develop lint test

all:
	true

clean:
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	pipenv --rm

develop:
	pipenv install --dev

shell:
	pipenv shell

lint:
	pipenv run flake8 --max-line-length=119 --exclude=.git,__pycache__,.tox,.eggs,*.egg

test: lint
	pipenv run pytest --verbose

update-deps:
	pipenv update
