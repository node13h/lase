PROJECT := lase
VERSION = $(shell cat VERSION)
SDIST_TARBALL = dist/$(PROJECT)-$(VERSION).tar.gz

export RELEASE_REMOTE := origin
export RELEASE_PUBLISH := 0

.PHONY: all clean mrproper develop shell lint build test update-deps e2e-test release-start release-finish sdist publish

all:

clean:
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -f Pipfile.lock

mrproper: clean
	-pipenv --rm

develop:
	pipenv install --dev

shell:
	pipenv shell

lint:
	pipenv run flake8 --max-line-length=119 --exclude=.git,__pycache__,.tox,.eggs,*.egg

build:
	python3 setup.py build

test: lint build
	pipenv run pytest --verbose

update-deps:
	pipenv update

e2e-test:
	pipenv run e2e/functional.sh

release-start: test e2e-test
	pipenv run lase $${RELEASE_REMOTE:+--remote "$${RELEASE_REMOTE}"} start $${RELEASE_VERSION:+--version "$${RELEASE_VERSION}"}

release-finish: test
	pipenv run lase $${RELEASE_REMOTE:+--remote "$${RELEASE_REMOTE}"} finish
	if [ "$${RELEASE_PUBLISH}" -eq 1 ]; then $(MAKE) -f $(lastword $(MAKEFILE_LIST)) publish; fi

sdist: $(SDIST_TARBALL)

$(SDIST_TARBALL):
	python3 setup.py sdist

publish: test e2e-test $(SDIST_TARBALL)
	pipenv run twine upload $(SDIST_TARBALL)
