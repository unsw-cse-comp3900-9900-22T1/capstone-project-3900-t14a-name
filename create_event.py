from datetime import datetime
import re
import boto3 
from seats import create_seats

client = boto3.client('dynamodb',region_name='ap-southeast-2',aws_access_key_id='AKIAQPNE33YVPQHU7F64',aws_secret_access_key='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')

event_types = ["Sports", "Arts", "Festivals", "Theatre"]
postcode_regex = re.compile(r'\d{4}')
url_safe = set("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ$–_.+!*‘(),")

def post_event_details(event_info):
    check_output = client.put_item(TableName='event_details',
    Item={
        # 'Event ID':{'S': event_info['event_id']},
        'Event Title':{'S': event_info['title']},
        'Description':{'S': event_info['description']},
        'Type':{'S': event_info['type']},
        'Venue':{'S': event_info['venue']},
        'Start Date':{'S': event_info['start_date']},
        'End Date':{'S': event_info['end_date']},
        'Tickets Available': {'S': event_info['tickets_available']},
        'Ticket Price': {'S': event_info['ticket_price']},
        'List of Attendees': {'L': event_info['list_attendees']},
        'Seats' : { 'M': create_seats()},
        'Host': {'S': event_info['host']},
        'Postcode' : {'S': str(event_info['postcode'])}
        }
    )

    client.put_item(TableName='review_details',
    Item={
        # 'Event ID':{'S': event_info['event_id']},
        'Event Title':{'S': event_info['title']},
        'Reviews':{'M': {}}
    }
    )

    return check_output


"""
event_info = {
    "title": request.form['title'],
    "description": request.form['description'],
    "type": request.form['type'],
    "venue": request.form['venue'],
    "start_date": request.form['start_date'],
    "end_date": request.form['end_date'],
    "tickets_available": request.form['tickets_available'],
    "ticket_price": request.form['ticket_price'],
    "postcode": request.form['postcode'],
    "host": user,
}
"""
def check_event_title(title):
    try:
        if set(title) <= url_safe:
            return True #Check the title contains only URL safe characters
    except:
        pass
    return False

def check_event_type(type):
    try:
        if type in event_types:
            return True
    except:
        pass
    return False

def check_event_dates(start_date, end_date):
    try:
        start_parsed = datetime.strptime(start_date,"%d/%m/%Y")
        end_parsed = datetime.strptime(end_date,"%d/%m/%Y")
        if datetime.today() > start_date:
            return False #Events must be in the future!
        if start_parsed > end_parsed:
            return False #Events must end after they start!
        return True
    except:
        pass
    return False

def check_event_tickets(tickets_available, ticket_price):
    try:
        if int(tickets_available) <= 0:
            return False
        if int(ticket_price) < 0:
            return False
        return True
    except:
        pass
    return False

def check_event_postcode(postcode):
    try:
        if re.fullmatch(postcode_regex, postcode):
            return True
    except:
        pass
    return False

def check_event_details(event_info):
    if (
        not event_info['title'] or
        not event_info['description'] or
        not event_info['type'] or
        not event_info['venue'] or
        not event_info['start_date'] or
        not event_info['end_date'] or
        not event_info['tickets_available'] or
        not event_info['ticket_price'] or
        not event_info['postcode'] or
        not event_info['host']
    ):
        return False
    if not check_event_title(event_info['title']):
        return False
    if not check_event_title(event_info['type']):
        return False
    if not check_event_dates(event_info['start_date'], event_info['end_date']):
        return False
    if not check_event_tickets(event_info['tickets_available'], event_info['ticket_price']):
        return False
    if not check_event_postcode(event_info['postcode']):
        return False
    return True
