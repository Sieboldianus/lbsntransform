# -*- coding: utf-8 -*-

from datetime import timezone
import re
import csv
import emoji
#from numpy import amin as np_min
#from numpy import amax as np_max
from lbsnstructure.lbsnstructure_pb2 import *
from google.protobuf.timestamp_pb2 import Timestamp
#from lbsnstructure.external.timestamp_pb2 import Timestamp
import datetime
import logging
import time
from collections import Counter
from json import JSONDecoder, JSONDecodeError
# for debugging only:
from google.protobuf import text_format
from shapely import geos, wkb, wkt
# https://gis.stackexchange.com/questions/225196/conversion-of-a-geojson-into-ewkb-format
geos.WKBWriter.defaults['include_srid'] = True

class HelperFunctions():

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
        limYMin = min(lats)
        limYMax = max(lats)
        limXMin = min(lngs)
        limXMax = max(lngs)
        return limYMin,limYMax,limXMin,limXMax

    def createNewLBSNRecord_with_id(record,id,origin):
            # initializes new record with composite ID
            c_Key = CompositeKey()
            c_Key.origin.CopyFrom(origin)
            c_Key.id = id
            record.pkey.CopyFrom(c_Key)
            return record

    def createNewLBSNRelationship_with_id(lbsnRelationship,relation_to_id, relation_from_id, relation_origin):
            # initializes new relationship with 2 composite IDs for one origin
            c_Key_to = CompositeKey()
            c_Key_to.origin.CopyFrom(relation_origin)
            c_Key_to.id = relation_to_id
            c_Key_from = CompositeKey()
            c_Key_from.origin.CopyFrom(relation_origin)
            c_Key_from.id = relation_from_id
            r_Key = RelationshipKey()
            r_Key.relation_to.CopyFrom(c_Key_to)
            r_Key.relation_from.CopyFrom(c_Key_from)
            lbsnRelationship.pkey.CopyFrom(r_Key)
            return lbsnRelationship

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
            refUserRecord = HelperFunctions.createNewLBSNRecord_with_id(lbsnUser(),userMention.get('id_str'),origin)
            refUserRecord.user_fullname = userMention.get('name') # Needs to be saved
            refUserRecord.user_name = userMention.get('screen_name')
            mentionedUsersList.append(refUserRecord)
        return mentionedUsersList

    def substituteReferencedUser(mainPost, origin, log):
        # Look for mentioned userRecords
        refUser_pkey = None
        userMentionsJson = mainPost.get('entities').get('user_mentions')
        if userMentionsJson:
            refUserRecords = HelperFunctions.getMentionedUsers(userMentionsJson,origin)
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
                recordAttr = HelperFunctions.clean_null_bytes_from_str(recordAttr)
            return recordAttr

    def null_check_datetime(recordAttr):
        if not recordAttr:
            return None
        else:
            if recordAttr.ToDatetime() == datetime.datetime(1970, 1, 1, 0, 0, 0):
                return None
            else:
                return recordAttr.ToDatetime()

    ## EWKB Conversion now in-code, not server-side
    #def geoconvertOrNone(geom):
    #    if geom:
    #        return "extensions.ST_GeomFromText(%s,4326)"
    #    else:
    #        return "%s"

    def returnEWKBFromGeoTEXT(text):
        if not text:
            return None
        geom = wkt.loads(text)
        geos.lgeos.GEOSSetSRID(geom._geom, 4326)
        geom = geom.wkb_hex
        return geom

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

    def merge_existing_records(oldrecord, newrecord):
        # Basic Compare function for GUIDS
        # First check if length of both ProtoBuf Messages are the same
        oldRecordString = oldrecord.SerializeToString()
        newRecordString = newrecord.SerializeToString()
        if not len(oldRecordString) == len(newRecordString):
            # no need to do anything if same lengt
            oldrecord.MergeFrom(newrecord)
            #updatedrecord = self.deepCompareMergeMessages(oldrecord,newrecord)

    def load_importer_mapping_module(origin):
        """ Switch import module based on origin input
            1 - Instagram, 2 - Flickr, 3 - Twitter
        """
        if origin == 2:
            from .field_mapping_flickr import FieldMappingFlickr as importer
        elif origin == 3:
            from .field_mapping_twitter import FieldMappingTwitter as importer
        return importer

    @staticmethod
    def dict_type_switcher(desc_name):
        """ Create protoBuf messages by name
        """
        dict_switcher = {
            lbsnCountry().DESCRIPTOR.name: lbsnCountry(),
            lbsnCity().DESCRIPTOR.name: lbsnCity(),
            lbsnPlace().DESCRIPTOR.name: lbsnPlace(),
            lbsnUser().DESCRIPTOR.name: lbsnUser(),
            lbsnUserGroup().DESCRIPTOR.name:  lbsnUserGroup(),
            lbsnPost().DESCRIPTOR.name: lbsnPost(),
            lbsnPostReaction().DESCRIPTOR.name: lbsnPostReaction(),
            lbsnRelationship().DESCRIPTOR.name: lbsnRelationship()
        }
        return dict_switcher.get(desc_name)

