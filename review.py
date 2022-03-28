import json
from tabnanny import check
import requests
import pprint
import boto3
from datetime import date

from auth import session_token_to_user

client = boto3.client('dynamodb',region_name='ap-southeast-2',aws_access_key_id='AKIAQPNE33YVPQHU7F64',aws_secret_access_key='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')

# to read reviews for an event, should be SELECT * FROM REVIEWS WHERE EVENT_TITLE = EVENT_TITLE SORT BY POSTED_DATE DESCENDING

'''

DB STRUCTURE: {
    'ID':{'N': event_info['review_id']},
    'Event Title':{'S': event_info['title']},
    'Review Text':{'S': event_info['description']},
    'Reply Text':{'S': event_info['type']},
    'Posted Date':{'S': event_info['venue']},
    'Edit Date':{'S': event_info['start_date']},
    'Reply Date':{'S': event_info['end_date']},
}

MEMORY STRUCTURE: {
    review_id: {
        "event_title"
        "username"
        "review_text"
        "reply_text"
        "posted_date"
        "edited_date"
        "reply_date"
    }
}
'''

reviews = {}

global review_id
review_id = 1


"""
"""
def review_exists(check_id):
    return check_id in reviews

"""
"""
def post_review(session_token, event_title, review_text):
    #check if session token is valid
    user = session_token_to_user(session_token)
    if user is None:
        return None

    #check if event exists and user has attended the event


    #check if a review by that user for that event does not already exist


    #post review
    review_id += 1
    current_review_id = review_id
    reviews[current_review_id] = {
        "event_title":event_title,
        "username":user.username,
        "review_text":review_text,
        "reply_text":None,
        "posted_date":date.today(),
        "edited_date":None,
        "reply_date":None
    }
    
    return current_review_id

"""
"""
def edit_review(session_token, review_id, new_review):
    #check if session token is valid
    user = session_token_to_user(session_token)
    if user is None:
        return None

    #check if a review does already exist
    #edit review
    reviews[review_id]["review_text"] = new_review
    reviews[review_id]["edited_date"] = date.today()
    return True

"""
"""
def delete_review(session_token, review_id):
    #check if session token is valid
    user = session_token_to_user(session_token)
    if user is None:
        return None

    #check if a review does already exist
    #delete review
    event_title = reviews[review_id]["event_title"]
    del reviews[review_id]

    #cleanup references to review in event and user

    return True

"""
"""
def reply_review(session_token, review_id, reply):
    #check if session token is valid
    user = session_token_to_user(session_token)
    if user is None:
        return None

    #check if a review does already exist


    #check if event exists and user hosted the event
    event_title = reviews[review_id]["event_title"]

    #reply to review
    reviews[review_id]["reply_text"] = reply
    reviews[review_id]["reply_date"] = date.today()

    return True
