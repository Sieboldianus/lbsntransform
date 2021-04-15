# -*- coding: utf-8 -*-

"""
Module for sql insert functions for LBSN (hll) db
"""

from lbsntransform.output.hll import hll_bases as hll
from lbsntransform.tools.helper_functions import HelperFunctions as HF


class HLLSql():
    """Maps LBSN Types to hll SQL Structure
    """

    @staticmethod
    def get_sql_attr_coalesce(attr_key: str, facet: str, base: str) -> str:
        """Get coalesce sql for base attr"""
        if attr_key in ('latlng_geom', 'geom_center'):
            return f'''{attr_key} = COALESCE(
                NULLIF(EXCLUDED.{attr_key},
                '{HF.NULL_GEOM_HEX}'),
                {facet}."{base}".{attr_key},
                '{HF.NULL_GEOM_HEX}')
                '''
        return f'''{attr_key} = COALESCE(
            EXCLUDED.{attr_key}, {facet}."{base}".{attr_key})
            '''

    @staticmethod
    def get_sql_hll_coalesce(hll_key: str, facet: str, base: str) -> str:
        """Get coalesce sql for base hll metrics"""
        return f'''{hll_key} = COALESCE(hll_union(EXCLUDED.{hll_key},
            {facet}."{base}".{hll_key}), hll_empty())
            '''

    @staticmethod
    def concat_sep_lists(len_list_concat: int) -> str:
        """Returns separator if list is not empty"""
        if len_list_concat == 0:
            return ''
        return ',\n'

    @staticmethod
    def hll_insertsql(values_str: str, record_type) -> str:
        """Compile SQL insert for hll upsert (update & insert)"""
        facet = record_type.facet
        base = record_type.base
        base_key = hll.BASE_KEY.get(record_type)
        attr_keys = hll.BASE_ATTRS.get(record_type)
        metric_keys = hll.BASE_METRICS.get(record_type)
        insert_sql = \
            f'''
            INSERT INTO {facet}."{base}" (
                {','.join(base_key + attr_keys + metric_keys)})
            VALUES {values_str}
            ON CONFLICT ({', '.join(base_key)})
            DO UPDATE SET
                {', '.join([
                    HLLSql.get_sql_attr_coalesce(
                        attr_key,
                        facet, base) for attr_key in attr_keys])}
                {HLLSql.concat_sep_lists(len(attr_keys))}
                {', '.join([
                    HLLSql.get_sql_hll_coalesce(
                        metric_key,
                        facet, base) for metric_key in metric_keys])};
            '''
        return insert_sql

    @staticmethod
    def get_hmac_hash_sql() -> str:
        """Returns hmac hash sql function"""

        sql = """/* Produce pseudonymized hash of input id with skey
        * - using skey as seed value
        * - sha256 cryptographic hash function
        * - encode in base64 to reduce length of hash
        * - remove trailing '=' from base64 string
        * - return as text
        */
        CREATE OR REPLACE FUNCTION
        extensions.crypt_hash (id text, skey text)
        RETURNS text
        AS $$
            SELECT
                RTRIM(
                    ENCODE(
                        HMAC(
                            id::bytea,
                            skey::bytea,
                            'sha256'),
                        'base64'),
                    '=')
        $$
        LANGUAGE SQL
        STRICT;
        """
        return sql