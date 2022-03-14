from lib2to3.pgen2.token import tok_name
from re import S
from flask import render_template, request, redirect, url_for, Flask, session
from get_dynamodb import get_dynamodb
from post_to_account_dynamodb import post_account_details
from register import check_username_exists
from login import check_account_credentials
from create_event import post_event_details, check_event_details
import secrets
from datetime import datetime, timedelta


'''
session_token: {
    "generated_timestamp"
    "valid_until"
    "username"
}
'''


active_sessions = {}

"""
"""
def generate_token(user):
    now = datetime.now()
    token_id = secrets.token_urlsafe(64)
    new_token = {
        "generated_timestamp":now,
        "valid_until":now + timedelta(days=7),
        "username":user
    }
    active_sessions[token_id] = new_token
    return active_sessions

"""
"""
def check_token(session_token):
    if session_token in active_sessions:
        now = datetime.now()
        session = active_sessions[session_token]
        if now > session["generated_timestamp"] and session["valid_until"] > now:
            return True
        else:
            del active_sessions[session_token]
        return False;
    return False

"""
"""
def remove_token(session_token):
    if check_token(session_token) == False:
        return None
    del active_sessions[session_token]
    return True

"""
"""
def session_token_to_user(session_token):
    if check_token(session_token) == False:
        return None
    return active_sessions[session_token]["username"]