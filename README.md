# lase - Gitflow release tool


## Installing

```sh
pip install lase
```


## Using

Start a release:

```sh
lase start
```

Finish a release:

```sh
lase finish
```


## Developing

Prerequisites:

- Python 3
- pipenv


Initialize a virtualenv with dev dependencies installed:

```sh
make develop
```

Run unit-tests:

```sh
make test
```

Run functional tests (you'll need [Shelter](https://github.com/node13h/shelter) installed to run these tests):

```sh
make e2e-test
```

Start a release:

```sh
make release-start
```

Finish a release:

```sh
make release-finish
```

Buld and publish the source distribution for the version X.Y.Z:

```sh
git checkout X.Y.Z
make publish
```
