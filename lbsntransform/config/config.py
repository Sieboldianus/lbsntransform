# -*- coding: utf-8 -*-
import argparse
import os
import sys

from lbsnstructure.lbsnstructure_pb2 import lbsnPost

class BaseConfig():
    def __init__(self):
        ## Set Default Config options here
        ## or define options as input args
        self.Origin = 3 # Defaults to 3: Twitter (1 - Instagram, 2 - Flickr, 3 - Twitter)
        self.is_local_input = False # Read from File/CSV
        self.local_file_type = 'json' # If localread, specify filetype (json, csv etc.)
        self.InputPath = None # optionally provide path to input folder, otherwise ./Input/ will be used
        self.is_stacked_json = False
        self.dbUser_Input = 'example-user-name'
        self.dbPassword_Input = 'example-user-password'
        self.dbServeradressInput = '222.22.222.22'
        self.dbNameInput = 'test_db2'
        self.dbUser_Output = None #'example-user-name2'
        self.dbPassword_Output = None #'example-user-password2'
        self.dbServeradressOutput = None #'111.11.11.11'
        self.dbNameOutput = None #'test_db'
        self.transferlimit = None
        self.transferCount = 50000 #default:50k # after how many parsed records should the result be transferred to the DB. Larger values improve speed, because duplicate check happens in Python and not in Postgres Coalesce; larger values are heavier on memory.
        self.number_of_records_to_fetch = 10000
        self.transferReactions = True
        # Enable this option in args to prevent empty posts stored due to Foreign Key Exists Requirement
        self.disableReactionPostReferencing = False # 0 = Save Original Tweets of Retweets in "posts"; 1 = do not store Original Tweets of Retweets; !Not implemented: 2 = Store Original Tweets of Retweets as "post_reactions"
        self.ignore_non_geotagged = False
        self.startWithdb_row_number = 0
        self.end_with_db_row_number = None
        self.debugMode = 'INFO' #needs to be implemented
        self.geocodeLocations = False # provide path to CSV file with location geocodes (CSV Structure: lat, lng, name)
        self.ignore_input_source_list = False # Provide a list of input_source types that will be ignored (e.g. to ignore certain bots etc.)
        self.input_lbsn_type = None # Input type, e.g. "post", "profile", "friendslist", "followerslist" etc.
        self.MapRelations = False # Set to true to map full relations, e.g. many-to-many relationships such as user_follows, user_friend, user_mentions etc. are mapped in a separate table
        self.CSVOutput = False # Set to True to Output all Submit values to CSV
        self.CSVsuppressLinebreaks = True # Set to False will not remove intext-linebreaks (\r or \n) in output CSVs
        self.recursiveLoad = False
        self.skip_until_file = "" # If local input, skip all files until file with name x appears (default: start immediately)
        self.min_geoaccuracy = None # set to 'latlng', 'place', or 'city' to limit output based on min geoaccuracy

    def parseArgs(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-sO', "--Origin", default=self.Origin)
        parser.add_argument('-lI', "--LocalInput", action='store_true', default=False)
        parser.add_argument('-lT', "--LocalFileType", default=self.local_file_type)
        parser.add_argument('-iP', "--InputPath", default=self.InputPath)
        parser.add_argument('-iS', "--isStackedJson", action='store_true', default=False)
        parser.add_argument('-pO', "--dbPassword_Output", default=self.dbPassword_Output)
        parser.add_argument('-uO', "--dbUser_Output", default=self.dbUser_Output)
        parser.add_argument('-aO', "--dbServeradressOutput", default=self.dbServeradressOutput)
        parser.add_argument('-nO', "--dbNameOutput", default=self.dbNameOutput)
        parser.add_argument('-pI', "--dbPassword_Input", default=self.dbPassword_Input)
        parser.add_argument('-uI', "--dbUser_Input", default=self.dbUser_Input)
        parser.add_argument('-aI', "--dbServeradressInput", default=self.dbServeradressInput)
        parser.add_argument('-nI', "--dbNameInput", default=self.dbNameInput)
        parser.add_argument('-t', "--transferlimit", default=self.transferlimit)
        parser.add_argument('-tC', "--transferCount", default=self.transferCount)
        parser.add_argument('-nR', "--numberOfRecordsToFetch", default=self.number_of_records_to_fetch)
        parser.add_argument('-tR', "--disableTransferReactions", action='store_true')
        parser.add_argument('-rR', "--disableReactionPostReferencing", action='store_true', default=False)
        parser.add_argument('-iG', "--ignoreNonGeotagged", action='store_true', default=self.ignore_non_geotagged)
        parser.add_argument('-rS', "--startWithDBRowNumber", default=self.startWithdb_row_number)
        parser.add_argument('-rE', "--endWithDBRowNumber", default=self.end_with_db_row_number)
        parser.add_argument('-d', "--debugMode", default=self.debugMode)
        parser.add_argument('-gL', "--geocodeLocations", default=self.geocodeLocations)
        parser.add_argument('-igS', "--ignoreInputSourceList", default=self.ignore_input_source_list)
        parser.add_argument('-iT', "--inputType", default=self.input_lbsn_type)
        parser.add_argument('-mR', "--mapFullRelations", action='store_true')
        parser.add_argument('-CSV', "--CSVOutput", action='store_true', default=self.CSVOutput)
        parser.add_argument('-CSVal', "--CSVallowLinebreaks", action='store_true', default=False)
        parser.add_argument('-rL', "--recursiveLoad", action='store_true', default=False)
        parser.add_argument('-sF', "--skipUntilFile", default=self.skip_until_file)
        parser.add_argument('-mGA', "--minGeoAccuracy", default=self.min_geoaccuracy)

        args = parser.parse_args()
        if args.LocalInput:
            self.is_local_input = True
            self.local_file_type = args.LocalFileType
            if args.isStackedJson:
                self.is_stacked_json = True
            if not args.InputPath:
                self.InputPath = f'{os.getcwd()}\\01_Input\\'
                print(f'Using Path: {self.InputPath}')
            else:
                if args.InputPath.endswith("\\"):
                    input_path = args.InputPath
                else:
                    input_path = f'{args.InputPath}\\'
                self.InputPath = input_path
        else:
            self.dbUser_Input = args.dbUser_Input
            self.dbPassword_Input = args.dbPassword_Input
            self.dbServeradressInput = args.dbServeradressInput
            self.dbNameInput = args.dbNameInput
        if args.Origin:
            self.Origin = int(args.Origin)
        if args.geocodeLocations:
            self.geocodeLocations = f'{os.getcwd()}\\{args.geocodeLocations}'
        if args.ignoreInputSourceList:
            self.ignore_input_source_list = f'{os.getcwd()}\\{args.ignoreInputSourceList}'
        if args.dbUser_Output:
            self.dbUser_Output = args.dbUser_Output
            self.dbPassword_Output = args.dbPassword_Output
            self.dbServeradressOutput = args.dbServeradressOutput
            self.dbNameOutput = args.dbNameOutput
        if args.transferlimit:
            self.transferlimit = int(args.transferlimit)
            if self.transferlimit == 0:
                self.transferlimit = None
        if args.transferCount:
            self.transferCount = int(args.transferCount)
        if args.numberOfRecordsToFetch:
            self.number_of_records_to_fetch = int(args.numberOfRecordsToFetch)
        if args.disableTransferReactions is True:
            self.transferReactions = False
        if args.disableReactionPostReferencing:
            self.disableReactionPostReferencing = True
        self.ignore_non_geotagged = args.ignoreNonGeotagged
        if args.startWithDBRowNumber:
            self.startWithdb_row_number = int(args.startWithDBRowNumber)
        if args.endWithDBRowNumber:
            self.end_with_db_row_number = int(args.endWithDBRowNumber)
        self.debugMode = args.debugMode
        if args.inputType:
            self.input_lbsn_type = args.inputType
        if args.mapFullRelations:
            self.MapRelations = True
        if args.CSVOutput:
            self.CSVOutput = True
        if args.CSVallowLinebreaks:
            self.CSVsuppressLinebreaks = False
        if args.recursiveLoad:
            self.recursiveLoad = True
        if args.skipUntilFile:
            self.skip_until_file = args.skipUntilFile
        if args.minGeoAccuracy:
            self.min_geoaccuracy = self.check_geoaccuracy_input(args.minGeoAccuracy)

    @staticmethod
    def check_geoaccuracy_input(geoaccuracy_string):
        """Checks geoaccuracy input string and matches 
        against proto buf spec
        """
        if geoaccuracy_string == 'latlng':
            return lbsnPost.LATLNG
        elif geoaccuracy_string == 'place':
            return lbsnPost.PLACE
        elif geoaccuracy_string == 'city':
            return lbsnPost.CITY
        else:
            print("Unknown geoaccuracy.")
            return None
