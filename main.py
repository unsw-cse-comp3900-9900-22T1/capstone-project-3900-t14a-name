from flask import render_template, request, redirect, url_for, Flask, make_response, session
from auth import generate_token, get_session_token, remove_token, session_token_to_user
from get_dynamodb import get_dynamodb, get_dynamodb_item
from post_to_account_dynamodb import post_account_details
from register import check_username_exists
from login import check_account_credentials
from create_event import post_event_details, check_event_details
from search import search_title_and_description,filter_event_types,search_all
from password import check_password_strength
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
        username = session_token_to_user(session_token)

    events_data = get_dynamodb("event_details")
    events_data = json.loads(events_data) # Converts it back to JSON so that html can format it properly
    events_data.sort(key=lambda x: datetime.datetime.strptime(x['Start Date'], '%d/%m/%Y')) # Sorts the Start Date from closest to far so thats the order it shows on the website

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
            return redirect(url_for("register"))

        if check_password_strength(password): # If password is too weak, fail registration
            return redirect(url_for("register"))

        if password != confirm_password: # type/copypaste passwords correctly please
            return redirect(url_for("register"))

        else: # Otherwise, It proceeds to the login page
            salt = secrets.token_urlsafe(64)
            password = hashlib.pbkdf2_hmac(
                'sha256', 
                bytes(request.form['password'],'utf-8'), 
                bytes(salt,'utf-8'),
                100000
            ).hex()

            post_account_details(username,salt,password)
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
            return redirect(url_for("login"))

    else:
        return render_template("login.html")


@app.route('/get_account_details', methods=["GET"])
def get_account_details():
    session_token = get_session_token(request)
    if session_token is None:
        return redirect(url_for("login"))

    if request.method == "GET":

        data = get_dynamodb("account_details")
        return data

@app.route('/get_event_details', methods=["GET"])
def get_event_details():
    session_token = get_session_token(request)
    if session_token is None:
        return redirect(url_for("login"))

    if request.method == "GET":

        data = get_dynamodb("event_details")
        return data

    
@app.route('/create_event', methods=["POST","GET"])
def create_event():
    session_token = get_session_token(request)
    if session_token is None:
        return redirect(url_for("login"))

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
        }

        # event_id += 1

        event_info ['list_attendees'] = ""
        
        if check_event_details(event_info):
            pass

        else:
            post_event_details(event_info)
            return redirect(url_for("home"))

    else:
        return render_template("create_event.html")

@app.route('/event_info=<Event_Title>', methods=["POST","GET"])
def event_info(Event_Title):
    session_token = get_session_token(request)
    if session_token is None:
        return redirect(url_for("login"))
    
    event_data = get_dynamodb_item("event_details",Event_Title)
    return render_template("event_info.html",data=event_data)


@app.route('/search', methods=["POST","GET"])
def search():
    session_token = get_session_token(request)
    if session_token is None:
        return redirect(url_for("login"))

    if request.method == "POST":
        search_input = request.form['search']
        events_data = search_title_and_description(search_input)
        return render_template("home.html",data=events_data)

    else:
        return render_template("home.html")

@app.route('/search_type=<Type>', methods=["POST","GET"])
def search_type(Type):
    session_token = get_session_token(request)
    if session_token is None:
        return redirect(url_for("login"))

    search_input = Type
    events_data = search_title_and_description(search_input)
    return render_template("home.html",data=events_data)



@app.route('/book_ticket/<event_id>', methods = ["POST","GET"])
def book_ticket(event_id):
    session_token = get_session_token(request)
    if session_token is None:
        return redirect(url_for("login"))

    if request.method == "POST":
        
        ticket = {
            "Pname": request.form['Pname'],
            "Pemail":request.form['Pemail'],
            "ticketQuantity":request.form['ticketQuantity'],
            "cardNumber":request.form['cardNumber'],
            "month":request.form['month'],
            "year":request.form['year'],
            "cvc":request.form['cvc'],        
        }
         
    else:
        return render_template("booking.html", content = event_id)


@app.route('/logout', methods=["POST","GET"])
def logout():
    session_token = get_session_token(request)
    if session_token is None:
        return redirect(url_for("login"))

    remove_token(session_token)

    response = make_response(redirect(url_for("home")))
    response.set_cookie("session-token", "", expires=0)
    return response

if __name__ == "__main__":
    app.run(debug=True, port=3500)