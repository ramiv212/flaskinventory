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
	itemdict2 = dictionaries.itemdict2
	audio_list = []
	video_list = []
	lighting_list = []
	rigging_list = []
	other_list = []

	for item in itemdict2:
			if dictionaries.itemdict2[item][5] == 'Audio':
				audio_list.append(item)
			elif dictionaries.itemdict2[item][5] == 'Video':
				video_list.append(item)
			elif dictionaries.itemdict2[item][5] == 'Lighting':
				lighting_list.append(item)
			elif dictionaries.itemdict2[item][5] == 'Rigging':
				rigging_list.append(item)
			elif dictionaries.itemdict2[item][5] == 'Other':
				other_list.append(item)

	print(itemdict2)

	return render_template("mobile/home.html",
		itemdict2=itemdict2,
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
		selected_event_id = dictionaries.eventdict[selected_event][0]
		selected_event_items = json.loads(dictionaries.eventdict[selected_event][5])['items']

		for item in selected_event_items:
			if dictionaries.itemdict2[item][5] == 'Audio':
				audio_list.append(item)
			elif dictionaries.itemdict2[item][5] == 'Video':
				video_list.append(item)
			elif dictionaries.itemdict2[item][5] == 'Lighting':
				lighting_list.append(item)
			elif dictionaries.itemdict2[item][5] == 'Rigging':
				rigging_list.append(item)
			elif dictionaries.itemdict2[item][5] == 'Other':
				other_list.append(item)

		return render_template("mobile/create-event.html",
			select_event_form=select_event_form,
			selected_event_items=selected_event_items,
			itemdict2=dictionaries.itemdict2,
			audio_list=audio_list,
			video_list=video_list,
			lighting_list=lighting_list,
			rigging_list=rigging_list,
			other_list=other_list)


	return render_template("mobile/create-event.html",
		select_event_form=select_event_form,
		selected_event_items=selected_event_items,
		itemdict2=dictionaries.itemdict2
		)

@mobile.route("/scanner", methods=['GET', 'POST'])
def mobile_scanner():
	return render_template("mobile/mobile_scanner.html")

