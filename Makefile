VERSION = $(shell cat VERSION)

.PHONY: all clean develop shell lint test update-deps e2e-test release-start release-finish release sdist publish

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

e2e-test:
	pipenv run e2e/functional.sh

release-start: test e2e-test
	pipenv run releasy --remote origin start

release-finish:
	pipenv run releasy --remote origin finish

release: release-start release-finish

sdist: dist/releasy-$(VERSION).tar.gz

dist/releasy-$(VERSION).tar.gz:
	python3 setup.py sdist

publish:
	pipenv run twine upload dist/*
