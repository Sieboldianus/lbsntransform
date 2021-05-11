[![PyPI version](https://lbsn.vgiscience.org/lbsntransform/pypi.svg?&kill_cache=2)](https://pypi.org/project/lbsntransform/) [![pylint](https://lbsn.vgiscience.org/lbsntransform/pylint.svg)](https://gitlab.vgiscience.de/lbsn/lbsntransform) [![pipeline](https://lbsn.vgiscience.org/lbsntransform/pipeline.svg?&kill_cache=2)](https://gitlab.vgiscience.de/lbsn/lbsntransform) [![Documentation](https://lbsn.vgiscience.org/lbsntransform/documentation.svg)](https://lbsn.vgiscience.org/lbsntransform/docs/)

# LBSNTransform

A python package that uses the [common location based social network (LBSN) data structure][lbsnstructure] 
(ProtoBuf) to import, transform and export Social Media data such as Twitter and Flickr.

![Illustration of functions](https://lbsn.vgiscience.org/lbsntransform/docs/inputoutput.svg)

## Motivation

The goal is to provide a common interface to handle Social Media Data, 
without the need to individually adapt to the myriad API endpoints available. 
As an example, consider the ProtoBuf spec [lbsn.Post][lbsnpost], which can be a Tweet on Twitter, 
a Photo shared on Flickr, or a post on Reddit. However, all of these objects share
a common set of attributes, which is reflected in the lbsnstructure.

The tool is based on a 4-Facet conceptual framework for LBSN, introduced in a paper 
by [Dunkel et al. (2018)](https://www.tandfonline.com/doi/full/10.1080/13658816.2018.1546390). 

The GDPR directly requests Social Media Network operators to allow 
users to transfer accounts and data in-between services.
While there are attempts by Google, Facebook etc. (e.g. see the [data-transfer-project][data-transfer-project]), 
this is not currently possible. With the lbsnstructure, a primary motivation is to systematically 
characterize LBSN data aspects in a common, cross-network data scheme that enables privacy-by-design 
for connected software, data handling and database design.

## Description

This tool enables data import from a Postgres database, JSON, or CSV and export to CSV, [LBSN ProtoBuf][lbsnstructure] 
or the [hll][hlldb] and [raw][rawdb] versions of the LBSN prepared Postgres Databases.
The tool will map Social Media endpoints (e.g. Twitter tweets) to a common [LBSN Interchange Structure][lbsnstructure] 
format in ProtoBuf. LBSNTransform can be used using the command line (CLI) or imported to other Python projects with 
`import lbsntransform`, for on-the-fly conversion.

## Quick Start

The recommended way to install lbsntransform, for both Linux and Windows, 
is through the conda package manager.

1. Create a conda env using `environment.yml`

First, create an environment with the dependencies for lbsntransform using
the [environment.yml][environment.yml] that is provided in the root of the repository.

```bash
git clone https://github.com/Sieboldianus/lbsntransform.git
cd lbsntransform
# not necessary, but recommended:
conda config --env --set channel_priority strict
conda env create -f environment.yml
```

2. Install lbsntransform without dependencies

Afterwards, install lbsntransform using pip, without dependencies.

```bash
conda activate lbsntransform
pip install lbsntransform --no-deps --upgrade
# or locally, from the latest commits on master
# pip install . --no-deps --upgrade
```

3. Import data using a mapping

For each data source, a mapping must be provided that
defines how data is mapped to the [lbsnstructure][lbsnstructure].

The default mapping is [lbsnraw][lbsnraw].

Additional mappings can be dynamically loaded from a folder.

We have provided two [example mappings][mappings] for the [Flickr YFCC100M dataset][yfcc100m] (CSV)
and Twitter (json).

For example, to import the first 1000 records from json data from Twitter to the 
[lbsn raw database][rawdb], clone [field_mapping_twitter.py][field_mapping_twitter] 
to a local folder `./resources/mappings/`, startup the Docker [rawdb][rawdb] container,
and use:

```shell
lbsntransform --origin 3 \
              --mappings_path ./resources/mappings/ \
              --file_input \
              --file_type "json" \
              --mappings_path ./resources/mappings/ \
              --dbpassword_output "sample-key" \
              --dbuser_output "postgres" \
              --dbserveraddress_output "127.0.0.1:5432" \
              --dbname_output "rawdb" \
              --dbformat_output "lbsn" \
              --transferlimit 1000
```

.. with the above input args, the the tool will:  
- read local json from `./01_Input/`
- and store lbsn records to the [lbsn rawdb][rawdb].

Vice versa, to import data directly to the privacy-aware
version of lbsnstructure, called [hlldb][hlldb], startup the
Docker container, and use:

```shell
lbsntransform --origin 3 \
              --mappings_path ./resources/mappings/ \
              --file_input \
              --file_type "json" \
              --mappings_path ./resources/mappings/ \
              --dbpassword_output "sample-key" \
              --dbuser_output "postgres" \
              --dbserveraddress_output "127.0.0.1:25432" \
              --dbname_output "hlldb" \
              --dbformat_output "hll" \
              --dbpassword_hllworker "sample-key" \
              --dbuser_hllworker "postgres" \
              --dbserveraddress_hllworker "127.0.0.1:25432" \
              --dbname_hllworker "hlldb" \
              --include_lbsn_objects "origin,post" \
              --include_lbsn_bases hashtag,place,date,community \
              --transferlimit 1000
```

.. with the above input args, the the tool will:  
- read local json from `./01_Input/`  
- and store lbsn records to the privacy-aware [lbsn hlldb][hlldb]  
- by converting only lbsn objects of type [origin][lbsnorigin] and [post][lbsnpost]  
- and updating the HyperLogLog (HLL) target tables `hashtag`, `place`, `date` and `community`  

A full list of possible input and output args is available in the 
[documentation](https://lbsn.vgiscience.org/lbsntransform/docs/).

## Built With

* [lbsnstructure](https://pypi.org/project/lbsnstructure/) - A common language independend and cross-network social-media datascheme
* [protobuf](https://github.com/google/protobuf) - Google's data interchange format
* [psycopg2](https://github.com/psycopg/psycopg2) - Python-PostgreSQL Database Adapter
* [ppygis3](https://github.com/AlexImmer/ppygis3) - A PPyGIS port for Python
* [shapely](https://github.com/Toblerity/Shapely) - Geometric objects processing in Python
* [emoji](https://github.com/carpedm20/emoji/) - Emoji handling in Python

## Authors

* **Alexander Dunkel** - Initial work

See also the list of [contributors](/../graphs/master).

## License

This project is licensed under the GNU GPLv3 or any higher - 
see the [LICENSE.md](LICENSE.md) file for details.

[lbsnstructure]: https://lbsn.vgiscience.org/structure/
[lbsnpost]: https://lbsn.vgiscience.org/structure/#post
[lbsnorigin]: https://lbsn.vgiscience.org/structure/#origin
[data-transfer-project]: https://datatransferproject.dev/
[rawdb]: https://gitlab.vgiscience.de/lbsn/databases/rawdb
[hlldb]: https://gitlab.vgiscience.de/lbsn/databases/hlldb
[lbsnraw]: lbsntransform/input/mappings/field_mapping_lbsn.py
[mappings]: resources/mappings
[field_mapping_twitter]: resources/mappings/field_mapping_twitter.py
[yfcc100m]: http://projects.dfki.uni-kl.de/yfcc100m/
