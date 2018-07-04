# -*- coding: utf-8 -*-

__author__      = "Alexander Dunkel"
__license__   = "GNU GPLv3"
__version__ = "0.1.3"

import getpass
import logging 
from classes.dbConnection import dbConnection
from classes.helperFunctions import helperFunctions
from classes.helperFunctions import lbsnRecordDicts as lbsnRecordDicts
from classes.helperFunctions import geocodeLocations as geocodeLocations
from classes.helperFunctions import timeMonitor as timeMonitor
#from classes.helperFunctions import memoryLeakDetec as memoryLeakDetec
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
# Only necessary for local import:
from glob import glob
import json


def main():
    # Set Output to Replace in case of encoding issues (console/windows)
    # Necessary? ProtoBuf will convert any problematic characters to Octal Escape Sequences anyway
    # see https://stackoverflow.com/questions/23173340/how-to-convert-octal-escape-sequences-with-python
    #sys.stdout = io.TextIOWrapper(sys.stdout.detach(), sys.stdout.encoding, 'replace')
    # Load Config
    # will be overwritten if args are given
    config = baseconfig()
    # Parse args
    config.parseArgs()
    sys.stdout.flush()
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
    
    # load from local json/csv or from PostgresDB
    if config.LocalInput:
        loc_filelist = glob(f'{config.InputPath}{config.LocalFileType}')
        inputCount = (len(loc_filelist))
        if inputCount == 0:
            sys.exit("No location files found.")
        #if not config.transferlimit:
        #    config.transferlimit = fileCount
    else:
        # establish input connection
        inputConnection = dbConnection(config.dbServeradressInput,
                                       config.dbNameInput,
                                       config.dbUser_Input,
                                       config.dbPassword_Input,
                                       True # ReadOnly Mode
                                       )
        conn_input, cursor_input = inputConnection.connect()
        inputCount = '∞'
    
    outputDB = lbsnDB(dbCursor = cursor_output, 
                  dbConnection = conn_output)    
    # start settings
    processedRecords = 0
    processedTotal = 0
    startNumber = 0   
    continueNumber = config.startWithDBRowNumber # Start Value, Modify to continue from last processing  
    endNumber = config.endWithDBRowNumber # End Value, Modify to continue from last processing   
     
    # Optional Geocoding
    geocodeDict = False
    if config.geocodeLocations:
        locationsGeocodeDict = geocodeLocations()
        locationsGeocodeDict.load_geocodelist(config.geocodeLocations)
        geocodeDict = locationsGeocodeDict.geocodeDict
      
    finished = False
    twitterRecords = fieldMappingTwitter(config.disableReactionPostReferencing, geocodeDict, config.MapRelations)
    # Manually add entries that need submission prior to parsing data
    # Example: A Group that applies to all entries
    #deutscherBundestagGroup = helperFunctions.createNewLBSNRecord_with_id(lbsnUserGroup(),"MdB (Bundestag)",twitterRecords.origin)
    #DBG_owner = helperFunctions.createNewLBSNRecord_with_id(lbsnUser(),"243586130",twitterRecords.origin)
    #DBG_owner.user_name = 'wahl_beobachter'
    #DBG_owner.user_fullname = 'Martin Fuchs'
    #deutscherBundestagGroup.user_owner_pkey.CopyFrom(DBG_owner.pkey)
    #deutscherBundestagGroup.usergroup_description = 'Alle twitternden Abgeordneten aus dem Deutschen Bundestag #bundestag'
    #twitterRecords.lbsnRecords.AddRecordToDict(DBG_owner)
    #twitterRecords.lbsnRecords.AddRecordToDict(deutscherBundestagGroup)
    
    howLong = timeMonitor()

    # loop input DB until transferlimit reached or no more rows are returned
    while not finished:
        if config.LocalInput:
            if continueNumber > len(loc_filelist)-1:
                break
            records = fetchJsonData_from_File(loc_filelist, continueNumber, config.isStackedJson)
            # skip empty files
            if not records:
                continueNumber += 1
                continue
        else:
            records = fetchJsonData_from_LBSN(cursor_input, continueNumber, config.transferlimit, config.numberOfRecordsToFetch) 
            if not records:
                break
        if config.LocalInput:
            continueNumber += 1
        else:
            continueNumber = records[-1][0] #last returned DBRowNumber
        processedCount, finished = loopInputRecords(records, config.transferlimit, twitterRecords, endNumber, config.LocalInput, config.InputType)  
        processedRecords += processedCount
        processedTotal += processedCount        
        print(f'{processedTotal} records processed ({continueNumber} of {inputCount}). Count per type: {twitterRecords.lbsnRecords.getTypeCounts()}records.', end='\n')
        # update console
        # On the first loop or after 500.000 processed records, transfer results to DB
        if not startNumber or processedRecords >= config.transferCount or finished:
            sys.stdout.flush()
            print(f'Transferring {twitterRecords.lbsnRecords.CountGlob} to db..')
            outputDB.submitLbsnRecordDicts(twitterRecords)
            outputDB.commitChanges()
            processedRecords = 0
            ## create a new empty dict of records
            twitterRecords = fieldMappingTwitter(config.disableReactionPostReferencing, geocodeDict, config.MapRelations)
        # remember the first processed DBRow ID
        if not startNumber:
            if config.LocalInput:
                startNumber = 1
            else:
                startNumber = records[0][0] #first returned DBRowNumber
    # submit remaining
    if twitterRecords.lbsnRecords.CountGlob > 0:
        print(f'Transferring remaining {twitterRecords.lbsnRecords.CountGlob} to db..')
        outputDB.submitLbsnRecordDicts(twitterRecords)
        outputDB.commitChanges()
    # Close connections to DBs       
    if not config.LocalInput: 
        cursor_input.close()
    cursor_output.close()
    log.info(f'\n\nProcessed {processedTotal} records (Input {startNumber} to {continueNumber}).')
    print(f'Done. {howLong.stop_time()}')
       
