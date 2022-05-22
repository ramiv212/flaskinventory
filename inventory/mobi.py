from flask import render_template, redirect, url_for, flash, request, send_from_directory,Blueprint
from flask_login import login_required
from inventory.models import Item, Event
from inventory.forms import CreateEventForm,ItemInspectorForm,CreateItemForm,AddToEventForm,SelectEventForm
from inventory import db
from inventory.mybarcode import export_barcode
from inventory.resources import Dictionaries,Scan,Funcs
import json
import os
from sqlalchemy.orm import load_only


mobile = Blueprint('mobile',__name__)


@mobile.route("/", methods=['GET', 'POST'])
def mobile_home():

	dictionaries = Dictionaries()
	select_event_form = SelectEventForm()
	ID_item_dict = dictionaries.ID_item_dict
	audio_list = []
	video_list = []
	lighting_list = []
	rigging_list = []
	other_list = []

	for item in ID_item_dict:
			if dictionaries.ID_item_dict[item]['category'] == 'Audio':
				audio_list.append(item)
			elif dictionaries.ID_item_dict[item]['category'] == 'Video':
				video_list.append(item)
			elif dictionaries.ID_item_dict[item]['category'] == 'Lighting':
				lighting_list.append(item)
			elif dictionaries.ID_item_dict[item]['category'] == 'Rigging':
				rigging_list.append(item)
			elif dictionaries.ID_item_dict[item]['category'] == 'Other':
				other_list.append(item)

	print(ID_item_dict)

	return render_template("mobile/home.html",
		ID_item_dict=ID_item_dict,
		audio_list=audio_list,
		video_list=video_list,
		lighting_list=lighting_list,
		rigging_list=rigging_list,
		other_list=other_list)
		


@mobile.route("/events", methods=['GET', 'POST'])
def mobile_events():
	dictionaries = Dictionaries()
	select_event_form = SelectEventForm()
	selected_event = None
	selected_event_id = None
	selected_event_items = []
	audio_list = []
	video_list = []
	lighting_list = []
	rigging_list = []
	other_list = []


	if select_event_form.submit.data and select_event_form.validate_on_submit():
		selected_event = select_event_form.event_field.data
		selected_event_id = dictionaries.eventdict[selected_event]
		selected_event_items = json.loads(dictionaries.eventdict[selected_event]['items'])

		for item in selected_event_items:
			if dictionaries.ID_item_dict[item]['category'] == 'Audio':
				audio_list.append(item)
			elif dictionaries.ID_item_dict[item]['category'] == 'Video':
				video_list.append(item)
			elif dictionaries.ID_item_dict[item]['category'] == 'Lighting':
				lighting_list.append(item)
			elif dictionaries.ID_item_dict[item]['category'] == 'Rigging':
				rigging_list.append(item)
			elif dictionaries.ID_item_dict[item]['category'] == 'Other':
				other_list.append(item)

		return render_template("mobile/create-event.html",
			select_event_form=select_event_form,
			selected_event_items=selected_event_items,
			ID_item_dict=dictionaries.ID_item_dict,
			audio_list=audio_list,
			video_list=video_list,
			lighting_list=lighting_list,
			rigging_list=rigging_list,
			other_list=other_list)


	return render_template("mobile/create-event.html",
		select_event_form=select_event_form,
		selected_event_items=selected_event_items,
		ID_item_dict=dictionaries.ID_item_dict
		)

@mobile.route("/scanner", methods=['GET', 'POST'])
def mobile_scanner():
	return render_template("mobile/mobile_scanner.html")


@login_required
@mobile.route('item/<barcode>', methods=['GET', 'POST'])
def item_page(barcode):
	dictionaries = Dictionaries()
	inspector_form = ItemInspectorForm()
	barcodedict = dictionaries.barcodedict
	funcs = Funcs()

	# function to update item
	if inspector_form.submit.data and inspector_form.validate_on_submit():
		funcs.update_item(inspector_form)

		flash(f'{inspector_form.name.data} was updated.')

		return render_template("mobile/item.html", 
			barcodedict = barcodedict,
			barcode = barcode,
			inspector_form = inspector_form)
	else:
		print(f"Did not validate: {inspector_form.validate_on_submit()}")
		print(inspector_form.submit.data)
		for err_msg in inspector_form.errors.values():
			print(err_msg)


	if barcode in barcodedict:

		inspector_form.ID.data = barcodedict[barcode]['ID']
		inspector_form.barcode.data = barcode
		inspector_form.serial.data = barcodedict[barcode]['serial']
		inspector_form.manufacturer.data = barcodedict[barcode]['manufacturer']
		inspector_form.name.data = barcodedict[barcode]['name']
		inspector_form.category.data = barcodedict[barcode]['category']
		inspector_form.storage.data = barcodedict[barcode]['storage']
		inspector_form.status.data = barcodedict[barcode]['status']
		inspector_form.notes.data = barcodedict[barcode]['notes']

		return render_template("mobile/item.html", 
			barcodedict = barcodedict,
			barcode = barcode,
			inspector_form = inspector_form)

	else:
		return f"<h2>{barcode} is not in the database.<h2>"

