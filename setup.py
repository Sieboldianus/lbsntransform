# -*- coding: utf-8 -*-

from setuptools import setup
import sys

with open('README.md') as f:
    long_description = f.read()
     
     
## setuptools dev
setup(  name = "lbsntransform",
        version = "0.1.4",
        description = "lbsn data structure format & transfer tool",
        long_description=long_description,
        long_description_content_type='text/markdown',
        author='Alexander Dunkel',
        author_email='alexander.dunkel@tu-dresden.de',
        url='https://gitlab.vgiscience.de/lbsn/lbsn-twitter-json-mapping',
        license='GNU GPLv3 or any higher',
        packages=['lbsntransform'],
        install_requires=[
            'lbsnstructure',
            'protobuf',
            'psycopg2',
            'ppygis3',
            'shapely',
            'emoji'
        ],
        entry_points={
        'console_scripts': [
            'lbsntransform = lbsntransform.__main__:main'
        ]
        })