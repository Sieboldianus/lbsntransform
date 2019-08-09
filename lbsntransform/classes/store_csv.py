# -*- coding: utf-8 -*-

"""
Module for storing common Proto LBSN Structure to CSV.
"""

# pylint: disable=no-member

import base64
import csv
import logging
import os
import sys
import traceback
from contextlib import ExitStack
from glob import glob
from heapq import merge as heapq_merge
from sys import exit

# for debugging only:
from google.protobuf import text_format
from google.protobuf.timestamp_pb2 import Timestamp
from lbsnstructure.lbsnstructure_pb2 import (CompositeKey, RelationshipKey,
                                             City, Country, Place,
                                             Post, PostReaction,
                                             Relationship, User,
                                             UserGroup)

from .helper_functions import HelperFunctions, LBSNRecordDicts
from .shared_structure_proto_lbsndb import ProtoLBSNMapping


class LBSNcsv():
    """Class to convert and store protobuf records to CSV file(s).

    Because the amount of data might be quite big,
    CSVs are stored incrementally first.
    After no new data arrives, the tool will merge
    all single CSV files and eliminate duplicates.
    This is done using heapq_merge:
        - individual files are first sorted based on primary key
        - lines beginning with the same primry key
        are merged (each field is compared)
    Afterwards, 2 file types are generated:
        a) archive (ProtoBuf)
        b) CSV_copy import (postgres)

    Attributes:
        output_path_file    Where the CSVs will be stored.
                            Note: check for existing files!
        db_mapping          Reference to access functions
                            from ProtoLBSM_db_Mapping class
        store_csv_part      Current Number of CSV file parts
        suppress_linebreaks Usually, linebreaks will not be
                            a problem, linebreaks are nonetheless surpressed.
    """

    def __init__(self, suppress_linebreaks=True):
        self.output_path_file = f'{os.getcwd()}\\02_Output\\'
        self.db_mapping = ProtoLBSNMapping()
        self.store_csv_part = 0
        self.suppress_linebreaks = suppress_linebreaks
        if not os.path.exists(self.output_path_file):
            os.makedirs(self.output_path_file)

    def store_append_batch_to_csv(self, records, round_nr,
                                  type_name, pg_copy_format=False):
        """ Takes proto buf lbsn record dict and appends all records
            to correct CSV (type-specific)
        """
        file_path = f'{self.output_path_file}{type_name}_{round_nr:03d}.csv'
        with open(file_path, 'a', encoding='utf8') as file_handle:
            # csvOutput = csv.writer(f, delimiter=',',
            #                       lineterminator='\n',
            #                       quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for record in records:
                serialized_record_b64 = self.serialize_encode_record(record)
                file_handle.write(
                    f'{record.pkey.id},{serialized_record_b64}\n')

    def serialize_encode_record(self, record):
        """ Serializes protobuf record as string and
            encodes in base64 for corrupt-resistant backup/store/transfer
        """
        serialized_record = record.SerializeToString()
        serialized_encoded_record = base64.b64encode(serialized_record)
        serialized_encoded_record_utf = serialized_encoded_record.decode(
            "utf-8")
        return serialized_encoded_record_utf

    # def writeCSVHeader(self, typeName):
    #    # create files and write headers
    #    #for typename, header in self.typeNamesHeaderDict.items():
    #    header = self.typeNamesHeaderDict[typeName]
    #    csvOutput = open(f'{self.output_path_file}'
    #                     f'{typeName}_{self.countRound:03d}.csv',
    #                     'w', encoding='utf8')
    #    csvOutput.write("%s\n" % header)

    def clean_csv_batches(self, batched_records):
        """ Merges all output streams per type at end
            and removes duplicates

            This is necessary because Postgres can't
            import Duplicates with /copy.
            Keep all records in RAM while processing input data is impossible,
            therefore merge happens only once at end.
        """
        x_cnt = 0
        self.store_csv_part += 1
        print('Cleaning and merging output files..')
        for type_name in batched_records:
            x_cnt += 1
            filelist = glob(f'{self.output_path_file}{type_name}_*.csv')
            if filelist:
                self.sort_files(filelist)
                if len(filelist) > 1:
                    print(
                        f'Cleaning & merging output files..{x_cnt}'
                        f'/{len(batched_records)}', end='\r')
                    self.merge_files(filelist, type_name)
                else:
                    # sec = input(f'only one File. {filelist}\n')
                    # no need to merge files if only one round
                    new_filename = filelist[0].replace('_001', '_Proto')
                    if os.path.isfile(new_filename):
                        os.remove(new_filename)
                    if os.path.isfile(filelist[0]):
                        os.rename(filelist[0], new_filename)
                self.remove_merge_duplicate_records_format_csv(type_name)

    def sort_files(self, filelist):
        """ Function for sorting files
            (precursor to remove duplicates)
        """
        for file_path in filelist:
            with open(file_path, 'r+', encoding='utf8') as batch_file:
                # skip header
                # header = batchFile.readline()
                lines = batch_file.readlines()
                # sort by first column
                lines.sort(key=lambda a_line: a_line.split()[0])
                # lines.sort()
                batch_file.seek(0)
                # delete original records in file
                batch_file.truncate()
                # write sorted records
                # batchFile.writeline(header)
                for line in lines:
                    batch_file.write(line)

    def merge_files(self, filelist, type_name):
        """ Merges multiple files to one
            using ExitStack
        """
        with ExitStack() as stack:
            files = [stack.enter_context(
                open(fname, encoding='utf8')) for fname in filelist]
            with open(f'{self.output_path_file}{type_name}_Proto.csv',
                      'w', encoding='utf8') as merged_file:
                merged_file.writelines(heapq_merge(*files))
        for file in filelist:
            os.remove(file)

    def create_proto_by_descriptor_name(self, desc_name):
        """Create new proto record by name
        """
        new_record = HelperFunctions.dict_type_switcher(desc_name)
        return new_record

    # def parse_message(self,msgType,stringMessage):
    #        #result_class = reflection.GeneratedProtocolMessageType(msgType,
    #        (stringMessage,),{'DESCRIPTOR': descriptor, '__module__': None})
    #        msgClass=lbsnstructure.Structure_pb2[msgType]
    #        message=msgClass()
    #        message.ParseFromString(stringMessage)
    #        return message

    def remove_merge_duplicate_records_format_csv(self, type_name):
        """ Will merge all single proto batches and
            - remove duplicates
            - output formatted csv

            This Mainloop uses procedures below.
        """
        merged_filename = f'{self.output_path_file}{type_name}_Proto.csv'
        cleaned_merged_filename = f'{self.output_path_file}' \
                                  f'{type_name}_cleaned.csv'
        cleaned_merged_filename_csv = f'{self.output_path_file}' \
                                      f'{type_name}_pgCSV.csv'
        if os.path.isfile(merged_filename):
            merged_file = open(merged_filename, 'r', encoding='utf8')
            cleaned_merged_file = open(
                cleaned_merged_filename, 'w', encoding='utf8')
            cleaned_merged_file_copy = open(
                cleaned_merged_filename_csv, 'w', encoding='utf8')
            self.clean_merged_file(
                merged_file, cleaned_merged_file,
                cleaned_merged_file_copy, type_name)
            os.remove(merged_filename)
            os.rename(cleaned_merged_filename, merged_filename)

    def get_record_id_from_base64_encoded_string(self, line):
        """ Gets record ID from base 64 encoded string
            (unused function)
        """
        record = self.get_record_from_base64_encoded_string(line)
        return record.pkey.id

    def get_record_from_base64_encoded_string(self, line, type_name=None):
        """ Gets ProtoBuf record from base 64 encoded string.
        """
        record = self.create_proto_by_descriptor_name(type_name)
        record.ParseFromString(base64.b64decode(line))  # .strip("\n"))
        return record

    def merge_records(self, duplicate_record_lines, type_name):
        """ Will merge multiple proto buf records to one,
            eliminating duplicates and merging information.
        """
        if len(duplicate_record_lines) > 1:
            # first do a simple compare/unique
            unique_records = set(duplicate_record_lines)
            if len(unique_records) > 1:
                # input(f'Len: {len(unique_records)} : {unique_records}')
                # if more than one unqiue record infos,
                # get first and deep-compare-merge with following
                prev_duprecord = self.get_record_from_base64_encoded_string(
                    duplicate_record_lines[0], type_name)
                for duprecord in duplicate_record_lines[1:]:
                    # merge current record with previous until no more found
                    record = self.get_record_from_base64_encoded_string(
                        duprecord, type_name)
                    # will modify/overwrite prev_duprecord
                    HelperFunctions.merge_existing_records(
                        prev_duprecord, record)
                merged_record = self.serialize_encode_record(prev_duprecord)
            else:
                # take first element
                merged_record = next(iter(unique_records))
        else:
            merged_record = duplicate_record_lines[0]
        return merged_record

    def format_b64_encoded_record_for_csv(self, record_b64, type_name):
        """ Will convert protobuf base 64 encoded (prepared) records and
            convert to CSV formatted list of lines.
        """
        record = self.get_record_from_base64_encoded_string(
            record_b64, type_name)
        # convert Protobuf to Value list
        prepared_record = self.db_mapping.func_prepare_selector(record)
        formatted_value_list = []
        for value in prepared_record:
            # CSV Writer can't produce CSV that can be directly read
            # by Postgres with /Copy
            # Format some types manually (e.g. arrays, null values)
            if isinstance(value, list):
                value = '{' + ",".join(value) + '}'
            elif self.suppress_linebreaks and isinstance(value, str):
                # replace linebreaks by actual string so we can use
                # heapqMerge to merge line by line
                value = value.replace('\n', '\\n').replace('\r', '\\r')
            formatted_value_list.append(value)
        return formatted_value_list

    def clean_merged_file(self, merged_file, cleaned_merged_file,
                          cleaned_merged_file_copy, type_name):
        """ Will merge files and remove duplicates records.
        """
        dupsremoved = 0
        with merged_file, cleaned_merged_file, cleaned_merged_file_copy:
            header = self.db_mapping.get_header_for_type(type_name)
            cleaned_merged_file_copy.write("%s\n" % header)
            csv_output = csv.writer(cleaned_merged_file_copy, delimiter=',',
                                    lineterminator='\n', quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
            # start readlines/compare
            previous_record_id, previous_record_b64 = next(
                merged_file).split(',', 1)
            # strip linebreak from line ending
            previous_record_b64 = previous_record_b64.strip()
            duplicate_record_lines = []
            for line in merged_file:
                record_id, record_b64 = line.split(',', 1)
                # strip linebreak from line ending
                record_b64 = record_b64.strip()
                if record_id == previous_record_id:
                    # if duplicate, add to list to merge later
                    duplicate_record_lines.extend(
                        (previous_record_b64, record_b64))
                    continue
                else:
                    # if different id, do merge [if necessary],
                    # then continue processing
                    if duplicate_record_lines:
                        # add/overwrite new record line
                        # write merged record and continue
                        merged_record_b64 = self.merge_records(
                            duplicate_record_lines, type_name)
                        dupsremoved += len(duplicate_record_lines) - 1
                        duplicate_record_lines = []
                        previous_record_b64 = merged_record_b64
                cleaned_merged_file.write(
                    f'{previous_record_id},{previous_record_b64}\n')
                formatted_value_list = self.format_b64_encoded_record_for_csv(
                    previous_record_b64, type_name)
                csv_output.writerow(formatted_value_list)
                previous_record_id = record_id
                previous_record_b64 = record_b64
            # finally
            if duplicate_record_lines:
                final_merged_record = self.merge_records(
                    duplicate_record_lines, type_name)
            else:
                final_merged_record = previous_record_b64
            cleaned_merged_file.write(
                f'{previous_record_id},{final_merged_record}\n')
            formatted_value_list = self.format_b64_encoded_record_for_csv(
                final_merged_record, type_name)
            csv_output.writerow(formatted_value_list)
        print(
            f'{type_name} Duplicates Merged: {dupsremoved}'
            f'                             ')  # needed for easy overwrite
