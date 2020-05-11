# -*- coding: utf-8 -*-

"""
Module for db input connection sql mapping
"""

import enum
from typing import Union, Optional, List, Tuple
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


def optional_schema_override(
        LBSN_SCHEMA: List[Tuple[str, str, str, str]],
        schema_table_overrides: List[Tuple[str, str]]) -> List[Tuple[str, str, str, str]]:
    """Override schema and table name for selected lbsn objects."""
    LBSN_SCHEMA_OVERRIDE = []
    for lbsn_type, schema_name, table_name, key_col in LBSN_SCHEMA:
        for schema_table_override in schema_table_overrides:
            lbsn_object_ref, schema_table_override = schema_table_override
            try:
                schema_override, table_override = schema_table_override.split(
                    ".")
            except ValueError as e:
                raise ValueError(
                    f"Cannot split schema and table from override "
                    f"({schema_table_override}). Make sure "
                    f"override_lbsn_query_schema entries are formatted "
                    f"correctly, e.g. schema_override.table_override") from e
            if lbsn_type.lower() == lbsn_object_ref:
                # append override
                LBSN_SCHEMA_OVERRIDE.append(
                    (lbsn_type, schema_override, table_override, key_col))
                break
        else:
            # append none-overrides
            # if no match has been found
            LBSN_SCHEMA_OVERRIDE.append(
                (lbsn_type, schema_name, table_name, key_col))
    return LBSN_SCHEMA_OVERRIDE


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
