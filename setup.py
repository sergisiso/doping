#!/usr/bin/env python

'''Python Project Setup script. Used by easy_install and pip.'''
import os

from setuptools import setup, find_packages

# Project Metadata
NAME = "Doping"
VERSION = "0.1"
AUTHOR = ("Sergi Siso <sergi.siso@stfc.ac.uk>,"
          "Jeyan Thiyagalingam <t.jeyan@stfc.ac.uk>")
AUTHOR_EMAIL = ("sergi.siso@stfc.ac.uk")
# LICENSE=""
# URL=""
# DOWNLOAD_URL=""


# Requierements information
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(BASE_PATH, "src")
PACKAGES = find_packages(where=SRC_PATH)

REQUIREMENTS = []
DEV_REQUIREMENTS = ["pytest", "pytest-cov", "pycodestyle",
                    "Sphinx", "sphinx_rtd_theme"]

if __name__ == '__main__':
    setup(
        name=NAME,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        packages=PACKAGES,
        package_dir={'': 'src'},
        install_requires=REQUIREMENTS,
        extras_require={
            'dev': DEV_REQUIREMENTS
            },
        scripts=['bin/doping']
    )
