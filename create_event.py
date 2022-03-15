import json
import boto3 

client = boto3.client('dynamodb',region_name='ap-southeast-2',aws_access_key_id='AKIAQPNE33YVPQHU7F64',aws_secret_access_key='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')


def post_event_details(event_info):

    check_output = client.put_item(TableName='event_details',

    Item={
        'Event ID':{'S': event_info['event_id']},
        'Event Title':{'S': event_info['title']},
        'Description':{'S': event_info['description']},
        'Type':{'S': event_info['type']},
        'Venue':{'S': event_info['venue']},
        'Start Date':{'S': event_info['start_date']},
        'End Date':{'S': event_info['end_date']},
        'Tickets Available': {'S': event_info['tickets_available']},
        'Ticket Price': {'S': event_info['ticket_price']},
        'List of Attendees': {'S': event_info['list_attendees']}
    }

    )

    return check_output


def check_event_details(event_info):
    # This is where you will check the event_info and whether they are valid. 
    return False