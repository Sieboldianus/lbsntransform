# -*- coding: utf-8 -*-

from datetime import timezone
import re
import emoji
import numpy as np
from lbsnstructure.Structure_pb2 import *
from lbsnstructure.external.timestamp_pb2 import Timestamp
import datetime

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
            if isinstance(record,lbsnPost):
                record.post_pkey.CopyFrom(c_Key)                
            elif isinstance(record,lbsnCountry):
                record.country_pkey.CopyFrom(c_Key)
            elif isinstance(record,lbsnCity):
                record.city_pkey.CopyFrom(c_Key)
            elif isinstance(record,lbsnPlace):
                record.place_pkey.CopyFrom(c_Key)
            elif isinstance(record,lbsnPostReaction):
                record.postreaction_pkey.CopyFrom(c_Key)   
            elif isinstance(record,lbsnUser):
                record.user_pkey.CopyFrom(c_Key)                         
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
        
    def updateRecordDicts(self,newLbsnRecordDicts):
        # this will overwrite values of keys in dict 1 with those in dict 2, if keys are the same
        # optimally, one should compare values and choose merge rules
        # e.g. https://www.quora.com/How-do-I-compare-two-different-dictionary-values-in-Python
        # SerializeToString() to compare messages
        # https://stackoverflow.com/questions/24296221/how-do-i-compare-the-contents-of-two-google-protocol-buffer-messages-for-equalit?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
        self.lbsnCountryDict = {** self.lbsnCountryDict, **newLbsnRecordDicts.lbsnCountryDict}
        self.lbsnCityDict = {** self.lbsnCountryDict, **newLbsnRecordDicts.lbsnCityDict}  
        self.lbsnPlaceDict = {** self.lbsnCountryDict, **newLbsnRecordDicts.lbsnPlaceDict}  
        self.lbsnUserDict = {** self.lbsnCountryDict, **newLbsnRecordDicts.lbsnUserDict}  
        self.lbsnPostDict = {** self.lbsnCountryDict, **newLbsnRecordDicts.lbsnPostDict}  
        self.lbsnPostReactionDict = {** self.lbsnCountryDict, **newLbsnRecordDicts.lbsnPostReactionDict}
        
    def Count(self):
        x = 0
        items = self.__dict__.items()
        for k,v in items:
            x += len(v) # count number of entries in specific dict (lbsnCountry, lbsnPost etc.)
        return x

    def MergeExistingRecords(self, newrecord,pkeyID,dict):
        # Compare Vaues, keep longer ones
        if pkeyID in dict:
            oldRecordString = dict[pkeyID].SerializeToString()
            newRecordString = newrecord.SerializeToString()
            if len(oldRecordString) <= len(newRecordString):
                dict[pkeyID] = newrecord
                print("overwritten")
            else:
                print("kept")
        else:
            dict[pkeyID] = newrecord
            
    def AddRecordsToDict(self,records):
        if isinstance(records,(list,)):
            for record in records:
                self.AddRecordToDict(record)
        else:
            record = records
            self.AddRecordToDict(record)
            
    def AddRecordToDict(self,record):
        print(type(record))
        if isinstance(record,lbsnPost):
            pkeyID = record.post_pkey.id
            dict = self.lbsnPostDict
        elif isinstance(record,lbsnCountry):
            pkeyID = record.country_pkey.id
            dict = self.lbsnCountryDict            
        elif isinstance(record,lbsnCity):
            pkeyID = record.city_pkey.id
            dict = self.lbsnCityDict              
        elif isinstance(record,lbsnPlace):
            pkeyID = record.place_pkey.id
            dict = self.lbsnPlaceDict              
        elif isinstance(record,lbsnPostReaction):
            pkeyID = record.postreaction_pkey.id
            dict = self.lbsnPostReactionDict            
        elif isinstance(record,lbsnUser):
            pkeyID = record.user_pkey.id
            dict = self.lbsnUserDict
        self.MergeExistingRecords(record,pkeyID,dict)