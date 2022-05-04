from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SECRET_KEY'] = '1c3c7811fb09da0e1cadcb7e'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

csrf = CSRFProtect(app)
db = SQLAlchemy(app)

# from inventory import routes


from .home_page import homepage
from .events_page import eventspage
from .json_routes import jsonroutes
from .resources import json_routes

app.register_blueprint(homepage, url_prefix='/')
app.register_blueprint(eventspage, url_prefix='/events/')
app.register_blueprint(jsonroutes, url_prefix='/json-routes/')
app.register_blueprint(json_routes, url_prefix='/json/')


print("Started!!")