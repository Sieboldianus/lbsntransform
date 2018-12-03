# -*- coding: utf-8 -*-

import psycopg2
from .helper_functions import HelperFunctions
from .helper_functions import LBSNRecordDicts
from .shared_structure_proto_lbsndb import ProtoLBSM_db_Mapping
#from lbsn2structure import *
from lbsnstructure.lbsnstructure_pb2 import *
from google.protobuf.timestamp_pb2 import Timestamp
import logging
from sys import exit
import traceback
import os
import sys
# for debugging only:
from google.protobuf import text_format
import re
import csv
from glob import glob
import shutil

from heapq import merge as heapq_merge
from operator import itemgetter
from contextlib import ExitStack

from google.protobuf.internal import encoder
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
import base64

class LBSNcsv():
    def __init__(self, SUPPRESS_LINEBREAKS = True):
        self.output_path_file = f'{os.getcwd()}\\02_Output\\'
        self.db_mapping = ProtoLBSM_db_Mapping()
        if not os.path.exists(self.output_path_file):
            os.makedirs(self.output_path_file)
        self.store_csv_part = 0

    def store_append_batch_to_csv(self, records, round_nr, type_name, pg_copy_format = False):
        """ Takes proto buf lbsn record dict and appends all records
            to correct CSV (type-specific)
        """
        filePath = f'{self.output_path_file}{type_name}_{round_nr:03d}.csv'
        with open(filePath, 'a', encoding='utf8') as f:
            #csvOutput = csv.writer(f, delimiter=',', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for record in records:
                serializedRecord_b64 = self.serialize_encode_record(record)
                f.write(f'{record.pkey.id},{serializedRecord_b64}\n')

    def serialize_encode_record(self, record):
        """ Serializes protobuf record as string and
            encodes in base64 for corrupt-resistant backup/store/transfer
        """
        serialized_record = record.SerializeToString()
        serialized_encoded_record = base64.b64encode(serialized_record)
        serialized_encoded_record_utf = serialized_encoded_record.decode("utf-8")
        return serialized_encoded_record_utf

    #def writeCSVHeader(self, typeName):
    #    # create files and write headers
    #    #for typename, header in self.typeNamesHeaderDict.items():
    #    header = self.typeNamesHeaderDict[typeName]
    #    csvOutput = open(f'{self.output_path_file}{typeName}_{self.countRound:03d}.csv', 'w', encoding='utf8')
    #    csvOutput.write("%s\n" % header)

    def clean_csv_batches(self, batched_records):
        """ Merges all output streams per type at end
            and removes duplicates

            This is necessary because Postgres can't import Duplicates with /copy.
            Keep all records in RAM while processing input data is impossible,
            therefore merge happens only once at end.
        """
        x=0
        self.store_csv_part += 1
        print('Cleaning and merging output files..')
        for type_name in batched_records:
            x+= 1
            filelist = glob(f'{self.output_path_file}{type_name}_*.csv')
            if filelist:
                self.sort_files(filelist)
                if len(filelist) > 1:
                    print(f'Cleaning & merging output files..{x}/{len(batched_records)}', end='\r')
                    self.merge_files(filelist,type_name)
                else:
                    # no need to merge files if only one round
                    new_filename = filelist[0].replace('_001','001Proto')
                    if os.path.isfile(new_filename):
                        os.remove(new_filename)
                    if os.path.isfile(filelist[0]):
                        os.rename(filelist[0], new_filename)
                self.remove_merge_duplicate_records_format_csv(type_name)

    def sort_files(self, filelist):
        """ Function for sorting files
            (precursor to remove duplicates)
        """
        for f in filelist:
            with open(f,'r+', encoding='utf8') as batch_file:
                #skip header
                #header = batchFile.readline()
                lines = batch_file.readlines()
                # sort by first column
                lines.sort(key=lambda a_line: a_line.split()[0])
                #lines.sort()
                batch_file.seek(0)
                # delete original records in file
                batch_file.truncate()
                # write sorted records
                #batchFile.writeline(header)
                for line in lines:
                    batch_file.write(line)

    def merge_files(self, filelist, type_name):
        """ Merges multiple files to one
            using ExitStack
        """
        with ExitStack() as stack:
            files = [stack.enter_context(open(fname, encoding='utf8')) for fname in filelist]
            with open(f'{self.output_path_file}{type_name}_Proto.csv','w', encoding='utf8') as merged_file:
                merged_file.writelines(heapq_merge(*files))
        for file in filelist:
            os.remove(file)

    def create_proto_by_descriptor_name(self, desc_name):
        """Create new proto record by name
        """
        new_record = HelperFunctions.dict_type_switcher(desc_name)
        return new_record

    #def parse_message(self,msgType,stringMessage):
    #        #result_class = reflection.GeneratedProtocolMessageType(msgType,(stringMessage,),{'DESCRIPTOR': descriptor, '__module__': None})
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
        mergedFilename = f'{self.output_path_file}{type_name}_Proto.csv'
        cleanedMergedFilename = f'{self.output_path_file}{type_name}_cleaned.csv'
        cleanedMergedFilename_CSV = f'{self.output_path_file}{type_name}_pgCSV.csv'
        if os.path.isfile(mergedFilename):
            merged_file = open(mergedFilename,'r', encoding='utf8')
            cleaned_merged_file = open(cleanedMergedFilename,'w', encoding='utf8')
            cleaned_merged_file_copy = open(cleanedMergedFilename_CSV,'w', encoding='utf8')
            cleanMergedFile(merged_file, cleaned_merged_file)
            os.remove(mergedFilename)
            os.rename(cleanedMergedFilename, mergedFilename)

    def get_record_id_from_base64_encoded_string(line):
        """ Gets record ID from base 64 encoded string
            (unused function)
        """
        record = get_record_from_base64_encoded_string(line)
        return record.pkey.id

    def get_record_from_base64_encoded_string(line, type_name):
        """ Gets ProtoBuf record from base 64 encoded string.
        """
        record = self.create_proto_by_descriptor_name(type_name)
        record.ParseFromString(base64.b64decode(line))#.strip("\n"))
        return record

    def merge_records(duplicate_record_lines, type_name):
        """ Will merge multiple proto buf records to one,
            eliminating duplicates and merging information.
        """
        if len(duplicate_record_lines) > 1:
            # first do a simple compare/unique
            unique_records = set(duplicate_record_lines)
            if len(unique_records) > 1:
                #input(f'Len: {len(unique_records)} : {unique_records}')
                # if more than one unqiue record infos, get first and deep-compare-merge with following
                prev_duprecord = self.get_record_from_base64_encoded_string(duplicate_record_lines[0], type_name)
                for duprecord in duplicate_record_lines[1:]:
                    # merge current record with previous until no more found
                    record = self.get_record_from_base64_encoded_string(duprecord, type_name)
                    # will modify/overwrite prev_duprecord
                    HelperFunctions.merge_existing_records(prev_duprecord, record)
                merged_record = self.serialize_encode_record(prev_duprecord)
            else:
                # take first element
                merged_record = next(iter(unique_records))
        else:
            merged_record = duplicate_record_lines[0]
        return merged_record

    def format_b64_encoded_record_for_csv(record_b64, type_name):
        """ Will convert protobuf base 64 encoded (prepared) records and
            convert to CSV formatted list of lines.
        """
        record = self.get_record_from_base64_encoded_string(record_b64, type_name)
        # convert Protobuf to Value list
        prepared_record = ProtoLBSM_db_Mapping.func_prepare_selector(record)
        formatted_value_list = []
        for value in prepared_record:
            # CSV Writer can't produce CSV that can be directly read by Postgres with /Copy
            # Format some types manually (e.g. arrays, null values)
            if isinstance(value, list):
                value = '{' + ",".join(value) + '}'
            elif self.SUPPRESS_LINEBREAKS and isinstance(value, str):
                # replace linebreaks by actual string so we can use heapqMerge to merge line by line
                value = value.replace('\n','\\n').replace('\r', '\\r')
            formatted_value_list.append(value)
        return formatted_value_list

    def clean_merged_file(merged_file, cleaned_merged_file, type_name):
        """ Will merge files and remove duplicates records.
        """
        dupsremoved = 0
        with merged_file, cleaned_merged_file, cleaned_merged_file_copy:
            header = self.db_mapping.get_header_for_type(type_name)
            cleaned_merged_file_copy.write("%s\n" % header)
            csvOutput = csv.writer(cleaned_merged_file_copy, delimiter=',', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            # start readlines/compare
            previous_record_id, previous_record_b64 = next(merged_file).split(',', 1)
            # strip linebreak from line ending
            previous_record_b64 = previous_record_b64.strip()
            duplicate_record_lines = []
            for line in merged_file:
                record_id, record_b64 = line.split(',', 1)
                # strip linebreak from line ending
                record_b64 = record_b64.strip()
                if record_id == previous_record_id:
                    # if duplicate, add to list to merge later
                    duplicate_record_lines.extend((previous_record_b64, record_b64))
                    continue
                else:
                    # if different id, do merge [if necessary], then continue processing
                    if duplicate_record_lines:
                        # add/overwrite new record line
                        # write merged record and continue
                        mergedRecord_b64 = self.merge_records(duplicate_record_lines, type_name)
                        dupsremoved += len(duplicate_record_lines) - 1
                        duplicate_record_lines = []
                        previous_record_b64 = mergedRecord_b64
                cleaned_merged_file.write(f'{previous_record_id},{previous_record_b64}\n')
                formatted_value_list = self.format_b64_encoded_record_for_csv(previous_record_b64, type_name)
                csvOutput.writerow(formatted_value_list)
                previous_record_id = record_id
                previous_record_b64 = record_b64
            # finally
            if duplicate_record_lines:
                final_merged_record = self.merge_records(duplicate_record_lines, type_name)
            else:
                final_merged_record = previous_record_b64
            cleaned_merged_file.write(f'{previous_record_id},{final_merged_record}\n')
            formatted_value_list = self.format_b64_encoded_record_for_csv(final_merged_record, type_name)
            csvOutput.writerow(formatted_value_list)
        print(f'{typeName} Duplicates Merged: {dupsremoved}                             ')