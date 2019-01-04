# -*- coding: utf-8 -*-

from setuptools import setup
import sys

with open('README.md') as f:
    long_description = f.read()

try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    pass

version = {}
with open("lbsntransform/version.py") as fp:
    exec(fp.read(), version)

setup(name="lbsntransform",
      version=version['__version__'],
      description="Location based social network (LBSN) "
                  "data structure format & transfer tool",
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Alexander Dunkel',
      author_email='alexander.dunkel@tu-dresden.de',
      url='https://gitlab.vgiscience.de/lbsn/lbsntransform',
      license='GNU GPLv3 or any higher',
      packages=['lbsntransform'],
      include_package_data=True,
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
