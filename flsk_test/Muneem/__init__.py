import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'Muneem/Templates'))
app.secret_key = 'b4d2c8a7e6e0499e875e5150d8e91562'  # Example secret key

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///muneem.db'
db = SQLAlchemy(app)

from Muneem import routes