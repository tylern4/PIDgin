#!/usr/bin/env python
from pathlib import Path
import os
from setuptools import setup
from glob import glob

_dir = Path(__file__).resolve().parent

with open(f"{_dir}/README.md") as f:
    long_desc = f.read()


print(glob('bin/*'))

setup(
    name="pagurus",
    description="Wrapper for getting process information.",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/tylern4/pagurus",
    author="Nick Tyler",
    author_email="tylern@lbl.gov",
    version='0.1.2',
    scripts=glob('bin/*'),
    install_requires=[
        'psutil==5.8.0',
        'matplotlib',
        'pandas'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.7",
)
