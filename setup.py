# -*- coding: utf-8 -*-

from setuptools import setup
import sys

with open('README.md') as f:
    long_description = f.read()

with open('VERSION') as version_file:
    version_var = version_file.read().strip()     
     
## setuptools dev
setup(  name = "lbsntransform",
        version = version_var,
        description = "Location based social network (LBSN) data structure format & transfer tool",
        long_description=long_description,
        long_description_content_type='text/markdown',
        author='Alexander Dunkel',
        author_email='alexander.dunkel@tu-dresden.de',
        url='https://gitlab.vgiscience.de/lbsn/lbsntransform',
        license='GNU GPLv3 or any higher',
        packages=['lbsntransform'],
        install_requires=[
            'lbsnstructure>=0.2.6.211',
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