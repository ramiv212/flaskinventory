from flask import render_template, redirect, url_for, flash, request, send_from_directory
from inventory.models import Item, Event
from inventory.forms import CreateEventForm,ItemInspectorForm,CreateItemForm,AddToEventForm,Blueprint
from inventory import db
from inventory.mybarcode import export_barcode
import json
from sqlalchemy.orm import load_only
from wtforms import SelectField
import os



jsonroutes = Blueprint("jsonroutes",__name__)



# this file path is for writing the JSON file to the static folder
json_file_path = f'{os.getcwd()}/inventory/static/json_data.json'

# this file path is for writing the JSON file to the static folder
json_barcode_file_path = f'{os.getcwd()}/inventory/static/json_barcode_data.json'

# this file path is to create a route for the JSON file to be rendered to so that it can be accessed
json_file_path2 = f'{os.getcwd()}/inventory/static/'

# this file path is for writing the JSON file to the static folder
json_event_file_path = f'{os.getcwd()}/inventory/static/json_event_data.json'



# render JSON file as a page
@jsonroutes.route('/json_data.json')
def mytopo_json():
    return send_from_directory(json_file_path2, "json_data.json") 


# render barcode JSON file as a page
@jsonroutes.route('/json_barcode_data.json')
def mytopo_barcode_json():
    return send_from_directory(json_file_path2, "json_barcode_data.json") 


# render event JSON file as a page
@jsonroutes.route('/json_event_data.json')
def mytopo_event_barcode_json():
    return send_from_directory(json_file_path2, "json_event_data.json") 