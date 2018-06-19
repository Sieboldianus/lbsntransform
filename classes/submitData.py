# -*- coding: utf-8 -*-

import psycopg2
from classes.helperFunctions import helperFunctions
from classes.helperFunctions import lbsnRecordDicts as lbsnRecordDicts
from lbsnstructure.Structure_pb2 import *
from lbsnstructure.external.timestamp_pb2 import Timestamp
import logging 
from sys import exit


class lbsnDB():
    def __init__(self, dbCursor = None, 
                 dbConnection = None,
                 commit_volume = 10000,
                 disableReactionPostReferencing = 0):
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
        self.disableReactionPostReferencing = disableReactionPostReferencing
        self.log = logging.getLogger('__main__')
        self.batchedCountries = []
        self.batchedCities = []
        self.batchedPlaces = []
        self.batchedUsers = []
        self.batchedPosts = []
        self.batchedPostReactions = []
        self.batchVolume = 100 # Records are batched and submitted in one insert with x number of records
    
    def commitChanges(self):
        self.dbConnection.commit() # commit changes to db
        self.count_entries_commit = 0
        
    def submitLbsnRecordDicts(self, recordsDicts):
        # order is important here, as PostGres will reject any records where Foreign Keys are violated
        # therefore, records are processed starting from lowest granularity, which is stored in allDicts()
        x = 0
        for recordsDict in recordsDicts.allDicts:
            type_name = recordsDict[1]
            for record_pkey, record in recordsDict[0].items():
                x += 1
                print(f'Transferring {x} of {recordsDicts.CountGlob} records to output db ({type_name})..', end='\r')
                self.prepareLbsnRecord(record,type_name)
                self.count_glob +=  1 #self.dbCursor.rowcount
                self.count_entries_commit +=  1 #self.dbCursor.rowcount
                if self.count_glob == 100 or self.count_entries_commit > self.commit_volume:
                    self.commitChanges()
        # submit remaining rest
        self.submitAllBatches()
                
    def prepareLbsnRecord(self, record, record_type):
        #record_type = record.DESCRIPTOR.name
        if record_type == lbsnPost().DESCRIPTOR.name:
            self.batchedPosts.append(self.prepareLbsnPost(record))
        elif record_type == lbsnCountry().DESCRIPTOR.name:
            self.batchedCountries.append(self.prepareLbsnCountry(record))
        elif record_type == lbsnCity().DESCRIPTOR.name:
            self.batchedCities.append(self.prepareLbsnCity(record))
        elif record_type == lbsnPlace().DESCRIPTOR.name:
            self.batchedPlaces.append(self.prepareLbsnPlace(record))
        elif record_type == lbsnPostReaction().DESCRIPTOR.name:
            self.batchedPostReactions.append(self.prepareLbsnPostReaction(record))
        elif record_type == lbsnUser().DESCRIPTOR.name:
            self.batchedUsers.append(self.prepareLbsnUser(record))
        
        if max([len(self.batchedPosts),len(self.batchedCountries),len(self.batchedCities),len(self.batchedPlaces),len(self.batchedPostReactions),len(self.batchedUsers)]) >= self.batchVolume:
            self.submitAllBatches()
                              
    def submitAllBatches(self):
        if self.batchedCountries:
            self.submitLbsnCountries()
            self.batchedCountries = []
        if self.batchedCities:
            self.submitLbsnCities()
            self.batchedCities = []
        if self.batchedPlaces:
            self.submitLbsnPlaces()
            self.batchedPlaces = []
        if self.batchedUsers:
            self.submitLbsnUsers()
            self.batchedUsers = []
        if self.batchedPosts:
            self.submitLbsnPosts()
            self.batchedPosts = []
        if self.batchedPostReactions:
            self.submitLbsnPostReactions()
            self.batchedPostReactions = []   
            
            
    def submitLbsnCountries(self):
        args_str = ','.join(self.batchedCountries)
        insert_sql = f'''
                        INSERT INTO "country" (origin_id, country_guid, name, name_alternatives, geom_center, geom_area, url)
                        VALUES {args_str}
                        ON CONFLICT (origin_id,country_guid)
                        DO UPDATE SET
                            name = COALESCE(EXCLUDED.name, "country".name),
                            name_alternatives = COALESCE((SELECT array_remove(altNamesNewArray,"country".name) from mergeArrays(EXCLUDED.name_alternatives, "country".name_alternatives) AS altNamesNewArray), ARRAY[]::text[]),
                            geom_center = COALESCE(EXCLUDED.geom_center, "country".geom_center),
                            geom_area = COALESCE(EXCLUDED.geom_area, "country".geom_area),
                            url = COALESCE(EXCLUDED.url, "country".url);
                        '''
                        # Array merge of alternatives:
                        # Arrays cannot be null, therefore COALESCE([if array not null],[otherwise create empty array])
                        # We don't want the english name to appear in alternatives, therefore: array_remove(altNamesNewArray,"country".name)
                        # Finally, merge New Entries with existing ones mergeArrays([new],[old]) uses custom mergeArrays function (see function definitions)
        self.submitBatch(insert_sql)
        
    def prepareLbsnCountry(self, record):
        # Get common attributes for place types Place, City and Country
        placeRecord = placeAttrShared(record)
        if not placeRecord.Guid in self.country_already_inserted:
            record_sql = '''(%s,%s,%s,%s,''' + placeRecord.geoconvertOrNoneCenter + ''',''' + placeRecord.geoconvertOrNoneGeom + ''',%s)'''
            preparedRecord = self.dbCursor.mogrify(record_sql, (placeRecord.OriginID,placeRecord.Guid,placeRecord.name,placeRecord.name_alternatives,placeRecord.geom_center,placeRecord.geom_area,placeRecord.url))
            #self.dbCursor.execute(insert_sql,(placeRecord.OriginID,placeRecord.Guid,placeRecord.name,placeRecord.name_alternatives,placeRecord.geom_center,placeRecord.geom_area,placeRecord.url))
            self.country_already_inserted.add(placeRecord.Guid)
            #mogrify returns a byte object, we decode it so it can be used as a string again
            return preparedRecord.decode()
    
    def submitLbsnCities(self):
        args_str = ','.join(self.batchedCities)
        insert_sql = f'''
                        INSERT INTO "city" (origin_id, city_guid, name, name_alternatives, geom_center, geom_area, url, country_guid, sub_type)
                        VALUES {args_str}
                        ON CONFLICT (origin_id,city_guid)
                        DO UPDATE SET
                            name = COALESCE(EXCLUDED.name, "city".name),
                            name_alternatives = COALESCE((SELECT array_remove(altNamesNewArray,"city".name) from mergeArrays(EXCLUDED.name_alternatives, "city".name_alternatives) AS altNamesNewArray), ARRAY[]::text[]),
                            geom_center = COALESCE(EXCLUDED.geom_center, "city".geom_center),
                            geom_area = COALESCE(EXCLUDED.geom_area, "city".geom_area),
                            url = COALESCE(EXCLUDED.url, "city".url),
                            country_guid = COALESCE(EXCLUDED.country_guid, "city".country_guid),
                            sub_type = COALESCE(EXCLUDED.sub_type, "city".sub_type);
                        '''
        self.submitBatch(insert_sql)
                  
    def prepareLbsnCity(self, record):
        placeRecord = placeAttrShared(record)
        countryGuid = helperFunctions.null_check(record.country_pkey.id)
        subType = helperFunctions.null_check(record.sub_type)
        if not placeRecord.Guid in self.city_already_inserted:
            record_sql = '''(%s,%s,%s,%s,''' + placeRecord.geoconvertOrNoneCenter + ''',''' + placeRecord.geoconvertOrNoneGeom + ''',%s,%s,%s)'''
            preparedRecord = self.dbCursor.mogrify(record_sql, (placeRecord.OriginID,placeRecord.Guid,placeRecord.name,placeRecord.name_alternatives,placeRecord.geom_center,placeRecord.geom_area,placeRecord.url,countryGuid,subType))
            #self.dbCursor.execute(insert_sql,(placeRecord.OriginID,placeRecord.Guid,placeRecord.name,placeRecord.name_alternatives,placeRecord.geom_center,placeRecord.geom_area,placeRecord.url,countryGuid,subType))
            self.country_already_inserted.add(placeRecord.Guid)
            return preparedRecord.decode()
            
    def submitLbsnPlaces(self):
        args_str = ','.join(self.batchedPlaces)
        insert_sql = f'''
                        INSERT INTO "place" (origin_id, place_guid, name, name_alternatives, geom_center, geom_area, url, city_guid, post_count)
                        VALUES {args_str}
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
        self.submitBatch(insert_sql)
                           
    def prepareLbsnPlace(self, record):
        placeRecord = placeAttrShared(record)
        cityGuid = helperFunctions.null_check(record.city_pkey.id)
        postCount = helperFunctions.null_check(record.post_count)
        if not placeRecord.Guid in self.city_already_inserted:
            record_sql = '''(%s,%s,%s,%s,''' + placeRecord.geoconvertOrNoneCenter + ''',''' + placeRecord.geoconvertOrNoneGeom + ''',%s,%s,%s)'''
            preparedRecord = self.dbCursor.mogrify(record_sql, (placeRecord.OriginID,placeRecord.Guid,placeRecord.name,placeRecord.name_alternatives,placeRecord.geom_center,placeRecord.geom_area,placeRecord.url,cityGuid,postCount))         
            #self.dbCursor.execute(insert_sql,(placeRecord.OriginID,placeRecord.Guid,placeRecord.name,placeRecord.name_alternatives,placeRecord.geom_center,placeRecord.geom_area,placeRecord.url,cityGuid,postCount))
            #self.place_already_inserted.add(placeRecord.Guid)
            return preparedRecord.decode() 
            
    def submitLbsnUsers(self):
        args_str = ','.join(self.batchedUsers)
        insert_sql = f'''
                        INSERT INTO "user" (origin_id, user_guid, user_name, user_fullname, follows, followed, group_count, biography, post_count, is_private, url, is_available, user_language, user_location, user_location_geom, liked_count, active_since, profile_image_url, user_timezone, user_utc_offset)
                        VALUES {args_str}
                        ON CONFLICT (origin_id, user_guid)
                        DO UPDATE SET
                        (user_name, user_fullname, follows, followed, group_count, biography, post_count, is_private, url, is_available, user_language, user_location, user_location_geom, liked_count, active_since, profile_image_url, user_timezone, user_utc_offset)
                        = (EXCLUDED.user_name, EXCLUDED.user_fullname, EXCLUDED.follows, EXCLUDED.followed, EXCLUDED.group_count, EXCLUDED.biography, EXCLUDED.post_count, EXCLUDED.is_private, EXCLUDED.url, EXCLUDED.is_available, EXCLUDED.user_language, EXCLUDED.user_location, EXCLUDED.user_location_geom, EXCLUDED.liked_count, EXCLUDED.active_since, EXCLUDED.profile_image_url, EXCLUDED.user_timezone, EXCLUDED.user_utc_offset);
                        '''
                        # No coalesce for user: in case user changes or removes information, this should also be removed from the record
        self.submitBatch(insert_sql)
                        
    def prepareLbsnUser(self, record):
        userRecord = userAttrShared(record)
        record_sql = '''(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,''' + userRecord.geoconvertOrNoneCenter + ''',%s,%s,%s,%s,%s)'''
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
                                         userRecord.user_location_geom,
                                         userRecord.liked_count,       
                                         userRecord.active_since,      
                                         userRecord.profile_image_url, 
                                         userRecord.user_timezone,     
                                         userRecord.user_utc_offset))
        return preparedRecord.decode()    
        
    def submitLbsnPosts(self):
        args_str = ','.join(self.batchedPosts)
        insert_sql = f'''
                        INSERT INTO "post" (origin_id, post_guid, post_latlng, place_guid, city_guid, country_guid, post_geoaccuracy, user_guid, post_create_date, post_publish_date, post_body, post_language, user_mentions, hashtags, emoji, post_like_count, post_comment_count, post_views_count, post_title, post_thumbnail_url, post_url, post_type, post_filter, post_quote_count, post_share_count, input_source)
                        VALUES {args_str}
                        ON CONFLICT (origin_id, post_guid)
                        DO UPDATE SET                                                                                           
                            post_latlng = COALESCE(EXCLUDED.post_latlng, "post".post_latlng),                                   
                            place_guid = COALESCE(EXCLUDED.place_guid, "post".place_guid),                                      
                            city_guid = COALESCE(EXCLUDED.city_guid, "post".city_guid),                                         
                            country_guid = COALESCE(EXCLUDED.country_guid, "post".country_guid),                                
                            post_geoaccuracy = COALESCE(EXCLUDED.post_geoaccuracy, "post".post_geoaccuracy),                    
                            user_guid = COALESCE(EXCLUDED.user_guid, "post".user_guid),                                         
                            post_create_date = COALESCE(EXCLUDED.post_create_date, "post".post_create_date),                    
                            post_publish_date = COALESCE(EXCLUDED.post_publish_date, "post".post_publish_date),                 
                            post_body = COALESCE(EXCLUDED.post_body, "post".post_body),                                         
                            post_language = COALESCE(EXCLUDED.post_language, "post".post_language),                             
                            user_mentions = COALESCE(EXCLUDED.user_mentions, "post".user_mentions),                             
                            hashtags = COALESCE(EXCLUDED.hashtags, "post".hashtags),                                            
                            emoji = COALESCE(EXCLUDED.emoji, "post".emoji),                                                     
                            post_like_count = COALESCE(EXCLUDED.post_like_count, "post".post_like_count),                       
                            post_comment_count = COALESCE(EXCLUDED.post_comment_count, "post".post_comment_count),                    
                            post_views_count = COALESCE(EXCLUDED.post_views_count, "post".post_views_count),                    
                            post_title = COALESCE(EXCLUDED.post_title, "post".post_title),                                      
                            post_thumbnail_url = COALESCE(EXCLUDED.post_thumbnail_url, "post".post_thumbnail_url),              
                            post_url = COALESCE(EXCLUDED.post_url, "post".post_url),                                            
                            post_type = COALESCE(EXCLUDED.post_type, "post".post_type),                                         
                            post_filter = COALESCE(EXCLUDED.post_filter, "post".post_filter),                                   
                            post_quote_count = COALESCE(EXCLUDED.post_quote_count, "post".post_quote_count),                    
                            post_share_count = COALESCE(EXCLUDED.post_share_count, "post".post_share_count),                    
                            input_source = COALESCE(EXCLUDED.input_source, "post".input_source);
                        '''
        self.submitBatch(insert_sql)
                        
    def prepareLbsnPost(self, record):
        postRecord = postAttrShared(record)
        record_sql = '''(%s,%s,''' + postRecord.geoconvertOrNoneCenter + ''',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        preparedRecord = self.dbCursor.mogrify(record_sql, (postRecord.OriginID,                                                              
                                         postRecord.Guid,
                                         postRecord.post_latlng,
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
        args_str = ','.join(self.batchedPostReactions)
        insert_sql = f'''
                        INSERT INTO "post_reaction" (origin_id, reaction_guid, reaction_latlng, user_guid, referencedPost_guid, referencedPostreaction_guid, reaction_type, reaction_date, reaction_content, reaction_like_count, user_mentions)
                        VALUES {args_str}
                        ON CONFLICT (origin_id, reaction_guid)
                        DO UPDATE SET                                                                                           
                            reaction_latlng = COALESCE(EXCLUDED.reaction_latlng, "post_reaction".reaction_latlng),                                   
                            user_guid = COALESCE(EXCLUDED.user_guid, "post_reaction".user_guid),                                      
                            referencedPost_guid = COALESCE(EXCLUDED.referencedPost_guid, "post_reaction".referencedPost_guid),                                         
                            referencedPostreaction_guid = COALESCE(EXCLUDED.referencedPostreaction_guid, "post_reaction".referencedPostreaction_guid),                                
                            reaction_type = COALESCE(EXCLUDED.reaction_type, "post_reaction".reaction_type),                    
                            reaction_date = COALESCE(EXCLUDED.reaction_date, "post_reaction".reaction_date),                                         
                            reaction_content = COALESCE(EXCLUDED.reaction_content, "post_reaction".reaction_content),                    
                            reaction_like_count = COALESCE(EXCLUDED.reaction_like_count, "post_reaction".reaction_like_count),
                            user_mentions = COALESCE(EXCLUDED.user_mentions, "post_reaction".user_mentions);
                        '''
        self.submitBatch(insert_sql)
                                           
    def prepareLbsnPostReaction(self, record):
        postReactionRecord = postReactionAttrShared(record)
        record_sql = '''(%s,%s,''' + postReactionRecord.geoconvertOrNoneCenter + ''',%s,%s,%s,%s,%s,%s,%s,%s)'''   
        preparedRecord = self.dbCursor.mogrify(record_sql, (postReactionRecord.OriginID,                                                              
                                         postReactionRecord.Guid,
                                         postReactionRecord.reaction_latlng,
                                         postReactionRecord.user_guid,
                                         postReactionRecord.referencedPost,
                                         postReactionRecord.referencedPostreaction,
                                         postReactionRecord.reaction_type,
                                         postReactionRecord.reaction_date,
                                         postReactionRecord.reaction_content,
                                         postReactionRecord.reaction_like_count,
                                         postReactionRecord.user_mentions)) 
        return preparedRecord.decode()
 
    def submitBatch(self,insert_sql):
        ## Needs testing: is using Savepoint for each insert slower than rolling back entire commit?
        ## for performance, see https://stackoverflow.com/questions/12206600/how-to-speed-up-insertion-performance-in-postgresql
        ## or this: https://stackoverflow.com/questions/8134602/psycopg2-insert-multiple-rows-with-one-query
        self.dbCursor.execute("SAVEPOINT submit_recordBatch")
        tsuccessful = False
        #issuesCount = 0
        while not tsuccessful:
            try:
                self.dbCursor.execute(insert_sql)
            except psycopg2.IntegrityError as e:
                            if '(post_language)' in e.diag.message_detail:
                                # If language does not exist, we'll trust Twitter and add this to our language list
                                missingLanguage = e.diag.message_detail.partition("(post_language)=(")[2].partition(") is not present")[0]
                                print(f'TransactionIntegrityError, inserting language "{missingLanguage}" first..')
                                #self.dbConnection.rollback()
                                self.dbCursor.execute("ROLLBACK TO SAVEPOINT submit_recordBatch")
                                insert_language_sql = '''
                                       INSERT INTO "language" (language_short,language_name,language_name_de)
                                       VALUES (%s,NULL,NULL);                                
                                       '''
                                self.dbCursor.execute(insert_language_sql,(missingLanguage,))
                                #self.prepareLbsnRecord(record,type_name)
            except ValueError as e:
                self.log.warning(f'{e}')
                input("Press Enter to continue... (entry will be skipped)")
                self.log.warning(f'{insert_sql}')
                input("args:... ")
                self.log.warning(f'{args_str}')
                self.dbCursor.execute("ROLLBACK TO SAVEPOINT submit_recordBatch")
                #continue
            else:
                self.dbCursor.execute("RELEASE SAVEPOINT submit_recordBatch")
                tsuccessful = True
                   
class placeAttrShared():   
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id # = 3
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
        self.geoconvertOrNoneCenter = helperFunctions.geoconvertOrNone(self.user_location_geom)
        self.liked_count = helperFunctions.null_check(record.liked_count)
        self.active_since = helperFunctions.null_check_datetime(record.active_since)
        self.profile_image_url = helperFunctions.null_check(record.profile_image_url)
        self.user_timezone = helperFunctions.null_check(record.user_timezone)
        self.user_utc_offset = helperFunctions.null_check(record.user_utc_offset)        

class postAttrShared():
    def __init__(self, record):
        self.OriginID = record.pkey.origin.origin_id
        self.Guid = record.pkey.id
        self.post_latlng = helperFunctions.null_check(record.post_latlng)
        self.geoconvertOrNoneCenter = helperFunctions.geoconvertOrNone(self.post_latlng)
        self.place_guid = helperFunctions.null_check(record.place_pkey.id)
        self.city_guid = helperFunctions.null_check(record.city_pkey.id)
        self.country_guid = helperFunctions.null_check(record.country_pkey.id)
        self.post_geoaccuracy = helperFunctions.null_check(lbsnPost().PostGeoaccuracy.Name(record.post_geoaccuracy)).lower()
        self.user_guid = helperFunctions.null_check(record.user_pkey.id)
        self.post_create_date = helperFunctions.null_check_datetime(record.post_create_date)
        self.post_publish_date = helperFunctions.null_check_datetime(record.post_publish_date)
        self.post_body = helperFunctions.null_check(record.post_body)
        self.post_language = helperFunctions.null_check(record.post_language.language_short)
        self.user_mentions = [pkey.id for pkey in record.user_mentions_pkey]
        self.hashtags = list(record.hashtags)
        self.emoji = list(record.emoji)
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
        self.geoconvertOrNoneCenter = helperFunctions.geoconvertOrNone(self.reaction_latlng)
        self.user_guid = helperFunctions.null_check(record.user_pkey.id)
        self.referencedPost = helperFunctions.null_check(record.referencedPost_pkey.id)
        self.referencedPostreaction = helperFunctions.null_check(record.referencedPostreaction_pkey.id)
        self.reaction_type = helperFunctions.null_check(lbsnPostReaction().ReactionType.Name(record.reaction_type)).lower()
        self.reaction_date = helperFunctions.null_check_datetime(record.reaction_date)
        self.reaction_content = helperFunctions.null_check(record.reaction_content)
        self.reaction_like_count = helperFunctions.null_check(record.reaction_like_count)
        self.user_mentions = [pkey.id for pkey in record.user_mentions_pkey]