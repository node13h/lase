# MIT license
# Copyright 2019 Sergej Alikov <sergej.alikov@gmail.com>

import re

from semver import VersionInfo

RE_PRERELEASE_NUM = r'^([a-zA-Z-_]+)?(\d+)$'
RE_SNAPSHOT = r'^(.*?)(-SNAPSHOT)?$'


def from_file(file_path):
    with open(file_path, 'r') as f:
        return f.read().strip()


def to_file(version, file_path):
    with open(file_path, 'w') as f:
        f.write('{}\n'.format(version))


def next_dev(version):
    match = re.match(RE_SNAPSHOT, version)

    if not match:
        raise RuntimeError('Unsupported version {}'.format(version))

    v = VersionInfo.parse(match[1])

    major = v.major
    minor = v.minor
    patch = v.patch

    prerelease = []

    match = re.match(RE_PRERELEASE_NUM, str(v.prerelease))

    if match:
        prerelease_num = int(match[2])
        prerelease.append(''.join(
            filter(None, [match[1], str(prerelease_num + 1)])))
    else:
        patch = patch + 1

    prerelease.append('SNAPSHOT')

    version = '{}.{}.{}-{}'.format(major, minor, patch, '-'.join(prerelease))

    return version


def release(version):
    match = re.match(RE_SNAPSHOT, version)

    if match:
        return match[1]
    else:
        raise RuntimeError('Unsupported version {}'.format(version))
