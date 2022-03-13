from flask import render_template, request, redirect, url_for, Flask, session
from get_dynamodb import get_dynamodb
from post_to_account_dynamodb import post_account_details
from register import check_username_exists
from login import check_account_credentials
from create_event import post_event_details, check_event_details
import json
import hashlib
import os

global event_id
event_id = 1

app = Flask(__name__)

@app.route('/', methods=["POST","GET"])
def home():

    events_data = get_dynamodb("event_details")
    return render_template("home.html",data=events_data)
    # return events_data

@app.route('/register', methods=["POST","GET"])
def register():

    if request.method == "POST":
        username = request.form['nm']

        if check_username_exists(username): # If username already exists then it redirects it again to registration page.
            return redirect(url_for("register"))

        else: # Otherwise, It proceeds to the login page
            salt = os.urandom(32).hex()
            password = hashlib.pbkdf2_hmac(
                'sha256', 
                bytes(request.form['pw'],'utf-8'), 
                bytes(salt,'utf-8'),
                100000
            ).hex()

            post_account_details(username,password)
            return redirect(url_for("home"))

    else:
        return render_template("register.html")


@app.route('/login', methods=["POST","GET"])
def login():

    if request.method == "POST":
        username = request.form['nm']
        plaintext = request.form['pw']

        if check_account_credentials(username,plaintext): # If an account like this exists, then it is succesfully logged in
            return "Succesfully Logged In"
        else:
            return redirect(url_for("login"))

    else:
        return render_template("login.html")


@app.route('/get_account_details', methods=["GET"])
def get_account_details():

    if request.method == "GET":

        data = get_dynamodb("account_details")
        return data

@app.route('/get_event_details', methods=["GET"])
def get_event_details():

    if request.method == "GET":

        data = get_dynamodb("event_details")
        return data

    
@app.route('/create_event', methods=["POST","GET"])
def create_event():

    if request.method == "POST":

        event_info = {
            "event_id": event_id,
            "title": request.form['title'],
            "description": request.form['description'],
            "type": request.form['type'],
            "venue": request.form['venue'],
            "start_date": request.form['start_date'],
            "end_date": request.form['end_date'],
            "tickets_available": request.form['tickets_available'],
            "ticket_price": request.form['ticket_price'],
        }

        event_id += 1

        event_info ['list_attendees'] = ""
        
        if check_event_details(event_info):
            pass

        else:
            post_event_details(event_info)
            return redirect(url_for("home"))

    else:
        return render_template("create_event.html")



@app.route('/book_ticket/<event_id>', methods = ["POST","GET"])
def book_ticket(event_id):
    
    if request.method == "POST":
        
        ticket = {
            "Pname": request.form['Pname'],
            "Pemail":request.form['Pemail'],
            "ticketQuantity":request.form['ticketQuantity'],
            "cardNumber":request.form['cardNumber'],
            "month":request.form['month'],
            "year":request.form['year'],
            "cvc":requst.form['cvc'],        
        }
         
    else:
        return render_template("booking.html", content = event_id)


if __name__ == "__main__":
    app.run(debug=True, port=3500)