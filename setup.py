# -*- coding: utf-8 -*-

from setuptools import setup
import sys
#from cx_Freeze import setup as setup_cx, Executable

#Derive Package Paths Dynamically
#import os.path
#PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))

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
        ])

# Dependencies are automatically detected, but it might need fine tuning.
#build_exe_options = {"packages": ["os"], "excludes": []}
#includes_mod = ['google.protobuf',
#                'psycopg2',
#                'ppygis3',
#                'shapely',
#                'emoji',
#                'numpy',
#                'shutil',
#                'heapq',
#                ]

## CXFreeze build
#excludes_mod = ['tkinter',
#                'matplotlib',
#                'IPython',
#                'ipykernel',
#                'jedi',
#                'jinja2',
#                'jupyter_client',
#                'multiprocessing',
#                'scipy',
#                'numpy']
#packages_mod = [
#            'psycopg2',
#            'ppygis3',
#            'shapely',
#            'emoji',
#            'shutil',
#            'heapq'
#        ]
#include_folders_files = [('tests/00_TransferAll_Default.sh', '00_TransferAll_Default.sh')
#                        ]
#build_exe_options = {'include_files': include_folders_files, "packages": packages_mod, "excludes": excludes_mod}
#base = None
#executables = [
#    Executable('transferData.py', base=base)
#]
#setup(  name = "lbsnDataTransfer",
#        version = "0.1.4",
#        description = "lbsn data structure format & transfer tool",
#        author='Alexander Dunkel',
#        url='https://gitlab.vgiscience.de/lbsn/lbsn-twitter-json-mapping',
#        license='GNU GPLv3 or any higher',
#        options = {'build_exe': build_exe_options },
#        executables = executables)