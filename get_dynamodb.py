import json
import requests
import pprint
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb',region_name='ap-southeast-2',aws_access_key_id='AKIAQPNE33YVPQHU7F64',aws_secret_access_key='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')
# Account Details -> account_details
# Event Details -> event_details
def get_dynamodb(table_name):

    # Get the data from dynamoDB table
    table = dynamodb.Table(table_name)
    response = table.scan()
    items = response['Items']
    
    
    while 'LastEvaluatedKey' in response:
        print(response['LastEvaluatedKey'])
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])

    
    return json.dumps(items)


def get_dynamodb_item(table_name,item):

    table = dynamodb.Table(table_name)

    response = table.get_item(
        Key={'Event Title': item }
    )

    return response['Item']

def get_dynamodb_item_user(item):

    table = dynamodb.Table("account_details")

    response = table.get_item(
        Key={'Username': item }
    )

    return response['Item']

def update_event(table_name,data):
    
    table = dynamodb.Table(table_name)
    table.put_item(Item = data)