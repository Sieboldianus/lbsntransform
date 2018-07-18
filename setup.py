from setuptools import setup 

setup(  name = "lbsnDataTransfer",
        version = "0.1.4",
        description = "lbsn data structure format & transfer tool",
        author='Alexander Dunkel',
        url='https://gitlab.vgiscience.de/lbsn/lbsn-twitter-json-mapping',
        license='GNU GPLv3 or any higher',
        packages=['classes',
                  'config',
                  'lbsnstructure'],
        install_requires=[
            'protobuf',
            'psycopg2',
            'ppygis3',
            'shapely',
            'emoji',
            'numpy',
            'shutil',
            'heapq',
            'contextlib'
        ])