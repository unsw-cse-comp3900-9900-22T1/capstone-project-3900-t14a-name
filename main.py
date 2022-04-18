
#from crypt import methods
from operator import attrgetter
from click import confirm
from flask import jsonify, render_template, request, redirect, url_for, Flask, session
from auth import generate_token
from get_dynamodb import get_dynamodb,get_dynamodb_item,delete_event


from flask import render_template, request, redirect, url_for, Flask, make_response, session
from auth import generate_token, get_session_token, remove_token, session_token_to_user
from get_dynamodb import get_dynamodb, get_dynamodb_item, update_event, get_dynamodb_item_user

from post_to_account_dynamodb import post_account_details, update_account_to_dynamoDB,update_event_to_dynamoDB
from register import check_username_exists
from review import edit_review, get_reviews_alt, post_review, get_review, reply_review
from login import check_account_credentials
from create_event import post_event_details, check_event_details
from search import search_title_and_description,search_by_location
from password import check_password_strength



from confirmation_email import confirm_booking,cancellation


import json
import hashlib
import secrets
import os
import datetime



global event_id
event_id = 1

app = Flask(__name__)

@app.route('/', methods=["POST","GET"])
def home():
    session_token = get_session_token(request)
    if session_token is None:
        username = ""
    else:
        session_alive = True
        username = session_token_to_user(session_token)

    events_data = get_dynamodb("event_details")
    events_data = json.loads(events_data) # Converts it back to JSON so that html can format it properly
    events_data.sort(key=lambda x: datetime.datetime.strptime(x['Start Date'], '%d/%m/%Y')) # Sorts the Start Date from closest to far so thats the order it shows on the website

    if session_token:
        return render_template("logged_in_home.html",data=events_data,username=username)
    else:
        return render_template("home.html",data=events_data,username=username)
    # return events_data


@app.route('/register', methods=["POST","GET"])
def register():

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        phone_number = request.form['phone']

        if check_username_exists(username): # If username already exists, fail registration
            return render_template("RegisterFailed.html")

        if check_password_strength(password): # If password is too weak, fail registration
            return render_template("RegisterFailed.html")

        if password != confirm_password: # type/copypaste passwords correctly please
            return render_template("RegisterFailed.html")

        else: # Otherwise, It proceeds to the login page
            salt = secrets.token_urlsafe(64)
            password = hashlib.pbkdf2_hmac(
                'sha256', 
                bytes(request.form['password'],'utf-8'), 
                bytes(salt,'utf-8'),
                100000
            ).hex()

            post_account_details(username,salt,password,email)
            return redirect(url_for("login"))

    else:
        return render_template("register.html")


@app.route('/login', methods=["POST","GET"])
def login():

    if request.method == "POST":
        username = request.form['nm']
        plaintext = request.form['pw']
        if check_account_credentials(username,plaintext): # If an account like this exists, then it is succesfully logged in
            token_id, valid_until = generate_token(username)
            response = make_response(redirect(url_for("home")))
            response.set_cookie("session-token", token_id, 604800, valid_until)
            return response
        else:
            return render_template("LoginFailed.html")

    else:
        return render_template("login.html")

@app.route('/logout', methods=["POST","GET"])
def logout():
    session_token = get_session_token(request)
    if session_token is None:
        return redirect(url_for("login"))

    remove_token(session_token)

    response = make_response(redirect(url_for("home")))
    response.set_cookie("session-token", "", expires=0)
    return response


@app.route('/get_account_details', methods=["GET"])
def get_account_details():
    # session_token = get_session_token(request)
    # if session_token is None:
    #     return redirect(url_for("login"))

    if request.method == "GET":

        data = get_dynamodb("account_details")
        return data


@app.route('/get_event_details', methods=["GET"])
def get_event_details():
#     session_token = get_session_token(request)
#     if session_token is None:
#         return redirect(url_for("login"))

    if request.method == "GET":

        data = get_dynamodb("event_details")
        return data

    
