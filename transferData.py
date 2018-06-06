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
    parser.add_argument('-t', "--transferlimit", default=0)
    parser.add_argument('-tR', "--transferReactions", default=0)
    parser.add_argument('-tG', "--transferNotGeotagged", default=0) 
    parser.add_argument('-rS', "--startWithDBRowNumber", default=0) 
    parser.add_argument('-rE', "--endWithDBRowNumber", default=None) 
    parser.add_argument('-d', "--debugMode", default="INFO") #needs to be implemented
    args = parser.parse_args()
    logging.basicConfig(handlers=[logging.FileHandler('test.log', 'w', 'utf-8')],
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    log = logging.getLogger(__name__)
    # Get Stream handler, so we can also print to console while logging to file
    logging.getLogger().addHandler(logging.StreamHandler())
        
    transferlimit = int(args.transferlimit)
    # We're dealing with Twitter, lets create the OriginID globally
    # this OriginID is required for all CompositeKeys
    origin = lbsnOrigin()
    origin.origin_id = lbsnOrigin.TWITTER
    
    outputConnection = dbConnection(args.serveradressOutput,
                                   args.dbnameOutput,
                                   args.usernameOutput,
                                   args.passwordOutput
                                   )
    conn_output, cursor_output = outputConnection.connect()
    outputDB = lbsnDB(dbCursor = cursor_output,dbConnection = conn_output)
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
    lbsnRecords = lbsnRecordDicts()
    while not finished:
        records, returnedRecord_count = fetchJsonData_from_LBSN(cursor_input, continueWithDBRowNumber)
        if not firstDBRowNumber:
            firstDBRowNumber = records[0][0]        
        if returnedRecord_count == 0:
            finished = True
            break
        else:
            lbsnRecords, processedRecords, continueWithDBRowNumber, finished = loopInputRecords(records, origin, processedRecords, transferlimit, finished, lbsnRecords, endWithDBRowNumber)
            print(f'{processedRecords} Processed. Count per type: {lbsnRecords.getTypeCounts()}records.', end='\r')
            # update console
            sys.stdout.flush()
            
    # Close connections to DBs        
    cursor_input.close()
    outputDB.submitLbsnRecordDicts(lbsnRecords)
    outputDB.commitChanges()
    cursor_output.close()
    log.info(f'\n\nProcessed {processedRecords} records (DBRowNumber {firstDBRowNumber} to {continueWithDBRowNumber}).')
    #print('10 Random samples for each type:\n')
    #for key,keyHash in lbsnRecords.KeyHashes.items():
    #    print(f'{key}: {", ".join(val for i, val in enumerate(random.sample(keyHash, min(10,len(keyHash)))))}')
    #print("Random Item for each type: \n")
    #print(f'lbsnCountry: {lbsnRecords.lbsnCountryDict[random.choice(list(lbsnRecords.lbsnCountryDict))]}')
    #print(f'lbsnCity: {lbsnRecords.lbsnCityDict[random.choice(list(lbsnRecords.lbsnCityDict))]}')
    #print(f'lbsnPlace: {lbsnRecords.lbsnPlaceDict[random.choice(list(lbsnRecords.lbsnPlaceDict))]}')
    #print(f'lbsnUser: {lbsnRecords.lbsnUserDict[random.choice(list(lbsnRecords.lbsnUserDict))]}')
    #print(f'lbsnPost: {lbsnRecords.lbsnPostDict[random.choice(list(lbsnRecords.lbsnPostDict))]}')
    #print(f'lbsnPostReaction: {lbsnRecords.lbsnPostReactionDict[random.choice(list(lbsnRecords.lbsnPostReactionDict))]}')  
    print('Done.')

    
def loopInputRecords(jsonRecords, origin, processedRecords, transferlimit, finished, lbsnRecords, endWithDBRowNumber):
    for record in jsonRecords:
        processedRecords += 1
        continueWithDBRowNumber = record[0]
        singleJSONRecordDict = record[2]
        if singleJSONRecordDict.get('limit'):
            # Skip Rate Limiting Notice
            continue
        lbsnRecords = fieldMappingTwitter.parseJsonRecord(singleJSONRecordDict, origin, lbsnRecords)
        if processedRecords >= transferlimit or (endWithDBRowNumber and continueWithDBRowNumber >= endWithDBRowNumber):
            finished = True
    return lbsnRecords, processedRecords, continueWithDBRowNumber, finished
   
def fetchJsonData_from_LBSN(cursor, startID = 0):
    query_sql = '''
            SELECT in_id,insert_time,data::json FROM public."input"
            WHERE in_id > %s
            ORDER BY in_id ASC LIMIT 10;
            '''
    cursor.execute(query_sql,(startID,))
    records = cursor.fetchall()
    return records, cursor.rowcount

if __name__ == "__main__":
    main()
    

    
