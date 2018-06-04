# -*- coding: utf-8 -*-

from datetime import timezone
import re
import emoji
import numpy as np
from lbsnstructure.Structure_pb2 import *
from lbsnstructure.external.timestamp_pb2 import Timestamp
import datetime
import logging
from collections import Counter

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
        
    def isPostReaction_Type(jsonString,return_type = False):
        reaction = lbsnPostReaction()
        if jsonString.get('in_reply_to_status_id_str'):
            if return_type:
                reaction.reaction_type = lbsnPostReaction.REPLY
                return reaction
            else:
                return True
        elif jsonString.get('quoted_status_id_str'):
            if return_type:
                reaction.reaction_type = lbsnPostReaction.QUOTE
                return reaction
            else:
                return True            
        elif jsonString.get('retweeted_status'):
            if return_type:
                reaction.reaction_type = lbsnPostReaction.SHARE
                return reaction
            else:
                return True         
        return False
    
    def isPost_Type(jsonString):
        # if post, get type of first entity
        if 'media' in jsonString:
            typeString = jsonString.get('entities').get('media')[0].get('type')
            # type is either photo, video, or animated_gif
            # https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/extended-entities-object.html
            if typeString:
                post = lbsnPost()
                if typeString == "photo":
                    post.post_type = lbsnPost.IMAGE
                elif typeString == "video" or typeString == "animated_gif":
                    post.post_type = lbsnPost.VIDEO
                else:
                    post.post_type = lbsnPost.TEXT
                return post
        else: 
            return False
      
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

class lbsnRecordDicts():  
    def __init__(self, lbsnCountryDict=dict(), lbsnCityDict=dict(),
                 lbsnPlaceDict=dict(),lbsnUserDict=dict(),lbsnPostDict=dict(), lbsnPostReactionDict=dict()):
        self.lbsnCountryDict = lbsnCountryDict
        self.lbsnCityDict = lbsnCityDict
        self.lbsnPlaceDict = lbsnPlaceDict
        self.lbsnUserDict = lbsnUserDict
        self.lbsnPostDict = lbsnPostDict
        self.lbsnPostReactionDict = lbsnPostReactionDict
        self.KeyHashes = {lbsnPost.DESCRIPTOR.name: set(), 
                         lbsnCountry.DESCRIPTOR.name: set(),
                         lbsnCity.DESCRIPTOR.name: set(),
                         lbsnPlace.DESCRIPTOR.name: set(),
                         lbsnUser.DESCRIPTOR.name: set(),
                         lbsnPostReaction.DESCRIPTOR.name: set()}
        
    def getTypeCounts(self):
        countList = []
        for x, y in self.KeyHashes.items():
            #sys.exit(f'Length: {len(y)}')
            countList.append(f'{x}: {len(y)} ')
        return ''.join(countList)
            
    def update_keyHash(self, record):
        # Keep lists of pkeys for each type
        # this can be used to check for duplicates or to get a total count for each type of records (Number of unique Users, Countries, Places etc.)
        # in this case we assume that origin_id remains the same in each program iteration!
        self.KeyHashes[record.DESCRIPTOR.name].add(record.pkey.id)

            
    def updateRecordDicts(self,newLbsnRecordDicts):
        # this will merge two recordsDicts
        # values of keys in dict 1 will be overwritten with those in dict 2, if matching keys are found
        # optimally, one should compare values and choose specific merge rules
        # e.g. https://www.quora.com/How-do-I-compare-two-different-dictionary-values-in-Python
        # SerializeToString() to compare messages
        # https://stackoverflow.com/questions/24296221/how-do-i-compare-the-contents-of-two-google-protocol-buffer-messages-for-equalit?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
        self.lbsnCountryDict = {** self.lbsnCountryDict, **newLbsnRecordDicts.lbsnCountryDict}
        self.lbsnCityDict = {** self.lbsnCityDict, **newLbsnRecordDicts.lbsnCityDict}  
        self.lbsnPlaceDict = {** self.lbsnPlaceDict, **newLbsnRecordDicts.lbsnPlaceDict}  
        self.lbsnUserDict = {** self.lbsnUserDict, **newLbsnRecordDicts.lbsnUserDict}  
        self.lbsnPostDict = {** self.lbsnPostDict, **newLbsnRecordDicts.lbsnPostDict}  
        self.lbsnPostReactionDict = {** self.lbsnPostReactionDict, **newLbsnRecordDicts.lbsnPostReactionDict}
        for dictKey in self.KeyHashes:
            self.KeyHashes[dictKey].union(newLbsnRecordDicts.KeyHashes[dictKey])
        
    def MergeExistingRecords(self, newrecord, dict):
        # Basic Compare function for GUIDS
        # Compare Length of ProtoBuf Messages, keep longer ones
        # This should be updated to compare the complete structure, including taking into account the timestamp of data, if two values exist
        pkeyID = newrecord.pkey.id
        if pkeyID in dict:
            oldRecordString = dict[pkeyID].SerializeToString()
            newRecordString = newrecord.SerializeToString()
            if len(oldRecordString) >= len(newRecordString):
                return
            #log = logging.getLogger(__name__)
            #log.warning(f'Message Overwritten! \n Old {type(dict[pkeyID])}: {oldRecordString} \n New {type(newrecord)}: {newRecordString}')
            #log.warning(f'OLD: {dict[pkeyID]}\n')
            #log.warning(f'NEW: {newrecord}\n' )
            #input("Press Enter to continue...")
        self.update_keyHash(newrecord)                                                                                              
        dict[pkeyID] = newrecord
            
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
        }
        return dictSwitcher.get(record.DESCRIPTOR.name)
            
    def AddRecordToDict(self,record):
        #print(type(record))
        dict = self.dictSelector(record)
        self.MergeExistingRecords(record,dict)