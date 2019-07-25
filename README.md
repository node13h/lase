# lase - Gitflow release tool


## Installing

```sh
pip install lase
```


## Using

Prerequisites:

- Git-based project with `master` and `develop` branches present, and Maven-style version
  number in the `VERSION` file


See `lase --help` for the list of all options.


### Starting a release of your project with remote operation enabled

```sh
cd /path/to/project/git/repo
lase --remote origin start
```

The above command will, and create the `release/X.Y.Z` release branch where `X.Y.Z` is the version
being released, bumping the version in the `VERSION` file on the `develop` branch at the same time.

After reviewing the diff between the release and `master` branches proceed to the finish step below.

### Finishing a release of a your project with remote operation enabled

```sh
cd /path/to/project/git/repo
lase --remote origin finish
```


## Developing

Prerequisites:

- Python 3
- pipenv

Initialize a virtualenv with dev dependencies installed:

```sh
make develop
```


### Running unit-tests

```sh
make test
```


### Running E2E tests

Prerequisites:

- [Shelter](https://github.com/node13h/shelter)

```sh
make e2e-test
```


### Starting a release

Variables:

- `RELEASE_REMOTE` set to the name of the Git remote. Set to empty to disable pushes to
remote. Default value: `origin`
- `RELEASE_VERSION` override the release version, or leave empty to release the current
snapshot (`-SNAPSHOT` will be stripped off). Empty by default

```sh
make release-start
```


### Finishing a release

Variables:

- `RELEASE_REMOTE` set to the name of the Git remote. Set to empty to disable pushes to
remote. Default value: `origin`
- `RELEASE_PUBLISH` - set to `1` to enable publishing of the sdist tarball after the release`

```sh
make release-finish
```


### Building and publishing the source distribution for the version X.Y.Z:

```sh
git checkout X.Y.Z
make publish
```
