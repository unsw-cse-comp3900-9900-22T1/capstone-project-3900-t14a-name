import json
import pprint
from get_dynamodb import get_dynamodb



def search_all(search_input,event_types):
    
    data = get_dynamodb("event_details")
    data = json.loads(data)
    list_of_related_events = []

    for each_event in data:
            
        if event_types == each_event['Type']:

            if search_input in each_event['Event Title'] or search_input in each_event['Description']:
                list_of_related_events.append(each_event)

    return list_of_related_events

def search_title_and_description(search_input):

    data = get_dynamodb("event_details")
    data = json.loads(data)
    list_of_related_events = []
    search_input = search_input.lower() # Compare all strings with lowercases

    for each_event in data:
        if search_input in each_event['Event Title'].lower():
            list_of_related_events.append(each_event)

        elif search_input in each_event['Description'].lower():
            list_of_related_events.append(each_event)

        elif search_input in each_event['Type'].lower():
            list_of_related_events.append(each_event)


    return list_of_related_events

def filter_event_types(event_type):

    data = get_dynamodb("event_details")
    data = json.loads(data)
    list_of_related_events = []

    for each_event in data:
            
        if event_type == each_event['Type']:
            list_of_related_events.append(each_event)

    return list_of_related_events