class LBSNRecordDicts():
    def __init__(self):
        self.lbsnCountryDict = dict()
        self.lbsnCityDict = dict()
        self.lbsnPlaceDict = dict()
        self.lbsnUserGroupDict = dict()
        self.lbsnUserDict = dict()
        self.lbsnPostDict = dict()
        self.lbsnPostReactionDict = dict()
        self.lbsnRelationshipDict = dict()
        self.KeyHashes = {lbsnPost.DESCRIPTOR.name: set(),
                         lbsnCountry.DESCRIPTOR.name: set(),
                         lbsnCity.DESCRIPTOR.name: set(),
                         lbsnPlace.DESCRIPTOR.name: set(),
                         lbsnUserGroup.DESCRIPTOR.name: set(),
                         lbsnUser.DESCRIPTOR.name: set(),
                         lbsnPostReaction.DESCRIPTOR.name: set(),
                         lbsnRelationship.DESCRIPTOR.name: set()}
        self.CountGlob = 0
        # returns all recordsDicts in correct order, with names as references (tuple)
        self.allDicts = [
            (self.lbsnCountryDict,lbsnCountry().DESCRIPTOR.name),
            (self.lbsnCityDict,lbsnCity().DESCRIPTOR.name),
            (self.lbsnPlaceDict,lbsnPlace().DESCRIPTOR.name),
            (self.lbsnUserGroupDict,lbsnUserGroup().DESCRIPTOR.name),
            (self.lbsnUserDict,lbsnUser().DESCRIPTOR.name),
            (self.lbsnPostDict,lbsnPost().DESCRIPTOR.name),
            (self.lbsnPostReactionDict,lbsnPostReaction().DESCRIPTOR.name),
            (self.lbsnRelationshipDict,lbsnRelationship().DESCRIPTOR.name)
            ]

    def getTypeCounts(self):
        countList = []
        for x, y in self.KeyHashes.items():
            countList.append(f'{x}: {len(y)} ')
        return ''.join(countList)

    def update_keyHash(self, record):
        # Keep lists of pkeys for each type
        # this can be used to check for duplicates or to get a total count for each type of records (Number of unique Users, Countries, Places etc.)
        # in this case we assume that origin_id remains the same in each program iteration!
        if record.DESCRIPTOR.name == lbsnRelationship().DESCRIPTOR.name:
            # we need the complete uuid of both entities for relationships because they can span different origin_ids
            self.KeyHashes[record.DESCRIPTOR.name].add(f'{record.pkey.relation_to.origin.origin_id}{record.pkey.relation_to.id}{record.pkey.relation_from.origin.origin_id}{record.pkey.relation_from.id}{record.relationship_type}')
        else:
            # all other entities can be globally uniquely identified by their local guid
            self.KeyHashes[record.DESCRIPTOR.name].add(record.pkey.id)

    def deepCompareMergeMessages(self,oldRecord,newRecord):
        # Do a deep compare
        # ProtoBuf MergeFrom does a fine job
        # only problem is it concatenates repeate strings, which may result in duplicate entries
        # we take care of this prior to submission (see submitData classes)
        oldRecord.MergeFrom(newRecord)
        #for descriptor in oldRecord.DESCRIPTOR.fields:
        #        if descriptor.label == descriptor.LABEL_REPEATED:
        #            if value_old == value_new:
        #                return oldRecord
        #            elif not value_old:
        #                newEntries = value_new
        #            else:
        #                # only add difference (e.g. = new values)
        #                newEntries = list(set(value_new) - set(value_old))
        #            x = getattr(oldRecord, descriptor.name)
        #            x.extend(newEntries)
        return oldRecord

    def AddRecordsToDict(self,records):
        if isinstance(records,(list,)):
            for record in records:
                self.AddRecordToDict(record)
        else:
            record = records
            self.AddRecordToDict(record)

    def dictSelector(self, record):
        """ Get dictionary by type name
        """
        dictSwitcher = {
            lbsnPost().DESCRIPTOR.name: self.lbsnPostDict,
            lbsnCountry().DESCRIPTOR.name: self.lbsnCountryDict,
            lbsnCity().DESCRIPTOR.name: self.lbsnCityDict,
            lbsnPlace().DESCRIPTOR.name: self.lbsnPlaceDict,
            lbsnPostReaction().DESCRIPTOR.name: self.lbsnPostReactionDict,
            lbsnUser().DESCRIPTOR.name: self.lbsnUserDict,
            lbsnUserGroup().DESCRIPTOR.name: self.lbsnUserGroupDict
        }
        return dictSwitcher.get(record.DESCRIPTOR.name)

    def AddRecordToDict(self,newrecord):
        dict = self.dictSelector(newrecord)
        pkeyID = newrecord.pkey.id
        if newrecord.pkey.id in dict:
            oldrecord = dict[pkeyID]
            # oldrecord will be modified/updated
            HelperFunctions.merge_existing_records(oldrecord,newrecord)
        else:
            # just count new entries
            self.countProgressReport()
            self.update_keyHash(newrecord) # update keyHash only necessary for new record
            dict[pkeyID] = newrecord

    def countProgressReport(self):
        self.CountGlob += 1
        if self.CountGlob % 1000 == 0:
            # progress report (modulo)
            print(f'Identified Output Records {self.CountGlob}..                                                    ', end='\r')
            sys.stdout.flush()

    def AddRelationshipToDict(self,newrelationship):
        pkeyID = f'{newrelationship.pkey.relation_to.origin.origin_id}{newrelationship.pkey.relation_to.id}{newrelationship.pkey.relation_from.origin.origin_id}{newrelationship.pkey.relation_from.id}{newrelationship.relationship_type}'
        if not pkeyID in self.lbsnRelationshipDict:
            self.countProgressReport()
            self.lbsnRelationshipDict[pkeyID] = newrelationship
            self.update_keyHash(newrelationship) # update keyHash only necessary for new record

