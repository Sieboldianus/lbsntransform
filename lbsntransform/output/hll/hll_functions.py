# -*- coding: utf-8 -*-

"""
Collection of functions used in hll transformation
"""

import datetime as dt
from collections import namedtuple
from typing import Any, Dict, Generator, List, Set, Tuple, Union

from lbsnstructure import lbsnstructure_pb2 as lbsn
from lbsntransform.tools.helper_functions import HelperFunctions as HF


class HLLFunctions():

    @staticmethod
    def merge_hll_tuples(
        base_tuples: List[Tuple[Union[str, int], ...]],
        hll_tuples: List[Tuple[Union[str, int], ...]]
    ) -> Generator[Tuple[Union[int, str], ...], None, None]:
        """Merges two lists of tuples,
        whereby only the third part of hll_tuples (the hll shard)
        is appended. The first part of base_tuples is used to collect hll
        shards per base"""
        # assign start values
        hll_baseidx_before = hll_tuples[0]
        merged_shard_batch = (hll_baseidx_before[2],)
        ix_before = hll_baseidx_before[0]
        # start from second element
        for hll_tup in hll_tuples[1:]:
            hll_shard = hll_tup[2]
            ix = hll_tup[0]
            if ix == ix_before:
                # if base is unchanged (and not the last hll_tuple),
                # concat hll shards per base into one tuple
                merged_shard_batch += (hll_shard,)
                ix_before = ix
                # continue with next shard
                continue
            # else: if base changed,
            # append hll_shards to base record
            merged_base_hll_tuple = base_tuples[ix_before] + merged_shard_batch
            merged_shard_batch = (hll_shard,)
            ix_before = ix
            # return merged record + hll tuple
            # and continue iteration
            yield merged_base_hll_tuple
        # final return of last item
        yield base_tuples[ix] + merged_shard_batch

    @staticmethod
    def concat_base_shards(
            records: List[Tuple[Union[str, int], ...]],
            hll_shards: List[Tuple[Union[str, int], ...]]
    ) -> List[Tuple[Union[int, str], ...]]:
        """Concat records with list of hll_shards

        For ease of calculation, hll_shards are reduced to
        a onedimensional list. Here, shards are assigned back to
        records using record base keys
        """
        merged_records = [
            merged_tuple for merged_tuple in
            HLLFunctions.merge_hll_tuples(records, hll_shards)]
        # if this ever evaluates to false
        # something went fundamentally wrong:
        # abort processing
        assert len(records) == len(merged_records)
        return merged_records

    @staticmethod
    def make_shard_sql(values_str: str):
        """SQL to calculate HLL Shards from sets of items

        Example values_str:
        ('2011-01-01'::date, 'user_hll', '2:4399297324604'),
        """
        insert_sql = \
            f'''
            SELECT base_id, metric_id, hll_add_agg(hll_hash_text(s.item_value))
            FROM (
            VALUES {values_str}
            ) s(base_id, metric_id, item_value)
            GROUP BY base_id, metric_id
            '''
        return insert_sql

    @staticmethod
    def calculate_item_shards(
        hllworker_cursor, values_str: List[str]
    ) -> List[Tuple[int, str, str]]:
        """Calculates shards from batched hll_items
        using hll_worker connection
        """
        shard_sql = HLLFunctions.make_shard_sql(values_str)
        hllworker_cursor.execute(shard_sql)
        hll_shards = hllworker_cursor.fetchall()
        return hll_shards

    @staticmethod
    def concat_base_metric_item(
            base_key: int,
            hll_items: List[Dict[str, set]]) -> Tuple[int, int, str]:
        """Concat hll item to (base_key, metric_key, item) tuple
        Note that only ids (0, 1, 2..), not the true keys are used
        for base_key and metric_key,
        following the separation of concerns principle
        """
        tuple_list = []
        for metric_ix, item_set in enumerate(hll_items.values()):
            if not item_set:
                tuple_list.append(
                    (base_key, metric_ix, None))
            else:
                for item in item_set:
                    tuple_list.append(
                        (base_key, metric_ix, item))
        return tuple_list

    @staticmethod
    def hll_concat_origin_guid(record) -> str:
        origin_guid = HLLFunctions.hll_concat(
            [record.pkey.origin.origin_id, record.pkey.id])
        return origin_guid

    @staticmethod
    def hll_concat_user(record: lbsn.Post) -> str:
        user_hll = HLLFunctions.hll_concat(
            [record.pkey.origin.origin_id, record.user_pkey.id])
        return user_hll

    @staticmethod
    def hll_concat_date(record: lbsn.Post) -> str:
        date_merged = HLLFunctions.merge_dates_post(record)
        if date_merged is None:
            return
        date_formatted = date_merged.strftime('%Y-%m-%d')
        return date_formatted

    @staticmethod
    def hll_concat_yearmonth(record: lbsn.Post) -> str:
        date_merged = HLLFunctions.merge_dates_post(record)
        date_formatted = date_merged.strftime('%Y-%m')
        return date_formatted

    @staticmethod
    def hll_concat_latlng(record: lbsn.Post) -> str:
        if record.post_geoaccuracy == 'latlng':
            coordinates_geom = HF.null_check(
                record.post_latlng)
            coordinates = HF.get_coordinates_from_ewkt(
                coordinates_geom
            )
            return f'{coordinates.lat}:{coordinates.lng}'
        else:
            return '0:0'

    @staticmethod
    def hll_concat_place(record: lbsn.Post) -> str:
        if record.post_geoaccuracy == 'place':
            return HLLFunctions.hll_concat(
                [record.pkey.origin.origin_id, record.place_pkey.id])
        else:
            return None

    @staticmethod
    def hll_concat_upt_hll(record: lbsn.Post) -> List[str]:
        body_terms = HF.select_terms(
            record.post_body)
        title_terms = HF.select_terms(
            record.post_title)
        tag_terms = {item.lower() for item in record.hashtags if len(item) > 2}
        all_post_terms = set.union(
            body_terms, title_terms, tag_terms)
        user_hll = HLLFunctions.hll_concat_user(
            record)
        upt_hll = HLLFunctions.hll_concat_user_terms(
            user_hll, all_post_terms)
        return upt_hll

    @staticmethod
    def hll_concat_user_terms(user: str, terms: List[str]) -> Set[str]:
        concat_user_terms = set()
        for term in terms:
            concat_user_terms.add(":".join([user, term]))
        return concat_user_terms

    @staticmethod
    def hll_concat(record_attr: List[Union[str, int]]) -> str:
        """Concat record attributes using colon """
        return ":".join(map(str, record_attr))

    @staticmethod
    def merge_dates_post(record: lbsn.Post = None) -> dt:
        """Merge post_publish and post_created attributes"""
        post_create_date = HF.null_check_datetime(
            record.post_create_date)
        post_publish_date = HF.null_check_datetime(
            record.post_publish_date)
        if post_create_date is None:
            return post_publish_date
        else:
            return post_create_date