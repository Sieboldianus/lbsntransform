![PyPI version](https://lbsn.vgiscience.org/lbsntransform/pypi.svg) ![pylint](https://lbsn.vgiscience.org/lbsntransform/pylint.svg) ![pipeline](https://lbsn.vgiscience.org/lbsntransform/pipeline.svg)

# LBSNTransform

A python package that uses the [common location based social network (LBSN) data structure concept](https://pypi.org/project/lbsnstructure/) (ProtoBuf) to import, transform and export Social Media data such as Twitter and Flickr.

## Motivation

The goal is to provide a common interface to handle Social Media Data, without custom adjustment to the myriad API Endpoints available. As an example, consider the ProtoBuf spec "Post", which can be a Tweet on Twitter, a Photo shared on Flickr, or a post on Reddit. This tool is based on a 4-Facet conceptual framework for LBSN, introduced in a paper by [Dunkel et al. (2018)](https://www.tandfonline.com/doi/full/10.1080/13658816.2018.1546390). In addition, the GDPR directly requests Social Media Network operators to allow users to transfer accounts and data inbetween services.
While there are attempts by Google, Facebook etc. (see data-transfer-prject), it is not currently possible. With this structure concept, a primary motivation is to systematically characterize LBSN data aspects in a common scheme that enables privacy-by-design for connected software, data handling and database design.

## Description

This tool enables data import from a Postgres database, JSON, or CSV and export to CSV, [LBSN ProtoBuf](https://gitlab.vgiscience.de/lbsn/concept) or a [LBSN prepared Postgres Database](https://gitlab.vgiscience.de/lbsn/database-setup).
The tool will map Social Media endpoints (e.g. Twitter tweets) to a common [LBSN Interchange Structure](https://gitlab.vgiscience.de/lbsn/concept) format in ProtoBuf. The tool can also be imported to other Python projects with `import lbsntransform` for on-the-fly conversion. 


## Quick Start

You can install the newest version with all its dependencies directly from the Git Repository:
```shell
pip install --upgrade git+git://gitlab.vgiscience.de:lbsn/lbsntransform.git
```

or install latest release using pip:
```shell
pip install lbsntransform
```

.. for non-developers, another option is to simply download the latest build and run with custom args,  
e.g. with the following command line args

```shell
lbsntransform.exe --Origin 3 --LocalInput --LocalFileType '*.json' --transferlimit 1000 --CSVOutput
```

.. with the above input args, the the tool will: 
- read local json from /01_Input/  
- and store lbsn records as CSV and ProtoBuf in /02_Output/  

A full list of possible input args is available with `lbsntransform --help` [config.py](/lbsntransform/config/config.py):

```
usage: lbsntransform [-h] [-sO ORIGIN] [-lI] [-lT LOCALFILETYPE]
                     [-iP INPUTPATH] [-iS] [-pO DBPASSWORD_OUTPUT]
                     [-uO DBUSER_OUTPUT] [-aO DBSERVERADRESSOUTPUT]
                     [-nO DBNAMEOUTPUT] [-pI DBPASSWORD_INPUT]
                     [-uI DBUSER_INPUT] [-aI DBSERVERADRESSINPUT]
                     [-nI DBNAMEINPUT] [-t TRANSFERLIMIT] [-tC TRANSFERCOUNT]
                     [-nR NUMBEROFRECORDSTOFETCH] [-tR] [-rR] [-iG]
                     [-rS STARTWITHDBROWNUMBER] [-rE ENDWITHDBROWNUMBER]
                     [-d DEBUGMODE] [-gL GEOCODELOCATIONS]
                     [-igS IGNOREINPUTSOURCELIST] [-iT INPUTTYPE] [-mR] [-CSV]
                     [-CSVal] [-rL] [-sF SKIPUNTILFILE] [-mGA MINGEOACCURACY]

optional arguments:
  -h, --help            show this help message and exit
  -sO ORIGIN, --Origin ORIGIN
                        Type of input source. Defaults to 3: Twitter (1 -
                        Instagram, 2 - Flickr, 3 - Twitter)

Local Input:
  -lI, --LocalInput     Process local json or csv
  -lT LOCALFILETYPE, --LocalFileType LOCALFILETYPE
                        If localread, specify filetype (json, csv etc.)
  -iP INPUTPATH, --InputPath INPUTPATH
                        Optionally provide path to input folder, otherwise
                        ./Input/ will be used
  -iS, --isStackedJson  Typical form is [{json1},{json2}], if is_stacked_json
                        is True: will process stacked jsons in the form of
                        {json1}{json2} (no comma)

DB Output:
  -pO DBPASSWORD_OUTPUT, --dbPassword_Output DBPASSWORD_OUTPUT
  -uO DBUSER_OUTPUT, --dbUser_Output DBUSER_OUTPUT
                        Default: example-user-name2
  -aO DBSERVERADRESSOUTPUT, --dbServeradressOutput DBSERVERADRESSOUTPUT
                        e.g. 111.11.11.11
  -nO DBNAMEOUTPUT, --dbNameOutput DBNAMEOUTPUT
                        e.g.: test_db

DB Input:
  -pI DBPASSWORD_INPUT, --dbPassword_Input DBPASSWORD_INPUT
  -uI DBUSER_INPUT, --dbUser_Input DBUSER_INPUT
                        Default: example-user-name
  -aI DBSERVERADRESSINPUT, --dbServeradressInput DBSERVERADRESSINPUT
                        e.g. 111.11.11.11
  -nI DBNAMEINPUT, --dbNameInput DBNAMEINPUT
                        e.g.: test_db

Additional settings:
  -t TRANSFERLIMIT, --transferlimit TRANSFERLIMIT
  -tC TRANSFERCOUNT, --transferCount TRANSFERCOUNT
                        Default to 50k: After how many parsed records should
                        the result be transferred to the DB. Larger values
                        improve speed, because duplicate check happens in
                        Python and not in Postgres Coalesce; larger values are
                        heavier on memory.
  -nR NUMBEROFRECORDSTOFETCH, --numberOfRecordsToFetch NUMBEROFRECORDSTOFETCH
  -tR, --disableTransferReactions
  -rR, --disableReactionPostReferencing
                        Enable this option in args to prevent empty posts
                        stored due to Foreign Key Exists Requirement 0 = Save
                        Original Tweets of Retweets in "posts"; 1 = do not
                        store Original Tweets of Retweets; !Not implemented: 2
                        = Store Original Tweets of Retweets as
                        "post_reactions"
  -iG, --ignoreNonGeotagged
  -rS STARTWITHDBROWNUMBER, --startWithDBRowNumber STARTWITHDBROWNUMBER
  -rE ENDWITHDBROWNUMBER, --endWithDBRowNumber ENDWITHDBROWNUMBER
  -d DEBUGMODE, --debugMode DEBUGMODE
                        Needs to be implemented.
  -gL GEOCODELOCATIONS, --geocodeLocations GEOCODELOCATIONS
                        Defaults to None. Provide path to CSV file with
                        location geocodes (CSV Structure: lat, lng, name)
  -igS IGNOREINPUTSOURCELIST, --ignoreInputSourceList IGNOREINPUTSOURCELIST
                        Provide a list of input_source types that will be
                        ignored (e.g. to ignore certain bots etc.)
  -iT INPUTTYPE, --inputType INPUTTYPE
                        Input type, e.g. "post", "profile", "friendslist",
                        "followerslist" etc.
  -mR, --mapFullRelations
                        Defaults to False. Set to true to map full relations,
                        e.g. many-to-many relationships such as user_follows,
                        user_friend, user_mentions etc. are mapped in a
                        separate table
  -CSV, --CSVOutput     Set to True to Output all Submit values to CSV
  -CSVal, --CSVallowLinebreaks
                        If set to False will not remove intext-linebreaks ( or
                        ) in output CSVs
  -rL, --recursiveLoad  Process Input Directories recursively (depth: 2)
  -sF SKIPUNTILFILE, --skipUntilFile SKIPUNTILFILE
                        If local input, skip all files until file with name x
                        appears (default: start immediately)
  -mGA MINGEOACCURACY, --minGeoAccuracy MINGEOACCURACY
                        Set to "latlng", "place", or "city" to limit output
                        based on min geoaccuracy
```

## Built With

* [lbsnstructure](https://pypi.org/project/lbsnstructure/) - A common language independend and cross-network social-media datascheme
* [protobuf](https://github.com/google/protobuf) - Google's data interchange format
* [psycopg2](https://github.com/psycopg/psycopg2) - Python-PostgreSQL Database Adapter
* [ppygis3](https://github.com/AlexImmer/ppygis3) - A PPyGIS port for Python
* [shapely](https://github.com/Toblerity/Shapely) - Geometric objects processing in Python
* [emoji](https://github.com/carpedm20/emoji/) - Emoji handling in Python

## Contributing

Field mapping from and to ProtoBuffers from different Social Media sites is provided in classes [field_mapping_xxx.py](/lbsntransform/classes/field_mapping_twitter.py).  
As an example, mapping of the Twitter json structure is given (see class `FieldMappingTwitter`). This class may be used to extend  
functionality to cover other networks such as Flickr or Foursquare.  

For development & testing, make a local clone of this repository  
```shell
git clone git@gitlab.vgiscience.de:lbsn/lbsntransform.git
```
..and (e.g.) create package in develop mode to symlink the folder to your  
Python's site-packages folder with:  
```shell
python setup.py develop
```
(use `python setup.py develop --uninstall` to uninstall tool in develop mode)

Now you can run the tool in your shell with (Origin 3 = Twitter):  
```shell
lbsntransform --Origin 3 --LocalInput --LocalFileType '*.json' --transferlimit 1000 --CSVOutput
```

..or import the package to other python projects with:  
```python
import lbsntransform
```

## Versioning and Changelog, and Download

For the releases available, see the [tags on this repository](/../tags). 
The latest windows build that is available for download is [0.1.4](https://cloudstore.zih.tu-dresden.de/index.php/s/MqtlCyqLbxmnnxr/download).
For all other systems use cx_freeze to build executable:
```shell
python cx_setup.py build
```

The versioning (major.minor.patch) is automated using [python-semantic-release](https://github.com/relekang/python-semantic-release).
Commit messages that follow the [Angular Commit Message Conventions](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines) will be automatically interpreted, followed by version bumps if necessary. Examples:  
- `fix: hotfix for bug xy` will result in a patch version bump  
- `feat: feature for processing xy` will result in minor version bump  
```git
perf(cluster): faster generation of alpha shapes

BRAKING CHANGE: Easy buffer option removed.
```
.. will result in a major release bump.

Some types used in this project:

```
feat: A new feature
fix: A bug fix
docs: Documentation only changes
style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
refactor: A code change that neither fixes a bug nor adds a feature
perf: A code change that improves performance
test: Adding missing or correcting existing tests
chore: Changes to the build process or auxiliary tools and libraries such as documentation generation
```

Except for feature and fixes, no version bumps will be made.

## Authors

* **Alexander Dunkel** - Initial work

See also the list of [contributors](/../graphs/master).  

## License

This project is licensed under the GNU GPLv3 or any higher - see the [LICENSE.md](LICENSE.md) file for details.