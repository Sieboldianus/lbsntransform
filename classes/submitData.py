# -*- coding: utf-8 -*-

import psycopg2
from decimal import Decimal
from classes.helperFunctions import helperFunctions
from classes.helperFunctions import lbsnRecordDicts as lbsnRecordDicts
from lbsnstructure.Structure_pb2 import *
from lbsnstructure.external.timestamp_pb2 import Timestamp
import logging 
from sys import exit

def null_check(recordAttr):
    if not recordAttr:
        return None
    else:
        return recordAttr
def geoconvertOrNone(geom):
    if geom:
        return "ST_GeomFromText(%s,4326)"
    else:
        return "%s"     
    
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
        # therefore, records are processed starting from lowest granularity
        # Code refactoring needed:
        for record_pkey, record in recordsDicts.lbsnCountryDict.items():
            self.submitLbsnCountry(record)
            self.count_glob +=  1 #self.dbCursor.rowcount
            self.count_entries_commit +=  1 #self.dbCursor.rowcount
            if self.count_glob == 100 or self.count_entries_commit > self.commit_volume:
                self.commitChanges()
        for record_pkey, record in recordsDicts.lbsnCityDict.items():
            self.submitLbsnCity(record)
            self.count_glob +=  1 #self.dbCursor.rowcount
            self.count_entries_commit +=  1 #self.dbCursor.rowcount
            if self.count_glob == 100 or self.count_entries_commit > self.commit_volume:
                self.commitChanges()
        for record_pkey, record in recordsDicts.lbsnPlaceDict.items():
            self.submitLbsnPlace(record)
            self.count_glob +=  1 #self.dbCursor.rowcount
            self.count_entries_commit +=  1 #self.dbCursor.rowcount
            if self.count_glob == 100 or self.count_entries_commit > self.commit_volume:
                self.commitChanges()
        for record_pkey, record in recordsDicts.lbsnUserDict.items():
            self.submitLbsnUser(record)
            self.count_glob +=  1 #self.dbCursor.rowcount
            self.count_entries_commit +=  1 #self.dbCursor.rowcount
            if self.count_glob == 100 or self.count_entries_commit > self.commit_volume:
                self.commitChanges()
        for record_pkey, record in recordsDicts.lbsnPostDict.items():
            self.submitLbsnPost(record)
            self.count_glob +=  1 #self.dbCursor.rowcount
            self.count_entries_commit +=  1 #self.dbCursor.rowcount
            if self.count_glob == 100 or self.count_entries_commit > self.commit_volume:
                self.commitChanges()
        for record_pkey, record in recordsDicts.lbsnPostReactionDict.items():
            self.submitLbsnPostReaction(record)
            self.count_glob +=  1 #self.dbCursor.rowcount
            self.count_entries_commit +=  1 #self.dbCursor.rowcount
            if self.count_glob == 100 or self.count_entries_commit > self.commit_volume:
                self.commitChanges()
    
    def submitLbsnCountry(self, record):
        #needs modification of ProtoBuffers Spec
        iCountry_OriginID = 3 #record.pkey.origin.origin_id
        iCountry_Guid = record.pkey.id
        iCountry_name = null_check(record.name)
        iCountry_name_alternatives = list(record.name_alternatives)
        if iCountry_name and iCountry_name in iCountry_name_alternatives:
            iCountry_name_alternatives.remove(iCountry_name)
        iCountry_url = null_check(record.url)
        iCountry_geom_center = null_check(record.geom_center)
        iCountry_geom_area = null_check(record.geom_area)
        # PostGis Geometry column must be either Null or explicitly contain formatted geometry 
        geoconvertOrNoneCenter = geoconvertOrNone(iCountry_geom_center)
        geoconvertOrNoneGeom = geoconvertOrNone(iCountry_geom_area)
        if not iCountry_Guid in self.country_already_inserted:
            insert_sql = '''
                        INSERT INTO "country" (origin_id, country_guid, name, name_alternatives, geom_center, geom_area, url)
                        VALUES (%s,%s,%s,%s,''' + geoconvertOrNoneCenter + ''',''' + geoconvertOrNoneGeom + ''',%s)
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
            self.dbCursor.execute(insert_sql,(iCountry_OriginID,iCountry_Guid,iCountry_name,iCountry_name_alternatives,iCountry_geom_center,iCountry_geom_area,iCountry_url))
            self.country_already_inserted.add(iCountry_Guid)
          
    def submitLbsnCity(self, record):
        print("Test")       
    def submitLbsnPlace(self, record):
        print("Test")   
    def submitLbsnUser(self, record):
        print("Test")   
    def submitLbsnPost(self, record):
        print("Test")   
    def submitLbsnPostReaction(self, record):
        print("Test")
   