from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)

UPLOAD_FOLDER = f"{os.getcwd()}/inventory/uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.getcwd()}/inventory/uploads/inventory.db'
app.config['SECRET_KEY'] = '1c3c7811fb09da0e1cadcb7e'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

csrf = CSRFProtect(app)
db = SQLAlchemy(app)

# from inventory import routes


from .home_page import homepage
from .events_page import eventspage
from .json_routes import jsonroutes
from .resources import json_routes
from .admin import adminpage
from .auth import authorize

app.register_blueprint(homepage, url_prefix='/')
app.register_blueprint(eventspage, url_prefix='/events/')
app.register_blueprint(jsonroutes, url_prefix='/json-routes/')
app.register_blueprint(json_routes, url_prefix='/json/')
app.register_blueprint(adminpage, url_prefix='/admin/')
app.register_blueprint(authorize, url_prefix='/auth/')


print("Started!!")
