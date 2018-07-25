# -*- coding: utf-8 -*-
import argparse
import os
import sys

class BaseConfig():
    def __init__(self):
        ## Set Default Config options here
        ## or define options as input args
        self.LocalInput = 0 # Read from File/CSV
        self.LocalFileType = '*.json' # If localread, specify filetype (*.json, *.csv etc.)
        self.InputPath = None # optionally provide path to input folder, otherwise ./Input/ will be used
        self.is_stacked_json = 0
        self.dbUser_Input = 'example-user-name'
        self.dbPassword_Input = 'example-user-password'
        self.dbServeradressInput = '222.22.222.22'
        self.dbNameInput = 'test_db2'
        self.dbUser_Output = None #'example-user-name2'
        self.dbPassword_Output = None #'example-user-password2'
        self.dbServeradressOutput = None #'111.11.11.11'
        self.dbNameOutput = None #'test_db'
        self.transferlimit = None
        self.transferCount = 50000#default:50k # after how many parsed records should the result be transferred to the DB. Larger values improve speed, because duplicate check happens in Python and not in Postgres Coalesce; larger values are heavier on memory.
        self.number_of_records_to_fetch = 10000
        self.transferReactions = 1
        self.disableReactionPostReferencing = None # 0 = Save Original Tweets of Retweets in "posts"; 1 = do not store Original Tweets of Retweets; !Not implemented: 2 = Store Original Tweets of Retweets as "post_reactions"
        self.transferNotGeotagged = 1
        self.startWithdb_row_number = 0
        self.end_with_db_row_number = None
        self.debugMode = 'INFO' #needs to be implemented
        self.geocodeLocations = False # provide path to CSV file with location geocodes (CSV Structure: lat, lng, name)
        self.input_type = None # Input type, e.g. "post", "profile", "friendslist", "followerslist" etc.
        self.MapRelations = False # Set to true to map full relations, e.g. many-to-many relationships such as user_follows, user_friend, user_mentions etc. are mapped in a separate table
        self.CSVOutput = False # Set to True to Output all Submit values to CSV
        self.CSVsuppressLinebreaks = True # Set to False will not remove intext-linebreaks (\r or \n) in output CSVs

    def parseArgs(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-lI', "--LocalInput", default=self.LocalInput)
        parser.add_argument('-lT', "--LocalFileType", default=self.LocalFileType)
        parser.add_argument('-iP', "--InputPath", default=self.LocalFileType)
        parser.add_argument('-iS', "--isStackedJson", default=self.is_stacked_json)
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
        parser.add_argument('-tR', "--transferReactions", default=self.transferReactions)
        parser.add_argument('-rR', "--disableReactionPostReferencing", default=self.disableReactionPostReferencing)
        parser.add_argument('-tG', "--transferNotGeotagged", default=self.transferNotGeotagged)
        parser.add_argument('-rS', "--startWithDBRowNumber", default=self.startWithdb_row_number)
        parser.add_argument('-rE', "--endWithDBRowNumber", default=self.end_with_db_row_number)
        parser.add_argument('-d', "--debugMode", default=self.debugMode)
        parser.add_argument('-gL', "--geocodeLocations", default=self.geocodeLocations)
        parser.add_argument('-iT', "--inputType", default=self.input_type)
        parser.add_argument('-mR', "--mapFullRelations", default=self.MapRelations)
        parser.add_argument('-CSV', "--CSVOutput", action='store_true', default=self.CSVOutput)
        parser.add_argument('-CSVal', "--CSVallowLinebreaks", action='store_true', default=False)

        args = parser.parse_args()
        if args.LocalInput and int(args.LocalInput) == 1:
            self.LocalInput = True
            self.LocalFileType = args.LocalFileType
            if args.isStackedJson:
                if int(args.isStackedJson) == 1:
                    self.is_stacked_json = True
                else:
                    self.is_stacked_json = False
            if not self.InputPath:
                self.InputPath = f'{os.getcwd()}\\01_Input\\'
                print(f'Using Path: {self.InputPath}')
            else:
                self.InputPath = args.InputPath
        else:
            self.dbUser_Input = args.dbUser_Input
            self.dbPassword_Input = args.dbPassword_Input
            self.dbServeradressInput = args.dbServeradressInput
            self.dbNameInput = args.dbNameInput
        if args.geocodeLocations:
            self.geocodeLocations = f'{os.getcwd()}\\{args.geocodeLocations}'
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
        self.transferReactions = args.transferReactions
        if args.disableReactionPostReferencing and int(args.disableReactionPostReferencing) == 1:
        # Enable this option in args to prevent empty posts stored due to Foreign Key Exists Requirement
            self.disableReactionPostReferencing = True
        else:
            self.disableReactionPostReferencing = False
        self.transferNotGeotagged = args.transferNotGeotagged
        if args.startWithDBRowNumber:
            self.startWithdb_row_number = int(args.startWithDBRowNumber)
        if args.endWithDBRowNumber:
            self.end_with_db_row_number = int(args.endWithDBRowNumber)
        self.debugMode = args.debugMode
        if args.inputType:
            self.input_type = args.inputType
        if args.mapFullRelations:
            self.MapRelations = True
        if args.CSVOutput:
            self.CSVOutput = True
        if args.CSVallowLinebreaks:
            self.CSVsuppressLinebreaks = False