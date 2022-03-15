import json
from tabnanny import check
import requests
import pprint
import boto3
import hashlib

client = boto3.client('dynamodb',region_name='ap-southeast-2',aws_access_key_id='AKIAQPNE33YVPQHU7F64',aws_secret_access_key='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')


def check_account_credentials(username,plaintext):

    try:

        response = client.get_item(TableName='account_details', Key={'Username':{'S': username}})
        salt = response['Item']['Salt']['S']

        password = hashlib.pbkdf2_hmac(
            'sha256',
            bytes(plaintext,'utf-8'),
            bytes(salt,'utf-8'),
            100000
        ).hex()

        if response['Item']['Username']['S'] == username and response['Item']['Password']['S'] == password:
            return True

    except:
        pass

    return False