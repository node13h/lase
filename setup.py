#!/usr/bin/env python3

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'VERSION')) as f:
    version = f.read().strip()


setup(
    name='lase',

    version=version,

    description='Gitflow release tool',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/node13h/lase',

    author='Sergej Alikov',
    author_email='sergej.alikov@gmail.com',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

    packages=find_packages(exclude=['tests']),
    include_package_data=True,

    # See https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'semver~=2.8',
    ],
    entry_points={
        'console_scripts': ['lase=lase:main'],
    },
)