def loopInputRecords(jsonRecords, transferlimit, twitterRecords, endWithDBRowNumber, isLocalInput, InputType):
    finished = False
    processedRecords = 0
    DBRowNumber = 0
    for record in jsonRecords:
        processedRecords += 1
        if isLocalInput:
            singleJSONRecordDict = record
        else:
            DBRowNumber = record[0]
            singleJSONRecordDict = record[2]
        if not singleJSONRecordDict or singleJSONRecordDict.get('limit'):
            # Skip Rate Limiting Notice or empty records
            continue
        twitterRecords.parseJsonRecord(singleJSONRecordDict, InputType)
        if (transferlimit and processedRecords >= transferlimit) or (not isLocalInput and endWithDBRowNumber and DBRowNumber >= endWithDBRowNumber):
            finished = True
            break
    return processedRecords, finished

## edit the following procedures to your structure

def fetchJsonData_from_LBSN(cursor, startID = 0, transferlimit = None, numberOfRecordsToFetch = 10000):
    #if transferlimit is below 10000, retrieve only necessary volume of records
    if transferlimit:
        numberOfRecordsToFetch = min(numberOfRecordsToFetch, transferlimit)
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
    
def fetchJsonData_from_File(loc_filelist, startFileID = 0, isStackedJson = False):
    x = 0
    records = []
    locFile = loc_filelist[startFileID]
    with open(locFile, 'r', encoding="utf-8", errors='replace') as file:
        # Stacked JSON is a simple file with many concatenated jsons, e.g. {json1}{json2} etc.
        if isStackedJson:
            try:
                for obj in helperFunctions.decode_stacked(file.read()):
                    records.append(obj)
            except json.decoder.JSONDecodeError:
                pass
        else:
            # normal json nesting, e.g. {{record1},{record2}}
            records = json.loads(file.read())
    if records:
        return records
    else:
        return None
    
if __name__ == "__main__":
    main()