class GeocodeLocations():
    def __init__(self):
        self.geocodeDict = dict()

    def load_geocodelist(self,file):
        with open(file, newline='', encoding='utf8') as f: #read each unsorted file and sort lines based on datetime (as string)
            #next(f) #Skip Headerrow
            locationfile_list = csv.reader(f, delimiter=',', quotechar='', quoting=csv.QUOTE_NONE)
            for location_geocode in locationfile_list:
                self.geocodeDict[location_geocode[2].replace(';',',')] = (float(location_geocode[0]),location_geocode[1]) # lat/lng
        print(f'Loaded {len(self.geocodeDict)} geocodes.')

class TimeMonitor():
    def __init__(self):
        self.now = time.time()

    def stop_time(self):
        later = time.time()
        hours, rem = divmod(later-self.now, 3600)
        minutes, seconds = divmod(rem, 60)
        difference = int(later - self.now)
        reportMsg = f'{int(hours):0>2} Hours {int(minutes):0>2} Minutes and {seconds:05.2f} Seconds passed.'
        return reportMsg

class MemoryLeakDetec():
    # use this class to identify memory leaks
    # execute .before() and .after() to see the difference in new objects being added
    # execute report to list
    # if there are high numbers of specific types of objects, use printType to print these, e.g. .printType(list)
    # see also http://tech.labs.oliverwyman.com/blog/2008/11/14/tracing-python-memory-leaks/
    os = __import__('os')
    def __init__(self):
        global defaultdict
        global get_objects
        from collections import defaultdict
        from gc import get_objects
        self._before = defaultdict(int)
        self._after = defaultdict(int)

    def before(self):
        for i in get_objects():
            self._before[type(i)] += 1

    def after(self):
        for i in get_objects():
            self._after[type(i)] += 1

    def report(self):
        reportStat = ""
        if self._before and self._after:
            reportStat = [(k, self._after[k] -  self._before[k]) for k in self._after if self._after[k] -  self._before[k]]
        return reportStat

    def printType(self, type, max = 100):
        x = 0
        toplist = []
        for obj in get_objects():
            if isinstance(obj, type):
                x += 1
                if x < max:
                    toplist.append(obj)
        print(f'Count all of Type {type}: {x}. Top {max}: {toplist}')