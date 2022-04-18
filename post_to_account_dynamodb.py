import json
import requests
import pprint
import boto3

client = boto3.client('dynamodb',region_name='ap-southeast-2',aws_access_key_id='AKIAQPNE33YVPQHU7F64',aws_secret_access_key='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')


def post_account_details(username,salt,password,email):

    check_output = post_account_to_dynamoDB(username,salt,password,email)

    # Checks if the username & password have been posted succesfully
    if check_output['ResponseMetadata']['HTTPStatusCode'] == 200:
        return True
    else:
        return False


def post_account_to_dynamoDB(username,salt,password,email):

    # When an user gets registered, an empty list is assigned.
    empty_events_list = [] 
    empty_favourites_list = []

    check_output = client.put_item(TableName='account_details',
    Item={
        'Username':{'S':username},
        'Salt':{'S':salt},
        'Password':{'S':password},
        'List of Events':{'L': empty_events_list},
        'Favourites List':{'L': empty_favourites_list},
        'Email' : {'S': email}
    }

    )

    return check_output

def update_account_to_dynamoDB(item):
    
    dynamodb = boto3.resource('dynamodb',region_name='ap-southeast-2',aws_access_key_id='AKIAQPNE33YVPQHU7F64',aws_secret_access_key='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')
    table = dynamodb.Table('account_details')

    table.put_item(
        Item={
            'Username':item['Username'],
            'Salt':item['Salt'],
            'List of Events':item['List of Events'],
            'Password':item['Password'],
            'Favourites List': item['Favourites List'],
            'Email': item['Email']
        }
    )

def update_event_to_dynamoDB(item):
    
    dynamodb = boto3.resource('dynamodb',region_name='ap-southeast-2',aws_access_key_id='AKIAQPNE33YVPQHU7F64',aws_secret_access_key='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')
    table = dynamodb.Table('event_details')

    table.put_item(
        Item={
            'Event Title':item['Event Title'],
            'Start Date':item['Start Date'],
            'Postcode':item['Postcode'],
            'Description':item['Description'],
            'Ticket Price': item['Ticket Price'],
            'Venue': item['Venue'],
            'Tickets Available': str(item['Tickets Available']),
            'Seats':item['Seats'],
            'Host': item['Host'],
            'List of Attendees': item['List of Attendees'],
            'End Date': item['End Date'],
            'Type': item['Type'],
        }
    )

        
