# -*- coding: utf-8 -*-

from setuptools import setup
import sys

## setuptools dev
setup(  name = "lbsntransform",
        version = "0.1.4",
        description = "lbsn data structure format & transfer tool",
        author='Alexander Dunkel',
        url='https://gitlab.vgiscience.de/lbsn/lbsn-twitter-json-mapping',
        license='GNU GPLv3 or any higher',
        packages=['lbsntransform'],
        install_requires=[
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