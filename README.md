# LBSNTRANSFORM

A python package that uses the [common lbsn data structure concept] (ProtoBuf) to import, transform and export Social Media data such as Twitter.

## Description

This tool will read JSON strings from a Postgres Database or local folder and map the Social Media Endpoints (e.g. Twitter)  
to the common [LBSN Interchange Structure](https://gitlab.vgiscience.de/lbsn/concept) in ProtoBuf. Output can be either a Postgres Database or local CSV.
The tool can also be imported to other Python projects with `import lbsntransform` for on-the-fly conversion.

## Quick Start

You can install the package with all its dependencies directly from the Git Repository:

`pip install --upgrade git+git://gitlab.vgiscience.de:lbsn/lbsntransform.git`

(Note: A PyPi package distribution is planned)

.. or, for non-developers, simply download the latest build and run with custom args,  
e.g. with the following args LBSNTRANSFORM will 
- read local json from /01_Input/  
- and store lbsn records as CSV and ProtoBuf in /02_Output/  

```python
lbsntransform.exe --LocalInput 1 --LocalFileType '*.json' --transferlimit 1000 --CSVOutput
```

For a full list of possible input args and descriptions see [config.py](/lbsntransform/configconfig.py).

## Built With

* [lbsnstructure](https://gitlab.vgiscience.de/lbsn/concept) - A common language independend and cross-network social-media datascheme
* [protobuf](https://github.com/google/protobuf) - Google's data interchange format
* [psycopg2](https://github.com/psycopg/psycopg2) - Python-PostgreSQL Database Adapter
* [ppygis3](https://github.com/AlexImmer/ppygis3) - A PPyGIS port for Python
* [shapely](https://github.com/Toblerity/Shapely) - Geometric objects processing in Python
* [emoji](https://github.com/carpedm20/emoji/) - Emoji handling in Python

## Contributing

Field mapping from and to ProtoBuffers from different Social Media sites is provided in [lbsntransform\classes\field_mapping.py].  
As an example, a mapping of Twitter json structure is given (see class `FieldMappingTwitter`). This class may be used to extend  
functionality to cover other networks such as Flickr or Foursquare.  

For development & testing, make a local clone of this repository 
`git clone git@gitlab.vgiscience.de:lbsn/lbsntransform.git`

..and create package in develop mode to symlink the folder to your  
Python's site-packages folder with:
`python setup.py develop`

Now you can run LBSNTRANSFORM in your shell with:
`lbsntransform --LocalInput 1 --LocalFileType '*.json' --transferlimit 1000 --CSVOutput`

or import the package to other python projects with
`import lbsntransform`

## Versioning and Changelog, and Download

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](/tags). 
Latest version is [0.1.4](/tags/v0.1.4). The latest windows build is available for download [here](https://cloudstore.zih.tu-dresden.de/index.php/s/MqtlCyqLbxmnnxr/download).
For all other systems use cx_freeze to build executable:

`python cx_setup.py build`

## Authors

* **Alexander Dunkel** - Initial work

See also the list of [contributors](/contributors).

## License

This project is licensed under the GNU GPLv3 or any higher - see the [LICENSE.md](LICENSE.md) file for details