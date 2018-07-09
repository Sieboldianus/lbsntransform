# -*- coding: utf-8 -*-

import psycopg2
from classes.helperFunctions import helperFunctions
from classes.helperFunctions import lbsnRecordDicts as lbsnRecordDicts
from lbsnstructure.Structure_pb2 import *
from lbsnstructure.external.timestamp_pb2 import Timestamp
import logging 
from sys import exit
import traceback
import os
# for debugging only:
from google.protobuf import text_format
import re


class lbsnDB():
    def __init__(self, dbCursor = None, 
                 dbConnection = None,
                 commit_volume = 10000,
                 disableReactionPostReferencing = 0, storeCSV = None):
        self.dbCursor = dbCursor
        self.dbConnection = dbConnection
        if not self.dbCursor:
            sys.exit("No DB Cursor available.")
        self.commit_volume = commit_volume
        self.count_entries_commit = 0
        self.count_affected = 0
        self.count_glob = 0
        self.null_island_count = 0
        self.country_already_inserted = set()
        self.city_already_inserted = set()
        self.disableReactionPostReferencing = disableReactionPostReferencing
        self.log = logging.getLogger('__main__')
        self.batchedCountries = []
        self.batchedCities = []
        self.batchedPlaces = []
        self.batchedUsers = []
        self.batchedUserGroups = []
        self.batchedPosts = []
        self.batchedPostReactions = []
        self.batchedRelationships = []       
        self.batchVolume = 100 # Records are batched and submitted in one insert with x number of records
        self.storeCSV = storeCSV
        self.typeNamesHeaderDict = {'city': 'origin_id, city_guid, name, name_alternatives, geom_center, geom_area, url, country_guid, sub_type',
                                    'country': 'origin_id, country_guid, name, name_alternatives, geom_center, geom_area, url',
                                    'place': 'origin_id, place_guid, name, name_alternatives, geom_center, geom_area, url, city_guid, post_count',
                                    'post': 'origin_id, post_guid, post_latlng, place_guid, city_guid, country_guid, post_geoaccuracy, user_guid, post_create_date, post_publish_date, post_body, post_language, user_mentions, hashtags, emoji, post_like_count, post_comment_count, post_views_count, post_title, post_thumbnail_url, post_url, post_type, post_filter, post_quote_count, post_share_count, input_source',
                                    'post_reaction': 'origin_id, reaction_guid, reaction_latlng, user_guid, referencedPost_guid, referencedPostreaction_guid, reaction_type, reaction_date, reaction_content, reaction_like_count, user_mentions',
                                    'user': 'origin_id, user_guid, user_name, user_fullname, follows, followed, group_count, biography, post_count, is_private, url, is_available, user_language, user_location, user_location_geom, liked_count, active_since, profile_image_url, user_timezone, user_utc_offset, user_groups_member, user_groups_follows',
                                    '_user_mentions_user': 'origin_id, user_guid, mentioneduser_guid',
                                    '_user_follows_group': 'origin_id, user_guid, group_guid',
                                    '_user_memberof_group': 'origin_id, user_guid, group_guid',
                                    '_user_connectsto_user': 'origin_id, user_guid, connectedto_user_guid',
                                    '_user_friends_user': 'origin_id, user_guid, friend_guid'
                               }
        if self.storeCSV:
            self.OutputPathFile = f'{os.getcwd()}\\Output\\'
            if not os.path.exists(self.OutputPathFile):
                os.makedirs(self.OutputPathFile)
            self.writeCSVHeaders()
    
    def commitChanges(self):
        self.dbConnection.commit() # commit changes to db
        self.count_entries_commit = 0
        
    def submitLbsnRecordDicts(self, fieldMappingTwitter):
        # order is important here, as PostGres will reject any records where Foreign Keys are violated
        # therefore, records are processed starting from lowest granularity, which is stored in allDicts()
        recordDicts = fieldMappingTwitter.lbsnRecords
        x = 0
        self.count_affected = 0
        for recordsDict in recordDicts.allDicts:
            type_name = recordsDict[1]
            for record_pkey, record in recordsDict[0].items():
                x += 1
                print(f'Transferring {x} of {recordDicts.CountGlob} records to output db ({type_name})..', end='\r')
                self.prepareLbsnRecord(record,type_name)
                self.count_glob +=  1 #self.dbCursor.rowcount
                self.count_entries_commit +=  1 #self.dbCursor.rowcount
                if self.count_glob == 100 or self.count_entries_commit > self.commit_volume:
                    self.commitChanges()
        # submit remaining rest
        self.submitAllBatches()
        print(f'\nUpdated/Inserted {self.count_affected} records.')
                
    def prepareLbsnRecord(self, record, record_type):
        # this can be done better
        #record_type = record.DESCRIPTOR.name
        if record_type == lbsnPost().DESCRIPTOR.name:
            preparedRecord = self.prepareLbsnPost(record)
            if preparedRecord:
                self.batchedPosts.append(preparedRecord)
        elif record_type == lbsnCountry().DESCRIPTOR.name:
            preparedRecord = self.prepareLbsnCountry(record)
            if preparedRecord:
                self.batchedCountries.append(preparedRecord)
        elif record_type == lbsnCity().DESCRIPTOR.name:
            preparedRecord = self.prepareLbsnCity(record)
            if preparedRecord:
                self.batchedCities.append(preparedRecord)
        elif record_type == lbsnPlace().DESCRIPTOR.name:
            preparedRecord = self.prepareLbsnPlace(record)
            if preparedRecord:
                self.batchedPlaces.append(preparedRecord)
        elif record_type == lbsnPostReaction().DESCRIPTOR.name:
            preparedRecord = self.prepareLbsnPostReaction(record)
            if preparedRecord:
                self.batchedPostReactions.append(preparedRecord)
        elif record_type == lbsnUserGroup().DESCRIPTOR.name:
            preparedRecord = self.prepareLbsnUserGroup(record)
            if preparedRecord:
                self.batchedUserGroups.append(preparedRecord)            
        elif record_type == lbsnUser().DESCRIPTOR.name:
            preparedRecord = self.prepareLbsnUser(record)
            if preparedRecord:
                self.batchedUsers.append(preparedRecord)
        elif record_type == lbsnRelationship().DESCRIPTOR.name:
            preparedRecord = self.prepareLbsnRelationship(record)
            if preparedRecord:
                self.batchedRelationships.append(preparedRecord)
                
        if max([len(self.batchedPosts),len(self.batchedCountries),len(self.batchedCities),len(self.batchedPlaces),len(self.batchedPostReactions),len(self.batchedUsers),len(self.batchedUserGroups),len(self.batchedRelationships)]) >= self.batchVolume:
            self.submitAllBatches()
                              
    def submitAllBatches(self):
        # this can be done better
        if self.batchedCountries:# and len(self.batchedCountries) > 0:
            #print(f'Count: {len(self.batchedCountries)}')
            self.submitLbsnCountries()
            self.batchedCountries = []
        if self.batchedCities:# and len(self.batchedCities) > 0:
            self.submitLbsnCities()
            self.batchedCities = []
        if self.batchedPlaces:#  and len(self.batchedPlaces) > 0:
            self.submitLbsnPlaces()
            self.batchedPlaces = []
        if self.batchedUsers:#  and len(self.batchedUsers) > 0:
            self.submitLbsnUsers()
            self.batchedUsers = []
        if self.batchedUserGroups:#  and len(self.batchedUserGroups) > 0:
            self.submitLbsnUserGroups()
            self.batchedUserGroups = []            
        if self.batchedPosts:#  and len(self.batchedPosts) > 0:
            self.submitLbsnPosts()
            self.batchedPosts = []
        if self.batchedPostReactions:#  and len(self.batchedPostReactions) > 0:
            self.submitLbsnPostReactions()
            self.batchedPostReactions = []   
        if self.batchedRelationships:#  and len(self.batchedPostReactions) > 0:
            self.submitLbsnRelationships()
            self.batchedRelationships = []   
            
    def submitLbsnCountries(self):
        if self.storeCSV:
            self.storeAppendCSV(self.batchedCountries, 'country')
        args_str = ','.join(self.batchedCountries)
        insert_sql = f'''
                        INSERT INTO data."country" ({self.typeNamesHeaderDict["country"]})
                        VALUES {args_str}
                        ON CONFLICT (origin_id,country_guid)
                        DO UPDATE SET
                            name = COALESCE(EXCLUDED.name, data."country".name),
                            name_alternatives = COALESCE((SELECT array_remove(altNamesNewArray,data."country".name) from extensions.mergeArrays(EXCLUDED.name_alternatives, data."country".name_alternatives) AS altNamesNewArray), ARRAY[]::text[]),
                            geom_center = COALESCE(EXCLUDED.geom_center, data."country".geom_center),
                            geom_area = COALESCE(EXCLUDED.geom_area, data."country".geom_area),
                            url = COALESCE(EXCLUDED.url, data."country".url);
                        '''
                        # Array merge of alternatives:
                        # Arrays cannot be null, therefore COALESCE([if array not null],[otherwise create empty array])
                        # We don't want the english name to appear in alternatives, therefore: array_remove(altNamesNewArray,"country".name)
                        # Finally, merge New Entries with existing ones (distinct): extensions.mergeArrays([new],[old]) uses custom mergeArrays function (see function definitions)

        self.submitBatch(insert_sql) 
        
    def prepareLbsnCountry(self, record):
        # Get common attributes for place types Place, City and Country
        placeRecord = placeAttrShared(record)
        preparedCSVRecord = None
        if not placeRecord.Guid in self.country_already_inserted:
            ## EWKB Conversion now in-code, not server-side
            #record_sql = '''(%s,%s,%s,%s,''' + placeRecord.geoconvertOrNoneCenter + ''',''' + placeRecord.geoconvertOrNoneGeom + ''',%s)'''
            record_sql = '''(%s,%s,%s,%s,%s,%s,%s)'''
            preparedRecord = self.dbCursor.mogrify(record_sql, (placeRecord.OriginID,placeRecord.Guid,placeRecord.name,placeRecord.name_alternatives,helperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_center),helperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_area),placeRecord.url))
            self.country_already_inserted.add(placeRecord.Guid)
            #mogrify returns a byte object, we decode it so it can be used as a string again
            return preparedRecord.decode()
    
    def submitLbsnCities(self):
        if self.storeCSV:
            self.storeAppendCSV(self.batchedCities, 'city')           
        args_str = ','.join(self.batchedCities)
        insert_sql = f'''
                        INSERT INTO data."city" ({self.typeNamesHeaderDict["city"]})
                        VALUES {args_str}
                        ON CONFLICT (origin_id,city_guid)
                        DO UPDATE SET
                            name = COALESCE(EXCLUDED.name, data."city".name),
                            name_alternatives = COALESCE((SELECT array_remove(altNamesNewArray,data."city".name) from extensions.mergeArrays(EXCLUDED.name_alternatives, data."city".name_alternatives) AS altNamesNewArray), ARRAY[]::text[]),
                            geom_center = COALESCE(EXCLUDED.geom_center, data."city".geom_center),
                            geom_area = COALESCE(EXCLUDED.geom_area, data."city".geom_area),
                            url = COALESCE(EXCLUDED.url, data."city".url),
                            country_guid = COALESCE(EXCLUDED.country_guid, data."city".country_guid),
                            sub_type = COALESCE(EXCLUDED.sub_type, data."city".sub_type);
                        '''
        self.submitBatch(insert_sql)
                  
    def prepareLbsnCity(self, record):
        placeRecord = placeAttrShared(record)
        countryGuid = helperFunctions.null_check(record.country_pkey.id)
        subType = helperFunctions.null_check(record.sub_type)
        if not placeRecord.Guid in self.city_already_inserted:
            record_sql = '''(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            preparedRecord = self.dbCursor.mogrify(record_sql, (placeRecord.OriginID,placeRecord.Guid,placeRecord.name,placeRecord.name_alternatives,helperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_center),helperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_area),placeRecord.url,countryGuid,subType))
            self.country_already_inserted.add(placeRecord.Guid)
            return preparedRecord.decode()
            
    def submitLbsnPlaces(self):
        if self.storeCSV:
            self.storeAppendCSV(self.batchedPlaces, 'place')           
        args_str = ','.join(self.batchedPlaces)
        insert_sql = f'''
                        INSERT INTO data."place" ({self.typeNamesHeaderDict["place"]})
                        VALUES {args_str}
                        ON CONFLICT (origin_id,place_guid)
                        DO UPDATE SET
                            name = COALESCE(EXCLUDED.name, data."place".name),
                            name_alternatives = COALESCE((SELECT array_remove(altNamesNewArray,data."place".name) from extensions.mergeArrays(EXCLUDED.name_alternatives, data."place".name_alternatives) AS altNamesNewArray), ARRAY[]::text[]),
                            geom_center = COALESCE(EXCLUDED.geom_center, data."place".geom_center),
                            geom_area = COALESCE(EXCLUDED.geom_area, data."place".geom_area),
                            url = COALESCE(EXCLUDED.url, data."place".url),
                            city_guid = COALESCE(EXCLUDED.city_guid, data."place".city_guid),
                            post_count = GREATEST(COALESCE(EXCLUDED.post_count, data."place".post_count), COALESCE(data."place".post_count, EXCLUDED.post_count));
                        '''
        self.submitBatch(insert_sql)
                           
    def prepareLbsnPlace(self, record):
        placeRecord = placeAttrShared(record)
        cityGuid = helperFunctions.null_check(record.city_pkey.id)
        postCount = helperFunctions.null_check(record.post_count)
        if not placeRecord.Guid in self.city_already_inserted:
            record_sql = '''(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            preparedRecord = self.dbCursor.mogrify(record_sql, (placeRecord.OriginID,placeRecord.Guid,placeRecord.name,placeRecord.name_alternatives,helperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_center),helperFunctions.returnEWKBFromGeoTEXT(placeRecord.geom_area),placeRecord.url,cityGuid,postCount))         
            return preparedRecord.decode() 
            
    def submitLbsnUsers(self):
        if self.storeCSV:
            self.storeAppendCSV(self.batchedUsers, 'user')          
        args_str = ','.join(self.batchedUsers)
        insert_sql = f'''
                        INSERT INTO data."user" ({self.typeNamesHeaderDict["user"]})
                        VALUES {args_str}
                        ON CONFLICT (origin_id, user_guid)
                        DO UPDATE SET
                            user_name = COALESCE(EXCLUDED.user_name, data."user".user_name),                                   
                            user_fullname = COALESCE(EXCLUDED.user_fullname, data."user".user_fullname),                                      
                            follows = GREATEST(COALESCE(EXCLUDED.follows, data."user".follows), COALESCE(data."user".follows, EXCLUDED.follows)),                                                         
                            followed = GREATEST(COALESCE(EXCLUDED.followed, data."user".followed), COALESCE(data."user".followed, EXCLUDED.followed)),
                            group_count = GREATEST(COALESCE(EXCLUDED.group_count, data."user".group_count), COALESCE(data."user".group_count, EXCLUDED.group_count)),
                            biography = COALESCE(EXCLUDED.biography, data."user".biography),
                            post_count = GREATEST(COALESCE(EXCLUDED.post_count, "user".post_count), COALESCE(data."user".post_count, EXCLUDED.post_count)),
                            is_private = COALESCE(EXCLUDED.is_private, data."user".is_private),
                            url = COALESCE(EXCLUDED.url, data."user".url),
                            is_available = COALESCE(EXCLUDED.is_available, data."user".is_available),
                            user_language = COALESCE(EXCLUDED.user_language, data."user".user_language),
                            user_location = COALESCE(EXCLUDED.user_location, data."user".user_location),
                            user_location_geom = COALESCE(EXCLUDED.user_location_geom, data."user".user_location_geom),
                            liked_count = GREATEST(COALESCE(EXCLUDED.liked_count, data."user".liked_count), COALESCE(data."user".liked_count, EXCLUDED.liked_count)),
                            active_since = COALESCE(EXCLUDED.active_since, data."user".active_since),
                            profile_image_url = COALESCE(EXCLUDED.profile_image_url, data."user".profile_image_url),
                            user_timezone = COALESCE(EXCLUDED.user_timezone, data."user".user_timezone),
                            user_utc_offset = COALESCE(EXCLUDED.user_utc_offset, data."user".user_utc_offset),
                            user_groups_member = COALESCE(extensions.mergeArrays(EXCLUDED.user_groups_member, data."user".user_groups_member), ARRAY[]::text[]),
                            user_groups_follows = COALESCE(extensions.mergeArrays(EXCLUDED.user_groups_follows, data."user".user_groups_follows), ARRAY[]::text[]);
                        '''
        self.submitBatch(insert_sql)
                        
    def prepareLbsnUser(self, record):
        userRecord = userAttrShared(record)
        record_sql = '''(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        preparedRecord = self.dbCursor.mogrify(record_sql, (userRecord.OriginID,          
                                         userRecord.Guid,              
                                         userRecord.user_name,         
                                         userRecord.user_fullname,     
                                         userRecord.follows,           
                                         userRecord.followed,          
                                         userRecord.group_count,       
                                         userRecord.biography,         
                                         userRecord.post_count,        
                                         userRecord.is_private,        
                                         userRecord.url,               
                                         userRecord.is_available,      
                                         userRecord.user_language,     
                                         userRecord.user_location,     
                                         helperFunctions.returnEWKBFromGeoTEXT(userRecord.user_location_geom),
                                         userRecord.liked_count,       
                                         userRecord.active_since,      
                                         userRecord.profile_image_url, 
                                         userRecord.user_timezone,     
                                         userRecord.user_utc_offset,
                                         userRecord.user_groups_member,
                                         userRecord.user_groups_follows))
        return preparedRecord.decode()    

    def submitLbsnUserGroups(self):
        if self.storeCSV:
            self.storeAppendCSV(self.batchedUserGroups, 'user_groups')             
        args_str = ','.join(self.batchedUserGroups)
        insert_sql = f'''
                        INSERT INTO data."user_groups" ({self.typeNamesHeaderDict["user_groups"]})
                        VALUES {args_str}
                        ON CONFLICT (origin_id, usergroup_guid)
                        DO UPDATE SET
                            usergroup_name = COALESCE(EXCLUDED.usergroup_name, data."user_groups".usergroup_name),                                   
                            usergroup_description = COALESCE(EXCLUDED.usergroup_description, data."user_groups".usergroup_description),                                      
                            member_count = GREATEST(COALESCE(EXCLUDED.member_count, data."user_groups".member_count), COALESCE(data."user_groups".member_count, EXCLUDED.member_count)),                                                         
                            usergroup_createdate = COALESCE(EXCLUDED.usergroup_createdate, data."user_groups".usergroup_createdate),
                            user_owner = COALESCE(EXCLUDED.user_owner, data."user_groups".user_owner);
                        '''
                        # No coalesce for user: in case user changes or removes information, this should also be removed from the record
        self.submitBatch(insert_sql)
                        
    def prepareLbsnUserGroup(self, record):
        userGroupRecord = userGroupAttrShared(record)
        record_sql = '''(%s,%s,%s,%s,%s,%s,%s)'''
        preparedRecord = self.dbCursor.mogrify(record_sql, (userGroupRecord.OriginID,          
                                         userGroupRecord.Guid,              
                                         userGroupRecord.usergroup_name,         
                                         userGroupRecord.usergroup_description,     
                                         userGroupRecord.member_count,           
                                         userGroupRecord.usergroup_createdate,
                                         userGroupRecord.user_owner))
        return preparedRecord.decode() 
            
    def submitLbsnPosts(self):
        if self.storeCSV:
            self.storeAppendCSV(self.batchedPosts, 'post')          
        args_str = ','.join(self.batchedPosts)
        insert_sql = f'''
                        INSERT INTO data."post" ({self.typeNamesHeaderDict["post"]})
                        VALUES {args_str}
                        ON CONFLICT (origin_id, post_guid)
                        DO UPDATE SET                                                                                           
                            post_latlng = COALESCE(EXCLUDED.post_latlng, data."post".post_latlng),                                   
                            place_guid = COALESCE(EXCLUDED.place_guid, data."post".place_guid),                                      
                            city_guid = COALESCE(EXCLUDED.city_guid, data."post".city_guid),                                         
                            country_guid = COALESCE(EXCLUDED.country_guid, data."post".country_guid),                                
                            post_geoaccuracy = COALESCE(EXCLUDED.post_geoaccuracy, data."post".post_geoaccuracy),                    
                            user_guid = COALESCE(EXCLUDED.user_guid, data."post".user_guid),                                         
                            post_create_date = COALESCE(EXCLUDED.post_create_date, data."post".post_create_date),                    
                            post_publish_date = COALESCE(EXCLUDED.post_publish_date, data."post".post_publish_date),                 
                            post_body = COALESCE(EXCLUDED.post_body, data."post".post_body),                                         
                            post_language = COALESCE(EXCLUDED.post_language, data."post".post_language),                             
                            user_mentions = COALESCE(EXCLUDED.user_mentions, data."post".user_mentions),                             
                            hashtags = COALESCE(extensions.mergeArrays(EXCLUDED.hashtags, data."post".hashtags), ARRAY[]::text[]),                                            
                            emoji = COALESCE(extensions.mergeArrays(EXCLUDED.emoji, data."post".emoji), ARRAY[]::text[]),                                                     
                            post_like_count = COALESCE(EXCLUDED.post_like_count, data."post".post_like_count),                       
                            post_comment_count = COALESCE(EXCLUDED.post_comment_count, data."post".post_comment_count),                    
                            post_views_count = COALESCE(EXCLUDED.post_views_count, data."post".post_views_count),                    
                            post_title = COALESCE(EXCLUDED.post_title, data."post".post_title),                                      
                            post_thumbnail_url = COALESCE(EXCLUDED.post_thumbnail_url, data."post".post_thumbnail_url),              
                            post_url = COALESCE(EXCLUDED.post_url, data."post".post_url),                                            
                            post_type = COALESCE(EXCLUDED.post_type, data."post".post_type),                                         
                            post_filter = COALESCE(EXCLUDED.post_filter, data."post".post_filter),                                   
                            post_quote_count = COALESCE(EXCLUDED.post_quote_count, data."post".post_quote_count),                    
                            post_share_count = COALESCE(EXCLUDED.post_share_count, data."post".post_share_count),                    
                            input_source = COALESCE(EXCLUDED.input_source, data."post".input_source);
                        '''
        self.submitBatch(insert_sql)
                        
    def prepareLbsnPost(self, record):
        postRecord = postAttrShared(record)
        record_sql = '''(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        preparedRecord = self.dbCursor.mogrify(record_sql, (postRecord.OriginID,                                                              
                                         postRecord.Guid,
                                         helperFunctions.returnEWKBFromGeoTEXT(postRecord.post_latlng),
                                         postRecord.place_guid,
                                         postRecord.city_guid,
                                         postRecord.country_guid,
                                         postRecord.post_geoaccuracy,
                                         postRecord.user_guid,
                                         postRecord.post_create_date,
                                         postRecord.post_publish_date,                                          
                                         postRecord.post_body,
                                         postRecord.post_language,
                                         postRecord.user_mentions,
                                         postRecord.hashtags,
                                         postRecord.emoji,
                                         postRecord.post_like_count,
                                         postRecord.post_comment_count,
                                         postRecord.post_views_count,
                                         postRecord.post_title,
                                         postRecord.post_thumbnail_url,
                                         postRecord.post_url,
                                         postRecord.post_type,
                                         postRecord.post_filter,
                                         postRecord.post_quote_count,
                                         postRecord.post_share_count,
                                         postRecord.input_source))         
        return preparedRecord.decode()                                                                                              
        
    def submitLbsnPostReactions(self):
        if self.storeCSV:
            self.storeAppendCSV(self.batchedPostReactions, 'post_reaction')         
        args_str = ','.join(self.batchedPostReactions)
        insert_sql = f'''
                        INSERT INTO data."post_reaction" ({self.typeNamesHeaderDict["post_reaction"]})
                        VALUES {args_str}
                        ON CONFLICT (origin_id, reaction_guid)
                        DO UPDATE SET                                                                                           
                            reaction_latlng = COALESCE(EXCLUDED.reaction_latlng, data."post_reaction".reaction_latlng),                                   
                            user_guid = COALESCE(EXCLUDED.user_guid, data."post_reaction".user_guid),                                      
                            referencedPost_guid = COALESCE(EXCLUDED.referencedPost_guid, data."post_reaction".referencedPost_guid),                                         
                            referencedPostreaction_guid = COALESCE(EXCLUDED.referencedPostreaction_guid, data."post_reaction".referencedPostreaction_guid),                                
                            reaction_type = COALESCE(EXCLUDED.reaction_type, data."post_reaction".reaction_type),                    
                            reaction_date = COALESCE(EXCLUDED.reaction_date, data."post_reaction".reaction_date),                                         
                            reaction_content = COALESCE(EXCLUDED.reaction_content, data."post_reaction".reaction_content),                    
                            reaction_like_count = COALESCE(EXCLUDED.reaction_like_count, data."post_reaction".reaction_like_count),
                            user_mentions = COALESCE(extensions.mergeArrays(EXCLUDED.user_mentions, data."post_reaction".user_mentions), ARRAY[]::text[]);
                        '''
        self.submitBatch(insert_sql)
                                           
    def prepareLbsnPostReaction(self, record):
        postReactionRecord = postReactionAttrShared(record)
        record_sql = '''(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''   
        preparedRecord = self.dbCursor.mogrify(record_sql, (postReactionRecord.OriginID,                                                              
                                         postReactionRecord.Guid,
                                         helperFunctions.returnEWKBFromGeoTEXT(postReactionRecord.reaction_latlng),
                                         postReactionRecord.user_guid,
                                         postReactionRecord.referencedPost,
                                         postReactionRecord.referencedPostreaction,
                                         postReactionRecord.reaction_type,
                                         postReactionRecord.reaction_date,
                                         postReactionRecord.reaction_content,
                                         postReactionRecord.reaction_like_count,
                                         postReactionRecord.user_mentions)) 
        return preparedRecord.decode()

    def submitLbsnRelationships(self):
        # submit relationships of different types record[1] is the PostgresQL formatted list of values, record[0] is the type of relationship that determines the table selection
        selectFriends = [relationship[1] for relationship in self.batchedRelationships if relationship[0] == "isfriend"]
        if selectFriends:
            if self.storeCSV:
                self.storeAppendCSV(selectFriends, '_user_friends_user')   
            args_isFriend = ','.join(selectFriends)
            insert_sql = f'''
                            INSERT INTO relations."_user_friends_user" ({self.typeNamesHeaderDict["_user_friends_user"]})
                            VALUES {args_isFriend}
                            ON CONFLICT (origin_id, user_guid, friend_guid)
                            DO NOTHING
                        '''
            self.submitBatch(insert_sql)
        selectConnected = [relationship[1] for relationship in self.batchedRelationships if relationship[0] == "isconnected"]
        if selectConnected:
            if self.storeCSV:
                self.storeAppendCSV(selectConnected, '_user_connectsto_user')  
            args_isConnected = ','.join(selectConnected)
            insert_sql = f'''
                            INSERT INTO relations."_user_connectsto_user" ({self.typeNamesHeaderDict["_user_connectsto_user"]})
                            VALUES {args_isConnected}
                            ON CONFLICT (origin_id, user_guid, connectedto_user_guid)
                            DO NOTHING
                        '''
            self.submitBatch(insert_sql)
        selectUserGroupMember = [relationship[1] for relationship in self.batchedRelationships if relationship[0] == "ingroup"]
        if selectUserGroupMember:
            if self.storeCSV:
                self.storeAppendCSV(selectUserGroupMember, '_user_memberof_group')  
            args_isInGroup = ','.join(selectUserGroupMember)
            insert_sql = f'''
                            INSERT INTO relations."_user_memberof_group" ({self.typeNamesHeaderDict["_user_memberof_group"]})
                            VALUES {args_isInGroup}
                            ON CONFLICT (origin_id, user_guid, group_guid)
                            DO NOTHING
                        '''
            self.submitBatch(insert_sql)
        selectUserGroupMember = [relationship[1] for relationship in self.batchedRelationships if relationship[0] == "followsgroup"]
        if selectUserGroupMember:
            if self.storeCSV:
                self.storeAppendCSV(selectUserGroupMember, '_user_follows_group')  
            args_isInGroup = ','.join(selectUserGroupMember)
            insert_sql = f'''
                            INSERT INTO relations."_user_follows_group" ({self.typeNamesHeaderDict["_user_follows_group"]})
                            VALUES {args_isInGroup}
                            ON CONFLICT (origin_id, user_guid, group_guid)
                            DO NOTHING
                        '''
            self.submitBatch(insert_sql)            
        selectUserMentions = [relationship[1] for relationship in self.batchedRelationships if relationship[0] == "mentions_user"]
        if selectUserMentions:
            if self.storeCSV:
                self.storeAppendCSV(selectUserMentions, '_user_mentions_user') 
            args_isInGroup = ','.join(selectUserMentions)
            insert_sql = f'''
                            INSERT INTO relations."_user_mentions_user" ({self.typeNamesHeaderDict["_user_mentions_user"]})
                            VALUES {args_isInGroup}
                            ON CONFLICT (origin_id, user_guid, mentioneduser_guid)
                            DO NOTHING
                        '''
            self.submitBatch(insert_sql)
                                                   
    def prepareLbsnRelationship(self, record):
        relationshipRecord = relationshipAttrShared(record)
        record_sql = '''(%s,%s,%s)'''
        preparedTypeRecordTuple = (relationshipRecord.relType,
                          self.dbCursor.mogrify(record_sql, (relationshipRecord.OriginID,          
                          relationshipRecord.Guid,                      
                          relationshipRecord.Guid_Rel)).decode())
        return preparedTypeRecordTuple 
     
    def submitBatch(self,insert_sql):
        ## Needs testing: is using Savepoint for each insert slower than rolling back entire commit?
        ## for performance, see https://stackoverflow.com/questions/12206600/how-to-speed-up-insertion-performance-in-postgresql
        ## or this: https://stackoverflow.com/questions/8134602/psycopg2-insert-multiple-rows-with-one-query
        self.dbCursor.execute("SAVEPOINT submit_recordBatch")
        tsuccessful = False
        while not tsuccessful:
            try:
                self.dbCursor.execute(insert_sql)
            except psycopg2.IntegrityError as e:
                if '(post_language)' in e.diag.message_detail or '(user_language)' in e.diag.message_detail:
                    # If language does not exist, we'll trust Twitter and add this to our language list
                    missingLanguage = e.diag.message_detail.partition("language)=(")[2].partition(") is not present")[0]
                    print(f'TransactionIntegrityError, inserting language "{missingLanguage}" first..               ')
                    self.dbCursor.execute("ROLLBACK TO SAVEPOINT submit_recordBatch")
                    insert_language_sql = '''
                           INSERT INTO data."language" (language_short,language_name,language_name_de)
                           VALUES (%s,NULL,NULL);                                
                           '''
                    self.dbCursor.execute(insert_language_sql,(missingLanguage,))
                else:
                    sys.exit(f'{e}')
            except ValueError as e:
                self.log.warning(f'{e}')
                input("Press Enter to continue... (entry will be skipped)")
                self.log.warning(f'{insert_sql}')
                input("args:... ")
                self.log.warning(f'{args_str}')
                self.dbCursor.execute("ROLLBACK TO SAVEPOINT submit_recordBatch")
                tsuccessful = True
            else:
                self.count_affected += self.dbCursor.rowcount # monitoring
                self.dbCursor.execute("RELEASE SAVEPOINT submit_recordBatch")
                tsuccessful = True
    
    def storeAppendCSV(self, values, typeName):
        csvOutput = open(f'{self.OutputPathFile}{typeName}.csv', 'a', encoding='utf8')
        for record in values:
            # this is ugly, see https://stackoverflow.com/questions/39025420/postgres-wont-allow-array-syntax-in-copy for a better way of doing this
            pg_formatted_record = re.sub(r',ARRAY\[(.*?)\],',self.csvModArrayQuote, record, flags=re.DOTALL)
            pg_formatted_record = pg_formatted_record.strip('()')
            #pg_formatted_record = pg_formatted_record.replace('NULL',"'NULL'")
            csvOutput.write("%s\n" % pg_formatted_record)
            
    def csvModArrayQuote(self, match):
        match = match.group(1)
        match = match.replace("'",'"')
        match = ",'{%s}'," % match
        return match
    
    def writeCSVHeaders(self):
        for typename, header in self.typeNamesHeaderDict.items():
            csvOutput = open(f'{self.OutputPathFile}{typename}.csv', 'w', encoding='utf8')
            csvOutput.write("%s\n" % header)
            
class placeAttrShared():   
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id # = 3
        self.Guid = record.pkey.id
        self.name = helperFunctions.null_check(record.name)
        # because ProtoBuf Repeated Field does not support distinct rule, we remove any duplicates in list fields prior to submission here
        self.name_alternatives = list(set(record.name_alternatives))
        if self.name and self.name in self.name_alternatives:
            self.name_alternatives.remove(self.name)
        self.url = helperFunctions.null_check(record.url)
        self.geom_center = helperFunctions.null_check(record.geom_center)
        self.geom_area = helperFunctions.null_check(record.geom_area)

class userAttrShared():   
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id
        self.Guid = record.pkey.id
        self.user_name = helperFunctions.null_check(record.user_name)
        self.user_fullname = helperFunctions.null_check(record.user_fullname)
        self.follows = helperFunctions.null_check(record.follows)
        self.followed = helperFunctions.null_check(record.followed)
        self.group_count = helperFunctions.null_check(record.group_count)
        self.biography = helperFunctions.null_check(record.biography)
        self.post_count = helperFunctions.null_check(record.post_count)
        self.url = helperFunctions.null_check(record.url)
        self.is_private = helperFunctions.null_check(record.is_private)
        self.is_available = helperFunctions.null_check(record.is_available)
        self.user_language = helperFunctions.null_check(record.user_language.language_short)
        self.user_location = helperFunctions.null_check(record.user_location)
        self.user_location_geom = helperFunctions.null_check(record.user_location_geom)
        self.liked_count = helperFunctions.null_check(record.liked_count)
        self.active_since = helperFunctions.null_check_datetime(record.active_since)
        self.profile_image_url = helperFunctions.null_check(record.profile_image_url)
        self.user_timezone = helperFunctions.null_check(record.user_timezone)
        self.user_utc_offset = helperFunctions.null_check(record.user_utc_offset)    
        self.user_groups_member = list(set(record.user_groups_member))
        self.user_groups_follows = list(set(record.user_groups_follows))
                    
class userGroupAttrShared():   
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id
        self.Guid = record.pkey.id
        self.usergroup_name = helperFunctions.null_check(record.usergroup_name)
        self.usergroup_description = helperFunctions.null_check(record.usergroup_description)
        self.member_count = helperFunctions.null_check(record.member_count)
        self.usergroup_createdate = helperFunctions.null_check_datetime(record.usergroup_createdate)
        self.user_owner = helperFunctions.null_check(record.user_owner_pkey.id)
        
class postAttrShared():
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id
        self.Guid = record.pkey.id
        self.post_latlng = helperFunctions.null_check(record.post_latlng)
        self.place_guid = helperFunctions.null_check(record.place_pkey.id)
        self.city_guid = helperFunctions.null_check(record.city_pkey.id)
        self.country_guid = helperFunctions.null_check(record.country_pkey.id)
        self.post_geoaccuracy = helperFunctions.null_check(lbsnPost().PostGeoaccuracy.Name(record.post_geoaccuracy)).lower()
        self.user_guid = helperFunctions.null_check(record.user_pkey.id)
        self.post_create_date = helperFunctions.null_check_datetime(record.post_create_date)
        self.post_publish_date = helperFunctions.null_check_datetime(record.post_publish_date)
        self.post_body = helperFunctions.null_check(record.post_body)
        self.post_language = helperFunctions.null_check(record.post_language.language_short)
        self.user_mentions = list(set([pkey.id for pkey in record.user_mentions_pkey]))
        self.hashtags = list(set(record.hashtags))
        self.emoji = list(set(record.emoji))
        self.post_like_count = helperFunctions.null_check(record.post_like_count)
        self.post_comment_count = helperFunctions.null_check(record.post_comment_count)
        self.post_views_count = helperFunctions.null_check(record.post_views_count)
        self.post_title = helperFunctions.null_check(record.post_title)
        self.post_thumbnail_url = helperFunctions.null_check(record.post_thumbnail_url)
        self.post_url = helperFunctions.null_check(record.post_url)
        self.post_type = helperFunctions.null_check(lbsnPost().PostType.Name(record.post_type)).lower()
        self.post_filter = helperFunctions.null_check(record.post_filter)
        self.post_quote_count = helperFunctions.null_check(record.post_quote_count)
        self.post_share_count = helperFunctions.null_check(record.post_share_count)
        self.input_source = helperFunctions.null_check(record.input_source)

class postReactionAttrShared():
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id
        self.Guid = record.pkey.id
        self.reaction_latlng = helperFunctions.null_check(record.reaction_latlng)
        self.user_guid = helperFunctions.null_check(record.user_pkey.id)
        self.referencedPost = helperFunctions.null_check(record.referencedPost_pkey.id)
        self.referencedPostreaction = helperFunctions.null_check(record.referencedPostreaction_pkey.id)
        self.reaction_type = helperFunctions.null_check(lbsnPostReaction().ReactionType.Name(record.reaction_type)).lower()
        self.reaction_date = helperFunctions.null_check_datetime(record.reaction_date)
        self.reaction_content = helperFunctions.null_check(record.reaction_content)
        self.reaction_like_count = helperFunctions.null_check(record.reaction_like_count)
        self.user_mentions = list(set([pkey.id for pkey in record.user_mentions_pkey]))

class relationshipAttrShared():   
    def __init__(self, relationship):
        self.OriginID = relationship.pkey.relation_to.origin.origin_id
        self.Guid = relationship.pkey.relation_to.id
        self.Guid_Rel = relationship.pkey.relation_from.id
        self.relType = helperFunctions.null_check(lbsnRelationship().RelationshipType.Name(relationship.relationship_type)).lower()