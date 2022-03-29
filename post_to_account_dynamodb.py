import json
import requests
import pprint
import boto3

client = boto3.client('dynamodb',region_name='ap-southeast-2',aws_access_key_id='AKIAQPNE33YVPQHU7F64',aws_secret_access_key='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')

def post_account_details(username,salt,password):

    check_output = post_account_to_dynamoDB(username,salt,password)

    # Checks if the username & password have been posted succesfully
    if check_output['ResponseMetadata']['HTTPStatusCode'] == 200:
        return True
    else:
        return False


def post_account_to_dynamoDB(username,salt,password):

    empty_events_list = [] # When an user gets registered, an empty list is assigned.

    check_output = client.put_item(TableName='account_details',
    Item={
        'Username':{'S':username},
        'Salt':{'S':salt},
        'Password':{'S':password},
        'List of Events':{'L': empty_events_list}
    }

    )

    return check_output