@app.route('/create_event', methods=["POST","GET"])
def create_event():
    session_token = get_session_token(request)
    if session_token is None:
        return redirect(url_for("login"))
    user = session_token_to_user(session_token)
    if request.method == "POST":

        event_info = {
            # "event_id": event_id,
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

        # event_id += 1
        event_info['list_attendees'] = []
        
        if check_event_details(event_info):
            pass

        else:
            post_event_details(event_info)
            #event = create_seatsio_event()
            #print("Event: \n")
            #print(event)
            return redirect(url_for("home"))

    else:
        #chart_key = create_chart()
        return render_template("create_event.html")


@app.route('/event_info/<Event_Title>', methods=["POST","GET"])
def event_info(Event_Title):
    session_token = get_session_token(request)
    if session_token is None:
        user = ""
    else:
        user = session_token_to_user(session_token)

    event_data = get_dynamodb_item("event_details",Event_Title)
    
    try:
        reviews = get_reviews_alt(Event_Title).values()
    except Exception:
        reviews = []

    all_events_data = get_dynamodb("event_details")
    all_events_data = json.loads(all_events_data) # Converts it back to JSON so that html can format it properly
    all_events_data.remove(event_data)
    return render_template("event_info.html",user=user,data=event_data,all_events_data=all_events_data,reviews=reviews)


@app.route('/search', methods=["POST","GET"])
def search():
    session_token = get_session_token(request)
    if session_token is None:
        user = ""
    else:
        user = session_token_to_user(session_token)

    if request.method == "POST":
        search_input = request.form['search']
        events_data = search_title_and_description(search_input)

        # First searches by title,description or event type...then searches by suburb/postcode
        if len(events_data) == 0:
            events_data = search_by_location(search_input)


        if session_token is None:
            return render_template("logged_in_home.html",data=events_data)
        else:
            return render_template("home.html",data=events_data)

    else:
        return render_template("home.html")


@app.route('/search_type=<Type>', methods=["POST","GET"])
def search_type(Type):
    session_token = get_session_token(request)
    if session_token is None:
        user = ""
    else:
        user = session_token_to_user(session_token)

    search_input = Type
    events_data = search_title_and_description(search_input)

    if session_token is None:
        return render_template("home.html",data=events_data)
    else:
        return render_template("logged_in_home.html",data=events_data)



'''
@app.route('/event_info/<Event_Title>/book_ticket', methods = ["POST","GET"])
def book_ticket(Event_Title):
    print("event = " + Event_Title)
    data = get_dynamodb_item("event_details",Event_Title)
    
    if request.method == "POST":
        
        try:
            checkout = {
                "payment": request.form.get('payment'),
                "cardholder": request.form.get('cardholder'),
                "date": request.form.get('date'),
                "verification": request.form.get('verification'),
                "cardnumber":request.form.get('cardnumber')
            }
            
            if checkout is not None:
                session_token = get_session_token(request)
                if session_token is None:
                    user = ""
                else:
                    user = session_token_to_user(session_token)
                    data['List of Attendees'].append(checkout['cardholder'])
                    user_data = get_dynamodb_item_user(user)
                    user_data['List of Events'].append(Event_Title)
                    update_event("event_details",data)
                    update_event("account_details",user_data)
            
        finally:
            
            
            data['List of Attendees'].append("Ricky")
            update_event("event_details",data)
            
            return render_template("booking.html" )
            
    else:
        return render_template("booking.html")
'''

@app.route('/leave_review/<event_name>', methods = ["POST"])
def leave_review(event_name):
    session_token = get_session_token(request)
    if session_token is None:
        return redirect(url_for("login"))

    if request.method == "POST":
        review = request.form['review_text']
        post_review(session_token, event_name, review)

    return redirect("/event_info/" + event_name)


@app.route('/edit_review/<event_name>', methods = ["GET", "POST"])
def edit_review_route(event_name):
    session_token = get_session_token(request)
    if session_token is None:
        return redirect(url_for("login"))

    user = session_token_to_user(session_token)
    old_review = get_review(event_name, user)["review_text"]

    if request.method == "GET":
        return render_template("edit_review.html",event_title=event_name, old_review=old_review)

    if request.method == "POST":
        new_review = request.form['new_review']
        edit_review(session_token, event_name, user, new_review)

    return redirect("/event_info/" + event_name)


@app.route('/reply_review/<event_name>/<username>', methods = ["GET", "POST"])
def reply_review_route(event_name, username):
    session_token = get_session_token(request)
    if session_token is None:
        return redirect(url_for("login"))

    review = get_review(event_name, username)["review_text"]

    if request.method == "GET":
        return render_template("reply_review.html",event_title=event_name, review=review, user=username)

    if request.method == "POST":
        reply = request.form['reply_text']
        reply_review(session_token, event_name, username, reply)
        
    return redirect("/event_info/" + event_name)
  
# Booking page place holder       
@app.route('/book_trial', methods = ["POST","GET"])
def book_trial():
    return render_template("booking.html")

@app.route('/add_to_favourites/<favourite_event>',methods = ["POST","GET"])
def add_to_favourites(favourite_event):

    session_token = get_session_token(request)
    if session_token is None:
        user = ""
    else:
        user = session_token_to_user(session_token)

    user_data = get_dynamodb_item_user(user)

    # Checks if the event doesn't already exist in the favourites list
    if favourite_event not in user_data['Favourites List']:
        user_data['Favourites List'].append(favourite_event)

    update_account_to_dynamoDB(user_data)
    
    return redirect(url_for("home"))

@app.route('/remove_from_favourites/<favourite_event>',methods = ["POST","GET"])
def remove_from_favourites(favourite_event):

    session_token = get_session_token(request)
    if session_token is None:
        user = ""
    else:
        user = session_token_to_user(session_token)

    user_data = get_dynamodb_item_user(user)

    # Checks if the event doesn't already exist in the favourites list
    user_data['Favourites List'].remove(favourite_event)

    update_account_to_dynamoDB(user_data)
    
    return redirect(url_for("favourites_list"))


@app.route('/favourites_list',methods = ["POST","GET"])
def favourites_list():

    session_token = get_session_token(request)
    if session_token is None:
        user = ""
        return redirect(url_for("home"))
    else:
        user = session_token_to_user(session_token)

    user_data = get_dynamodb_item_user(user)
    user_favourites_list_titles = user_data['Favourites List']
    events_data = get_dynamodb("event_details")
    events_data = json.loads(events_data) # Converts it back to JSON so that html can format it properly
    user_favourites_list_data = []

    for event in events_data:

        if event['Event Title'] in user_favourites_list_titles:
            user_favourites_list_data.append(event)
    

    return render_template("favourites_list.html",data=user_favourites_list_data,username=user)



@app.route('/event_info/<Event_Title>/book_ticket',methods = ["POST","GET"])
def book_event(Event_Title):
    event = get_dynamodb_item("event_details",Event_Title)
    
    if request.method == "POST":
        
        # Decreases the number of available tickets
        if int(event['Tickets Available']) <= 0:
            event['Tickets Available'] = "SOLD OUT"
            update_event_to_dynamoDB(event)
            return redirect(url_for("login"))

            
        try:
            tickets_available = event['Tickets Available']
            tickets_available = int(tickets_available)
            remaining_tickets = tickets_available - 1
            event['Tickets Available'] = remaining_tickets
            update_event_to_dynamoDB(event)
        except:
            pass

        print(request.form.getlist('seat'))
        return render_template("book_event.html")      
    
    elif request.method == "GET":
        return render_template("book_event.html")


     
@app.route('/event_info/<Event_Title>/booking.html',methods = ["POST","GET"])
def pay_event(Event_Title):
    data = get_dynamodb_item("event_details",Event_Title)
    
    if request.method == "POST":

        try:
            checkout = {
                "payment": request.form.get('payment'),
                "cardholder": request.form.get('cardholder'),
                "date": request.form.get('date'),
                "verification": request.form.get('verification'),
                "cardnumber":request.form.get('cardnumber')
            }
            
            if checkout is not None:
                session_token = get_session_token(request)
                if session_token is None:
                    user = ""
                else:
                    user = session_token_to_user(session_token)
                    #data['List of Attendees'].append(checkout['cardholder'])
                    user_data = get_dynamodb_item_user(user)
                    data['List of Attendees'].append(user_data['Username'])
                    user_data['List of Events'].append(Event_Title)
                    update_event("event_details",data)
                    update_event("account_details",user_data)
                    #print('User Email: ' + user_data['Email'] + ',Event: ' + Event_Title)
                    confirm_booking(user_data['Email'],Event_Title)
            
        finally:
            
            return render_template("booking.html" )
            
    else:
        return render_template("booking.html")


@app.route('/<Event_Title>/cancel',methods = ["GET"])
def cancel_event(Event_Title):
    
 
    data = get_dynamodb_item("event_details",Event_Title)
    for user in data['List of Attendees']:
        userdata = get_dynamodb_item_user(user)
        cancellation(userdata['Email'],Event_Title)
        userdata['List of Events'].remove(Event_Title)
        update_event("account_details",userdata)
            
    delete_event(Event_Title)
    
    return render_template('cancellation.html') 
        #return json.dumps(data['List of Attendees'])


@app.route('/recommendations', methods = ["POST","GET"])
def recommendations():
    
    session_token = get_session_token(request)
    if session_token is None:
        user = ""
        return redirect(url_for("login"))
    else:
        user = session_token_to_user(session_token)
    
    event_data = get_dynamodb("event_details")
    event_data = json.loads(event_data)

    list_of_attended_events = []


    # Saves all events that the user attends
    list_of_booked_hosts = []
    for event in event_data:

        if user in event["List of Attendees"]:
            list_of_attended_events.append(event)


    # Finds common events for recommendations
    list_of_recommendated_events = []
    for attended_event in list_of_attended_events:

        for event in event_data:
            
            if event in list_of_recommendated_events:
                continue

            if attended_event['Event Title'] == event['Event Title']:
                continue
            
            if attended_event['Type'] == event['Type']:
                list_of_recommendated_events.append(event)
                continue

            if event['Host'] == attended_event['Host']:
                list_of_recommendated_events.append(event)

            event_description_words = set(event['Description'].split())
            attended_event_description_words = set(attended_event['Description'].split())
            common_words = event_description_words & attended_event_description_words
            if len(common_words) > 2:
                list_of_recommendated_events.append(event)

    # Removes common events that are already booked
    list_of_new_recommendated_events = []
    for event in list_of_recommendated_events:

        if event not in list_of_attended_events:
            list_of_new_recommendated_events.append(event)

    return render_template("recommendated_events.html",data=list_of_new_recommendated_events,username=user)
    


@app.route('/list_of_booked_events', methods = ["POST","GET"])
def list_of_booked_events():

    session_token = get_session_token(request)
    if session_token is None:
        user = ""
        return redirect(url_for("login"))
    else:
        user = session_token_to_user(session_token)
    
    event_data = get_dynamodb("event_details")
    event_data = json.loads(event_data)

    list_of_attended_events = []

    # Saves all events that the user attends
    for event in event_data:

        if user in event["List of Attendees"]:
            list_of_attended_events.append(event)

    return render_template("attended_events.html",data=list_of_attended_events,username=user)





@app.route('/<Event_Title>/list',methods = ["GET"])
def list_event(Event_Title):
    
    if request.method == "GET":
        data = get_dynamodb_item("event_details",Event_Title)
        return json.dumps(data['List of Attendees'])  
    

@app.route('/event_info/<Event_Title>/cancel', methods = ["GET","POST"])
def user_cancel(Event_Title):
    
    session_token = get_session_token(request)
    if session_token is None:
        user = ""
        return redirect(url_for("login"))
    else:
        user = session_token_to_user(session_token)
    
    user_data = get_dynamodb_item_user(user)
    event_data =  get_dynamodb_item("event_details",Event_Title)
    event_data['List of Attendees'].remove(user_data['Username'])
    user_data['List of Events'].remove(Event_Title)
    update_event("event_details",event_data)
    update_event("account_details",user_data)

   
    return render_template("cancellation.html")

@app.route('/confirm_booking', methods = ["GET","POST"])
def confirmation():
    return render_template('confirmation.html')


if __name__ == "__main__":
    app.run(debug=True, port=3500)
