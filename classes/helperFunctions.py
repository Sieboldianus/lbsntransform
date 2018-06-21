# -*- coding: utf-8 -*-

from datetime import timezone
import re
import csv
import emoji
import numpy as np
from lbsnstructure.Structure_pb2 import *
from lbsnstructure.external.timestamp_pb2 import Timestamp
import datetime
import logging
import time
from collections import Counter
from json import JSONDecoder, JSONDecodeError
# for debugging only:
from google.protobuf import text_format

class helperFunctions():  
    
    def utc_to_local(utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
    
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext
    
    def extract_emojis(str):
        #str = str.decode('utf-32').encode('utf-32', 'surrogatepass')
        #return list(c for c in str if c in emoji.UNICODE_EMOJI)
        return list(c for c in str if c in emoji.UNICODE_EMOJI)
    
    def getRectangleBounds(points):
        lats = []
        lngs = []
        for point in points:
            lngs.append(point[0])
            lats.append(point[1])
        limYMin = np.min(lats)       
        limYMax = np.max(lats)    
        limXMin = np.min(lngs)       
        limXMax = np.max(lngs)
        return limYMin,limYMax,limXMin,limXMax
    
    def createNewLBSNRecord_with_id(record,id,origin):
            # initializes new record with composite ID
            c_Key = CompositeKey()
            c_Key.origin.CopyFrom(origin)
            c_Key.id = id
            record.pkey.CopyFrom(c_Key)                        
            return record
        
    def isPostReaction(jsonString):
        if 'quoted_status' in jsonString or 'retweeted_status' in jsonString or jsonString.get('in_reply_to_status_id_str'):
            # The retweeted field will return true if a tweet _got_ retweeted
            # To detect if a tweet is a retweet of other tweet, check the retweeted_status field
            return True
        else:
            return False
    
    def assignMediaPostType(jsonMediaString):
        # if post, get type of first entity
        typeString = jsonMediaString[0].get('type')
        # type is either photo, video, or animated_gif
        # https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/extended-entities-object.html
        if typeString:
            if typeString == "photo":
                post_type = lbsnPost.IMAGE
            elif typeString in ("video","animated_gif"):
                post_type = lbsnPost.VIDEO
            
        else:
            post_type = lbsnPost.OTHER
            log.debug(f'Other Post type detected: {jsonMediaString}')
        return post_type
    
    def parseJSONDateStringToProtoBuf(jsonDateString):
        # Parse String -Timestamp Format found in Twitter json
        dateTimeRecord = datetime.datetime.strptime(jsonDateString,'%a %b %d %H:%M:%S +0000 %Y') 
        protobufTimestampRecord = Timestamp()
        # Convert to ProtoBuf Timestamp Recommendation
        protobufTimestampRecord.FromDatetime(dateTimeRecord)
        return protobufTimestampRecord
    
    def getMentionedUsers(userMentions_jsonString,origin):
        mentionedUsersList = []
        for userMention in userMentions_jsonString:    #iterate over the list
            refUserRecord = helperFunctions.createNewLBSNRecord_with_id(lbsnUser(),userMention.get('id_str'),origin)
            refUserRecord.user_fullname = userMention.get('name') # Needs to be saved
            refUserRecord.user_name = userMention.get('screen_name')
            mentionedUsersList.append(refUserRecord)
        return mentionedUsersList
    
    def substituteReferencedUser(mainPost, origin, log):
        # Look for mentioned userRecords
        refUser_pkey = None
        userMentionsJson = mainPost.get('entities').get('user_mentions')
        if userMentionsJson:
            refUserRecords = helperFunctions.getMentionedUsers(userMentionsJson,origin)
            # if it is a retweet, and the status contains 'RT @', and the mentioned UserID is in status, we can almost be certain that it is the userid who posted the original tweet that was retweeted
            if refUserRecords and refUserRecords[0].user_name.lower() in mainPost.get('text').lower() and  mainPost.get('text').startswith(f'RT @'):
                refUser_pkey = refUserRecords[0].pkey
            if refUser_pkey is None:
                log.warning(f'No User record found for referenced post in: {mainPost}')     
                input("Press Enter to continue... (post will be saved without userid)")
        return refUser_pkey

    def null_check(recordAttr):
        if not recordAttr:
            return None
        else:
            # This function will also remove Null bytes from string, which aren't supported by Postgres
            if isinstance(recordAttr, str):
                recordAttr = helperFunctions.clean_null_bytes_from_str(recordAttr)
            return recordAttr

    def null_check_datetime(recordAttr):
        if not recordAttr:
            return None
        else:
            if recordAttr.ToDatetime() == datetime.datetime(1970, 1, 1, 0, 0, 0):
                return None
            else:
                return recordAttr.ToDatetime()
            
    def geoconvertOrNone(geom):
        if geom:
            return "ST_GeomFromText(%s,4326)"
        else:
            return "%s"
        
    def decode_stacked(document, pos=0, decoder=JSONDecoder()):
        NOT_WHITESPACE = re.compile(r'[^\s]')
        while True:
            match = NOT_WHITESPACE.search(document, pos)
            if not match:
                return
            pos = match.start()
    
            try:
                obj, pos = decoder.raw_decode(document, pos)
            except JSONDecodeError:
                # do something sensible if there's some error
                raise
            yield obj
            
    def clean_null_bytes_from_str(str):
        str_without_null_byte = str.replace('\x00','') 
        return str_without_null_byte            
                 
class lbsnRecordDicts():
    def __init__(self, lbsnCountryDict=dict(), lbsnCityDict=dict(),
                 lbsnPlaceDict=dict(),lbsnUserGroupDict=dict(),lbsnUserDict=dict(),lbsnPostDict=dict(), lbsnPostReactionDict=dict()):
        self.lbsnCountryDict = lbsnCountryDict
        self.lbsnCityDict = lbsnCityDict
        self.lbsnPlaceDict = lbsnPlaceDict
        self.lbsnUserGroupDict = lbsnUserGroupDict
        self.lbsnUserDict = lbsnUserDict
        self.lbsnPostDict = lbsnPostDict
        self.lbsnPostReactionDict = lbsnPostReactionDict
        self.KeyHashes = {lbsnPost.DESCRIPTOR.name: set(), 
                         lbsnCountry.DESCRIPTOR.name: set(),
                         lbsnCity.DESCRIPTOR.name: set(),
                         lbsnPlace.DESCRIPTOR.name: set(),
                         lbsnUserGroup.DESCRIPTOR.name: set(),
                         lbsnUser.DESCRIPTOR.name: set(),
                         lbsnPostReaction.DESCRIPTOR.name: set()}
        self.CountGlob = 0
        # returns all recordsDicts in correct order, with names as references (tuple)
        self.allDicts = [
            (self.lbsnCountryDict,lbsnCountry().DESCRIPTOR.name),
            (self.lbsnCityDict,lbsnCity().DESCRIPTOR.name),
            (self.lbsnPlaceDict,lbsnPlace().DESCRIPTOR.name),
            (self.lbsnUserGroupDict,lbsnUserGroup().DESCRIPTOR.name),
            (self.lbsnUserDict,lbsnUser().DESCRIPTOR.name),
            (self.lbsnPostDict,lbsnPost().DESCRIPTOR.name),
            (self.lbsnPostReactionDict,lbsnPostReaction().DESCRIPTOR.name)
            ]

    #def allDicts(self):
    #    # returns all recordsDicts
    #    recordsDictsMembers = []
    #    for attr, value in self.__dict__.items():
    #        if not attr == "KeyHashes":
    #            recordsDictsMembers.append(value)
    #    return recordsDictsMembers
                    
    def getTypeCounts(self):
        countList = []
        for x, y in self.KeyHashes.items():
            countList.append(f'{x}: {len(y)} ')
        return ''.join(countList)
            
    def update_keyHash(self, record):
        # Keep lists of pkeys for each type
        # this can be used to check for duplicates or to get a total count for each type of records (Number of unique Users, Countries, Places etc.)
        # in this case we assume that origin_id remains the same in each program iteration!
        self.KeyHashes[record.DESCRIPTOR.name].add(record.pkey.id)
        
    def MergeExistingRecords(self, newrecord, dict):
        # Basic Compare function for GUIDS
        # Compare Length of ProtoBuf Messages, keep longer ones
        # This should be updated to compare the complete structure, including taking into account the timestamp of data, if two values exist
        pkeyID = newrecord.pkey.id
        if pkeyID in dict:
            # First check if length of both ProtoBuf Messages are the same
            oldRecordString = dict[pkeyID].SerializeToString()
            newRecordString = newrecord.SerializeToString()
            if len(oldRecordString) == len(newRecordString):
                # no need to do anything
                return
            else:
                # Do a deep compare
                dict[pkeyID] = self.deepCompareMergeMessages(dict[pkeyID],newrecord)                   
                return
        else:
            # just count new entries
            self.CountGlob += 1
            if self.CountGlob % 1000 == 0:
                # progress report (modulo)
                print(f'Processing Records {self.CountGlob}..                                                    ', end='\r') 
                sys.stdout.flush()
        self.update_keyHash(newrecord) # update keyHash only necessary for new record                                                                                                 
        dict[pkeyID] = newrecord
    
    def deepCompareMergeMessages(self,oldRecord,newRecord):
        # needs testing for posts!
        #found = False
        #if oldRecord.pkey.id == '984048002967982080':
        #if oldRecord.DESCRIPTOR.name == lbsnPost().DESCRIPTOR.name:
        #    print('###################################################################')
        #    print(f'Old Record: {text_format.MessageToString(oldRecord,as_utf8=True)}')
        #    print('#######')
        #    print(f'New Record: {text_format.MessageToString(newRecord,as_utf8=True)}')
        #    print('#######')
        #    #found = True

        # this is a basic routine that will make a full compare of all fields of two lbsnRecords
        # None Values will be filled, repeated fields will be updated with new values
        # similar values remain, changed values will overwrite older values
        oldRecord.MergeFrom(newRecord)
        #for descriptor in newRecord.DESCRIPTOR.fields:
        #
        #    value_old = getattr(oldRecord, descriptor.name)
        #    value_new = getattr(newRecord, descriptor.name)
        #    if found and descriptor.name == 'active_since':
        #        print(f'Old: {value_old}')
        #        print(f'New: {value_new}')
        #        print(f'Old byte: {value_old.ByteSize()}')   
        #        print(f'New byte: {value_new.ByteSize()}')   
        #                   
        #    # only compare if not Empty or None
        #    # we can use ByteSize to see if message/field is set to default (will return 0 byte size)
        #    if value_new and value_new.ByteSize():
        #        if descriptor.label == descriptor.LABEL_REPEATED:
        #            if value_old == value_new:
        #                return oldRecord
        #            elif not value_old:
        #                newEntries = value_new
        #            else:
        #                # only add difference (e.g. = new values)
        #                newEntries = list(set(value_new) - set(value_old))   
        #            if descriptor.name == "name_alternatives":
        #                # necessary because sometimes Twitter submits English names that are not marked as English
        #                # these get moved to name_alternatives, although they exist already as the main name
        #                mainName = getattr(oldRecord, "name")
        #                if mainName and mainName in newEntries:
        #                    newEntries.remove(mainName)
        #            x = getattr(oldRecord, descriptor.name)
        #            x.extend(newEntries)
        #        # todo?
        #        #elif descriptor.label == descriptor.TYPE_ENUM:
        #        # .type gives constants according to: https://developers.google.com/protocol-buffers/docs/reference/python/google.protobuf.descriptor.FieldDescriptor-class
        #        # TYPE_MESSAGE = 11
        #        elif descriptor.type == 11:
        #            
        #            #value_old.CopyFrom(value_new)
        #            #setattr(oldRecord, descriptor.name, value_old)
        #            if found and descriptor.name == 'active_since':
        #                print(f'New X: ')
        #        else:
        #            if not value_old:
        #                setattr(oldRecord, descriptor.name, value_new)
        #            else:
        #                if not value_old == value_new:
        #                    # overwrite old value with new value
        #                    setattr(oldRecord,descriptor.name,value_new)
        #if oldRecord.pkey.id == '984048002967982080':
        #if oldRecord.DESCRIPTOR.name == lbsnPost().DESCRIPTOR.name:
        #    input(f'Record after: {text_format.MessageToString(oldRecord,as_utf8=True)}')
        return oldRecord
           
    def AddRecordsToDict(self,records):
        if isinstance(records,(list,)):
            for record in records:
                self.AddRecordToDict(record)
        else:
            record = records
            self.AddRecordToDict(record)
            
    def dictSelector(self, record):
        dictSwitcher = {
            lbsnPost().DESCRIPTOR.name: self.lbsnPostDict,
            lbsnCountry().DESCRIPTOR.name: self.lbsnCountryDict,
            lbsnCity().DESCRIPTOR.name: self.lbsnCityDict,
            lbsnPlace().DESCRIPTOR.name: self.lbsnPlaceDict,
            lbsnPostReaction().DESCRIPTOR.name: self.lbsnPostReactionDict,
            lbsnUser().DESCRIPTOR.name: self.lbsnUserDict,
            lbsnUserGroup().DESCRIPTOR.name: self.lbsnUserGroupDict,
        }
        return dictSwitcher.get(record.DESCRIPTOR.name)
            
    def AddRecordToDict(self,record):
        dict = self.dictSelector(record)
        self.MergeExistingRecords(record,dict)

class geocodeLocations():
    def __init__(self):
        self.geocodeDict = dict()
            
    def load_geocodelist(self,file):
        with open(file, newline='', encoding='utf8') as f: #read each unsorted file and sort lines based on datetime (as string)
            #next(f) #Skip Headerrow
            locationfile_list = csv.reader(f, delimiter=',', quotechar='', quoting=csv.QUOTE_NONE)
            for location_geocode in locationfile_list:
                self.geocodeDict[location_geocode[2].replace(';',',')] = (float(location_geocode[0]),location_geocode[1]) # lat/lng
        print(f'Loaded {len(self.geocodeDict)} geocodes.')

class timeMonitor():
    def __init__(self):
        self.now = time.time()
        
    def stop_time(self):
        later = time.time()
        hours, rem = divmod(later-self.now, 3600)
        minutes, seconds = divmod(rem, 60)
        difference = int(later - self.now)
        reportMsg = f'{int(hours):0>2} Hours {int(minutes):0>2} Minutes and {seconds:05.2f} Seconds passed.'
        return reportMsg