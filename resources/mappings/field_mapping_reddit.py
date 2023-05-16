# -*- coding: utf-8 -*-

"""
Module for mapping Reddit submissions and comments (json) to common LBSN Structure.

Notes:
- "author_flair_text" for comments not yet processed (not available in lbsn format)
"""


import logging
from typing import Any, Dict, Optional

# pylint: disable=no-member
import lbsnstructure as lbsn

from lbsntransform.tools.helper_functions import HelperFunctions as HF

MAPPING_ID = 81
SKIP_DELETED = False  # Set to true to skip posts of deleted users;
# otherwise, all of these posts will be assigned to a user
# named "None"


class importer:
    """Provides mapping function from Reddit endpoints to
    protobuf lbsnstructure
    """

    ORIGIN_NAME = "Reddit"
    ORIGIN_ID = 8

    def __init__(
        self,
        disable_reaction_post_referencing=False,
        geocodes=False,
        map_reactions=True,
        ignore_non_geotagged=False,
        **_,
    ):
        if ignore_non_geotagged:
            raise Warning(
                "Reddit does not support geotagging. Disabling "
                "transformation of geotagged posts will exclude all data."
            )
        # Create the OriginID globally
        # this OriginID is required for all CompositeKeys
        origin = lbsn.Origin()
        origin.origin_id = lbsn.Origin.REDDIT
        self.origin = origin
        # this is where all the data will be stored
        self.lbsn_records = []
        self.lbsn_relationships = []
        self.null_island = 0
        self.log = logging.getLogger("__main__")
        self.disable_reaction_post_referencing = disable_reaction_post_referencing
        self.geocodes = geocodes
        self.map_reactions = map_reactions
        self.skipped_low_geoaccuracy = 0

    def parse_json_record(self, json_string_dict: Optional[Dict[str, Any]], *_):
        """Parse a standard Reddit json (comment or submission)"""
        return_list = []
        if json_string_dict is None:
            return
        extracted = self.extract_submission(json_string_dict)
        if extracted is None:
            return
        post_record, user_record = extracted
        # self.lbsn_records.append(post_record)
        submission_id = json_string_dict.get("submission_id")
        if submission_id:
            return_objects = self.extract_comment(json_string_dict, post_record)
            return_list.append(user_record)
            return_list.extend(return_objects)
        else:
            return_list.extend([user_record, post_record])
        # return list of submission and (optional) comment + parent comment
        return return_list

    def extract_user(self, user: str) -> lbsn.User:
        """Create lbsn.User from author name"""
        user_record = HF.new_lbsn_record_with_id(lbsn.User(), user, self.origin)
        return user_record

    def extract_submission(
        self,
        json_string_dict: Dict[str, Any],
    ):
        """Extract standard Reddit submission"""
        post_guid = json_string_dict.get("id")
        if not HF.check_notice_empty_post_guid(post_guid):
            return
        post_record = HF.new_lbsn_record_with_id(lbsn.Post(), post_guid, self.origin)
        user_record = None
        username = json_string_dict.get("author")
        if username:
            if username == "None" and SKIP_DELETED:
                return
            # Get Post/Reaction Details of User
            user_record = self.extract_user(username)
        if not user_record:
            self.log.warning(
                "No User record found for post: %s (post saved without userid)..",
                post_guid,
            )
        post_record.post_publish_date.CopyFrom(
            HF.json_date_timestamp_to_proto(json_string_dict.get("created_utc"))
        )
        if user_record:
            post_record.user_pkey.CopyFrom(user_record.pkey)

        def value_count(x):
            return 0 if x is None else x

        post_record.post_comment_count = value_count(
            json_string_dict.get("num_comments")
        )
        post_record.post_like_count = value_count(json_string_dict.get("score"))
        post_permalink = json_string_dict.get("permalink")
        is_url = json_string_dict.get("url")
        if is_url:
            # if shared url is available, we override original URL of post,
            # pointing to the shared URL/Link instead
            post_record.post_url = is_url
        else:
            post_record.post_url = f"http://www.reddit.com{post_permalink}"
        thumb = json_string_dict.get("thumbnail")
        if thumb and thumb not in ("self", "default"):
            post_record.post_thumbnail_url = thumb
        post_caption = json_string_dict.get("selftext")
        if post_caption:
            post_record.post_body = post_caption
            hashtags = HF.extract_hashtags_from_string(post_caption)
            if hashtags:
                for hashtag in hashtags:
                    post_record.hashtags.append(hashtag)
        # if submission.is_self is True, then it's a text-only post.
        # If it's False, then it's a link post.
        is_text = json_string_dict.get("is_self")
        is_media = json_string_dict.get("media")
        if is_text:
            post_record.post_type = lbsn.Post.TEXT
        elif is_media:
            if is_media.get("type") == "imgur.com":
                post_record.post_type = lbsn.Post.IMAGE
            elif is_media.get("type").startswith("youtube"):
                post_record.post_type = lbsn.Post.VIDEO
            else:
                # dig deeper
                media_type = is_media.get("oembed").get("type")
                if media_type == "video":
                    post_record.post_type = lbsn.Post.VIDEO
                elif media_type == "rich":
                    post_record.post_type = lbsn.Post.OTHER
        elif is_url:
            if is_url.endswith((".jpg", ".webp", ".jpeg", ".png", ".gif")):
                post_record.post_type = lbsn.Post.IMAGE
            else:
                # fallback to LINK
                post_record.post_type = lbsn.Post.LINK
        else:
            # e.g. posts where the content was removed
            # and it not possible to tell anymore what it was
            post_record.post_type = lbsn.Post.OTHER
        post_record.emoji.extend(HF.extract_emoji(post_record.post_body))
        title = json_string_dict.get("title")
        if title:
            post_record.post_title = title
        flair = json_string_dict.get("link_flair_text")
        if flair:
            post_record.post_filter = flair
        subreddit = json_string_dict.get("subreddit")
        if subreddit:
            post_record.topic_group.append(subreddit)
        downvotes = json_string_dict.get("downs")
        if downvotes:
            post_record.post_downvotes = downvotes
        mentioned_users_str = HF.extract_user_mentions(post_record.post_body)
        if mentioned_users_str:
            mentioned_users = HF.create_mentioned_users(
                mentioned_users_str, self.origin
            )
            post_record.user_mentions_pkey.extend(
                [user_ref.pkey for user_ref in mentioned_users]
            )
        return post_record, user_record

    def extract_comment(
        self, json_string_dict: Dict[str, Any], comment_stub: lbsn.Post
    ):
        """Reddit comments are threaded/nested. A comment always includes a
        parent_id object. The parent_id can point to a submission (the original post),
        or any comment of a submission. Parent (a reaction or post)
        and submission a post) must be created before processing a comment
        further. The result is returned as a list of lbsn Objects.
        """
        return_list = []
        # submission_id only available for comments
        post_reaction_record = importer.map_postrecord_to_postreactionrecord(
            comment_stub
        )
        parent_id = json_string_dict.get("parent_id")
        if not parent_id:
            raise Warning("No reference/parent reaction/submission found for reaction")
        # strip t1_, t3_ etc.
        parent_reaction_id = parent_id.split("_")[1]
        submission_id = json_string_dict.get("submission_id")
        # create submission (original post) stub
        ref_post_record = HF.new_lbsn_record_with_id(
            lbsn.Post(), submission_id, self.origin
        )
        # we can get the subreddit from the first part of the permalink, e.g.
        # /r/de/comments/12tthec/forderung_nach_importstopp_eu_streitet_\u00fcber/jh489vx/
        permalink = json_string_dict.get("permalink")
        if permalink:
            reddit_pre = "/r/"
            if permalink.startswith(reddit_pre):
                subreddit_l = permalink.lstrip(reddit_pre).split("/")
                if len(subreddit_l) > 0:
                    ref_post_record.topic_group.append(subreddit_l[0])
                    return_list.append(ref_post_record)
        # compare the parent reaction ID with the submission ID
        if not parent_reaction_id == submission_id:
            # not the first comment, but a nested one
            # first create the parent comment
            referenced_post_reaction = HF.new_lbsn_record_with_id(
                lbsn.PostReaction(), parent_reaction_id, self.origin
            )
            # we know that parent reaction is of type comment
            referenced_post_reaction.reaction_type = lbsn.PostReaction.COMMENT
            # all comments reference the same original post
            referenced_post_reaction.referencedPost_pkey.CopyFrom(ref_post_record.pkey)
            return_list.append(referenced_post_reaction)
            # append ID to comment as reference
            post_reaction_record.referencedPostreaction_pkey.CopyFrom(
                referenced_post_reaction.pkey
            )
        # now finalize the comment, referencing the parent comment and submission post
        reaction_body = json_string_dict.get("body")
        if reaction_body:
            post_reaction_record.reaction_content = reaction_body
        post_reaction_record.reaction_type = lbsn.PostReaction.COMMENT
        post_reaction_record.referencedPost_pkey.CopyFrom(ref_post_record.pkey)
        mentioned_users_str = HF.extract_user_mentions(reaction_body)
        if mentioned_users_str:
            mentioned_users = HF.create_mentioned_users(
                mentioned_users_str, self.origin
            )
            post_reaction_record.user_mentions_pkey.extend(
                [user_ref.pkey for user_ref in mentioned_users]
            )
        return_list.append(post_reaction_record)
        # TODO: Map Relationships (see Twitter mapping "map_full_relations")
        # and add "mentions"-relationship, if map_full_relations is active
        return return_list

    @staticmethod
    def map_postrecord_to_postreactionrecord(post_record):
        """Reduces lbsn.Post to lbsn.PostReaction record"""
        post_reaction_record = lbsn.PostReaction()
        post_reaction_record.pkey.CopyFrom(post_record.pkey)
        post_reaction_record.user_pkey.CopyFrom(post_record.user_pkey)
        # better post_create_date, but not available from Twitter
        post_reaction_record.reaction_date.CopyFrom(post_record.post_publish_date)
        post_reaction_record.reaction_like_count = post_record.post_like_count
        # Note: downvotes not available for lbsn.PostReactions
        post_reaction_record.reaction_content = post_record.post_body
        return post_reaction_record
