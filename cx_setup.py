# -*- coding: utf-8 -*-

from cx_Freeze import setup, Executable
import sys

# Derive Package Paths Dynamically
import os.path
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))

with open('VERSION') as version_file:
    version_var = version_file.read().strip()     
    
# Dependencies are automatically detected, but it can be fine tuned
#includes_mod = ['lbsntransform',
#                ]

excludes_mod = ['tkinter',
                'matplotlib',
                'IPython',
                'ipykernel',
                'jedi',
                'jinja2',
                'jupyter_client',
                'multiprocessing',
                'scipy',
                'numpy']
packages_mod = [
                'lbsnstructure>=0.2.6.211',
                'protobuf',
                'psycopg2',
                'ppygis3',
                'shapely',
                'emoji'
        ]
include_folders_files = [('scripts/00_TransferAll_Default.sh')
                    ]
build_exe_options = {'include_files': include_folders_files, "packages": packages_mod, "excludes": excludes_mod}
base = None
executables = [
    Executable('lbsntransform/__main__.py', base=base)
]
setup(  name = "lbsntransform",
        version = version_var,
        description = "Location based social network (LBSN) data structure format & transfer tool",
        author='Alexander Dunkel',
        url='https://gitlab.vgiscience.de/lbsn/lbsntransform',
        license='GNU GPLv3 or any higher',
        options = {'build_exe': build_exe_options },
        executables = executables,
    )