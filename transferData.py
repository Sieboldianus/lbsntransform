# -*- coding: utf-8 -*-

__author__      = "Alexander Dunkel"
__license__   = "GNU GPLv3"
__version__ = "0.1.1"

import getpass
import logging 
from classes.dbConnection import dbConnection
from classes.helperFunctions import helperFunctions
from classes.helperFunctions import lbsnRecordDicts as lbsnRecordDicts
from classes.fieldMapping import fieldMappingTwitter as fieldMappingTwitter
from classes.submitData import lbsnDB as lbsnDB
from config.config import baseconfig as baseconfig
# LBSN Structure Import from ProtoBuf
from lbsnstructure.Structure_pb2 import *
from lbsnstructure.external.timestamp_pb2 import Timestamp
import io
import sys
import datetime
from google.protobuf import text_format
import random
import psycopg2
#from multiprocessing.pool import ThreadPool
#pool = ThreadPool(processes=1)

def main():
    # Set Output to Replace in case of encoding issues (console/windows)
    # Necessary? ProtoBuf will convert any problematic characters to Octal Escape Sequences anyway
    # see https://stackoverflow.com/questions/23173340/how-to-convert-octal-escape-sequences-with-python
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), sys.stdout.encoding, 'replace')
    # Load Config
    # will be overwritten if args are given
    config = baseconfig()
    # Parse args
    config.parseArgs()
    # set logger
    logging.basicConfig(handlers=[logging.FileHandler('test.log', 'w', 'utf-8')],
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    log = logging.getLogger(__name__)
    # Get Stream handler, so we can also print to console while logging to file
    logging.getLogger().addHandler(logging.StreamHandler())
    # establish output connection
    outputConnection = dbConnection(config.dbServeradressOutput,
                                   config.dbNameOutput,
                                   config.dbUser_Output,
                                   config.dbPassword_Output
                                   )
    conn_output, cursor_output = outputConnection.connect()
    outputDB = lbsnDB(dbCursor = cursor_output, 
                      dbConnection = conn_output)
    # establish input connection
    inputConnection = dbConnection(config.dbServeradressInput,
                                   config.dbNameInput,
                                   config.dbUser_Input,
                                   config.dbPassword_Input,
                                   True # ReadOnly Mode
                                   )
    # start settings
    processedRecords = 0
    processedTotal = 0
    firstDBRowNumber = 0   
    continueWithDBRowNumber = config.startWithDBRowNumber # Start Value, Modify to continue from last processing  
    endWithDBRowNumber = config.endWithDBRowNumber # End Value, Modify to continue from last processing    
    conn_input, cursor_input = inputConnection.connect()
    finished = False
    twitterRecords = fieldMappingTwitter(config.disableReactionPostReferencing)
    # loop input DB until transferlimit reached or no more rows are returned
    while not finished:    
        records = fetchJsonData_from_LBSN(cursor_input, continueWithDBRowNumber, config.transferlimit, config.numberOfRecordsToFetch)
        if not records:
            break      
        continueWithDBRowNumber = records[-1][0] #last returned DBRowNumber
        twitterRecords, processedCount, finished = loopInputRecords(records, config.transferlimit, twitterRecords, endWithDBRowNumber)
        processedRecords += processedCount
        processedTotal += processedCount        
        print(f'{processedTotal} Processed. Count per type: {twitterRecords.lbsnRecords.getTypeCounts()}records.', end='\n')
        # update console
        sys.stdout.flush()
        # On the first loop or after 500.000 processed records, transfer results to DB
        if not firstDBRowNumber or processedRecords >= config.transferCount or finished:
            print(f'Transferring {processedRecords} records to output db..', end='\r')
            sys.stdout.flush()
            # Async Submit needs further work:
            #asyncTransfer = pool.apply_async(submitAsync, (outputDB,twitterRecords.lbsnRecords))
            tsuccessful = False
            issuesCount = 0
            while not tsuccessful and issuesCount < 5:
                try:
                    outputDB.submitLbsnRecordDicts(twitterRecords.lbsnRecords)
                    tsuccessful = True
                except psycopg2.IntegrityError as e:
                    # If language does not exist, we'll trust Twitter and add this to our language list
                    missingLanguage = e.diag.message_detail.partition("(post_language)=(")[2].partition(") is not present")[0]
                    print(f'TransactionIntegrityError occurred on or after DBRowNumber {records[0][0]}, inserting language "{missingLanguage}" first..')
                    conn_output.rollback()
                    insert_sql = '''
                           INSERT INTO "language" (language_short,language_name,language_name_de)
                           VALUES (%s,NULL,NULL);                                
                           '''
                    outputDB.dbCursor.execute(insert_sql,(missingLanguage,))
                issuesCount += 1 
            outputDB.commitChanges()
            # create a new empty dict of records
            twitterRecords = fieldMappingTwitter(config.disableReactionPostReferencing)
            print(f'Transferring {processedRecords} records to output db..Done (up to DB Row {continueWithDBRowNumber}).')
            processedRecords = 0
        # remember the first processed DBRow ID
        if not firstDBRowNumber:
            firstDBRowNumber = records[0][0] #first returned DBRowNumber       
    # Close connections to DBs        
    cursor_input.close()
    cursor_output.close()
    log.info(f'\n\nProcessed {processedTotal} records (DBRowNumber {firstDBRowNumber} to {continueWithDBRowNumber}).')
    print('Done.')
       
def loopInputRecords(jsonRecords,transferlimit, twitterRecords, endWithDBRowNumber):
    finished = False
    processedRecords = 0
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
            break
    return twitterRecords, processedRecords, finished
   
def fetchJsonData_from_LBSN(cursor, startID = 0, transferlimit = None, numberOfRecordsToFetch = 10000):
    #if transferlimit is below 10000, retrieve only necessary volume of records
    if transferlimit:
        numberOfRecordsToFetch = min(numberOfRecordsToFetch,transferlimit)
    query_sql = '''
            SELECT in_id,insert_time,data::json FROM public."input"
            WHERE in_id > %s
            ORDER BY in_id ASC LIMIT %s;
            '''
    cursor.execute(query_sql,(startID,numberOfRecordsToFetch)) 
    records = cursor.fetchall()
    if cursor.rowcount == 0:
        return None
    else:
        return records

if __name__ == "__main__":
    main()
    
#def submitAsync(outputDB, records):
#    
#    tsuccessful = False
#    issuesCount = 0
#    while not tsuccessful and issuesCount < 5:
#        try:
#            #asyncTransfer = pool.apply_async(outputDB.submitLbsnRecordDicts, (twitterRecords.lbsnRecords,))
#            outputDB.submitLbsnRecordDicts(records)
#            tsuccessful = True
#        except psycopg2.IntegrityError as e:
#            # If language does not exist, we'll trust Twitter and add this to our language list
#            missingLanguage = e.diag.message_detail.partition("(post_language)=(")[2].partition(") is not present")[0]
#            print(f'TransactionIntegrityError occurred on or after DBRowNumber {records[0][0]}, inserting language "{missingLanguage}" first..')
#            conn_output.rollback()
#            insert_sql = '''
#                   INSERT INTO "language" (language_short,language_name,language_name_de)
#                   VALUES (%s,NULL,NULL);                                
#                   '''
#            outputDB.dbCursor.execute(insert_sql,(missingLanguage,))
#        issuesCount += 1 
#    outputDB.commitChanges()
    

    
