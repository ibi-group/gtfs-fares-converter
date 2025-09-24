# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

setup(
    name="gtfs-fares-converter",
    version="0.1.0",
    description="converts GTFS fares v1 data to fares v2 data",
    license="MIT",
    author="miles-grant-ibigroup",
    packages=find_packages(),
    install_requires=[],
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.13",
    ]
)
