from flask import render_template, request, redirect, url_for, Flask, session
from get_dynamodb import get_dynamodb
from post_to_account_dynamodb import post_account_details
from register import check_username_exists
from login import check_account_credentials
from create_event import post_event_details, check_event_details
import hashlib
import os

active_sessions = {}

"""
"""
def generate_token(user):
    return

"""
"""
def clear_tokens(user):
    return

"""
"""
def check_token(session_token):
    return

"""
"""
def session_token_to_user(session_token):
    check_token(session_token)
    return