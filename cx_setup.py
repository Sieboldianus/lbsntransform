# -*- coding: utf-8 -*-

"""Setup config for cx_freeze (build)
"""


import os.path

from cx_Freeze import Executable, setup

# Derive Package Paths Dynamically
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))

VERSION_DICT = {}
with open("lbsntransform/version.py") as fp:
    exec(fp.read(), VERSION_DICT)  # pylint: disable=W0122
VERSION = VERSION_DICT['__version__']

EXCLUDES_MOD = ['tkinter',
                'matplotlib',
                'IPython',
                'ipykernel',
                'jedi',
                'jinja2',
                'jupyter_client',
                'multiprocessing',
                'scipy',
                'numpy']
PACKAGES_MOD = [
    'lbsnstructure>=0.5.1',
    'protobuf',
    'psycopg2',
    'ppygis3',
    'shapely',
    'emoji',
    'requests'
]
INCLUDE_FOLDERS_FILES = [('scripts/00_TransferAll_Default.sh')
                         ]
BUILD_EXE_OPTIONS = {'include_files': INCLUDE_FOLDERS_FILES,
                     "packages": PACKAGES_MOD, "excludes": EXCLUDES_MOD}
BASE = None
EXECUTABLES = [
    Executable('lbsntransform/__main__.py', base=BASE,
               targetName="lbsntransform.exe")
]
setup(name="lbsntransform",
      version=VERSION,
      description="Location based social network (LBSN) "
                  "data structure format & transfer tool",
      author='Alexander Dunkel',
      url='https://gitlab.vgiscience.de/lbsn/lbsntransform',
      license='GNU GPLv3 or any higher',
      options={'build_exe': BUILD_EXE_OPTIONS},
      executables=EXECUTABLES,
      )
