VERSION = $(shell cat VERSION)

.PHONY: all clean develop shell lint test update-deps e2e-test release-start release-finish release sdist publish

all:
	true

clean:
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	pipenv --rm || true

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
	pipenv run lase --remote origin start $${RELEASE_VERSION:+--version "$${RELEASE_VERSION}"}

release-finish:
	pipenv run lase --remote origin finish

release: release-start release-finish

sdist: dist/lase-$(VERSION).tar.gz

dist/lase-$(VERSION).tar.gz:
	python3 setup.py sdist

publish: test e2e-test dist/lase-$(VERSION).tar.gz
	pipenv run twine upload dist/lase-$(VERSION).tar.gz
