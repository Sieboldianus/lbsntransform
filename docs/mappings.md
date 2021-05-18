# Mappings
## Input Mappings
### Concept

For any conversion, a mapping must exist. A mapping is defined in 
a python file (`.py`) and describes how any input data is converted
to the [common lbsn structure](https://lbsn.vgiscience.org/), which
is available from the Python version of the Proto Buf Spec.

Mappings are loaded dynamically. You can provide a path to a folder 
containing mappings with the flag `--mappings_path ./subfolder`.

To use the provided example mappings (Twitter or YFCC100M), clone the
repository and use:
```bash
lbsntransform --mappings_path ./resources/mappings/
```

If no path is provided, `lbsn raw` is assumed as input, for which
the file mapping is available in [field_mapping_lbsn.py](/lbsntransform/docs/api/input/mappings/field_mapping_lbsn.html),
including lbsn db query syntax defined in [db_query.py](/lbsntransform/docs/api/input/mappings/db_query.html).

Predefined mappings exist for the [Flickr YFCC100M dataset](https://lbsn.vgiscience.org/yfcc-introduction/) (CSV) and Twitter (JSON).

Have a look at the two mappings in the [resources folder](https://gitlab.vgiscience.de/lbsn/lbsntransform/-/tree/master/resources/mappings).

If the git repository is cloned to a local folder, use
`--mappings_path ./resources/mappings/` to load Flickr or Twitter mappings.

Input mappings must have some specific attributes to be recognized.

Primarily, a class constant `MAPPING_ID` is used to assign mappings to input data when lbsntransform is run.

 
For example, the [field_mapping_lbsn.py](/lbsntransform/docs/api/input/mappings/field_mapping_lbsn.html)
has the following module level constant:
```py
MAPPING_ID = 0
```

This is the default mapping, and it will be used for reading data with the default `--origin 0` flag used.

### Examples

To load data with the default mapping, with the MAPPING_ID "0", use `lbsntransform --origin 0`.

To load data from Twitter json, use 
```bash
lbsntransform --origin 3 \
              --mappings_path ./resources/mappings/ \
              --file_input \
              --file_type "json"
```

To load data from Flickr YFCC100M, use 

```bash
lbsntransform --origin 21 \
              --mappings_path ./resources/mappings/ \
              --file_input \
              --file_type "csv" \
              --csv_delimiter $'\t'
```

To load data from native LBSN (RAW) DB, running locally
on port `15432`:

```bash
lbsntransform --origin 0 \
              --dbpassword_input "eX4mP13p455w0Rd" \
              --dbuser_input "postgres" \
              --dbserveraddress_input "127.0.0.1:15432" \
              --dbname_input "rawdb" \
              --dbformat_input "lbsn" \
              --include_lbsn_bases hashtag,place,date,community \
              --include_lbsn_objects "origin,post"
```

!!! note
    The example commands above are missing output
    information. Below is a full example that
    shows how to read from local lbsn raw db
    to local lbsn hll db, which includes the use of
    a third, empty [hll importer db](https://gitlab.vgiscience.de/lbsn/tools/importer)
    for the purpose of separation of concerns.

```bash
lbsntransform --origin 0 \
    --dbpassword_input "eX4mP13p455w0Rd" \
    --dbuser_input "postgres" \
    --dbserveraddress_input "127.0.0.1:15432" \
    --dbname_input "rawdb" \
    --dbformat_input "lbsn" \
    --dbpassword_output "eX4mP13p455w0Rd" \
    --dbuser_output "postgres" \
    --dbserveraddress_output "127.0.0.1:25432" \
    --dbname_output "hlldb" \
    --dbformat_output "hll" \
    --dbpassword_hllworker "eX4mP13p455w0Rd" \
    --dbuser_hllworker "postgres" \
    --dbserveraddress_hllworker "127.0.0.1:5432" \
    --dbname_hllworker "hllworkerdb" \
    --include_lbsn_bases hashtag,place,date,community \
    --include_lbsn_objects "origin,post"
```
    
### Custom Input Mappings

Start with any of the predefined mappings, either from [field_mapping_lbsn.py](/lbsntransform/docs/api/input/mappings/field_mapping_lbsn.html),
or [field_mapping_twitter.py](https://gitlab.vgiscience.de/lbsn/lbsntransform/-/blob/master/resources/mappings/field_mapping_twitter.py) (JSON) and
[field_mapping_yfcc100m.py](https://gitlab.vgiscience.de/lbsn/lbsntransform/-/blob/master/resources/mappings/field_mapping_yfcc100m.py) (CSV).

A minimal template looks as follows:

```py
# -*- coding: utf-8 -*-

"""
Module for mapping example Posts dataset to common LBSN Structure.
"""

from typing import Optional
from lbsnstructure import lbsnstructure_pb2 as lbsn
from lbsntransform.tools.helper_functions import HelperFunctions as HF

MAPPING_ID = 99

class importer():
    """ Provides mapping function from Example Post Source to
        protobuf lbsnstructure
    """
    ORIGIN_NAME = "Example Post Source"
    ORIGIN_ID = 2

    def __init__(self,
                 disable_reaction_post_referencing=False,
                 geocodes=False,
                 map_full_relations=False,
                 map_reactions=True,
                 ignore_non_geotagged=False,
                 ignore_sources_set=None,
                 min_geoaccuracy=None):
        origin = lbsn.Origin()
        origin.origin_id = 99
        self.origin = origin
        self.null_island = 0
        self.skipped_count = 0
        self.skipped_low_geoaccuracy = 0

    def parse_csv_record(self, record, record_type: Optional[str] = None):
        """Entry point for processing CSV data:
        Attributes:
        record    A single row from CSV, stored as list type.
        """
        # extract/convert all lbsn records
        lbsn_records = []
        lbsn_record = self.extract_post(record)
        lbsn_records.append(lbsn_record)
        return lbsn_records

    # def parse_json_record(self, record, record_type: Optional[str] = None):
    #   """Entry point for processing JSON data:
    #   Attributes:
    #   record    A single record, stored as dictionary type.
    #   """
    #   # extract lbsn objects
    #   return lbsn_records
    
    def extract_post(self, record):
        post_record = HF.new_lbsn_record_with_id(
            lbsn.Post(), post_guid, self.origin)
        return post_record
```

### FAQ

* **Json or CSV?** Database records and JSON objects are read as nested dictionaries.
  CSV records are read using dict_reader, and provided as flat dictionaries.  
* Each mapping must have either `parse_csv_record()` or `parse_json_record()` defined.  
* Both json and CSV mapping can be mapped in one file, but it is recommended to separate
  mappings for different input file formats in two mappings.  
* The class attributes provided above are currently required to be defined. It is
  not necessary to actually make use of these.  
* Both `parse_csv_record()` and `parse_json_record()` must return a list of lbsn Objects.
    

!!! note
    For one lbsn origin, many mappings may exist. For example, 
    for the above example origin with id `99`, you may have 
    mappings with ids `991`, `992`, `993` etc. This can be used to 
    create separate mappings for json, csv etc.
    
    The actual `origin_id` that is stored in the database is 
    given in the `importer.origin` attributes.

## Output Mappings

**lbsntransform** can output data to a database with the [common lbsn structure](https://lbsn.vgiscience.org/structure/), 
called [rawdb](https://gitlab.vgiscience.de/lbsn/databases/rawdb)
or the privacy-aware version, called [hlldb](https://gitlab.vgiscience.de/lbsn/databases/hlldb).

**Examples:**

To output data to rawdb:

```bash
lbsntransform --dbpassword_output "sample-key" \
              --dbuser_output "postgres" \
              --dbserveraddress_output "127.0.0.1:5432" \
              --dbname_output "rawdb" \
              --dbformat_output "lbsn"
```

The syntax for conversion to hlldb is a little bit more complex, 
since the output structure may vary to a large degree, depending 
on each use case.

!!! note
    The hlldb and structure are still in an early stage of development.
    We're beyond the initial proof of concept and are working on
    simplifying custom mappings.

To output data to hlldb:
```bash
lbsntransform --dbpassword_output "sample-key" \
              --dbuser_output "postgres" \
              --dbserveraddress_output "127.0.0.1:25432" \
              --dbname_output "hlldb" \
              --dbformat_output "hll" \
              --dbpassword_hllworker "sample-key" \
              --dbuser_hllworker "postgres" \
              --dbserveraddress_hllworker "127.0.0.1:15432" \
              --dbname_hllworker "hllworkerdb" \
              --include_lbsn_objects "origin,post" \
```

Above, a separate connection to a "hll_worker" database is provided.
It is used to make hll calculations (union, hashing etc.). No items
will be written to this database, a read_only user will suffice. A
[Docker container with a predefined user](https://gitlab.vgiscience.de/lbsn/databases/pg-hll-empty) 
is available.

Having two hll databases, one for calculations and one for storage means
that concerns can be separated: There is no need for hlldb to receive any
raw data. Likewise, the hll worker does not need to know contextual data,
for union of specific hll sets. Such a setup improves robustness and privacy.
It further allows to separate processing into individual components.

If no hll worker is available, hlldb may be used.

!!! note "Why do I need a database connection?"
    There's a [python package](https://github.com/AdRoll/python-hll) available that
    allows making hll calculations in python. However, it is not as performant
    as the native Postgres implementation.
    
Use `--include_lbsn_objects` to specify which input data you want to convert to 
the privacy aware version. For example, `--include_lbsn_objects "origin,post"`
would process [lbsn objects](https://lbsn.vgiscience.org/structure/) 
of type origin and post (default).

Use `--include_lbsn_bases` to specify which output data you want to convert to.

We refer to the different output structures as "bases", and they are defined 
in [lbsntransform.output.hll.hll_bases](/lbsntransform/docs/api/output/hll/hll_bases.html),

Bases can be separated by comma and may include:

- Temporal Facet:  
    - `monthofyear`
    - `month`
    - `dayofmonth`
    - `dayofweek`
    - `hourofday`
    - `year`
    - `month`
    - `date`
    - `timestamp`

- Spatial Facet:  
    - `country`
    - `region`
    - `city`
    - `place`
    - `latlng`

- Social Facet:  
    - `community`

- Topical Facet:  
    - `hashtag`
    - `emoji`
    - `term`

- Composite Bases:  
    - `_hashtag_latlng`
    - `_term_latlng`
    - `_emoji_latlng`
    - `_month_latlng`
    - `_month_hashtag`


For example:
```bash
lbsntransform --include_lbsn_bases hashtag,place,date,community
```

..would convert and transfer any input data to the hlldb structures:  

- `topical.hashtag`  
- `spatial.place`  
- `temporal.date`  
- `social.community`  

The name refers to `schema.table` in the Postgres implementation.

!!! note "Upsert (Insert or Update)"
    Because it is entirely unknown to lbsntransform whether output
    records (primary keys) already exist, any data is transferred using the
    [Upsert](https://wiki.postgresql.org/wiki/UPSERT) syntax, which means
    `INSERT ... ON CONFLICT UPDATE`. This means that records are either 
    inserted if primary keys do not exist yet, or updated, using `hll_union()`.

It is possible to define own output hll db mappings. The best place
to start is [lbsntransform.output.hll.hll_bases](/lbsntransform/docs/api/output/hll/hll_bases.html).

Have a look at the pre-defined bases and add any additional needed. It is recommended
to use inheritance. After adding your own mappings, the hlldb must be prepared with
respective table structures. Have a look at the 
[predefined structures available](https://gitlab.vgiscience.de/lbsn/structure/hlldb/-/blob/master/structure/98-create-tables.sql).

