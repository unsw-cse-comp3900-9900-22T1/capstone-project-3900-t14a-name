import json
from tabnanny import check
import requests
import pprint
import re
import boto3
from password import check_password_strength

client = boto3.client('dynamodb',region_name='ap-southeast-2',aws_access_key_id='AKIAQPNE33YVPQHU7F64',aws_secret_access_key='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')

email_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
phone_regex = re.compile(r'(?:\+\d{2})?\d{3,4}\D?\d{3}\D?\d{3}')
url_safe = set("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ$–_.+!*‘(),")

def check_valid_username(username):
    try:
        response = client.get_item(TableName='account_details', Key={'Username':{'S': username}})
        if response['Item']['Username']['S'] == username:
            return False
    except:
        return False
    try:
        if set(username) <= url_safe:
            return True  #Check the username contains only URL safe characters
    except:
        pass
    return False

def check_valid_email(email):
    try:
        if re.fullmatch(email_regex, email):
            return True
    except:
        pass
    return False

def check_valid_phone(phone):
    try:
        if re.fullmatch(phone_regex, phone):
            return True
    except:
        pass
    return False

def do_registration_checks(username, password, fullname, confirm_password, email, phone):
    if not username or not password or not fullname or not confirm_password or not email or not phone:
        return False
    if password != confirm_password: # type/copypaste passwords correctly please
        return False
    if not check_valid_username(username): # If username already exists, fail registration
        return False
    if not check_password_strength(password): # If password is too weak, fail registration
        return False
    if not check_valid_email(email):
        return False
    if not check_valid_phone(phone):
        return False
    return False
