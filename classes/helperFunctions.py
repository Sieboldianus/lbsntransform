# -*- coding: utf-8 -*-

from datetime import timezone
import re
import emoji
import numpy as np
from lbsnstructure.Structure_pb2 import *
from lbsnstructure.external.timestamp_pb2 import Timestamp

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
                reaction.post_type = lbsnPostReaction.REPLY
                return reaction
            else:
                return True
        elif jsonString.get('quoted_status_id_str'):
            if return_type:
                reaction.post_type = lbsnPostReaction.QUOTE
                return reaction
            else:
                return True            
        elif jsonString.get('retweeted_status'):
            if return_type:
                reaction.post_type = lbsnPostReaction.SHARE
                return reaction
            else:
                return True
        return False