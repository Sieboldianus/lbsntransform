# -*- coding: utf-8 -*-

"""
Module for db input connection sql mapping
"""

import enum
from typing import Union, Optional
from lbsnstructure import lbsnstructure_pb2 as lbsn

"""Schema convention from lbsn db spec"""
LBSN_SCHEMA = [
    (lbsn.Origin().DESCRIPTOR.name, "social", "origin", "origin_id"),
    (lbsn.Country().DESCRIPTOR.name, "spatial", "country", "country_guid"),
    (lbsn.City().DESCRIPTOR.name, "spatial", "city", "city_guid"),
    (lbsn.Place().DESCRIPTOR.name, "spatial", "place", "place_guid"),
    (lbsn.UserGroup().DESCRIPTOR.name, "social", "user_groups", "usergroup_guid"),
    (lbsn.User().DESCRIPTOR.name, "social", "user", "user_guid"),
    (lbsn.Post().DESCRIPTOR.name, "topical", "post", "post_guid"),
    (lbsn.PostReaction().DESCRIPTOR.name,
     "topical", "post_reaction", "reaction_guid"),
]


class InputSQL(enum.Enum):
    """SQL for default JSON records stored in DB

    In this example, records are stored in table "input" in schema
    public. They're 3 columns, in_id, insert_time and data.
    Table data is cast to json type.

    The two %s string formatters allow substitution of values
    during the query. The first %s is the key, the second %s is the limit of
    records to get during the query (default 10000)
    """
    DEFAULT = '''
            SELECT in_id, insert_time, data::json
            FROM {schema_name}."{table_name}"
            WHERE {key_col} > {start_id}
            ORDER BY {key_col} ASC
            LIMIT {number_of_records_to_fetch};
            '''

    """SQL for LBSN records stored in DB"""
    LBSN = '''
            SELECT * FROM {schema_name}."{table_name}"
            {optional_where}
            ORDER BY {key_col} ASC
            LIMIT {number_of_records_to_fetch};
            '''

    DB_CUSTOM = '''Define your own DB Mapping SQL here'''

    def get_sql(
            self, schema_name: str = "public", table_name: str = "input",
            start_id: Optional[Union[int, str]] = None,
            number_of_records_to_fetch: int = 10000,
            key_col="in_id"):
        """Get SQL formatted string"""
        optional_where = ""
        if start_id is not None:
            quote_subst = ""
            if self.name == "LBSN":
                # quoted string required
                quote_subst = "'"
            optional_where = \
                f"WHERE {key_col} > {quote_subst}{start_id}{quote_subst}"
        # self.value refers to current ENUM,
        # which is always string
        return self.value.format(
            schema_name=schema_name,
            table_name=table_name,
            optional_where=optional_where,
            number_of_records_to_fetch=number_of_records_to_fetch,
            key_col=key_col)
