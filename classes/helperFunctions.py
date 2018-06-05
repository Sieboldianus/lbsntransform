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
        self.update_keyHash(newrecord) # update keyHash only necessary for new record                                                                                          
        dict[pkeyID] = newrecord

    def deepCompareMergeMessages(self,oldRecord,newRecord):
        # this is a basic routine that will make a full compare of all fields of two lbsnRecords
        # None Values will be filled, repeated fields will be updated with new values
        # similar values remain, changed values will overwrite older values
        for descriptor in newRecord.DESCRIPTOR.fields:
            value_old = getattr(oldRecord, descriptor.name)
            value_new = getattr(newRecord, descriptor.name)
            # only compare if not Empty or None
            if value_new:
                if descriptor.label == descriptor.LABEL_REPEATED:
                    if value_old == value_new:
                        return oldRecord
                    elif not value_old:
                        newEntries = value_new
                    else:
                        # only add difference (e.g. = new values)
                        newEntries = list(set(value_new) - set(value_old))   
                    if descriptor.name == "name_alternatives":
                        # necessary because sometimes Twitter submits English names that are not marked as English
                        # these get moved to name_alternatives, although they exist already as the main name
                        mainName = getattr(oldRecord, "name")
                        if mainName and mainName in newEntries:
                            newEntries.remove(mainName)
                    x = getattr(oldRecord, descriptor.name)
                    x.extend(newEntries)
                #elif descriptor.label == descriptor.TYPE_ENUM: 
                elif descriptor.type == descriptor.TYPE_MESSAGE:
                   x = getattr(oldRecord, descriptor.name)
                   x.CopyFrom(value_new)
                else:
                    if not value_old:
                        setattr(oldRecord, descriptor.name, value_new)
                    else:
                        if not value_old == value_new:
                            # overwrite old value with new value
                            setattr(oldRecord,descriptor.name,value_new)
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
        }
        return dictSwitcher.get(record.DESCRIPTOR.name)
            
    def AddRecordToDict(self,record):
        #print(type(record))
        dict = self.dictSelector(record)
        self.MergeExistingRecords(record,dict)