# -*- coding: utf-8 -*-

class lbsnPost():  
    def __init__(self, 
            recordType="Post",     
            origin_id = 3, #3 = Twitter
            post_guid=None, 
            post_body=None,
            input_source=None,
            post_publish_date=None,
            user_guid=None, 
            post_latlng_WKT=None,
            post_quote_count=None,
            post_comment_count=None,                 
            post_share_count=None, 
            post_like_count=None,
            hashtags=None,
            post_type=None,                
            post_language=None,
            emoji=None):
        self.recordType = recordType
        self.post_guid = post_guid
        self.post_body = post_body
        self.input_source = input_source
        self.post_publish_date = post_publish_date
        self.user_guid = user_guid
        self.post_latlng_WKT = post_latlng_WKT
        self.post_quote_count = post_quote_count
        self.post_comment_count = post_comment_count
        self.post_share_count = post_share_count
        self.post_like_count = post_like_count
        self.hashtags = hashtags
        self.post_type = post_type
        self.post_language = post_language
        self.emoji = emoji
        
    def attr_list(self, should_print=False):
        items = self.__dict__.items()
        if should_print:
            [print(f"attribute: {k}    value: {v}") for k, v in items]

        return items                
class lbsnPlace():  
    def __init__(self, 
            recordType="Place",
            origin_id = 3, #3 = Twitter
            country_name=None,
            country_guid=None,
            city_name=None,
            city_guid=None,
            place_type=None,
            place_url=None,
            geom_center=None,
            geom_area=None):
        self.recordType = recordType
        self.country_name = country_name
        self.country_guid = country_guid
        self.city_guid = city_guid
        self.city_name = city_name
        self.place_type = place_type
        self.place_url = place_url
        self.geom_center = geom_center
        self.geom_area = geom_area
        
    def attr_list(self, should_print=False):
        items = self.__dict__.items()
        if should_print:
            [print(f"attribute: {k}    value: {v}") for k, v in items]
            
class lbsnCity():  
    def __init__(self, 
            recordType="City",
            origin_id = 3, #3 = Twitter
            country_name=None,
            country_guid=None,
            city_name=None,
            city_guid=None,
            place_type=None,
            place_url=None,
            geom_center=None,
            geom_area=None):
        self.recordType = recordType
        self.country_name = country_name
        self.country_guid = country_guid
        self.city_guid = city_guid
        self.city_name = city_name
        self.place_type = place_type
        self.place_url = place_url
        self.geom_center = geom_center
        self.geom_area = geom_area
        
    def attr_list(self, should_print=False):
        items = self.__dict__.items()
        if should_print:
            [print(f"attribute: {k}    value: {v}") for k, v in items]
            
class lbsnCountry():  
    def __init__(self, 
            recordType="Country",
            origin_id = 3, #3 = Twitter
            country_name=None,
            country_guid=None,
            city_name=None,
            city_guid=None,
            place_type=None,
            place_url=None,
            geom_center=None,
            geom_area=None):
        self.recordType = recordType
        self.country_name = country_name
        self.country_guid = country_guid
        self.city_guid = city_guid
        self.city_name = city_name
        self.place_type = place_type
        self.place_url = place_url
        self.geom_center = geom_center
        self.geom_area = geom_area
        
    def attr_list(self, should_print=False):
        items = self.__dict__.items()
        if should_print:
            [print(f"attribute: {k}    value: {v}") for k, v in items]
                                            
class lbsnUser():  
    def __init__(self, 
            recordType="User",
            origin_id = 3, #3 = Twitter
            user_guid=None, 
            user_fullname=None,
            user_name=None,
            user_location=None,
            user_location_geom=None, 
            user_bio_url=None,
            biography=None,
            followed=None,
            follows=None, 
            liked_count=None,
            post_count=None,
            active_since=None,
            user_language=None, 
            profile_image_url=None):
        self.recordType = recordType
        self.user_guid = user_guid
        self.user_fullname = user_fullname
        self.user_name = user_name
        self.user_location = user_location    
        self.user_location_geom = user_location_geom
        self.user_bio_url = user_bio_url
        self.biography = biography
        self.followed = followed
        self.follows = follows
        self.liked_count = liked_count
        self.post_count = post_count
        self.active_since = active_since
        self.user_language = user_language
        self.profile_image_url = profile_image_url
        
    def attr_list(self, should_print=False):
        items = self.__dict__.items()
        if should_print:
            [print(f"attribute: {k}    value: {v}".encode('utf-8')) for k, v in items]        
                    
class lbsnPostReaction():  
    def __init__(self, 
            recordType="Reaction",
            reaction_type=None,
            origin_id = 3, #3 = Twitter
            reaction_guid=None, 
            post_guid=None,
            user_guid=None, 
            reaction_latlng_WKT=None,
            reaction_date=None,
            reaction_content=None,
            reaction_like_count=None
            ):
        self.recordType = recordType
        self.reaction_type = reaction_type   
        self.reaction_guid = reaction_guid
        self.post_guid = post_guid
        self.user_guid = user_guid
        self.reaction_latlng_WKT = reaction_latlng_WKT   
        self.reaction_date = reaction_date
        self.reaction_content = reaction_content
        self.reaction_like_count = reaction_like_count
        
    def attr_list(self, should_print=False):
        items = self.__dict__.items()
        if should_print:
            [print(f"attribute: {k}    value: {v}".encode('utf-8')) for k, v in items]        