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
the file mapping is available in [lbsntransform/input/field_mapping_lbsn.py](/lbsntransform/docs/api/input/mappings/field_mapping_lbsn.html),
including lbsn db query syntax defined in [lbsntransform/input/db_query.py](/lbsntransform/docs/api/input/mappings/db_query.html).

Predefined mappings exist for the [Flickr YFCC100M dataset](https://lbsn.vgiscience.org/yfcc-introduction/) (CSV) and Twitter (JSON).

Have a look at the two mappings in the [resources folder](https://gitlab.vgiscience.de/lbsn/lbsntransform/-/tree/master/resources/mappings).

If the git repository is cloned to a local folder, use
`--mappings_path ./resources/mappings/` to load Flickr or Twitter mappings.

Input mappings must have some specific attributes to be recognized.

Primarily, a class constant "MAPPING_ID" is used to load mappings, 
e.g. the [field_mapping_lbsn.py](/lbsntransform/docs/api/input/mappings/field_mapping_lbsn.html)
has the following module level constant:
```py
MAPPING_ID = 0
```

**Examples:**

To load data with the default mapping, with the MAPPING_ID "0", use `lbsntransform --origin 0`.

To load data from Twitter json, use 
```bash
lbsntransform --origin 3 \
              --mappings_path ./resources/mappings/ \
              --file_input \
              --file_type "json" \
              --mappings_path ./resources/mappings/
```

To load data from Flickr YFCC100M, use 

```bash
lbsntransform --origin 21 \
              --mappings_path ./resources/mappings/ \
              --file_input \
              --file_type "csv" \
              --csv_delimiter $'\t' \
              --mappings_path ./resources/mappings/
```

# Custom Input Mappings

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


* **Json or CSV?** Database records and JSON objects are read as nested dictionaries.
  CSV records are read using dict_reader, and provided as flat dictionaries.  
* Each mapping must have either `parse_csv_record()` or `parse_json_record()` defined.  
* Both json and CSV mapping can be mapped in one file, but it is recommended to separate
  mappings for different input file formats in two mappings.  
* The class attributes provided above are currently required to be defined. It is
  not necessary to actually make use of these.  
* Both `parse_csv_record()` and `parse_json_record()` must return a list of lbsn Objects.
    

!!! Note
    For one lbsn origin, many mappings may exist. For example, 
    for the above example origin with id `99`, you may have 
    mappings with ids `991`, `992`, `993` etc. This can be used to 
    create separate mappings for json, csv etc.
    
    The actual `origin_id` that is stored in the database is 
    given in the `importer.origin` attributes.