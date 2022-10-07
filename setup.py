#!/usr/bin/env python
from ensurepip import version
from pathlib import Path
import os
from setuptools import setup
from glob import glob

_dir = Path(__file__).resolve().parent

with open(f"{_dir}/README.md") as f:
    long_desc = f.read()

#with open(f"{_dir}/VERSION") as f:
#    version = f.read()
#    __version__ = version

setup(
    name="pagurus",
    description="Wrapper for getting process information.",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/tylern4/pagurus",
    author="Nick Tyler",
    author_email="tylern@lbl.gov",
    version='1.0.2',
    scripts=glob('bin/*'),
    install_requires=[
        'psutil==5.8.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.7",
)
