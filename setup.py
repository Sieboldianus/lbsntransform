# -*- coding: utf-8 -*-

"""Setuptools config file
"""

import sys
from setuptools import setup, find_packages

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    pass

VERSION_DICT = {}
with open("lbsntransform/version.py") as fp:
    exec(fp.read(), VERSION_DICT)  # pylint: disable=W0122
VERSION = VERSION_DICT['__version__']

setup(name="lbsntransform",
      version=VERSION,
      description="Location based social network (LBSN) "
                  "data structure format & transfer tool",
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      author='Alexander Dunkel',
      author_email='alexander.dunkel@tu-dresden.de',
      url='https://gitlab.vgiscience.de/lbsn/lbsntransform',
      license='GNU GPLv3 or any higher',
      packages=find_packages(
          include=['lbsntransform', 'lbsntransform.*']),
      include_package_data=True,
      install_requires=[
          'lbsnstructure>=0.5.1',
          'protobuf<=3.19.4',
          'psycopg2',
          'ppygis3',
          'shapely',
          'emoji',
          'requests',
          'geos',
          'numpy',
          'requests',
          'regex'
      ],
      extras_require={
          'nltk_stopwords':  [
              "nltk"  # python -c 'import nltk;nltk.download("stopwords")'
          ]
      },
      entry_points={
          'console_scripts': [
              'lbsntransform = lbsntransform.__main__:main'
          ]
      })
