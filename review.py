import json
from tabnanny import check
import requests
import boto3
from datetime import date

from auth import session_token_to_user
from get_dynamodb import get_dynamodb_item

client = boto3.client('dynamodb',region_name='ap-southeast-2',aws_access_key_id='AKIAQPNE33YVPQHU7F64',aws_secret_access_key='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')

'''
Item={
    'Event Title':{'S': event_title},
    'Reviews':{'M': {
        user:{'M': {
            "review_text":{'S':review['review_text']},
            "reply_posted":{'BOOL':review['reply_posted']},
            "reply_text":{'S':review['reply_text']},
            "posted_date":{'S':str(review['posted_date'])},
            "edited_date":{'S':str(review['edited_date'])},
            "reply_date":{'S':str(review['reply_date'])}
            }}
    }}
}

get_dynamodb_item("review_details","Free Beer")
'''

def post_review_to_db(event_title, user, review):
    check_output = client.update_item(TableName='review_details',
    Key={'Event Title':{'S': event_title}},
    UpdateExpression="SET Reviews."+user+"=:r",
     ExpressionAttributeValues ={
        ':r':{
            'M': {
                "review_text":{'S':review['review_text']},
                "reply_posted":{'BOOL':review['reply_posted']},
                "reply_text":{'S':review['reply_text']},
                "posted_date":{'S':str(review['posted_date'])},
                "edited_date":{'S':str(review['edited_date'])},
                "reply_date":{'S':str(review['reply_date'])}
                }
            }
        }
    )
    return check_output

"""
"""
def get_reviews(event_title):
    reviews = get_dynamodb_item("review_details",event_title)['Reviews']
    return reviews

"""
stupid hack to include keys 
"""
def get_reviews_alt(event_title):
    reviews = get_dynamodb_item("review_details",event_title)['Reviews']
    for reviewer in reviews:
        reviews[reviewer]['username'] = reviewer
    return reviews

"""
"""
def review_exists(event_title, user):
    try:
        return user in get_reviews(event_title)
    except Exception:
        return False

"""
"""
def get_review(event_title, user):
    reviews = get_dynamodb_item("review_details",event_title)['Reviews']
    return reviews[user]

"""
"""
def post_review(session_token, event_title, review_text):
    #check if session token is valid
    user = session_token_to_user(session_token)
    if user is None:
        return False

    #check if event exists and user has attended the event


    #check if a review by that user for that event does not already exist
    if review_exists(event_title, user):
        return False

    review = {
        "review_text":review_text,
        "reply_posted":False,
        "reply_text":"",
        "posted_date":date.today(),
        "edited_date":None,
        "reply_date":None
    }

    post_review_to_db(event_title, user, review)

    return True

"""
"""
def edit_review(session_token, event_title, username, new_review):
    #check if session token is valid
    user = session_token_to_user(session_token)
    if not user == username:
        return False

    #check if a review does already exist
    if not review_exists(event_title, username):
        return False

    #edit review
    review = get_review(event_title, username)
    review["review_text"] = new_review
    review["edited_date"] = date.today()
    post_review_to_db(event_title, user, review)

    return True

"""
"""
def reply_review(session_token, event_title, username, reply):
    #check if session token is valid
    user = session_token_to_user(session_token)
    if user is None:
        return False

    #check if a review does already exist
    if not review_exists(event_title, username):
        return False

    #check if user hosted the event

    #reply to review
    review = get_review(event_title, username)
    review["reply_text"] = reply
    review["reply_posted"] = True
    review["reply_date"] = date.today()
    post_review_to_db(event_title, username, review)

    return True


"""
"""
def delete_review(session_token, event_title, username):
    #check if session token is valid
    user = session_token_to_user(session_token)
    if not user == username:
        return False

    #check if a review does already exist
    if not review_exists(event_title, username):
        return False

    #delete review
    review = get_review(event_title, username)

    post_review_to_db(event_title, user, review)

    #cleanup references to review in event and user

    return True
