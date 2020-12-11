For any conversion, a mapping must exist. A mapping is defined in 
a python file (`.py`) and describes how any input data is converted
to the [common lbsn structure](https://lbsn.vgiscience.org/), which
is available from the Python version of the Proto Buf Spec.

Mappings are loaded dynamically. You can provide a path to a folder 
containing mappings with the flag `--mappings_path ./subfolder`.

If no path is provided, `lbsn raw` is assumed as input, for which
the file mapping is available in [lbsntransform/input/field_mapping_lbsn.py](/api/input/mappings/field_mapping_lbsn.html),
including lbsn db query syntax defined in [lbsntransform/input/db_query.py](/api/input/mappings/db_query.html).

Predefined mappings exist for Flickr (CSV/JSON) and Twitter (JSON)
in the [resources folder](https://gitlab.vgiscience.de/lbsn/lbsntransform/resources).
If the git repository is cloned to a local folder, use
`--mappings_path ./resources/mappings/` to load Flickr or Twitter mappings.

Input mappings must have some specific attributes to be recognized.

Primarily, a class constant "MAPPING_ID" is used to load mappings, 
e.g. the [field_mapping_lbsn.py](/api/input/mappings/field_mapping_lbsn.html)
has the following module level constant:
```py
MAPPING_ID = 0
```

**Examples:**

To load data with the default mapping, use `lbsntransform --origin 0`.

To load data from Twitter json, use use 
```bash
lbsntransform --origin 3 \
              --mappings_path ./resources/mappings/ \
              --file_input \
              --file_type "json"
```

To load data from Flickr YFCC100M, use use 

```bash
lbsntransform --origin 21 \
              --mappings_path ./resources/mappings/ \
              --file_input \
              --file_type "csv" \
              --csv_delimiter $'\t'
```

# Custom Input Mappings

Start with any of the predefined mappings, either from [field_mapping_lbsn.py](/api/input/mappings/field_mapping_lbsn.html),
or [field_mapping_twitter.py](https://gitlab.vgiscience.de/lbsn/lbsntransform/resources/field_mapping_twitter.py) (JSON) and
[field_mapping_yfcc100m.py](https://gitlab.vgiscience.de/lbsn/lbsntransform/resources/field_mapping_yfcc100m.py) (CSV).

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
        lbsn_records = self.extract_post(record)
        return lbsn_records

    def extract_post(self, record):
        post_record = HF.new_lbsn_record_with_id(
            lbsn.Post(), post_guid, self.origin)
```

!!! Note
    For one lbsn origin, many mappings may exist. For example, 
    for the above example origin with id "99", you may have 
    mappings with ids 991, 992, 993 etc. This can be used to 
    create separate mappings for json, csv etc.