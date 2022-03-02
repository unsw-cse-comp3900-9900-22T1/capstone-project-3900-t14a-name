from flask import Flask
import json
import os


app = Flask(__name__)

@app.route('/', methods=["GET"])
def home():
  
  return "This is a Flask Server"


if __name__ == "__main__":
    app.run(debug=True)
