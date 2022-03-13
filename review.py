import json
from tabnanny import check
import requests
import pprint
import boto3

client = boto3.client('dynamodb',region_name='ap-southeast-2',aws_access_key_id='AKIAQPNE33YVPQHU7F64',aws_secret_access_key='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')

# to read reviews for an event, should be SELECT * FROM REVIEWS WHERE EVENT_ID = EVENT_ID SORT BY POSTED_DATE DESCENDING

'''
review = {
    "review_id"
    "event_id"
    "username"
    "review_text"
    "reply_text"
    "posted_date"
}
'''

global review_id

def post_review(session_token):
    #check if session token is valid
    #check if event exists
    #check if user has attended the event
    #check if a review does not already exist
    #post review

    review_id += 1
    return

def edit_review(session_token):
    #check if session token is valid
    #check if event exists
    #check if user has attended the event
    #check if a review does already exist
    #edit review

    return

def delete_review(session_token):
    #check if session token is valid
    #check if event exists
    #check if user has attended the event
    #check if a review does already exist
    #delete review

    return

def reply_review(session_token):
    #check if session token is valid
    #check if event exists
    #check if user hosted the event
    #check if a review does already exist
    #reply to review

    return