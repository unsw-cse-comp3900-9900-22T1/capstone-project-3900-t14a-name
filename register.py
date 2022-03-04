import json
from tabnanny import check
import requests
import pprint
import boto3

client = boto3.client('dynamodb',region_name='ap-southeast-2',aws_access_key_id='AKIAQPNE33YVPQHU7F64',aws_secret_access_key='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')


def check_username_exists(username):

    try:

        response = client.get_item(TableName='account_details', Key={'Username':{'S': username}})
        if response['Item']['Username']['S'] == username:
            return True

    except:
        pass

    return False
