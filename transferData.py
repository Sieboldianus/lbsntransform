# -*- coding: utf-8 -*-

__author__      = "Alexander Dunkel"
__license__   = "GNU GPLv3"
__version__ = "0.1.0"

import getpass
import argparse
import logging 
from classes.dbConnection import dbConnection
from classes.helperFunctions import helperFunctions
from classes.helperFunctions import lbsnRecordDicts as lbsnRecordDicts
from classes.fieldMapping import fieldMappingTwitter as fieldMappingTwitter
from classes.submitData import lbsnDB as lbsnDB
#LBSN Structure Import from ProtoBuf
from lbsnstructure.Structure_pb2 import *
from lbsnstructure.external.timestamp_pb2 import Timestamp
import io
import sys
import datetime
from google.protobuf import text_format
import random
import psycopg2

def import_config():
    import config
    input_username = getattr(config, 'dbUser_Input', 0)
    input_userpw = getattr(config, 'dbPassword_Input', 0)
    output_username = getattr(config, 'dbUser_Output', 0)
    output_userpw = getattr(config, 'dbPassword_Output', 0)    
    return input_username,input_userpw,output_username,output_userpw
    
def main():
    # Set Output to Replace in case of encoding issues (console/windows)
    # Necessary? ProtoBuf will convert any problematic characters to Octal Escape Sequences anyway
    # see https://stackoverflow.com/questions/23173340/how-to-convert-octal-escape-sequences-with-python
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), sys.stdout.encoding, 'replace')
    # Load Config
    # will be overwritten if args are given
    input_username,input_userpw,output_username,output_userpw = import_config()
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('-pO', "--passwordOutput", default=0) 
    parser.add_argument('-uO', "--usernameOutput", default="test")
    parser.add_argument('-aO', "--serveradressOutput", default="111.11.11.11")
    parser.add_argument('-nO', "--dbnameOutput", default="test_db")
    parser.add_argument('-pI', "--passwordInput", default=input_userpw) 
    parser.add_argument('-uI', "--usernameInput", default=input_username)
    parser.add_argument('-aI', "--serveradressInput", default="222.22.222.22") 
    parser.add_argument('-nI', "--dbnameInput", default="test_db2")    
    parser.add_argument('-t', "--transferlimit", default=None)
    parser.add_argument('-tR', "--transferReactions", default=1)
    parser.add_argument('-rR', "--disableReactionPostReferencing", default=0) # 0 = Save Original Tweets of Retweets in "posts"; 1 = do not store Original Tweets of Retweets; !Not implemented: 2 = Store Original Tweets of Retweets as "post_reactions"
    parser.add_argument('-tG', "--transferNotGeotagged", default=1) 
    parser.add_argument('-rS', "--startWithDBRowNumber", default=0) 
    parser.add_argument('-rE', "--endWithDBRowNumber", default=None) 
    parser.add_argument('-d', "--debugMode", default="INFO") #needs to be implemented
    args = parser.parse_args()
    if args.disableReactionPostReferencing == 0:
        # Enable this option in args to prevent empty posts stored due to Foreign Key Exists Requirement
        disableReactionPostReferencing = None
    else:
        disableReactionPostReferencing = True
    logging.basicConfig(handlers=[logging.FileHandler('test.log', 'w', 'utf-8')],
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    log = logging.getLogger(__name__)
    # Get Stream handler, so we can also print to console while logging to file
    logging.getLogger().addHandler(logging.StreamHandler())
        
    transferlimit = int(args.transferlimit)

    #origin = lbsnOrigin()
    #origin.origin_id = lbsnOrigin.TWITTER
    
    outputConnection = dbConnection(args.serveradressOutput,
                                   args.dbnameOutput,
                                   args.usernameOutput,
                                   args.passwordOutput
                                   )
    conn_output, cursor_output = outputConnection.connect()
    outputDB = lbsnDB(dbCursor = cursor_output, 
                      dbConnection = conn_output)
    inputConnection = dbConnection(args.serveradressInput,
                                   args.dbnameInput,
                                   args.usernameInput,
                                   args.passwordInput,
                                   True # ReadOnly Mode
                                   )
    processedRecords = 0
    firstDBRowNumber = 0   
    continueWithDBRowNumber = args.startWithDBRowNumber # Start Value, Modify to continue from last processing  
    endWithDBRowNumber = args.endWithDBRowNumber # End Value, Modify to continue from last processing    
    conn_input, cursor_input = inputConnection.connect()
    finished = False
    while not finished:
        #lbsnRecords = lbsnRecordDicts()
        twitterRecords = fieldMappingTwitter(disableReactionPostReferencing)
        records, returnedRecord_count = fetchJsonData_from_LBSN(cursor_input, continueWithDBRowNumber, transferlimit)
        continueWithDBRowNumber = records[-1][0] #last returned DBRowNumber
        if not firstDBRowNumber:
            firstDBRowNumber = records[0][0] #first returned DBRowNumber    
        if returnedRecord_count == 0:
            finished = True
            break
        else:
            twitterRecords, processedRecords, finished = loopInputRecords(records, processedRecords, transferlimit, finished, twitterRecords, endWithDBRowNumber)
            print(f'{processedRecords} Processed. Count per type: {twitterRecords.lbsnRecords.getTypeCounts()}records.', end='\n')
            # update console
            sys.stdout.flush()
        tsuccessful = False
        tcount = 0
        while not tsuccessful and tcount < 5:
            try:
                outputDB.submitLbsnRecordDicts(twitterRecords.lbsnRecords)
                tsuccessful = True
            except psycopg2.IntegrityError as e:
                # If language does not exist, we'll trust Twitter and add this to our language list
                missingLanguage = e.diag.message_detail.partition("(post_language)=(")[2].partition(") is not present")[0]
                print(f'\nTransactionIntegrityError occurred on or after DBRowNumber {records[0][0]}, inserting language "{missingLanguage}" first..')
                insert_sql = '''
                       INSERT INTO "language" (language_short,language_name,language_name_de)
                       VALUES (%s,NULL,NULL)
                       ON CONFLICT (language_short)
                       DO UPDATE SET                                                                                           
                           language_short = EXCLUDED.language_short;                                
                       '''
                outputDB.dbCursor.execute(insert_sql,(missingLanguage,))
            tcount += 1 
        outputDB.commitChanges()
        sys.stdout.flush()
            
    # Close connections to DBs        
    cursor_input.close()
    cursor_output.close()
    log.info(f'\n\nProcessed {processedRecords} records (DBRowNumber {firstDBRowNumber} to {continueWithDBRowNumber}).')
    print('Done.')

    
def loopInputRecords(jsonRecords, processedRecords, transferlimit, finished, twitterRecords, endWithDBRowNumber):
    for record in jsonRecords:
        processedRecords += 1
        DBRowNumber = record[0]
        singleJSONRecordDict = record[2]
        if singleJSONRecordDict.get('limit'):
            # Skip Rate Limiting Notice
            continue
        twitterRecords.parseJsonRecord(singleJSONRecordDict)
        #lbsnRecords = fieldMappingTwitter
        if processedRecords >= transferlimit or (endWithDBRowNumber and DBRowNumber >= endWithDBRowNumber):
            finished = True
    return twitterRecords, processedRecords, finished
   
def fetchJsonData_from_LBSN(cursor, startID = 0, transferlimit = None):
    if transferlimit:
        numberOfRecordsToFetch = min(10000,transferlimit)
    else:
        numberOfRecordsToFetch = 10000
    query_sql = '''
            SELECT in_id,insert_time,data::json FROM public."input"
            WHERE in_id > %s
            ORDER BY in_id ASC LIMIT %s;
            '''
    cursor.execute(query_sql,(startID,numberOfRecordsToFetch)) #if transferlimit is below 10000, retrieve only necessary volume of records
    records = cursor.fetchall()
    return records, cursor.rowcount

if __name__ == "__main__":
    main()
    

    
