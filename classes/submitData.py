# -*- coding: utf-8 -*-

import psycopg2
from decimal import Decimal
from classes.helperFunctions import helperFunctions
from classes.helperFunctions import lbsnRecordDicts as lbsnRecordDicts
from lbsnstructure.Structure_pb2 import *
from lbsnstructure.external.timestamp_pb2 import Timestamp
import logging 
from sys import exit
from pygments.lexers import eiffel
#from classes.helperFunctions import null_check #helperFunctions.null_check as null_check
#from classes.helperFunctions import null_check #helperFunctions.geoconvertOrNone as geoconvertOrNone

 

class lbsnDB():
    def __init__(self, dbCursor = None, 
                 dbConnection = None,
                 commit_volume = 10000):
        self.dbCursor = dbCursor
        self.dbConnection = dbConnection
        if not self.dbCursor:
            sys.exit("No DB Cursor available.")
        self.commit_volume = commit_volume
        self.count_entries_commit = 0
        self.count_glob = 0
        self.null_island_count = 0
        self.country_already_inserted = set()
        self.city_already_inserted = set()
    
    def commitChanges(self):
        self.dbConnection.commit() # commit changes to db
        self.count_entries_commit = 0
        
    def submitLbsnRecordDicts(self, recordsDicts):
        # order is important here, as PostGres will reject any records where Foreign Keys are violated
        # therefore, records are processed starting from lowest granularity, which is returned by allDicts()
        for recordsDict in recordsDicts.allDicts:
            type_name = recordsDict[1]
            for record_pkey, record in recordsDict[0].items():
                self.submitLbsnRecord(record,type_name)
                self.count_glob +=  1 #self.dbCursor.rowcount
                self.count_entries_commit +=  1 #self.dbCursor.rowcount
                if self.count_glob == 100 or self.count_entries_commit > self.commit_volume:
                    self.commitChanges()
                
    def submitLbsnRecord(self, record, record_type):
        #record_type = record.DESCRIPTOR.name
        if record_type == lbsnPost().DESCRIPTOR.name:
            self.submitLbsnPost(record)
        elif record_type == lbsnCountry().DESCRIPTOR.name:
            self.submitLbsnCountry(record)
        elif record_type == lbsnCity().DESCRIPTOR.name:
            self.submitLbsnCity(record)
        elif record_type == lbsnPlace().DESCRIPTOR.name:
            self.submitLbsnPlace(record)
        elif record_type == lbsnPostReaction().DESCRIPTOR.name:
            self.submitLbsnPostReaction(record)
        elif record_type == lbsnUser().DESCRIPTOR.name:
            self.submitLbsnUser(record)
    
    def submitLbsnCountry(self, record):
        # Get common attributes for place types Place, City and Country
        placeRecord = placeAttrShared(record)
        if not placeRecord.Guid in self.country_already_inserted:
            insert_sql = '''
                        INSERT INTO "country" (origin_id, country_guid, name, name_alternatives, geom_center, geom_area, url)
                        VALUES (%s,%s,%s,%s,''' + placeRecord.geoconvertOrNoneCenter + ''',''' + placeRecord.geoconvertOrNoneGeom + ''',%s)
                        ON CONFLICT (origin_id,country_guid)
                        DO UPDATE SET
                            name = COALESCE(EXCLUDED.name, "country".name),
                            name_alternatives = COALESCE((SELECT array_remove(altNamesNewArray,"country".name) from mergeArrays(EXCLUDED.name_alternatives, "country".name_alternatives) AS altNamesNewArray), ARRAY[]::text[]),
                            geom_center = COALESCE(EXCLUDED.geom_center, "country".geom_center),
                            geom_area = COALESCE(EXCLUDED.geom_area, "country".geom_area),
                            url = COALESCE(EXCLUDED.url, "country".url);
                        '''
            # Array merge of alternatives:
            # Arrays cannot be null, therefore COALESCE([if array not null],[otherwise create empoty array])
            # We don't want the english name to appear in alternatives, therefore: array_remove(altNamesNewArray,"country".name)
            # Finally, merge New Entries with existing ones mergeArrays([new],[old]) uses custom mergeArrays function (see function definitions)
            self.dbCursor.execute(insert_sql,(placeRecord.OriginID,placeRecord.Guid,placeRecord.name,placeRecord.name_alternatives,placeRecord.geom_center,placeRecord.geom_area,placeRecord.url))
            self.country_already_inserted.add(placeRecord.Guid)
          
    def submitLbsnCity(self, record):
        placeRecord = placeAttrShared(record)
        countryGuid = helperFunctions.null_check(record.country_pkey.id)
        if not placeRecord.Guid in self.city_already_inserted:
            insert_sql = '''
                        INSERT INTO "city" (origin_id, city_guid, name, name_alternatives, geom_center, geom_area, url, country_guid)
                        VALUES (%s,%s,%s,%s,''' + placeRecord.geoconvertOrNoneCenter + ''',''' + placeRecord.geoconvertOrNoneGeom + ''',%s,%s)
                        ON CONFLICT (origin_id,city_guid)
                        DO UPDATE SET
                            name = COALESCE(EXCLUDED.name, "city".name),
                            name_alternatives = COALESCE((SELECT array_remove(altNamesNewArray,"city".name) from mergeArrays(EXCLUDED.name_alternatives, "city".name_alternatives) AS altNamesNewArray), ARRAY[]::text[]),
                            geom_center = COALESCE(EXCLUDED.geom_center, "city".geom_center),
                            geom_area = COALESCE(EXCLUDED.geom_area, "city".geom_area),
                            url = COALESCE(EXCLUDED.url, "city".url),
                            country_guid = COALESCE(EXCLUDED.country_guid, "city".country_guid);
                        '''
            self.dbCursor.execute(insert_sql,(placeRecord.OriginID,placeRecord.Guid,placeRecord.name,placeRecord.name_alternatives,placeRecord.geom_center,placeRecord.geom_area,placeRecord.url,countryGuid))
            self.country_already_inserted.add(placeRecord.Guid)
               
    def submitLbsnPlace(self, record):
        placeRecord = placeAttrShared(record)
        cityGuid = helperFunctions.null_check(record.city_pkey.id)
        postCount = helperFunctions.null_check(record.post_count)
        if not placeRecord.Guid in self.city_already_inserted:
            insert_sql = '''
                        INSERT INTO "place" (origin_id, place_guid, name, name_alternatives, geom_center, geom_area, url, city_guid, post_count)
                        VALUES (%s,%s,%s,%s,''' + placeRecord.geoconvertOrNoneCenter + ''',''' + placeRecord.geoconvertOrNoneGeom + ''',%s,%s,%s)
                        ON CONFLICT (origin_id,place_guid)
                        DO UPDATE SET
                            name = COALESCE(EXCLUDED.name, "place".name),
                            name_alternatives = COALESCE((SELECT array_remove(altNamesNewArray,"place".name) from mergeArrays(EXCLUDED.name_alternatives, "place".name_alternatives) AS altNamesNewArray), ARRAY[]::text[]),
                            geom_center = COALESCE(EXCLUDED.geom_center, "place".geom_center),
                            geom_area = COALESCE(EXCLUDED.geom_area, "place".geom_area),
                            url = COALESCE(EXCLUDED.url, "place".url),
                            city_guid = COALESCE(EXCLUDED.city_guid, "place".city_guid),
                            post_count = GREATEST(COALESCE(EXCLUDED.post_count, "place".post_count), COALESCE("place".post_count,EXCLUDED.post_count));
                        '''
            self.dbCursor.execute(insert_sql,(placeRecord.OriginID,placeRecord.Guid,placeRecord.name,placeRecord.name_alternatives,placeRecord.geom_center,placeRecord.geom_area,placeRecord.url,cityGuid,postCount))
            #self.place_already_inserted.add(placeRecord.Guid) 
            
    def submitLbsnUser(self, record):
        print("Test")   
    def submitLbsnPost(self, record):
        print("Test")   
    def submitLbsnPostReaction(self, record):
        print("Test")
        
class placeAttrShared():   
    def __init__(self, record):
        self.OriginID = 3 #record.pkey.origin.origin_id
        self.Guid = record.pkey.id
        self.name = helperFunctions.null_check(record.name)
        self.name_alternatives = list(record.name_alternatives)
        if self.name and self.name in self.name_alternatives:
            self.name_alternatives.remove(self.name)
        self.url = helperFunctions.null_check(record.url)
        self.geom_center = helperFunctions.null_check(record.geom_center)
        self.geom_area = helperFunctions.null_check(record.geom_area)
        self.geoconvertOrNoneCenter  = helperFunctions.geoconvertOrNone(self.geom_center)
        self.geoconvertOrNoneGeom  = helperFunctions.geoconvertOrNone(self.geom_area)
        
